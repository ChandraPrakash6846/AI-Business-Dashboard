import os
import pandas as pd

from modules.data_processor import clean_and_validate, get_smart_column_mapping
from modules.ai_engine import generate_statistical_insights, detect_anomalies, process_natural_language_query
from modules.database import init_db, save_analysis_history, fetch_history, save_nl_query, fetch_query_history
from modules.export_engine import export_to_pdf, export_to_excel

def test_all():
    print("--- Starting AI Business Dashboard Test Suite ---")
    
    # 1. Test Dataset Loading & Cleaning
    csv_path = os.path.join(os.path.dirname(__file__), "sample_data", "retail_sales_sample.csv")
    assert os.path.exists(csv_path), "Sample CSV file missing!"
    
    df_raw = pd.read_csv(csv_path)
    df_clean, health = clean_and_validate(df_raw)
    
    print(f"[SUCCESS] Data Cleaning Success: {health['original_rows']} rows -> {health['final_rows']} rows.")
    assert health['final_rows'] > 0, "Dataframe clean failed"
    
    mapping = get_smart_column_mapping(df_clean)
    print(f"[SUCCESS] Smart Column Mapping: {mapping}")
    assert mapping['sales'] is not None, "Sales column mapping failed"

    # Multi-File Merge Test
    from modules.data_processor import merge_multiple_datasets
    df_merged = merge_multiple_datasets([csv_path, csv_path], mode="concat")
    print(f"[SUCCESS] Multi-File Concat Merge: {len(df_merged)} rows created from 2 files.")
    assert len(df_merged) == len(df_raw) * 2, "Multi-file concat failed"


    # 2. Test Statistical Insights & Anomalies
    insights = generate_statistical_insights(df_clean)
    print(f"[SUCCESS] AI Insights Generated: {len(insights)} items.")
    assert len(insights) > 0, "AI insights generation failed"

    df_anom, anomalies = detect_anomalies(df_clean)
    print(f"[SUCCESS] Anomaly Detection Run: Found {len(anomalies)} anomalies.")

    # 3. Test Natural Language Query Parsing
    res_df, chart_type, summary, group_col, target_metric = process_natural_language_query("Total sales by category", df_clean)
    print(f"[SUCCESS] NL Query Executed: {summary}")
    assert not res_df.empty, "NL query returned empty dataframe"

    # 4. Test SQLite Database & Built-in SQL Seeder
    from modules.sql_connector import seed_sample_sql_database, list_tables
    db_test_path = os.path.join(os.path.dirname(__file__), "test_sample.db")
    sql_engine = seed_sample_sql_database(db_test_path)
    sql_tables = list_tables(sql_engine)
    print(f"[SUCCESS] Built-in SQL Database Seeded: Found tables {sql_tables}")
    assert "sales_orders" in sql_tables and "product_catalog" in sql_tables, "SQL Seeder failed"

    init_db()
    kpis = {"Total Sales": "$25,000.00", "Net Profit": "$5,000.00"}
    save_analysis_history("test_dataset.csv", len(df_clean), len(df_clean.columns), health, insights, kpis)
    history = fetch_history(5)
    print(f"[SUCCESS] Database History Records Fetched: {len(history)} items.")
    assert len(history) > 0, "History database test failed"


    # 5. Test Export Generators (PDF & Excel)
    pdf_bytes = export_to_pdf(df_clean, health, kpis, insights)
    excel_bytes = export_to_excel(df_clean, health, kpis, insights)
    print(f"[SUCCESS] PDF Generated: {len(pdf_bytes)} bytes.")
    print(f"[SUCCESS] Excel Generated: {len(excel_bytes)} bytes.")
    assert len(pdf_bytes) > 0 and len(excel_bytes) > 0, "Export engine test failed"

    print("--- ALL TESTS PASSED SUCCESSFULLY! ---")

if __name__ == "__main__":
    test_all()

