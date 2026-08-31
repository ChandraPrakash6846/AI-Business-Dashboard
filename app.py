"""
AI Business Dashboard - Main Application
A Streamlit-powered dashboard for business data analysis with AI insights.
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.data_loader import load_file, load_sqlite_db, get_data_summary
from utils.data_cleaner import clean_data, detect_column_types
from utils.kpi_generator import detect_kpi_columns, calculate_kpis
from utils.chart_generator import (
    create_bar_chart, create_line_chart, create_pie_chart,
    create_scatter_chart, create_histogram, create_heatmap,
    create_box_plot, create_area_chart
)
from utils.analysis import trend_analysis, correlation_analysis, anomaly_detection, distribution_analysis
from utils.ai_insights import generate_insights, generate_recommendations
from utils.nl_query import process_query, get_sample_queries
from utils.export_utils import export_to_excel, export_to_pdf, get_download_timestamp
from utils.history import AnalysisHistory

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="AI Business Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# LOAD CSS
# ============================================================
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ============================================================
# INITIALIZE SESSION STATE
# ============================================================
if 'df' not in st.session_state:
    st.session_state.df = None
if 'cleaned_df' not in st.session_state:
    st.session_state.cleaned_df = None
if 'cleaning_report' not in st.session_state:
    st.session_state.cleaning_report = None
if 'filename' not in st.session_state:
    st.session_state.filename = None
if 'history' not in st.session_state:
    db_path = os.path.join(os.path.dirname(__file__), "history.db")
    st.session_state.history = AnalysisHistory(db_path=db_path)

history = st.session_state.history

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 📊 AI Business Dashboard")
    st.markdown("---")



    # File Upload Section
    st.markdown("### 📁 Data Source")
    uploaded_file = st.file_uploader(
        "Upload your dataset",
        type=["csv", "xlsx", "xls", "db", "sqlite"],
        help="Supports CSV, Excel, and SQLite files"
    )

    use_sample = st.checkbox("📂 Use Sample Data", value=False, help="Load the built-in sample sales dataset")

    # Data loading logic
    if uploaded_file is not None:
        fname = uploaded_file.name.lower()
        if fname.endswith(('.db', '.sqlite')):
            tables = load_sqlite_db(uploaded_file)
            if tables:
                table_name = st.selectbox("Select Table", list(tables.keys()))
                raw_df = tables[table_name]
                st.session_state.filename = f"{uploaded_file.name} → {table_name}"
            else:
                st.error("No tables found in the database.")
                raw_df = None
        else:
            raw_df = load_file(uploaded_file)
            st.session_state.filename = uploaded_file.name

        if raw_df is not None and not raw_df.empty:
            st.session_state.df = raw_df
            cleaned, report = clean_data(raw_df)
            st.session_state.cleaned_df = cleaned
            st.session_state.cleaning_report = report
            history.log_action(st.session_state.filename, "Data Upload",
                             f"Loaded {len(raw_df)} rows, {len(raw_df.columns)} columns")

    elif use_sample:
        sample_path = os.path.join(os.path.dirname(__file__), "sample_data", "sample_sales.csv")
        if os.path.exists(sample_path):
            raw_df = pd.read_csv(sample_path)
            st.session_state.df = raw_df
            st.session_state.filename = "sample_sales.csv"
            cleaned, report = clean_data(raw_df)
            st.session_state.cleaned_df = cleaned
            st.session_state.cleaning_report = report
        else:
            st.error("Sample data file not found!")


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def render_kpi_cards(kpis):
    """Render KPI metric cards using Streamlit columns."""
    if not kpis:
        return
    cols = st.columns(min(len(kpis), 4))
    for i, kpi in enumerate(kpis):
        with cols[i % len(cols)]:
            delta_color = "normal"
            st.metric(
                label=f"{kpi['icon']} {kpi['name']}",
                value=kpi['formatted_value'],
                delta=kpi['delta_formatted']
            )


def get_column_types_for_insights(df):
    """Convert detect_column_types output to the format ai_insights expects."""
    ct = detect_column_types(df)
    return {
        'numeric': ct.get('numeric_columns', []),
        'categorical': ct.get('categorical_columns', []),
        'date': ct.get('date_columns', []),
    }


# ============================================================
# MAIN CONTENT
# ============================================================
df = st.session_state.cleaned_df
raw_df = st.session_state.df

# ---- WELCOME PAGE (no data loaded) ----
if df is None or df.empty:
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-title">📊 AI Business Dashboard</div>
        <div class="welcome-subtitle">
            Upload your CSV, Excel, or SQLite data to get instant KPIs, 
            interactive charts, AI-powered insights, and natural language queries — 
            all without any API key.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-grid">
        <div class="feature-item">
            <div class="feature-icon">📁</div>
            <div class="feature-name">Upload Data</div>
            <div class="feature-desc">CSV, Excel, and SQLite databases supported</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🧹</div>
            <div class="feature-name">Auto Cleaning</div>
            <div class="feature-desc">Automatic duplicate removal, missing value handling & outlier detection</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">📈</div>
            <div class="feature-name">KPI Cards</div>
            <div class="feature-desc">Sales, Revenue, Profit, Customers — auto-detected</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">📊</div>
            <div class="feature-name">Interactive Charts</div>
            <div class="feature-desc">Bar, Line, Pie, Scatter, Heatmap, Histogram & more</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🤖</div>
            <div class="feature-name">AI Insights</div>
            <div class="feature-desc">Statistical insights & recommendations — no API key needed</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">💬</div>
            <div class="feature-name">Ask Questions</div>
            <div class="feature-desc">Natural language queries about your data</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.info("👈 **Upload a dataset** or check **Use Sample Data** in the sidebar to get started!")
    st.stop()


# ============================================================
# DATA LOADED — Show pages
# ============================================================

# Show data info in sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📋 Data Info")
    st.caption(f"**File:** {st.session_state.filename}")
    st.caption(f"**Rows:** {len(df):,}")
    st.caption(f"**Columns:** {len(df.columns)}")

    report = st.session_state.cleaning_report
    if report and report.get('total_issues_fixed', 0) > 0:
        st.markdown("### 🧹 Cleaning Summary")
        if report.get('duplicates_removed', 0) > 0:
            st.caption(f"🔄 Duplicates removed: {report['duplicates_removed']}")
        if report.get('missing_filled'):
            total_filled = sum(report['missing_filled'].values())
            st.caption(f"📝 Missing values filled: {total_filled}")
        if report.get('types_converted'):
            st.caption(f"📅 Date columns detected: {len(report['types_converted'])}")
        if report.get('outliers_detected'):
            total_outliers = sum(report['outliers_detected'].values())
            st.caption(f"⚡ Outliers detected: {total_outliers}")


# ============================================================
# HORIZONTAL NAVIGATION
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
page = st.pills(
    "Navigate",
    ["📊 Dashboard", "🔍 Analysis", "🤖 AI Insights", "💬 Ask Questions", "📥 Export", "📜 History"],
    default="📊 Dashboard",
    label_visibility="collapsed"
)

# Prevent the page from becoming empty if the user toggles the active pill off
if not page:
    page = "📊 Dashboard"
    
st.markdown("---")

# ============================================================
# PAGE: DASHBOARD
# ============================================================
if page == "📊 Dashboard":
    st.markdown('<div class="section-header"><h2>📊 Dashboard Overview</h2></div>', unsafe_allow_html=True)

    # KPI Cards
    kpis = calculate_kpis(df)
    render_kpi_cards(kpis)

    st.markdown("---")

    # Interactive Charts Section
    st.markdown('<div class="section-header"><h2>📈 Interactive Charts</h2></div>', unsafe_allow_html=True)

    col_types = detect_column_types(df)
    num_cols = col_types['numeric_columns']
    cat_cols = col_types['categorical_columns']
    date_cols = col_types['date_columns']
    all_cols = df.columns.tolist()

    # Chart configuration
    chart_col1, chart_col2 = st.columns([1, 3])

    with chart_col1:
        chart_type = st.selectbox("Chart Type", [
            "Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot",
            "Histogram", "Box Plot", "Area Chart"
        ])

        x_axis = st.selectbox("X-Axis", all_cols, index=0)

        if chart_type in ["Pie Chart"]:
            y_axis = st.selectbox("Values", num_cols if num_cols else all_cols, index=0)
        elif chart_type == "Histogram":
            y_axis = None
        else:
            default_y = 0
            if num_cols:
                y_options = num_cols
            else:
                y_options = all_cols
            y_axis = st.selectbox("Y-Axis", y_options, index=default_y)

        color_by = st.selectbox("Color By (optional)", ["None"] + cat_cols)
        color_by = None if color_by == "None" else color_by

    with chart_col2:
        try:
            plot_df = df.copy()
            # If x-axis is highly categorical, aggregate to top 20 to keep it readable
            if x_axis in cat_cols and df[x_axis].nunique() > 20 and y_axis is not None:
                is_num_y = y_axis in num_cols
                agg_type = "sum" if is_num_y else "count"
                st.warning(f"Too many unique categories for {x_axis}. Showing Top 20 by {agg_type} of {y_axis}.")
                
                if color_by:
                    if is_num_y:
                        plot_df = df.groupby([x_axis, color_by])[y_axis].sum().reset_index()
                    else:
                        plot_df = df.groupby([x_axis, color_by])[y_axis].count().reset_index()
                else:
                    if is_num_y:
                        plot_df = df.groupby(x_axis)[y_axis].sum().reset_index()
                    else:
                        plot_df = df.groupby(x_axis)[y_axis].count().reset_index()
                        
                # Get top 20 categories
                if is_num_y:
                    top_cats = plot_df.groupby(x_axis)[y_axis].sum().nlargest(20).index
                else:
                    top_cats = plot_df.groupby(x_axis)[y_axis].count().nlargest(20).index
                plot_df = plot_df[plot_df[x_axis].isin(top_cats)]
                
                # Sort descending for a cleaner top 20 graph
                plot_df = plot_df.sort_values(by=y_axis, ascending=False)
            
            if chart_type == "Bar Chart":
                fig = create_bar_chart(plot_df, x_axis, y_axis, color=color_by, title=f"{y_axis} by {x_axis}")
            elif chart_type == "Line Chart":
                fig = create_line_chart(plot_df, x_axis, y_axis, color=color_by, title=f"{y_axis} over {x_axis}")
            elif chart_type == "Pie Chart":
                fig = create_pie_chart(plot_df, x_axis, y_axis, title=f"{y_axis} Distribution by {x_axis}")
            elif chart_type == "Scatter Plot":
                fig = create_scatter_chart(plot_df, x_axis, y_axis, color=color_by, title=f"{x_axis} vs {y_axis}")
            elif chart_type == "Histogram":
                fig = create_histogram(plot_df, x_axis, color=color_by, title=f"Distribution of {x_axis}")
            elif chart_type == "Box Plot":
                fig = create_box_plot(plot_df, x=x_axis, y=y_axis, color=color_by, title=f"{y_axis} Distribution by {x_axis}")
            elif chart_type == "Area Chart":
                fig = create_area_chart(plot_df, x_axis, y_axis, color=color_by, title=f"{y_axis} over {x_axis}")
            else:
                fig = create_bar_chart(plot_df, x_axis, y_axis, title="Chart")

            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating chart: {e}")

    # Data Preview
    st.markdown("---")
    st.markdown('<div class="section-header"><h2>📋 Data Preview</h2></div>', unsafe_allow_html=True)

    with st.expander("View Raw Data", expanded=False):
        st.dataframe(df.head(100), use_container_width=True)

    with st.expander("Data Summary Statistics", expanded=False):
        st.dataframe(df.describe(), use_container_width=True)


# ============================================================
# PAGE: ANALYSIS
# ============================================================
elif page == "🔍 Analysis":
    st.markdown('<div class="section-header"><h2>🔍 Advanced Analysis</h2></div>', unsafe_allow_html=True)

    col_types = detect_column_types(df)
    num_cols = col_types['numeric_columns']
    date_cols = col_types['date_columns']

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trend Analysis", "🔗 Correlation", "🚨 Anomaly Detection", "📊 Distribution"])

    # ---- TREND ANALYSIS ----
    with tab1:
        st.subheader("📈 Trend Analysis")
        all_potential_date_cols = date_cols + [c for c in df.columns if any(kw in c.lower() for kw in ['date', 'time', 'year', 'month'])]
        all_potential_date_cols = list(dict.fromkeys(all_potential_date_cols))  # deduplicate

        if all_potential_date_cols and num_cols:
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                date_col = st.selectbox("Date Column", all_potential_date_cols, key="trend_date")
            with t_col2:
                value_col = st.selectbox("Value Column", num_cols, key="trend_value")

            window_short = st.slider("Short Moving Average Window", 2, 15, 3, key="trend_window_short")

            result = trend_analysis(df, date_col, value_col, window_short=window_short, window_long=max(window_short * 3, 7))

            if 'error' not in result:
                # Summary metrics
                m1, m2, m3 = st.columns(3)
                with m1:
                    direction_emoji = "📈" if result['direction'] == 'upward' else "📉" if result['direction'] == 'downward' else "➡️"
                    st.metric("Trend Direction", f"{direction_emoji} {result['direction'].title()}")
                with m2:
                    st.metric("Growth Rate", f"{result['growth_rate']:.1f}%")
                with m3:
                    st.metric("Data Points", len(result['trend_data']))

                st.info(result['summary'])

                # Trend chart
                trend_data = result['trend_data']
                ma_short_col = f"{value_col}_MA_short"
                ma_long_col = f"{value_col}_MA_long"

                import plotly.graph_objects as go
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=trend_data[date_col], y=trend_data[value_col],
                                        mode='markers', name=value_col, marker=dict(color='#667eea', size=6)))
                fig.add_trace(go.Scatter(x=trend_data[date_col], y=trend_data[ma_short_col],
                                        mode='lines', name=f'MA ({window_short})', line=dict(color='#00c864', width=2)))
                fig.add_trace(go.Scatter(x=trend_data[date_col], y=trend_data[ma_long_col],
                                        mode='lines', name=f'MA (Long)', line=dict(color='#ff6b6b', width=2)))
                fig.update_layout(template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)',
                                 paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e0e0ff'),
                                 title=f"{value_col} Trend with Moving Averages")
                st.plotly_chart(fig, use_container_width=True)

                history.log_action(st.session_state.filename, "Trend Analysis",
                                 f"Column: {value_col}", result['summary'])
            else:
                st.warning(result['error'])
        else:
            st.warning("Need at least one date-like column and one numeric column for trend analysis.")

    # ---- CORRELATION ----
    with tab2:
        st.subheader("🔗 Correlation Analysis")
        if len(num_cols) >= 2:
            corr_result = correlation_analysis(df)
            if 'error' not in corr_result:
                st.info(corr_result['summary'])

                # Heatmap
                fig = create_heatmap(corr_result['matrix'], title="Pearson Correlation Matrix")
                st.plotly_chart(fig, use_container_width=True)

                # Strong correlations table
                if corr_result['strong_correlations']:
                    st.subheader("Strong Correlations (|r| > 0.7)")
                    corr_data = []
                    for c1, c2, val in corr_result['strong_correlations']:
                        strength = "Very Strong" if abs(val) > 0.9 else "Strong"
                        direction = "Positive" if val > 0 else "Negative"
                        corr_data.append({"Column 1": c1, "Column 2": c2, "Correlation": f"{val:.3f}",
                                        "Strength": strength, "Direction": direction})
                    st.dataframe(pd.DataFrame(corr_data), use_container_width=True)

                history.log_action(st.session_state.filename, "Correlation Analysis",
                                 f"{len(num_cols)} numeric columns", corr_result['summary'])
            else:
                st.warning(corr_result['error'])
        else:
            st.warning("Need at least 2 numeric columns for correlation analysis.")

    # ---- ANOMALY DETECTION ----
    with tab3:
        st.subheader("🚨 Anomaly Detection")
        if num_cols:
            a_col1, a_col2 = st.columns(2)
            with a_col1:
                anomaly_col = st.selectbox("Select Column", num_cols, key="anomaly_col")
            with a_col2:
                threshold = st.slider("Z-Score Threshold", 1.0, 4.0, 2.0, 0.5, key="anomaly_thresh")

            anomaly_result = anomaly_detection(df, anomaly_col, threshold=threshold)

            if 'error' not in anomaly_result:
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Anomalies Found", anomaly_result['count'])
                with m2:
                    st.metric("Mean", f"{anomaly_result['mean']:.2f}")
                with m3:
                    st.metric("Std Dev", f"{anomaly_result['std']:.2f}")

                st.info(anomaly_result['summary'])

                if anomaly_result['count'] > 0:
                    st.subheader("Anomalous Records")
                    st.dataframe(anomaly_result['anomalies'], use_container_width=True)

                # Distribution chart with anomaly markers
                import plotly.graph_objects as go
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=df[anomaly_col], name='Distribution',
                                          marker_color='#667eea', opacity=0.7))
                if anomaly_result['count'] > 0:
                    anomaly_vals = anomaly_result['anomalies'][anomaly_col]
                    fig.add_trace(go.Scatter(x=anomaly_vals, y=[0]*len(anomaly_vals),
                                            mode='markers', name='Anomalies',
                                            marker=dict(color='red', size=12, symbol='x')))
                fig.update_layout(template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)',
                                 paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e0e0ff'),
                                 title=f"Distribution of {anomaly_col} with Anomalies")
                st.plotly_chart(fig, use_container_width=True)

                history.log_action(st.session_state.filename, "Anomaly Detection",
                                 f"Column: {anomaly_col}, Threshold: {threshold}",
                                 anomaly_result['summary'])
            else:
                st.warning(anomaly_result['error'])
        else:
            st.warning("No numeric columns found for anomaly detection.")

    # ---- DISTRIBUTION ----
    with tab4:
        st.subheader("📊 Distribution Analysis")
        if num_cols:
            dist_col = st.selectbox("Select Column", num_cols, key="dist_col")
            dist_result = distribution_analysis(df, dist_col)

            if 'error' not in dist_result:
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Mean", f"{dist_result['mean']:.2f}")
                with m2:
                    st.metric("Median", f"{dist_result['median']:.2f}")
                with m3:
                    st.metric("Skewness", f"{dist_result['skewness']:.2f}")
                with m4:
                    st.metric("Normal?", "✅ Yes" if dist_result['is_normal'] else "❌ No")

                st.info(dist_result['summary'])

                # Histogram + Box plot
                c1, c2 = st.columns(2)
                with c1:
                    fig = create_histogram(df, dist_col, title=f"Histogram of {dist_col}")
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    fig = create_box_plot(df, y=dist_col, title=f"Box Plot of {dist_col}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(dist_result['error'])
        else:
            st.warning("No numeric columns found for distribution analysis.")


# ============================================================
# PAGE: AI INSIGHTS
# ============================================================
elif page == "🤖 AI Insights":
    st.markdown('<div class="section-header"><h2>🤖 AI-Generated Business Insights</h2></div>', unsafe_allow_html=True)
    st.caption("Powered by statistical analysis — no API key required")

    col_types_for_ai = get_column_types_for_insights(df)
    insights = generate_insights(df, column_types=col_types_for_ai)

    if insights:
        for insight in insights:
            priority_colors = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
            priority_badge = priority_colors.get(insight.get('priority', 'low'), '🟢')

            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">{insight['icon']} {insight['title']} {priority_badge}</div>
                <div class="insight-detail">{insight['detail']}</div>
                <div class="insight-recommendation">💡 <strong>Recommendation:</strong> {insight['recommendation']}</div>
            </div>
            """, unsafe_allow_html=True)

        history.log_action(st.session_state.filename, "AI Insights",
                         f"Generated {len(insights)} insights")
    else:
        st.info("No insights could be generated from this dataset.")

    # Recommendations Section
    st.markdown("---")
    st.markdown('<div class="section-header"><h2>🎯 Actionable Recommendations</h2></div>', unsafe_allow_html=True)

    recommendations = generate_recommendations(df, insights)
    if recommendations:
        for rec in recommendations:
            impact_badge = "🔴" if rec['impact'] == 'high' else "🟡" if rec['impact'] == 'medium' else "🟢"
            effort_text = f"Effort: {rec['effort'].title()}"
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">{rec['icon']} {rec['title']} {impact_badge}</div>
                <div class="insight-detail">{rec['description']}</div>
                <div class="insight-recommendation">⚡ {effort_text} | Impact: {rec['impact'].title()}</div>
            </div>
            """, unsafe_allow_html=True)


# ============================================================
# PAGE: ASK QUESTIONS
# ============================================================
elif page == "💬 Ask Questions":
    st.markdown('<div class="section-header"><h2>💬 Ask Questions About Your Data</h2></div>', unsafe_allow_html=True)
    st.caption("Ask questions in plain English and get instant answers with charts")

    # Sample queries
    sample_queries = get_sample_queries(df)
    st.markdown("**💡 Try these example questions:**")
    query_cols = st.columns(min(len(sample_queries), 3))
    for i, sq in enumerate(sample_queries[:6]):
        with query_cols[i % 3]:
            if st.button(sq, key=f"sq_{i}", use_container_width=True):
                st.session_state['current_query'] = sq

    st.markdown("---")

    # Query input
    default_query = st.session_state.get('current_query', '')
    user_query = st.text_input("🔍 Type your question:", value=default_query,
                                placeholder="e.g., What is the total revenue by region?")

    if user_query:
        with st.spinner("Analyzing your question..."):
            result = process_query(df, user_query)

        if result['success']:
            st.markdown(f"""
            <div class="query-answer">
                <strong>📊 Answer:</strong> {result['answer']}
            </div>
            """, unsafe_allow_html=True)

            if result.get('chart') is not None:
                st.plotly_chart(result['chart'], use_container_width=True)

            if result.get('data') is not None:
                with st.expander("📋 View Result Data", expanded=True):
                    st.dataframe(result['data'], use_container_width=True)

            history.log_action(st.session_state.filename, "NL Query",
                             user_query, result['answer'])
        else:
            st.warning(result['answer'])

        # Clear the session query after processing
        if 'current_query' in st.session_state:
            del st.session_state['current_query']


# ============================================================
# PAGE: EXPORT
# ============================================================
elif page == "📥 Export":
    st.markdown('<div class="section-header"><h2>📥 Export Reports</h2></div>', unsafe_allow_html=True)

    timestamp = get_download_timestamp()
    kpis = calculate_kpis(df)
    col_types_for_ai = get_column_types_for_insights(df)
    insights = generate_insights(df, column_types=col_types_for_ai)

    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-title">📗 Excel Report</div>
            <div class="insight-detail">Download a multi-sheet Excel workbook with your data, summary statistics, KPIs, and AI insights.</div>
        </div>
        """, unsafe_allow_html=True)

        excel_bytes = export_to_excel(df, kpis=kpis, insights=insights)
        if excel_bytes:
            st.download_button(
                label="⬇️ Download Excel Report",
                data=excel_bytes,
                file_name=f"dashboard_report_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    with exp_col2:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-title">📕 PDF Report</div>
            <div class="insight-detail">Download a formatted PDF report with data summary, KPIs, top insights, and statistical analysis.</div>
        </div>
        """, unsafe_allow_html=True)

        pdf_bytes = export_to_pdf(df, kpis=kpis, insights=insights)
        if pdf_bytes:
            st.download_button(
                label="⬇️ Download PDF Report",
                data=bytes(pdf_bytes),
                file_name=f"dashboard_report_{timestamp}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    st.markdown("---")
    st.markdown('<div class="section-header"><h2>📋 Export Data Only</h2></div>', unsafe_allow_html=True)

    data_col1, data_col2 = st.columns(2)
    with data_col1:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Cleaned Data (CSV)",
            data=csv_data,
            file_name=f"cleaned_data_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with data_col2:
        excel_data_only = export_to_excel(df)
        if excel_data_only:
            st.download_button(
                label="⬇️ Download Cleaned Data (Excel)",
                data=excel_data_only,
                file_name=f"cleaned_data_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    if kpis or insights:
        history.log_action(st.session_state.filename, "Export", "Report generated")


# ============================================================
# PAGE: HISTORY
# ============================================================
elif page == "📜 History":
    st.markdown('<div class="section-header"><h2>📜 Analysis History</h2></div>', unsafe_allow_html=True)

    hist_df = history.get_history()

    if not hist_df.empty:
        # Timeline view
        for _, row in hist_df.iterrows():
            ts = row.get('timestamp', '')
            if ts:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(ts)
                    ts_display = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    ts_display = ts
            else:
                ts_display = "Unknown"

            action_icons = {
                'Data Upload': '📁', 'Data Cleaning': '🧹', 'AI Insights': '🤖',
                'NL Query': '💬', 'Export': '📥', 'Trend Analysis': '📈',
                'Correlation Analysis': '🔗', 'Anomaly Detection': '🚨'
            }
            icon = action_icons.get(row.get('action', ''), '📌')

            st.markdown(f"""
            <div class="history-item">
                <div class="history-time">{icon} {ts_display}</div>
                <div class="history-action">
                    <strong>{row.get('action', 'Action')}</strong> — {row.get('filename', 'File')}<br>
                    <small>{row.get('details', '')} {(' | ' + row.get('result_summary', '')) if row.get('result_summary') else ''}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Table view
        with st.expander("📋 View as Table"):
            st.dataframe(hist_df, use_container_width=True)

        # Clear history button
        if st.button("🗑️ Clear History", type="secondary"):
            history.clear_history()
            st.success("History cleared!")
            st.rerun()
    else:
        st.info("No analysis history yet. Start exploring your data to build history!")


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.8rem;'>"
    "📊 AI Business Dashboard | Built with Streamlit, Pandas, Plotly | No API Key Required"
    "</div>",
    unsafe_allow_html=True
)
