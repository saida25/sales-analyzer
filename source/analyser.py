import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

def load_sales_data(filepath):
    """Load and preprocess CSV"""
    df = pd.read_csv(filepath, parse_dates=['date'])
    df['total'] = df['quantity'] * df['unit_price']
    return df

def generate_insights(df):
    """Calculate key metrics"""
    return {
        'start_date': df['date'].min().strftime('%Y-%m-%d'),
        'end_date': df['date'].max().strftime('%Y-%m-%d'),
        'total_sales': f"${df['total'].sum():,.2f}",
        'avg_order': f"${df['total'].mean():,.2f}",
        'top_product': df.groupby('product')['total'].sum().idxmax()
    }

def create_plots(df, report_dir):
    """Generate visualization files"""
    # Sales trend
    plt.figure(figsize=(10,5))
    df.groupby(df['date'].dt.date)['total'].sum().plot(
        kind='line', 
        title='Daily Sales Trend',
        color='teal'
    )
    plt.savefig(f"{report_dir}/sales_trend.png")
    plt.close()

    # Product distribution
    df.groupby('product')['total'].sum().plot.pie(
        autopct='%1.1f%%',
        figsize=(8,8))
    plt.savefig(f"{report_dir}/product_dist.png")
    plt.close()

def generate_report(csv_path):
    """Main analysis workflow"""
    df = load_sales_data(csv_path)
    month = pd.to_datetime(df['date'].iloc[0]).strftime('%B')
    report_dir = f"reports/{month.lower()}"
    os.makedirs(report_dir, exist_ok=True)

    insights = generate_insights(df)
    create_plots(df, report_dir)
    
    # Save metrics to CSV
    pd.DataFrame([insights]).to_csv(f"{report_dir}/metrics.csv", index=False)
    return insights

if __name__ == "__main__":
    for csv_file in os.listdir("data"):
        if csv_file.endswith(".csv"):
            print(f"📊 Processing {csv_file}...")
            results = generate_report(f"data/{csv_file}")
            print(f"✅ Generated report for {results['start_date']} to {results['end_date']}")