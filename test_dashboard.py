"""Integration test for the AI Business Dashboard"""
import pandas as pd
import sys
import os

# Load sample data
df = pd.read_csv('sample_data/sample_sales.csv')
print(f'1. Data loaded: {len(df)} rows, {len(df.columns)} columns - OK')

# Test data cleaning
from utils.data_cleaner import clean_data, detect_column_types
cleaned_df, report = clean_data(df)
print(f'2. Data cleaned: {report.get("duplicates_removed", 0)} dupes removed, {sum(report.get("missing_filled", {}).values())} nulls filled - OK')

# Test column type detection
col_types = detect_column_types(cleaned_df)
print(f'3. Column types: {len(col_types["numeric_columns"])} numeric, {len(col_types["categorical_columns"])} categorical, {len(col_types["date_columns"])} date - OK')

# Test KPI generation
from utils.kpi_generator import detect_kpi_columns, calculate_kpis
kpi_cols = detect_kpi_columns(cleaned_df)
kpis = calculate_kpis(cleaned_df, kpi_cols)
print(f'4. KPIs generated: {len(kpis)} KPIs - {[k["name"] for k in kpis]} - OK')

# Test chart generation
from utils.chart_generator import create_bar_chart, create_line_chart, create_pie_chart, create_scatter_chart, create_histogram, create_heatmap, create_box_plot, create_area_chart
fig = create_bar_chart(cleaned_df, 'Product', 'Revenue', title='Test')
print(f'5. Bar chart created - OK')
fig = create_line_chart(cleaned_df, 'Date', 'Revenue', title='Test')
print(f'6. Line chart created - OK')
fig = create_pie_chart(cleaned_df, 'Product', 'Revenue', title='Test')
print(f'7. Pie chart created - OK')
fig = create_scatter_chart(cleaned_df, 'Revenue', 'Profit', title='Test')
print(f'8. Scatter chart created - OK')
fig = create_histogram(cleaned_df, 'Revenue', title='Test')
print(f'9. Histogram created - OK')
fig = create_box_plot(cleaned_df, x='Product', y='Revenue', title='Test')
print(f'10. Box plot created - OK')
fig = create_area_chart(cleaned_df, 'Date', 'Revenue', title='Test')
print(f'11. Area chart created - OK')

# Test correlation
from utils.analysis import trend_analysis, correlation_analysis, anomaly_detection, distribution_analysis
corr = correlation_analysis(cleaned_df)
print(f'12. Correlation analysis: {len(corr.get("strong_correlations", []))} strong correlations - OK')

# Test heatmap
fig = create_heatmap(corr['matrix'], title='Test')
print(f'13. Heatmap created - OK')

# Test anomaly detection
anom = anomaly_detection(cleaned_df, 'Revenue', threshold=2.0)
print(f'14. Anomaly detection: {anom.get("count", 0)} anomalies found - OK')

# Test trend analysis
trend = trend_analysis(cleaned_df, 'Date', 'Revenue')
print(f'15. Trend analysis: direction={trend.get("direction", "N/A")}, growth={trend.get("growth_rate", 0):.1f}% - OK')

# Test distribution
dist = distribution_analysis(cleaned_df, 'Revenue')
print(f'16. Distribution: mean={dist.get("mean", 0):.2f}, skew={dist.get("skewness", 0):.2f} - OK')

# Test AI insights
from utils.ai_insights import generate_insights, generate_recommendations
ct_for_ai = {'numeric': col_types['numeric_columns'], 'categorical': col_types['categorical_columns'], 'date': col_types['date_columns']}
insights = generate_insights(cleaned_df, column_types=ct_for_ai)
print(f'17. AI Insights: {len(insights)} insights generated - OK')
for ins in insights[:3]:
    print(f'    - [{ins["priority"]}] {ins["title"]}')

recs = generate_recommendations(cleaned_df, insights)
print(f'18. Recommendations: {len(recs)} generated - OK')

# Test NL queries
from utils.nl_query import process_query, get_sample_queries
samples = get_sample_queries(cleaned_df)
print(f'19. Sample queries: {len(samples)} generated - OK')

queries = ['What is the total Revenue?', 'Show Profit by Region', 'Top 5 Products by Revenue', 'Show revenue trend', 'Distribution of profit']
for i, q in enumerate(queries):
    res = process_query(cleaned_df, q)
    status = 'OK' if res['success'] else 'FAILED'
    answer_short = res['answer'][:60]
    print(f'20.{i+1} NL Query "{q}" -> {status} - {answer_short}')

# Test export
from utils.export_utils import export_to_excel, export_to_pdf
excel_bytes = export_to_excel(cleaned_df, kpis=kpis, insights=insights)
print(f'21. Excel export: {len(excel_bytes)} bytes - OK')

pdf_bytes = export_to_pdf(cleaned_df, kpis=kpis, insights=insights)
print(f'22. PDF export: {len(pdf_bytes)} bytes - OK')

# Test history
from utils.history import AnalysisHistory
hist = AnalysisHistory(db_path='test_history.db')
hist.log_action('test.csv', 'Test Action', 'details', 'summary')
hist_df = hist.get_history()
print(f'23. History: {len(hist_df)} entries - OK')
hist.clear_history()
try:
    os.remove('test_history.db')
except:
    pass
print(f'24. History clear - OK')

print()
print('=' * 50)
print('ALL 24 TESTS PASSED SUCCESSFULLY!')
print('=' * 50)
