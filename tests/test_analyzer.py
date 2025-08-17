import pytest
import pandas as pd
from analyzer import SalesAnalyzer
import os

@pytest.fixture
def analyzer():
    return SalesAnalyzer()

def test_valid_csv_loading(analyzer, tmp_path):
    # Create temporary CSV
    csv_path = tmp_path / "valid.csv"
    csv_path.write_text("""date,product,quantity,unit_price
2024-01-01,Laptop,2,999.99""")
    
    df = analyzer.load_sales_data(str(csv_path))
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

def test_missing_columns(analyzer, tmp_path):
    csv_path = tmp_path / "invalid.csv"
    csv_path.write_text("date,product\n2024-01-01,Laptop")
    
    df = analyzer.load_sales_data(str(csv_path))
    assert df is None

def test_report_generation(analyzer, tmp_path):
    csv_path = tmp_path / "test_sales.csv"
    csv_path.write_text("""date,product,quantity,unit_price
2024-01-05,Laptop,1,999.99
2024-01-10,Monitor,2,249.50""")
    
    report = analyzer.generate_report(str(csv_path))
    assert report is not None
    assert float(report['total_sales'].strip('$').replace(',','')) == 1498.99
    assert os.path.exists(f"{analyzer.report_dir}/january/metrics.csv")

# Run with: python -m pytest tests/ -v