# --- Environment Setup ---
# Load environment variables from .env file before anything else
from dotenv import load_dotenv
load_dotenv()

# --- Standard Library Imports ---
import io
import json
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List

# --- Third-Party Imports ---
import joblib
import pandas as pd
from fastapi import FastAPI, File, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
# from weasyprint import HTML, CSS  # Commented out due to Windows compatibility issues

# --- Local Application Imports ---
# Use relative imports (the leading dot) to find modules in the same directory.
from .agents.monitoring_agent import check_for_drift, load_baseline_data
from .agents.recommendation_agent import (
    generate_html_report, generate_recommendations_report
)
from .inference_preprocess import preprocess_inference
from .schema import EmailRequest

app = FastAPI(title="Churn Prediction API")

# Add CORS middleware to allow all origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Use absolute paths for model files
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "xgb_pipeline.joblib")
xgb_pipe = joblib.load(model_path)

threshold_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "xgb_threshold.json")
with open(threshold_path) as f:
    xgb_threshold = json.load(f)["best_threshold"]



# Removed /predict endpoint - using /predict_churn for all predictions


@app.post("/predict_churn")
async def predict_churn(
    file: UploadFile = File(...),
    k_value: int = Query(default=None, description="Number of top churners to return (optional)")
):
    """
    Predict churn from uploaded CSV file.
    
    Args:
        file: CSV file containing customer data
        k_value: Optional parameter to return top K churners
    
    Returns:
        JSON response with original data augmented with churn predictions
    """
    # Read uploaded CSV file
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    
    # Store original data for response
    original_data = df.copy()
    
    # Preprocess the data
    df_processed = preprocess_inference(df)
    
    # Get churn probabilities
    proba = xgb_pipe.predict_proba(df_processed)[:, 1]
    
    # Apply threshold to get class predictions
    preds = [int(p >= xgb_threshold) for p in proba]
    
    # Add predictions to original data
    original_data['churn_probability'] = proba
    original_data['prediction'] = preds
    
    # If k_value is provided, return top K churners
    if k_value is not None and k_value > 0:
        # Sort by churn probability in descending order and get top K
        top_k_data = original_data.nlargest(k_value, 'churn_probability')
        result_data = top_k_data.to_dict('records')
    else:
        # Return all data with predictions
        result_data = original_data.to_dict('records')
    
    # Generate summary
    total = len(preds)
    churn_count = sum(preds)
    no_churn_count = total - churn_count
    
    summary = {
        "total_customers": total,
        "churn_count": churn_count,
        "no_churn_count": no_churn_count,
        "churn_percentage": round(100 * churn_count / total, 2) if total > 0 else 0,
        "no_churn_percentage": round(100 * no_churn_count / total, 2) if total > 0 else 0
    }
    
    return {
        "data": result_data,
        "summary": summary,
        "threshold_used": xgb_threshold,
        "k_value_applied": k_value
    }


