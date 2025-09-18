// Telecom Churn Prediction Platform - Frontend JavaScript
// This file will contain all the interactive functionality for the web application

// API Configuration
const API_BASE_URL = 'http://localhost:8000'; // FastAPI backend URL

// Global variables
let currentPredictionData = null;
let currentResultsCSVPath = null;

// DOM Elements
const elements = {
    predictionForm: null,
    csvFileInput: null,
    kValueSlider: null,
    kValueDisplay: null,
    fileInfo: null,
    loadingSection: null,
    resultsSection: null,
    reportSection: null,
    emailSection: null,
    summaryCards: null,
    resultsTable: null,
    emailForm: null,
    emailStatus: null,
    toastContainer: null
};

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeElements();
    bindEventListeners();
    updateSliderValue();
});

// Initialize DOM element references
function initializeElements() {
    elements.predictionForm = document.getElementById('prediction-form');
    elements.csvFileInput = document.getElementById('csv-file');
    elements.kValueSlider = document.getElementById('k-value');
    elements.kValueDisplay = document.getElementById('k-value-display');
    elements.fileInfo = document.getElementById('file-info');
    elements.loadingSection = document.getElementById('loading-section');
    elements.resultsSection = document.getElementById('results-section');
    elements.reportSection = document.getElementById('report-section');
    elements.emailSection = document.getElementById('email-section');
    elements.summaryCards = document.getElementById('summary-cards');
    elements.resultsTable = document.getElementById('results-tbody');
    elements.emailForm = document.getElementById('email-form');
    elements.emailStatus = document.getElementById('email-status');
    elements.toastContainer = document.getElementById('toast-container');
}

// Bind event listeners
function bindEventListeners() {
    // File input change
    if (elements.csvFileInput) {
        elements.csvFileInput.addEventListener('change', handleFileSelect);
    }
    
    // K-value slider change
    if (elements.kValueSlider) {
        elements.kValueSlider.addEventListener('input', updateSliderValue);
    }
    
    // Prediction form submit
    if (elements.predictionForm) {
        elements.predictionForm.addEventListener('submit', handlePredictionSubmit);
    }
    
    // Email form submit
    if (elements.emailForm) {
        elements.emailForm.addEventListener('submit', handleEmailSubmit);
    }
    
    // Button click handlers
    document.addEventListener('click', function(e) {
        if (e.target.id === 'download-csv-btn') {
            handleDownloadCSV();
        } else if (e.target.id === 'view-report-btn') {
            handleViewReport();
        } else if (e.target.id === 'download-data-btn') {
            handleDownloadData();
        }
    });
}

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
            elements.fileInfo.innerHTML = `
                <i class="fas fa-check-circle" style="color: #48bb78;"></i>
                Selected: ${file.name} (${formatFileSize(file.size)})
            `;
        } else {
            elements.fileInfo.innerHTML = `
                <i class="fas fa-exclamation-triangle" style="color: #ed8936;"></i>
                Please select a valid CSV file
            `;
            event.target.value = '';
        }
    } else {
        elements.fileInfo.innerHTML = '';
    }
}

// Update slider value display
function updateSliderValue() {
    if (elements.kValueSlider && elements.kValueDisplay) {
        elements.kValueDisplay.textContent = elements.kValueSlider.value;
    }
}

