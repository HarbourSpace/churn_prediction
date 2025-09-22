import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import io
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set matplotlib backend for server environments
plt.switch_backend('Agg')

def check_for_drift(new_data_df: pd.DataFrame, baseline_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Check for data drift between new data and baseline training data.
    
    Args:
        new_data_df: DataFrame containing new/current data
        baseline_df: DataFrame containing baseline training data
        
    Returns:
        Dictionary containing drift warnings and base64 encoded visualizations
    """
    
    # Key features to monitor
    numerical_features = ['tenure', 'MonthlyCharges', 'TotalCharges']
    categorical_features = ['Contract', 'InternetService', 'PaymentMethod', 'gender']
    
    drift_results = {
        'drift_detected': False,
        'drift_warnings': [],
        'numerical_drift': {},
        'categorical_drift': {},
        'visualizations': {},
        'summary_stats': {}
    }
    
    # Check numerical features for drift
    for feature in numerical_features:
        if feature in new_data_df.columns and feature in baseline_df.columns:
            drift_info = _check_numerical_drift(new_data_df, baseline_df, feature)
            drift_results['numerical_drift'][feature] = drift_info
            
            if drift_info['drift_detected']:
                drift_results['drift_detected'] = True
                drift_results['drift_warnings'].append(drift_info['warning'])
    
    # Check categorical features for drift
    for feature in categorical_features:
        if feature in new_data_df.columns and feature in baseline_df.columns:
            drift_info = _check_categorical_drift(new_data_df, baseline_df, feature)
            drift_results['categorical_drift'][feature] = drift_info
            
            if drift_info['drift_detected']:
                drift_results['drift_detected'] = True
                drift_results['drift_warnings'].append(drift_info['warning'])
    
    # Generate visualizations
    drift_results['visualizations'] = _generate_drift_visualizations(
        new_data_df, baseline_df, numerical_features, categorical_features
    )
    
    # Generate summary statistics
    drift_results['summary_stats'] = _generate_summary_stats(
        new_data_df, baseline_df, numerical_features, categorical_features
    )
    
    return drift_results


def _check_numerical_drift(new_data_df: pd.DataFrame, baseline_df: pd.DataFrame, 
                          feature: str, threshold: float = 0.10) -> Dict[str, Any]:
    """Check for drift in numerical features."""
    
    # Clean data - remove non-numeric values
    new_values = pd.to_numeric(new_data_df[feature], errors='coerce').dropna()
    baseline_values = pd.to_numeric(baseline_df[feature], errors='coerce').dropna()
    
    if len(new_values) == 0 or len(baseline_values) == 0:
        return {
            'drift_detected': False,
            'warning': f"Insufficient data for {feature} drift analysis",
            'new_mean': None,
            'baseline_mean': None,
            'mean_change_pct': None,
            'new_std': None,
            'baseline_std': None
        }
    
    new_mean = new_values.mean()
    baseline_mean = baseline_values.mean()
    new_std = new_values.std()
    baseline_std = baseline_values.std()
    
    # Calculate percentage change in mean
    if baseline_mean != 0:
        mean_change_pct = abs((new_mean - baseline_mean) / baseline_mean)
    else:
        mean_change_pct = 0
    
    # Detect drift
    drift_detected = mean_change_pct > threshold
    
    warning = ""
    if drift_detected:
        direction = "increased" if new_mean > baseline_mean else "decreased"
        warning = f"DRIFT ALERT: {feature} mean has {direction} by {mean_change_pct:.1%} " \
                 f"(from {baseline_mean:.2f} to {new_mean:.2f})"
    
    return {
        'drift_detected': drift_detected,
        'warning': warning,
        'new_mean': float(new_mean),
        'baseline_mean': float(baseline_mean),
        'mean_change_pct': float(mean_change_pct),
        'new_std': float(new_std),
        'baseline_std': float(baseline_std)
    }


def _check_categorical_drift(new_data_df: pd.DataFrame, baseline_df: pd.DataFrame, 
                           feature: str, threshold: float = 0.20) -> Dict[str, Any]:
    """Check for drift in categorical features."""
    
    new_counts = new_data_df[feature].value_counts(normalize=True)
    baseline_counts = baseline_df[feature].value_counts(normalize=True)
    
    # Get all unique categories
    all_categories = set(new_counts.index) | set(baseline_counts.index)
    
    max_shift = 0
    shifted_categories = []
    
    for category in all_categories:
        new_prop = new_counts.get(category, 0)
        baseline_prop = baseline_counts.get(category, 0)
        
        # Calculate absolute change in proportion
        prop_change = abs(new_prop - baseline_prop)
        
        if prop_change > max_shift:
            max_shift = prop_change
        
        if prop_change > threshold:
            shifted_categories.append({
                'category': category,
                'new_proportion': float(new_prop),
                'baseline_proportion': float(baseline_prop),
                'change': float(prop_change)
            })
    
    drift_detected = max_shift > threshold
    
    warning = ""
    if drift_detected:
        warning = f"DRIFT ALERT: {feature} distribution has shifted significantly. " \
                 f"Max category shift: {max_shift:.1%}. " \
                 f"Affected categories: {[cat['category'] for cat in shifted_categories]}"
    
    return {
        'drift_detected': drift_detected,
        'warning': warning,
        'max_shift': float(max_shift),
        'shifted_categories': shifted_categories,
        'new_distribution': new_counts.to_dict(),
        'baseline_distribution': baseline_counts.to_dict()
    }


def _generate_drift_visualizations(new_data_df: pd.DataFrame, baseline_df: pd.DataFrame,
                                 numerical_features: List[str], 
                                 categorical_features: List[str]) -> Dict[str, str]:
    """Generate base64 encoded visualizations for drift analysis."""
    
    visualizations = {}
    
    # Set style for better looking plots
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Generate numerical feature histograms
    for feature in numerical_features:
        if feature in new_data_df.columns and feature in baseline_df.columns:
            try:
                fig, ax = plt.subplots(1, 1, figsize=(10, 6))
                
                # Clean data
                new_values = pd.to_numeric(new_data_df[feature], errors='coerce').dropna()
                baseline_values = pd.to_numeric(baseline_df[feature], errors='coerce').dropna()
                
                if len(new_values) > 0 and len(baseline_values) > 0:
                    # Create histograms
                    ax.hist(baseline_values, alpha=0.7, label='Baseline (Training)', 
                           bins=30, color='skyblue', density=True)
                    ax.hist(new_values, alpha=0.7, label='New Data', 
                           bins=30, color='lightcoral', density=True)
                    
                    ax.set_xlabel(feature)
                    ax.set_ylabel('Density')
                    ax.set_title(f'{feature} Distribution Comparison')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    
                    # Add mean lines
                    ax.axvline(baseline_values.mean(), color='blue', linestyle='--', 
                              label=f'Baseline Mean: {baseline_values.mean():.2f}')
                    ax.axvline(new_values.mean(), color='red', linestyle='--', 
                              label=f'New Data Mean: {new_values.mean():.2f}')
                    
                    plt.tight_layout()
                    
                    # Convert to base64
                    buffer = io.BytesIO()
                    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
                    buffer.seek(0)
                    image_base64 = base64.b64encode(buffer.getvalue()).decode()
                    visualizations[f'{feature}_histogram'] = image_base64
                    
                plt.close(fig)
                
            except Exception as e:
                print(f"Error generating histogram for {feature}: {e}")
    
    # Generate categorical feature bar charts
    for feature in categorical_features:
        if feature in new_data_df.columns and feature in baseline_df.columns:
            try:
                fig, ax = plt.subplots(1, 1, figsize=(12, 6))
                
                new_counts = new_data_df[feature].value_counts(normalize=True)
                baseline_counts = baseline_df[feature].value_counts(normalize=True)
                
                # Get all categories
                all_categories = list(set(new_counts.index) | set(baseline_counts.index))
                
                # Prepare data for plotting
                baseline_props = [baseline_counts.get(cat, 0) for cat in all_categories]
                new_props = [new_counts.get(cat, 0) for cat in all_categories]
                
                x = np.arange(len(all_categories))
                width = 0.35
                
                ax.bar(x - width/2, baseline_props, width, label='Baseline (Training)', 
                      color='skyblue', alpha=0.8)
                ax.bar(x + width/2, new_props, width, label='New Data', 
                      color='lightcoral', alpha=0.8)
                
                ax.set_xlabel(feature)
                ax.set_ylabel('Proportion')
                ax.set_title(f'{feature} Distribution Comparison')
                ax.set_xticks(x)
                ax.set_xticklabels(all_categories, rotation=45, ha='right')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                plt.tight_layout()
                
                # Convert to base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                visualizations[f'{feature}_barplot'] = image_base64
                
                plt.close(fig)
                
            except Exception as e:
                print(f"Error generating bar plot for {feature}: {e}")
    
    # Generate summary drift heatmap
    try:
        drift_summary = _create_drift_summary_heatmap(new_data_df, baseline_df, 
                                                     numerical_features, categorical_features)
        if drift_summary:
            visualizations['drift_summary_heatmap'] = drift_summary
    except Exception as e:
        print(f"Error generating drift summary heatmap: {e}")
    
    return visualizations


def _create_drift_summary_heatmap(new_data_df: pd.DataFrame, baseline_df: pd.DataFrame,
                                 numerical_features: List[str], 
                                 categorical_features: List[str]) -> str:
    """Create a summary heatmap showing drift levels across features."""
    
    features = []
    drift_scores = []
    
    # Calculate drift scores for numerical features
    for feature in numerical_features:
        if feature in new_data_df.columns and feature in baseline_df.columns:
            drift_info = _check_numerical_drift(new_data_df, baseline_df, feature)
            if drift_info['mean_change_pct'] is not None:
                features.append(feature)
                drift_scores.append(drift_info['mean_change_pct'])
    
    # Calculate drift scores for categorical features
    for feature in categorical_features:
        if feature in new_data_df.columns and feature in baseline_df.columns:
            drift_info = _check_categorical_drift(new_data_df, baseline_df, feature)
            features.append(feature)
            drift_scores.append(drift_info['max_shift'])
    
    if not features:
        return ""
    
    # Create heatmap
    fig, ax = plt.subplots(1, 1, figsize=(10, 2))
    
    # Reshape data for heatmap
    data = np.array(drift_scores).reshape(1, -1)
    
    # Create heatmap
    im = ax.imshow(data, cmap='RdYlBu_r', aspect='auto', vmin=0, vmax=0.5)
    
    # Set ticks and labels
    ax.set_xticks(range(len(features)))
    ax.set_xticklabels(features, rotation=45, ha='right')
    ax.set_yticks([0])
    ax.set_yticklabels(['Drift Score'])
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Drift Score', rotation=270, labelpad=15)
    
    # Add text annotations
    for i, score in enumerate(drift_scores):
        ax.text(i, 0, f'{score:.2f}', ha='center', va='center', 
               color='white' if score > 0.25 else 'black', fontweight='bold')
    
    ax.set_title('Feature Drift Summary')
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close(fig)
    
    return image_base64


def _generate_summary_stats(new_data_df: pd.DataFrame, baseline_df: pd.DataFrame,
                          numerical_features: List[str], 
                          categorical_features: List[str]) -> Dict[str, Any]:
    """Generate summary statistics for the drift analysis."""
    
    summary = {
        'data_size_comparison': {
            'new_data_rows': len(new_data_df),
            'baseline_rows': len(baseline_df),
            'size_ratio': len(new_data_df) / len(baseline_df) if len(baseline_df) > 0 else 0
        },
        'feature_coverage': {
            'numerical_features_analyzed': [],
            'categorical_features_analyzed': [],
            'missing_features': []
        }
    }
    
    # Check feature coverage
    for feature in numerical_features:
        if feature in new_data_df.columns and feature in baseline_df.columns:
            summary['feature_coverage']['numerical_features_analyzed'].append(feature)
        else:
            summary['feature_coverage']['missing_features'].append(feature)
    
    for feature in categorical_features:
        if feature in new_data_df.columns and feature in baseline_df.columns:
            summary['feature_coverage']['categorical_features_analyzed'].append(feature)
        else:
            summary['feature_coverage']['missing_features'].append(feature)
    
    return summary


def load_baseline_data(baseline_path: str = None) -> pd.DataFrame:
    """
    Load baseline training data for drift comparison.
    
    Args:
        baseline_path: Path to baseline data file
        
    Returns:
        DataFrame containing baseline training data
    """
    if baseline_path is None:
        # Default path - try multiple locations
        possible_paths = [
            "data/baseline_train.pkl",
            "../data/baseline_train.pkl",
            "../../data/baseline_train.pkl",
            "data/telco_train.csv",
            "../data/telco_train.csv",
            "../../data/telco_train.csv"
        ]
        
        for path in possible_paths:
            try:
                if path.endswith('.pkl'):
                    return pd.read_pickle(path)
                else:
                    return pd.read_csv(path)
            except FileNotFoundError:
                continue
        
        # If no file found, create a mock baseline from the current data structure
        raise FileNotFoundError("No baseline data found. Please provide baseline training data.")
    
    else:
        return pd.read_csv(baseline_path)