@app.post("/generate_recommendations_report")
async def generate_recommendations_report_endpoint(churners_data: List[Dict[str, Any]]):
    """
    Generate actionable recommendations report for top-K churners.
    
    Args:
        churners_data: List of dictionaries containing customer data with churn predictions
        
    Returns:
        JSON response with success status and report path
    """
    try:
        # Convert input data to DataFrame
        df_churners = pd.DataFrame(churners_data)
        
        # Load baseline data for drift analysis
        try:
            baseline_df = load_baseline_data()
            # Perform drift analysis
            drift_results = check_for_drift(df_churners, baseline_df)
        except Exception as e:
            print(f"Warning: Could not perform drift analysis: {e}")
            drift_results = None
        
        # Generate recommendations using the agent
        recommendations = generate_recommendations_report(df_churners)
        
        # Calculate total revenue at risk
        total_revenue_at_risk = sum(rec['revenue_at_risk'] for rec in recommendations)
        top_k_customers = len(df_churners)
        
        # Calculate critical cases
        critical_cases = sum(1 for r in recommendations if r['urgency_level'] == 'CRITICAL')
        
        # Calculate average churn probability for the top-K group
        avg_churn_prob = sum(r['churn_probability'] for r in recommendations) / len(recommendations) if recommendations else 0
        
        # Generate HTML report with drift analysis
        html_content = generate_html_report(
            recommendations=recommendations,
            total_customers=top_k_customers,
            total_revenue_at_risk=total_revenue_at_risk,
            drift_results=drift_results,
            critical_cases=critical_cases,
            avg_churn_prob=avg_churn_prob
        )
        
        # Save the report directly to the frontend directory where it's used
        project_root = os.path.dirname(os.path.dirname(__file__))
        report_path = os.path.join(project_root, "telecom_churn_frontend", "drift_report.html")
        
        # Write the report file
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return {
            "success": True,
            "message": "Recommendations report generated successfully",
            "report_path": report_path,
            "total_customers": top_k_customers,
            "high_risk_customers": len(recommendations),
            "total_revenue_at_risk": round(total_revenue_at_risk, 2),
            "critical_cases": critical_cases,
            "recommendations_preview": recommendations[:3]  # First 3 recommendations for preview
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error generating recommendations report: {str(e)}",
            "error_details": str(e)
        }


