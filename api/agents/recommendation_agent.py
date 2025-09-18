import pandas as pd
from typing import List, Dict, Any
from datetime import datetime


def generate_recommendations_report(df_churners: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Generate personalized retention recommendations for top-K churners.
    
    Args:
        df_churners: DataFrame containing customer data with churn predictions
        
    Returns:
        List of dictionaries containing customer details and recommendations
    """
    recommendations = []
    
    for _, customer in df_churners.iterrows():
        customer_id = customer.get('customerID', 'Unknown')
        churn_prob = customer.get('churn_probability', 0)
        
        # Extract key features for recommendation logic
        contract = customer.get('Contract', 'Unknown')
        internet_service = customer.get('InternetService', 'Unknown')
        monthly_charges = customer.get('MonthlyCharges', 0)
        tenure = customer.get('tenure', 0)
        payment_method = customer.get('PaymentMethod', 'Unknown')
        tech_support = customer.get('TechSupport', 'Unknown')
        online_security = customer.get('OnlineSecurity', 'Unknown')
        online_backup = customer.get('OnlineBackup', 'Unknown')
        device_protection = customer.get('DeviceProtection', 'Unknown')
        streaming_tv = customer.get('StreamingTV', 'Unknown')
        streaming_movies = customer.get('StreamingMovies', 'Unknown')
        
        # Generate personalized recommendations based on customer profile
        recommendation_text = _generate_personalized_recommendation(
            contract, internet_service, monthly_charges, tenure, payment_method,
            tech_support, online_security, online_backup, device_protection,
            streaming_tv, streaming_movies, churn_prob
        )
        
        # Calculate urgency level
        urgency = _calculate_urgency_level(churn_prob, tenure)
        
        # Estimate potential revenue at risk
        revenue_at_risk = monthly_charges * 12  # Annual revenue
        
        recommendations.append({
            'customer_id': customer_id,
            'churn_probability': round(churn_prob * 100, 2),
            'urgency_level': urgency,
            'revenue_at_risk': round(revenue_at_risk, 2),
            'recommendation': recommendation_text,
            'contract_type': contract,
            'monthly_charges': monthly_charges,
            'tenure_months': tenure,
            'internet_service': internet_service,
            'payment_method': payment_method
        })
    
    return recommendations


def _generate_personalized_recommendation(contract, internet_service, monthly_charges, 
                                        tenure, payment_method, tech_support, 
                                        online_security, online_backup, device_protection,
                                        streaming_tv, streaming_movies, churn_prob):
    """Generate personalized recommendation based on customer profile."""
    
    recommendations = []
    
    # Contract-based recommendations
    if contract == 'Month-to-month':
        if churn_prob > 0.7:
            recommendations.append("URGENT: Offer immediate 20% discount for 12-month contract commitment")
        else:
            recommendations.append("Offer 15% discount for 12-month contract upgrade")
    elif contract == 'One year':
        recommendations.append("Offer 10% discount for 24-month contract extension")
    
    # Pricing-based recommendations
    if monthly_charges > 80:
        recommendations.append("Consider premium retention package with added value services")
    elif monthly_charges > 50:
        recommendations.append("Offer mid-tier service bundle with 10% discount")
    else:
        recommendations.append("Provide loyalty discount and service upgrade options")
    
    # Tenure-based recommendations
    if tenure < 12:
        recommendations.append("Assign dedicated customer success manager for first-year support")
    elif tenure < 24:
        recommendations.append("Offer loyalty rewards and service enhancement consultation")
    else:
        recommendations.append("Recognize long-term loyalty with exclusive benefits program")
    
    # Service-specific recommendations
    if tech_support == 'No':
        recommendations.append("Offer complimentary tech support for 6 months")
    
    if online_security == 'No':
        recommendations.append("Provide free online security service trial")
    
    if online_backup == 'No':
        recommendations.append("Include free cloud backup service")
    
    if device_protection == 'No':
        recommendations.append("Offer device protection plan at 50% discount")
    
    # Entertainment services
    if streaming_tv == 'No' and streaming_movies == 'No':
        recommendations.append("Bundle streaming services at promotional rate")
    
    # Payment method optimization
    if payment_method == 'Electronic check':
        recommendations.append("Incentivize automatic payment setup with billing discount")
    
    # Internet service optimization
    if internet_service == 'DSL':
        recommendations.append("Offer fiber upgrade with installation incentives")
    
    return " | ".join(recommendations[:4])  # Limit to top 4 recommendations


def _calculate_urgency_level(churn_prob, tenure):
    """Calculate urgency level based on churn probability and tenure."""
    if churn_prob > 0.8:
        return "CRITICAL"
    elif churn_prob > 0.6:
        return "HIGH"
    elif churn_prob > 0.4:
        return "MEDIUM"
    else:
        return "LOW"


def generate_html_report(recommendations: List[Dict[str, Any]], 
                        total_customers: int, 
                        total_revenue_at_risk: float,
                        drift_results: Dict[str, Any] = None,
                        critical_cases: int = None,
                        avg_churn_prob: float = None) -> str:
    """
    Generate HTML report for the recommendations.
    
    Args:
        recommendations: List of recommendation dictionaries
        total_customers: Total number of customers analyzed
        total_revenue_at_risk: Total revenue at risk
        drift_results: Optional drift analysis results with visualizations
        
    Returns:
        HTML string for the report
    """
    
    # Use provided values or calculate from recommendations
    critical_count = critical_cases if critical_cases is not None else sum(1 for r in recommendations if r['urgency_level'] == 'CRITICAL')
    high_count = sum(1 for r in recommendations if r['urgency_level'] == 'HIGH')
    avg_churn_prob_value = avg_churn_prob if avg_churn_prob is not None else (sum(r['churn_probability'] for r in recommendations) / len(recommendations) if recommendations else 0)
    
    # Prepare drift analysis section
    drift_section = ""
    if drift_results and drift_results.get('drift_detected'):
        drift_warnings = drift_results.get('drift_warnings', [])
        visualizations = drift_results.get('visualizations', {})
        
        drift_section = f"""
            <div class="drift-analysis">
                <h2>🚨 Data Drift Analysis</h2>
                <div class="drift-warnings">
                    <h3>Drift Alerts</h3>
                    <ul class="warning-list">
                        {''.join(f'<li class="warning-item">{warning}</li>' for warning in drift_warnings)}
                    </ul>
                </div>
                
                <div class="drift-visualizations">
                    <h3>Distribution Comparisons</h3>
                    <div class="visualization-grid">
        """
        
        # Add visualizations
        for viz_name, viz_data in visualizations.items():
            if viz_data:
                clean_name = viz_name.replace('_', ' ').title()
                drift_section += f"""
                        <div class="visualization-item">
                            <h4>{clean_name}</h4>
                            <img src="data:image/png;base64,{viz_data}" alt="{clean_name}" class="drift-chart">
                        </div>
                """
        
        drift_section += """
                    </div>
                </div>
            </div>
        """
    elif drift_results:
        drift_section = """
            <div class="drift-analysis">
                <h2>✅ Data Drift Analysis</h2>
                <div class="no-drift-message">
                    <p>No significant data drift detected. The new data appears consistent with the training baseline.</p>
                </div>
            </div>
        """
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Churn Prediction - Actionable Recommendations Report</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
                color: #333;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }}
            .header p {{
                margin: 10px 0 0 0;
                font-size: 1.1em;
                opacity: 0.9;
            }}
            .summary {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                padding: 30px;
                background-color: #f8f9fa;
            }}
            .summary-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                text-align: center;
            }}
            .summary-card h3 {{
                margin: 0 0 10px 0;
                color: #666;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .summary-card .value {{
                font-size: 2em;
                font-weight: bold;
                color: #333;
            }}
            .critical {{ color: #dc3545; }}
            .high {{ color: #fd7e14; }}
            .medium {{ color: #ffc107; }}
            .low {{ color: #28a745; }}
            .recommendations {{
                padding: 30px;
            }}
            .recommendations h2 {{
                margin: 0 0 30px 0;
                color: #333;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }}
            .customer-card {{
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                margin-bottom: 20px;
                overflow: hidden;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }}
            .customer-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }}
            .customer-header {{
                padding: 20px;
                background-color: #f8f9fa;
                border-bottom: 1px solid #e9ecef;
                display: grid;
                grid-template-columns: 1fr auto auto auto;
                gap: 20px;
                align-items: center;
            }}
            .customer-id {{
                font-weight: bold;
                font-size: 1.1em;
            }}
            .urgency-badge {{
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.8em;
                font-weight: bold;
                text-transform: uppercase;
            }}
            .urgency-critical {{
                background-color: #dc3545;
                color: white;
            }}
            .urgency-high {{
                background-color: #fd7e14;
                color: white;
            }}
            .urgency-medium {{
                background-color: #ffc107;
                color: #333;
            }}
            .urgency-low {{
                background-color: #28a745;
                color: white;
            }}
            .churn-prob {{
                font-weight: bold;
                font-size: 1.1em;
            }}
            .revenue-risk {{
                color: #dc3545;
                font-weight: bold;
            }}
            .customer-details {{
                padding: 20px;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}
            .detail-group h4 {{
                margin: 0 0 10px 0;
                color: #666;
                font-size: 0.9em;
                text-transform: uppercase;
            }}
            .detail-item {{
                margin-bottom: 5px;
            }}
            .recommendation-text {{
                grid-column: 1 / -1;
                background-color: #e3f2fd;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #2196f3;
                margin-top: 15px;
            }}
            .recommendation-text h4 {{
                margin: 0 0 10px 0;
                color: #1976d2;
            }}
            .drift-analysis {{
                padding: 30px;
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                margin-bottom: 30px;
            }}
            .drift-warnings {{
                margin-bottom: 20px;
            }}
            .warning-list {{
                list-style-type: none;
                padding: 0;
            }}
            .warning-item {{
                background-color: #f8d7da;
                color: #721c24;
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 5px;
                border-left: 4px solid #dc3545;
            }}
            .no-drift-message {{
                background-color: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #28a745;
            }}
            .visualization-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            .visualization-item {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            .visualization-item h4 {{
                margin: 0 0 15px 0;
                color: #333;
                text-align: center;
            }}
            .drift-chart {{
                width: 100%;
                height: auto;
                border-radius: 5px;
            }}
            .footer {{
                background-color: #333;
                color: white;
                text-align: center;
                padding: 20px;
                font-size: 0.9em;
            }}
            @media (max-width: 768px) {{
                .customer-header {{
                    grid-template-columns: 1fr;
                    gap: 10px;
                    text-align: center;
                }}
                .customer-details {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Churn Prediction Report</h1>
                <p>Actionable Recommendations for Customer Retention</p>
                <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                <div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin-top: 20px; font-size: 0.9em;">
                    <p><strong>📊 Report Scope:</strong> This report analyzes the top {total_customers} highest-risk customers from your dataset. All customers shown here are predicted to have high churn probability based on our AI model.</p>
                </div>
            </div>
            
            <div class="summary">
                <div class="summary-card">
                    <h3>Top-K High-Risk Customers</h3>
                    <div class="value">{total_customers:,}</div>
                    <div style="font-size: 0.8em; color: #666; margin-top: 5px;">Analyzed in this report</div>
                </div>
                <div class="summary-card">
                    <h3>All High-Risk Customers</h3>
                    <div class="value critical">{len(recommendations):,}</div>
                    <div style="font-size: 0.8em; color: #666; margin-top: 5px;">100% of top-K group</div>
                </div>
                <div class="summary-card">
                    <h3>Critical Cases</h3>
                    <div class="value critical">{critical_count}</div>
                    <div style="font-size: 0.8em; color: #666; margin-top: 5px;">{(critical_count/len(recommendations)*100):.1f}% of high-risk</div>
                </div>
                <div class="summary-card">
                    <h3>Total Revenue at Risk</h3>
                    <div class="value">${total_revenue_at_risk:,.2f}</div>
                    <div style="font-size: 0.8em; color: #666; margin-top: 5px;">Annual potential loss</div>
                </div>
                <div class="summary-card">
                    <h3>Average Churn Probability</h3>
                    <div class="value">{avg_churn_prob_value:.1f}%</div>
                    <div style="font-size: 0.8em; color: #666; margin-top: 5px;">In high-risk group</div>
                </div>
            </div>
            
            {drift_section}
            
            <div class="recommendations">
                <h2>Individual Customer Recommendations</h2>
    """
    
    # Add individual customer recommendations
    for rec in recommendations:
        urgency_class = f"urgency-{rec['urgency_level'].lower()}"
        html_template += f"""
                <div class="customer-card">
                    <div class="customer-header">
                        <div class="customer-id">Customer: {rec['customer_id']}</div>
                        <div class="urgency-badge {urgency_class}">{rec['urgency_level']}</div>
                        <div class="churn-prob">{rec['churn_probability']}% Risk</div>
                        <div class="revenue-risk">${rec['revenue_at_risk']:,.2f}/year</div>
                    </div>
                    <div class="customer-details">
                        <div class="detail-group">
                            <h4>Account Information</h4>
                            <div class="detail-item"><strong>Contract:</strong> {rec['contract_type']}</div>
                            <div class="detail-item"><strong>Tenure:</strong> {rec['tenure_months']} months</div>
                            <div class="detail-item"><strong>Monthly Charges:</strong> ${rec['monthly_charges']:.2f}</div>
                        </div>
                        <div class="detail-group">
                            <h4>Service Details</h4>
                            <div class="detail-item"><strong>Internet:</strong> {rec['internet_service']}</div>
                            <div class="detail-item"><strong>Payment:</strong> {rec['payment_method']}</div>
                        </div>
                        <div class="recommendation-text">
                            <h4>Recommended Actions</h4>
                            <p>{rec['recommendation']}</p>
                        </div>
                    </div>
                </div>
        """
    
    html_template += """
            </div>
            
            <div class="footer">
                <p>This report was generated by the Churn Prediction AI System</p>
                <p>For questions or support, contact your data science team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_template