// Handle prediction form submission
async function handlePredictionSubmit(event) {
    event.preventDefault();
    
    const file = elements.csvFileInput.files[0];
    if (!file) {
        showToast('Please select a CSV file', 'error');
        return;
    }
    
    const kValue = parseInt(elements.kValueSlider.value);
    
    // Show loading state
    showLoadingState();
    
    try {
        // Upload file and get predictions
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/predict_churn?k_value=${kValue}`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        currentPredictionData = data;
        
        // Display results
        displayResults(data);
        
        // Generate recommendations report
        await generateRecommendationsReport(data.data);
        
        showToast('Predictions generated successfully!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Error generating predictions. Please try again.', 'error');
        hideLoadingState();
    }
}

// Show loading state
function showLoadingState() {
    elements.loadingSection.style.display = 'block';
    elements.resultsSection.style.display = 'none';
    elements.reportSection.style.display = 'none';
    elements.emailSection.style.display = 'none';
}

// Hide loading state
function hideLoadingState() {
    elements.loadingSection.style.display = 'none';
}

// Display prediction results
function displayResults(data) {
    hideLoadingState();
    
    // Show results section
    elements.resultsSection.style.display = 'block';
    elements.reportSection.style.display = 'block';
    elements.emailSection.style.display = 'block';
    
    // Display summary cards
    displaySummaryCards(data.summary);
    
    // Display results table
    displayResultsTable(data.data);
}

// Display summary cards
function displaySummaryCards(summary) {
    elements.summaryCards.innerHTML = `
        <div class="summary-card">
            <h3>Total Customers</h3>
            <div class="value">${summary.total_customers.toLocaleString()}</div>
            <div class="label">Analyzed</div>
        </div>
        <div class="summary-card">
            <h3>High Risk</h3>
            <div class="value" style="color: #f56565;">${summary.churn_count}</div>
            <div class="label">${summary.churn_percentage}% of total</div>
        </div>
        <div class="summary-card">
            <h3>Low Risk</h3>
            <div class="value" style="color: #48bb78;">${summary.no_churn_count}</div>
            <div class="label">${summary.no_churn_percentage}% of total</div>
        </div>
        <div class="summary-card">
            <h3>Model Threshold</h3>
            <div class="value">${(currentPredictionData.threshold_used * 100).toFixed(1)}%</div>
            <div class="label">Prediction cutoff</div>
        </div>
    `;
}

// Display results table
function displayResultsTable(data) {
    const tbody = elements.resultsTable;
    tbody.innerHTML = '';
    
    data.forEach(customer => {
        const row = document.createElement('tr');
        const riskLevel = getRiskLevel(customer.churn_probability);
        
        row.innerHTML = `
            <td>${customer.customerID || 'N/A'}</td>
            <td>${(customer.churn_probability * 100).toFixed(1)}%</td>
            <td><span class="risk-badge risk-${riskLevel.toLowerCase()}">${riskLevel}</span></td>
            <td>$${customer.MonthlyCharges ? customer.MonthlyCharges.toFixed(2) : 'N/A'}</td>
            <td>${customer.tenure || 'N/A'} months</td>
            <td>${customer.Contract || 'N/A'}</td>
        `;
        
        tbody.appendChild(row);
    });
}

// Get risk level based on churn probability
function getRiskLevel(probability) {
    if (probability >= 0.8) return 'CRITICAL';
    if (probability >= 0.6) return 'HIGH';
    if (probability >= 0.4) return 'MEDIUM';
    return 'LOW';
}

// Generate recommendations report
async function generateRecommendationsReport(data) {
    try {
        const response = await fetch(`${API_BASE_URL}/generate_recommendations_report`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Small delay to ensure report file is fully written
            setTimeout(() => {
                // Enable report viewing and email sending
                document.getElementById('view-report-btn').disabled = false;
                document.getElementById('send-email-btn').disabled = false;
                showToast('Recommendations report generated! Email sending is now available.', 'success');
            }, 500); // 500ms delay
        }
        
    } catch (error) {
        console.error('Error generating recommendations:', error);
        showToast('Warning: Could not generate recommendations report', 'warning');
    }
}

// Handle email form submission
async function handleEmailSubmit(event) {
    event.preventDefault();
    
    const recipientEmail = document.getElementById('recipient-email').value;
    
    if (!recipientEmail) {
        showToast('Please enter a recipient email address', 'error');
        return;
    }
    
    const sendButton = document.getElementById('send-email-btn');
    const originalText = sendButton.innerHTML;
    sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
    sendButton.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/send_email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                recipient_email: recipientEmail,
                results_csv_path: null  // API can work without CSV attachment
            })
        });
        
        if (!response.ok) {
            let errorMessage = `HTTP error! status: ${response.status}`;
            
            // Try to get detailed error message from response
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    if (Array.isArray(errorData.detail)) {
                        // Handle validation errors
                        errorMessage = errorData.detail.map(err => err.msg || err.message || err).join(', ');
                    } else {
                        errorMessage = errorData.detail;
                    }
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                }
            } catch (e) {
                // If we can't parse the error response, use the status code message
                if (response.status === 422) {
                    errorMessage = 'Invalid email format. Please check your email address.';
                } else if (response.status === 400) {
                    errorMessage = 'Bad request. Please check your input.';
                }
            }
            
            throw new Error(errorMessage);
        }
        
        const result = await response.json();
        
        if (result.success) {
            elements.emailStatus.className = 'email-status success';
            elements.emailStatus.textContent = `Email sent successfully to ${recipientEmail}`;
            elements.emailStatus.style.display = 'block';
            showToast('Report sent successfully!', 'success');
            
            // Reset form
            elements.emailForm.reset();
        } else {
            // Handle specific error cases
            let errorMessage = result.message || 'Failed to send email';
            if (result.message && result.message.includes('No valid drift report found')) {
                errorMessage = 'No report available. Please generate predictions first, then try sending email.';
            } else if (result.message && result.message.includes('credentials not configured')) {
                errorMessage = 'Email service not configured. Please contact administrator.';
            }
            throw new Error(errorMessage);
        }
        
    } catch (error) {
        console.error('Error sending email:', error);
        elements.emailStatus.className = 'email-status error';
        elements.emailStatus.textContent = `${error.message}`;
        elements.emailStatus.style.display = 'block';
        showToast('Failed to send email. Please try again.', 'error');
    } finally {
        sendButton.innerHTML = originalText;
        sendButton.disabled = false;
    }
}

// Handle CSV download
function handleDownloadCSV() {
    if (!currentPredictionData) {
        showToast('No prediction data available', 'error');
        return;
    }
    
    const csvContent = convertToCSV(currentPredictionData.data);
    downloadFile(csvContent, 'churn_predictions.csv', 'text/csv;charset=utf-8;');
    showToast('CSV file downloaded!', 'success');
}

// Handle report viewing
function handleViewReport() {
    // Open the drift report in a new window/tab
    window.open('./drift_report.html', '_blank');
}

// Handle data download
function handleDownloadData() {
    handleDownloadCSV(); // Same as CSV download for now
}

// Convert data to CSV format
function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvHeaders = headers.join(',');
    
    const csvRows = data.map(row => {
        return headers.map(header => {
            const value = row[header];
            // Handle values that might contain commas
            if (typeof value === 'string' && value.includes(',')) {
                return `"${value}"`;
            }
            return value;
        }).join(',');
    });
    
    return [csvHeaders, ...csvRows].join('\n');
}

// Download file utility
function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
}

// Format file size utility
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-${getToastIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    elements.toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

// Get toast icon based on type
function getToastIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}