@app.post("/send_email")
async def send_email(email_data: EmailRequest):
    """
    Send the generated drift report via email with CSV attachment.
    
    Args:
        email_data: EmailRequest containing recipient_email and results_csv_path
        
    Returns:
        JSON response indicating success or failure
    """
    try:
        recipient_email = email_data.recipient_email
        results_csv_path = email_data.results_csv_path
        
        if not recipient_email:
            return {
                "success": False,
                "message": "recipient_email is required",
                "error": "Missing recipient email address"
            }
        
        # Email configuration from environment variables
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        email_username = os.getenv("EMAIL_USERNAME")
        email_password = os.getenv("EMAIL_PASSWORD")
        
        if not email_username or not email_password:
            return {
                "success": False,
                "message": "Email credentials not configured. Please set EMAIL_USERNAME and EMAIL_PASSWORD environment variables.",
                "error": "EMAIL_USERNAME and EMAIL_PASSWORD environment variables are required"
            }
        
        # Read the drift report HTML content
        # Try multiple possible locations for the drift report
        project_root = os.path.dirname(os.path.dirname(__file__))
        possible_report_paths = [
            os.path.join(project_root, "telecom_churn_frontend", "drift_report.html"),
            os.path.join(project_root, "reports", "drift_report.html"),
            "drift_report.html"  # Current directory fallback
        ]
        
        report_path = None
        html_content = None
        
        print(f"DEBUG - Looking for drift report in multiple locations...")
        for path in possible_report_paths:
            print(f"DEBUG - Checking: {path}")
            print(f"DEBUG - File exists: {os.path.exists(path)}")
            
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if this is a meaningful report (not empty or minimal)
                    if len(content.strip()) > 100 and "Churn Prediction" in content:
                        report_path = path
                        html_content = content
                        print(f"DEBUG - Found valid drift report at: {path}")
                        print(f"DEBUG - Report length: {len(html_content)} characters")
                        break
                    else:
                        print(f"DEBUG - File exists but appears to be empty/minimal at: {path}")
                        
                except Exception as e:
                    print(f"DEBUG - Error reading file at {path}: {e}")
                    continue
        
        if not report_path or not html_content:
            print(f"DEBUG - No valid drift report found!")
            return {
                "success": False,
                "message": "No valid drift report found. Please generate a report first.",
                "error": f"No valid report file found in any of the expected locations: {possible_report_paths}"
            }
        
        # Generate report URL for online viewing
        print(f"DEBUG - Preparing report for online viewing...")
        report_url = f"http://localhost:3000/drift_report.html"
        pdf_content = None  # Not generating PDF due to Windows compatibility issues
        
        # Create MIMEMultipart email
        msg = MIMEMultipart('alternative')
        msg['From'] = email_username
        msg['To'] = recipient_email
        msg['Subject'] = "Churn Prediction Report & Recommendations"
        
        # Create HTML part (simplified version for email)
        email_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>📊 Churn Prediction Report</h2>
            <p>Dear Team,</p>
            <p>Your comprehensive churn prediction report with actionable recommendations and data drift analysis is ready for viewing.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>📈 Report Highlights:</h3>
                <ul>
                    <li><strong>Customer Analysis:</strong> Complete churn risk assessment</li>
                    <li><strong>AI Recommendations:</strong> Personalized retention strategies</li>
                    <li><strong>Data Drift Analysis:</strong> Model performance monitoring</li>
                    <li><strong>Visual Analytics:</strong> Interactive charts and graphs</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{report_url}" 
                   style="background-color: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                    📊 View Complete Report
                </a>
            </div>
            
            <p><strong>🔗 Report Link:</strong> <a href="{report_url}">{report_url}</a></p>
            
            <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>💡 Note:</strong> The report contains interactive visualizations and detailed analysis. For the best viewing experience, open the link in your web browser.</p>
            </div>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
            <p style="font-size: 12px; color: #666;">
                Generated by Telecom Churn Prediction Platform<br>
                <em>AI-Powered Customer Retention Analytics</em>
            </p>
        </body>
        </html>
        """
        
        html_part = MIMEText(email_html, 'html')
        msg.attach(html_part)
        
        # Note: PDF attachment removed due to Windows compatibility issues with WeasyPrint
        print(f"DEBUG - Using online report link instead of PDF attachment")
        
        # Attach CSV file if provided and exists
        if results_csv_path and os.path.exists(results_csv_path):
            try:
                with open(results_csv_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                
                # Add header for CSV attachment
                filename = os.path.basename(results_csv_path)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )
                
                msg.attach(part)
                
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Error attaching CSV file: {str(e)}",
                    "error": str(e)
                }
        
        # Send email
        try:
            print(f"DEBUG - Connecting to SMTP server: {smtp_server}:{smtp_port}")
            server = smtplib.SMTP(smtp_server, smtp_port)
            print(f"DEBUG - Connected to SMTP server")
            
            print(f"DEBUG - Starting TLS...")
            server.starttls()  # Enable security
            print(f"DEBUG - TLS started")
            
            print(f"DEBUG - Logging in with username: {email_username}")
            server.login(email_username, email_password)
            print(f"DEBUG - Login successful")
            
            text = msg.as_string()
            print(f"DEBUG - Sending email to: {recipient_email}")
            server.sendmail(email_username, recipient_email, text)
            print(f"DEBUG - Email sent successfully")
            
            server.quit()
            print(f"DEBUG - SMTP connection closed")
            
            attachments = []
            if results_csv_path and os.path.exists(results_csv_path):
                attachments.append(os.path.basename(results_csv_path))
                
            return {
                "success": True,
                "message": "Email sent successfully with report link",
                "recipient": recipient_email,
                "attachments": attachments,
                "smtp_server": smtp_server,
                "report_url": report_url
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "message": "SMTP authentication failed",
                "error": "Invalid email credentials or app password required"
            }
        except smtplib.SMTPRecipientsRefused:
            return {
                "success": False,
                "message": "Recipient email address refused",
                "error": f"Invalid recipient email: {recipient_email}"
            }
        except smtplib.SMTPException as e:
            return {
                "success": False,
                "message": f"SMTP error occurred: {str(e)}",
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Unexpected error sending email: {str(e)}",
                "error": str(e)
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing email request: {str(e)}",
            "error": str(e)
        }


@app.get("/")
def root():
    return {"status": "ok", "service": "churn-api", "endpoints": ["/predict_churn", "/generate_recommendations_report", "/send_email", "/docs"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)