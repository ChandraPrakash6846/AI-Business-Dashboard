import streamlit as st

def apply_custom_styles():
    """
    Applies modern glassmorphism aesthetic, typography, and polished UI theme to Streamlit.
    """
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 95%;
    }

    /* Metric Card Styling */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        color: #F8FAFC;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(37, 99, 235, 0.25);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38BDF8;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 4px;
    }

    /* AI Insight Card */
    .insight-card {
        border-left: 4px solid #2563EB;
        background: rgba(30, 41, 59, 0.5);
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .insight-positive { border-left-color: #10B981; }
    .insight-warning { border-left-color: #F59E0B; }
    .insight-info { border-left-color: #3B82F6; }

    /* Custom Header Banner */
    .header-banner {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 24px 32px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 24px;
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .header-subtitle {
        color: #94A3B8;
        font-size: 1rem;
        margin-top: 4px;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
