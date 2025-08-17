import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from jinja2 import Template
import json
# ...existing imports...

def load_config(config_filename="config.json"):
    config_path = os.path.join(os.path.dirname(__file__), config_filename)
    with open(config_path) as f:
        return json.load(f)

def load_sales_data(filepath):
    """Load and preprocess CSV"""
    df = pd.read_csv(filepath)
    # Ensure 'date' is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
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

def email_report(month, report_dir,recipient,sender):
    print(f"DEBUG: Entered email_report for {month}, recipient={recipient}, sender={sender}")  # <--- Add this line
    msg = MIMEMultipart()
    msg['Subject'] = f"{month.capitalize()} Sales Report"
    msg['From'] = sender if sender else "debug@example.com"
    msg['To'] = recipient

    # Attach metrics CSV
    metrics_path = f"{report_dir}/metrics.csv"
    with open(metrics_path, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="metrics.csv"')
        msg.attach(part)

    # Attach images
    for img in ["sales_trend.png", "product_dist.png"]:
        img_path = f"{report_dir}/{img}"
        with open(img_path, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{img}"')
            msg.attach(part)

    # Optional: add a message body
    msg.attach(MIMEText(f"Please find attached the {month.capitalize()} sales report.", "plain"))

    server = smtplib.SMTP('localhost', 1025)
    server.sendmail(msg['From'], [msg['To']], msg.as_string())
    server.quit()
def generate_html_report(insights, month, report_dir):
    template_path = os.path.join("templates", "report_template.html")
    with open(template_path) as f:
        template = Template(f.read())
    html = template.render(
        month=month,
        insights=insights,
        sales_trend=f"{report_dir}/sales_trend.png",
        product_dist=f"{report_dir}/product_dist.png"
    )
    html_path = f"{report_dir}/report.html"
    with open(html_path, "w") as f:
        f.write(html)
    return html_path

def generate_pdf_report(html_path, report_dir):
    pdf_path = f"{report_dir}/report.pdf"
    pdfkit.from_file(html_path, pdf_path)
    return pdf_path

def generate_report(csv_path,recipient):
    """Main analysis workflow"""
    df = load_sales_data(csv_path)
    month = pd.to_datetime(df['date'].iloc[0]).strftime('%B')
    report_dir = f"reports/{month.lower()}"
    os.makedirs(report_dir, exist_ok=True)

    insights = generate_insights(df)
    create_plots(df, report_dir)
    
    # Save metrics to CSV
    pd.DataFrame([insights]).to_csv(f"{report_dir}/metrics.csv", index=False)
    # Generate HTML and PDF reports
    html_path = generate_html_report(insights, month, report_dir)
    pdf_path = generate_pdf_report(html_path, report_dir)

    # Email report if recipient is provided
    if recipient:
        email_report(month, report_dir, recipient,sender)
    return insights

if __name__ == "__main__":
    config = load_config()
    recipient = config.get("recipient") 
    sender=config.get("sender")
    for csv_file in os.listdir("data"):
        if csv_file.endswith(".csv"):
            print(f"📊 Processing {csv_file}...")
            results = generate_report(f"data/{csv_file}", recipient)            
            print(f"✅ Generated report for {results['start_date']} to {results['end_date']}")