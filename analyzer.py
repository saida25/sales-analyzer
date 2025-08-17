import pandas as pd
import matplotlib.pyplot as plt
import os
import logging
from datetime import datetime
from typing import Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='sales_analysis.log'
)

class SalesAnalyzer:
    REQUIRED_COLUMNS = {'date', 'product', 'quantity', 'unit_price'}
    
    def __init__(self):
        self.report_dir = "reports"
        os.makedirs(self.report_dir, exist_ok=True)

    def _validate_dataframe(self, df: pd.DataFrame) -> bool:
        """Check for required columns and valid data types"""
        if not self.REQUIRED_COLUMNS.issubset(df.columns):
            logging.error(f"Missing columns. Required: {self.REQUIRED_COLUMNS}")
            return False
        
        try:
            pd.to_numeric(df['quantity'])
            pd.to_numeric(df['unit_price'])
            pd.to_datetime(df['date'])
        except ValueError as e:
            logging.error(f"Data type error: {str(e)}")
            return False
            
        return True

    def load_sales_data(self, filepath: str) -> Optional[pd.DataFrame]:
        """Load and validate CSV file"""
        try:
            df = pd.read_csv(filepath)
            if not self._validate_dataframe(df):
                return None
                
            df['date'] = pd.to_datetime(df['date'])
            df['total'] = df['quantity'] * df['unit_price']
            return df
            
        except Exception as e:
            logging.error(f"Failed to load {filepath}: {str(e)}")
            return None

    def generate_report(self, csv_path: str) -> Optional[Dict]:
        """Full report generation pipeline"""
        try:
            df = self.load_sales_data(csv_path)
            if df is None or df.empty:
                return None
                
            month = df['date'].dt.strftime('%B').iloc[0]
            report_dir = f"{self.report_dir}/{month.lower()}"
            os.makedirs(report_dir, exist_ok=True)
            
            insights = self._calculate_metrics(df)
            self._generate_visualizations(df, report_dir)
            
            metrics_path = f"{report_dir}/metrics.csv"
            pd.DataFrame([insights]).to_csv(metrics_path, index=False)
            
            logging.info(f"Report generated: {metrics_path}")
            return insights
            
        except Exception as e:
            logging.critical(f"Report generation failed: {str(e)}")
            return None

    # ... (rest of the methods remain similar but with try-catch blocks)