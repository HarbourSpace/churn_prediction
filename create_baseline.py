import pandas as pd
import os

# Create baseline training data for drift comparison
def create_baseline_data():
    try:
        # Load training data
        df = pd.read_csv('data/telco_train.csv')
        
        # Save as pickle for faster loading
        df.to_pickle('data/baseline_train.pkl')
        
        print(f"✓ Created baseline_train.pkl with {len(df)} records")
        print(f"✓ Columns: {list(df.columns)}")
        
    except Exception as e:
        print(f"Error creating baseline data: {e}")

if __name__ == "__main__":
    create_baseline_data()
