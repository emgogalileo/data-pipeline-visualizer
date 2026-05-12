import pandas as pd
import numpy as np
import os
import json

def generate_sample_data(num_rows=1000):
    print("Generating sample data...")
    dates = pd.date_range(start='1/1/2026', periods=num_rows, freq='H')
    data = {
        'timestamp': dates,
        'user_id': np.random.randint(1000, 5000, size=num_rows),
        'action': np.random.choice(['login', 'purchase', 'view', 'logout'], size=num_rows),
        'amount': np.random.uniform(10.0, 500.0, size=num_rows)
    }
    df = pd.DataFrame(data)
    df.loc[df['action'] != 'purchase', 'amount'] = 0.0
    return df

def process_data(df):
    print("Processing data pipeline...")
    # Extract
    extracted_df = df.copy()
    
    # Transform
    # 1. Group by action
    summary = extracted_df.groupby('action').agg(
        count=('action', 'count'),
        total_revenue=('amount', 'sum')
    ).reset_index()
    
    # 2. Daily active users
    extracted_df['date'] = extracted_df['timestamp'].dt.date
    dau = extracted_df.groupby('date')['user_id'].nunique().reset_index()
    dau.rename(columns={'user_id': 'unique_users'}, inplace=True)
    
    return summary, dau

def load_data(summary, dau, output_dir='output'):
    print(f"Loading data to {output_dir}...")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    summary.to_csv(os.path.join(output_dir, 'action_summary.csv'), index=False)
    dau.to_csv(os.path.join(output_dir, 'daily_active_users.csv'), index=False)
    
    # Save a JSON metadata file
    metadata = {
        "status": "success",
        "processed_records": int(summary['count'].sum()),
        "total_revenue": float(summary['total_revenue'].sum())
    }
    with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=4)
        
    print("ETL Pipeline completed successfully!")

if __name__ == "__main__":
    raw_data = generate_sample_data(5000)
    summary_df, dau_df = process_data(raw_data)
    load_data(summary_df, dau_df)
