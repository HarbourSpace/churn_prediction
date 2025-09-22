# Telecom Churn Prediction Platform

A comprehensive AI-powered telecom churn prediction platform with FastAPI backend, modern web frontend, intelligent recommendations, dynamic model monitoring, and automated reporting capabilities.

## 🏗️ **Project Structure**

```
churn_prediction/
├── api/                        # 🚀 FastAPI Backend
│   ├── main.py                # Main API application
│   ├── schema.py              # Pydantic schemas
│   ├── inference_preprocess.py # Data preprocessing
│   └── agents/                # AI agents
│       ├── recommendation_agent.py
│       └── monitoring_agent.py
├── telecom_churn_frontend/     # 🌐 Web Frontend
│   ├── index.html             # Main web interface
│   ├── style.css              # Styling
│   ├── app.js                 # Frontend logic
│   └── drift_report.html      # Generated reports
├── train/                      # 🤖 Model Training
│   ├── train.py               # Training pipeline
│   ├── prepare_telco.py       # Data preparation
│   └── utils.py               # Training utilities
├── data/                       # 📊 Data Files
│   ├── telco_raw.csv          # Raw customer data
│   ├── telco_train.csv        # Training dataset
│   ├── telco_scoring_sample.csv # Sample scoring data
│   └── baseline_train.pkl     # Baseline for drift detection
├── models/                     # 🎯 Trained Models
│   ├── xgb_pipeline.joblib    # XGBoost model pipeline
│   └── xgb_threshold.json     # Optimal threshold
├── app/                        # 📱 Alternative UI
│   └── streamlit_app.py       # Streamlit interface
├── create_baseline.py          # Baseline data creation
├── requirements.txt            # Python dependencies
├── Makefile                    # Build automation
└── README.md                   # This documentation
```

## ✅ **Features**

### 🚀 **Core Prediction Engine**
- **FastAPI Backend**: High-performance REST API with automatic documentation
- **XGBoost Model**: Pre-trained churn prediction with optimized thresholds
- **CSV File Upload**: Batch processing of customer data
- **Top-K Selection**: Configurable ranking of highest-risk customers

### 🤖 **AI-Powered Agents**
- **Recommendation Agent**: Generates personalized retention strategies
- **Monitoring Agent**: Real-time data drift detection and visualization
- **Dynamic Reports**: HTML reports with embedded charts and insights

### 🎨 **Modern Web Frontend**
- **Responsive Design**: Modern glassmorphism UI with mobile support
- **File Upload**: Drag-and-drop CSV upload with validation
- **Interactive Results**: Risk level badges, summary cards, and data tables
- **Real-time Feedback**: Toast notifications and loading states

### 📊 **Advanced Analytics**
- **Data Drift Detection**: Monitors numerical and categorical feature drift
- **Visual Analytics**: Base64-encoded charts for distribution comparisons
- **Risk Stratification**: CRITICAL/HIGH/MEDIUM/LOW risk categorization
- **Revenue Impact**: Calculates potential revenue at risk

### 📧 **Communication & Reporting**
- **Email Integration**: SMTP-based report delivery with attachments
- **HTML Reports**: Professional styled reports with CSS
- **CSV Export**: Downloadable prediction results
- **Report Viewing**: In-browser drift report visualization

## 🚀 **Quickstart**

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Data Preparation
```bash
# Prepare training and scoring files
python train/prepare_telco.py

# Create baseline data for drift detection
python create_baseline.py

# Train the model
python train/train.py
```

### 3. Start the Platform
```bash
# Option 1: Using Makefile
make api          # Start API server
make frontend     # Start web frontend (in another terminal)

# Option 2: Manual commands
# Terminal 1: Start the FastAPI backend (from the main project folder)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start the frontend server
cd telecom_churn_frontend
python -m http.server 3000
```

### 4. Access the Platform
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health**: http://localhost:8000

## 📡 **Backend API**

The FastAPI backend provides three main endpoints:

### 1. Churn Prediction
```http
POST /predict_churn?k_value=10
Content-Type: multipart/form-data

# Upload CSV file with customer data
# Returns top-K customers ranked by churn risk
```

### 2. AI Recommendations
```http
POST /generate_recommendations_report
Content-Type: application/json

# Generates actionable retention strategies
# Creates HTML report with drift monitoring
```

### 3. Email Reports
```http
POST /send_email
Content-Type: application/json

{
  "recipient_email": "manager@company.com",
  "results_csv_path": "path/to/results.csv"
}
```

## 🎨 **Frontend Web App**

The modern web interface provides:

- **File Upload**: Drag-and-drop CSV upload with validation
- **Risk Analysis**: Interactive results with risk level badges
- **Report Generation**: One-click recommendations and drift reports
- **Email Integration**: Send reports directly from the interface

## 🛠️ **Development**

### **Using Makefile**
```bash
make help         # Show all available commands
make install      # Install dependencies
make prepare      # Prepare data
make train        # Train model
make baseline     # Create baseline data
make api          # Start API server
make frontend     # Start web frontend
make ui           # Start Streamlit UI
make test         # Run tests
make clean        # Clean cache files
```

### **Manual Commands**
```bash
# Install dependencies
pip install -r requirements.txt

# Prepare data
python train/prepare_telco.py

# Train model
python train/train.py

# Create baseline
python create_baseline.py

# Start API
uvicorn api.main:app --reload --port 8000

# Start frontend
cd telecom_churn_frontend && python -m http.server 3000

# Start Streamlit UI
streamlit run app/streamlit_app.py --server.port 8501
```

## 📧 **Email Configuration**

To enable email functionality, set these environment variables:

```bash
# Windows
set EMAIL_USERNAME=your-email@gmail.com
set EMAIL_PASSWORD=your-app-password
set SMTP_SERVER=smtp.gmail.com
set SMTP_PORT=587

# macOS/Linux
export EMAIL_USERNAME=your-email@gmail.com
export EMAIL_PASSWORD=your-app-password
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Import Errors**: Ensure you're in the correct directory when running commands
2. **Model Not Found**: Run `python train/train.py` to create model files
3. **Port Already in Use**: Change ports in Makefile or kill existing processes
4. **Email Not Working**: Check environment variables and use app passwords for Gmail

### **Data Requirements**

Your CSV file should contain these columns:
- `customerID`, `gender`, `SeniorCitizen`, `Partner`, `Dependents`
- `tenure`, `PhoneService`, `MultipleLines`, `InternetService`
- `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`
- `StreamingTV`, `StreamingMovies`, `Contract`, `PaperlessBilling`
- `PaymentMethod`, `MonthlyCharges`, `TotalCharges`

## 📊 **Model Performance**

The XGBoost model achieves:
- **Accuracy**: ~80%
- **Precision**: ~65%
- **Recall**: ~55%
- **F1-Score**: ~60%
- **ROC-AUC**: ~85%

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.
