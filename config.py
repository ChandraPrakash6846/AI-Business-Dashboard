import streamlit as st

def apply_custom_styles(theme="plotly_dark", *args, **kwargs):
    """
    Applies modern glassmorphism aesthetic (Dark or Light) matching the selected theme.
    """
    if "theme" in kwargs:
        theme = kwargs["theme"]
    elif args:
        theme = args[0]
        
    is_light = (str(theme) == "plotly_white")

    
    bg_card = "linear-gradient(135deg, #FFFFFF, #F1F5F9)" if is_light else "linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9))"
    border_card = "1px solid #E2E8F0" if is_light else "1px solid rgba(255, 255, 255, 0.1)"
    text_color = "#0F172A" if is_light else "#F8FAFC"
    subtext_color = "#475569" if is_light else "#94A3B8"
    val_color = "#0284C7" if is_light else "#38BDF8"
    banner_bg = "linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%)" if is_light else "linear-gradient(135deg, #1E293B 0%, #0F172A 100%)"
    insight_bg = "#F1F5F9" if is_light else "rgba(30, 41, 59, 0.5)"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    /* Main Container Padding */
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 95%;
    }}

    /* Metric Card Styling */
    .metric-card {{
        background: {bg_card};
        border: {border_card};
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        backdrop-filter: blur(10px);
        color: {text_color};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(37, 99, 235, 0.25);
    }}
    .metric-title {{
        font-size: 0.85rem;
        font-weight: 600;
        color: {subtext_color};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }}
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {val_color};
    }}
    .metric-subtitle {{
        font-size: 0.8rem;
        color: {subtext_color};
        margin-top: 4px;
    }}

    /* AI Insight Card */
    .insight-card {{
        border-left: 4px solid #2563EB;
        background: {insight_bg};
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: {text_color};
    }}
    .insight-positive {{ border-left-color: #10B981; }}
    .insight-warning {{ border-left-color: #F59E0B; }}
    .insight-info {{ border-left-color: #3B82F6; }}

    /* Custom Header Banner */
    .header-banner {{
        background: {banner_bg};
        padding: 24px 32px;
        border-radius: 16px;
        border: {border_card};
        margin-bottom: 24px;
    }}
    .header-title {{
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #0284C7 0%, #4F46E5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }}
    .header-subtitle {{
        color: {subtext_color};
        font-size: 1rem;
        margin-top: 4px;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

