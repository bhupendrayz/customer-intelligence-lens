"""
theme.py — modern visual layer for the Customer 360 dashboard.

Keeps every existing CSS class name, so app.py's HTML keeps working.
Look: cool light canvas, ink-navy sidebar, teal primary, amber for money,
coral for risk. Fonts: Sora (headings/numbers) + DM Sans (body).
"""
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

INK, TEAL, AMBER, CORAL = "#0F1B2D", "#0E7C86", "#E8A33D", "#E5564B"
CANVAS, PANEL, LINE, MUTED = "#EEF2F6", "#FFFFFF", "#DCE3EC", "#5B6B7F"

COLORWAY = [TEAL, "#3B6FD4", AMBER, CORAL, "#7C5CBF", "#2FA37A", "#8A97A8"]

# Semantic palettes (import these in app.py in place of the old dicts)
HEALTH_COLORS = {"Excellent": "#2FA37A", "Healthy": "#8BC34A", "Watchlist": AMBER,
                 "At Risk": "#EF7B45", "Critical": CORAL}
CHURN_COLORS = {"Low Risk": "#2FA37A", "Medium Risk": "#8BC34A", "High Risk": "#EF7B45",
                "Critical Risk": CORAL, "Not Scored": "#9AA7B8"}
PRIO_COLORS = {"Priority 1": CORAL, "Priority 2": "#EF7B45", "Priority 3": AMBER,
               "Priority 4": TEAL, "Priority 5": "#9AA7B8"}


def register_plotly_template(name: str = "c360") -> str:
    """Register a clean chart template and make it the default. Returns its name."""
    pio.templates[name] = go.layout.Template(
        layout=dict(
            font=dict(family="DM Sans, Segoe UI, sans-serif", color=INK, size=13),
            colorway=COLORWAY,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="rgba(15,27,45,0.06)", zeroline=False,
                       linecolor=LINE, ticks="outside", tickcolor=LINE),
            yaxis=dict(gridcolor="rgba(15,27,45,0.06)", zeroline=False,
                       linecolor="rgba(0,0,0,0)"),
            hoverlabel=dict(bgcolor=INK, font_color="#fff", bordercolor=INK),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            bargap=0.28,
        )
    )
    pio.templates.default = name
    return name


def inject_theme() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Sora:wght@500;600;700&display=swap');

html, body, [class*="css"], .stApp {{ font-family: 'DM Sans', 'Segoe UI', sans-serif; }}
.stApp {{ background: {CANVAS}; color: {INK}; }}
.block-container {{ padding-top: 1.6rem; max-width: 1400px; }}
footer, #MainMenu {{ visibility: hidden; }}

/* ── Header: flat ink banner with a teal edge ── */
.header-card {{
    background: {INK}; border-radius: 6px 20px 6px 20px;
    padding: 28px 34px 22px; margin-bottom: 22px; color: #fff;
    border-bottom: 4px solid {TEAL};
}}
.header-title {{ font-family: 'Sora', sans-serif; font-size: 2rem; font-weight: 700;
    letter-spacing: -0.02em; color: #fff; margin: 0 0 6px; }}
.header-subtitle {{ font-size: 0.95rem; color: #9FB3C8; margin: 0 0 10px; }}
.header-owner {{ font-size: 0.84rem; color: #C9D6E4; margin: 0 0 14px; }}
.header-links {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }}
.header-link {{ color: #fff !important; padding: 5px 14px; border-radius: 6px;
    text-decoration: none; font-size: 0.8rem; font-weight: 500;
    border: 1px solid rgba(255,255,255,0.28); transition: all .15s; }}
.header-link:hover {{ background: {TEAL}; border-color: {TEAL}; }}
.header-currency-note {{ font-size: 0.76rem; color: #8DA2B8;
    border-top: 1px solid rgba(255,255,255,0.12); padding-top: 10px; }}

/* ── Section headings ── */
.section-heading {{ font-family: 'Sora', sans-serif; font-size: 1rem; font-weight: 600;
    color: {INK}; margin: 1.5rem 0 0.5rem; padding-bottom: 6px;
    border-bottom: 2px solid {LINE}; }}

/* ── KPI cards: flat, hairline border, teal top rule ── */
.metric-card {{ background: {PANEL}; border: 1px solid {LINE}; border-top: 3px solid {TEAL};
    border-radius: 6px 14px 6px 14px; padding: 16px 18px; text-align: left; height: 100%; }}
.metric-label {{ font-size: 0.78rem; font-weight: 500; color: {MUTED}; margin-bottom: 6px; }}
.metric-value {{ font-family: 'Sora', sans-serif; font-size: 1.55rem; font-weight: 600;
    color: {INK}; letter-spacing: -0.02em; }}
.metric-delta {{ font-size: 0.78rem; color: {MUTED}; margin-top: 4px; }}

/* ── Callouts: colour = meaning, left rule instead of boxes-in-boxes ── */
.insight-box, .warning-box, .success-box, .danger-box {{
    background: {PANEL}; border: 1px solid {LINE}; border-left: 4px solid {TEAL};
    border-radius: 4px 10px 10px 4px; padding: 12px 16px; margin: 8px 0;
    font-size: 0.9rem; line-height: 1.55; color: {INK}; }}
.warning-box {{ border-left-color: {AMBER}; }}
.success-box {{ border-left-color: #2FA37A; }}
.danger-box  {{ border-left-color: {CORAL}; }}

/* ── Tabs: underline style ── */
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {LINE}; }}
.stTabs [data-baseweb="tab"] {{ height: 46px; padding: 0 16px; color: {MUTED};
    font-weight: 500; background: transparent; }}
.stTabs [aria-selected="true"] {{ color: {INK} !important; font-weight: 600; }}
.stTabs [data-baseweb="tab-highlight"] {{ background: {TEAL}; height: 3px; }}

/* ── Sidebar: ink navy ── */
[data-testid="stSidebar"] {{ background: {INK}; }}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label, [data-testid="stSidebar"] summary,
[data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] .stMarkdown p {{ color: #D5E0EC; }}
[data-testid="stSidebar"] [data-testid="stExpander"] {{
    border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; background: rgba(255,255,255,0.03); }}
[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.12); }}
[data-testid="stSidebar"] .stButton button {{ background: transparent; color: #fff;
    border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; }}
[data-testid="stSidebar"] .stButton button:hover {{ background: {TEAL}; border-color: {TEAL}; }}

.sidebar-contact {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px; padding: 12px 14px; margin-top: 10px; }}
.sidebar-contact-name {{ font-family: 'Sora', sans-serif; font-weight: 600; color: #fff; font-size: 0.9rem; }}
.sidebar-contact-role {{ color: #8DA2B8; font-size: 0.74rem; margin: 2px 0 10px; line-height: 1.4; }}
.sidebar-contact-links {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.sidebar-link {{ background: {TEAL}; color: #fff !important; padding: 3px 11px; border-radius: 6px;
    text-decoration: none; font-size: 0.74rem; font-weight: 500; }}
.sidebar-link:hover {{ background: #0A6068; }}

/* ── Contact cards + footer ── */
.contact-card {{ background: {PANEL}; border: 1px solid {LINE}; border-radius: 6px 14px 6px 14px;
    padding: 18px 20px; text-align: left; margin-bottom: 8px; }}
.contact-card-icon {{ font-size: 1.4rem; margin-bottom: 6px; }}
.contact-card-title {{ font-size: 0.8rem; font-weight: 500; color: {MUTED}; margin-bottom: 4px; }}
.contact-card-link {{ font-size: 0.9rem; color: {TEAL} !important; text-decoration: none; font-weight: 600; }}
.contact-card-link:hover {{ text-decoration: underline; }}

.site-footer {{ margin-top: 48px; padding: 22px 0 10px; border-top: 1px solid {LINE}; text-align: center; }}
.footer-name {{ font-family: 'Sora', sans-serif; font-size: 0.92rem; font-weight: 600; margin-bottom: 8px; }}
.footer-links {{ display: flex; justify-content: center; flex-wrap: wrap; gap: 18px; margin-bottom: 10px; }}
.footer-link {{ font-size: 0.84rem; color: {TEAL} !important; text-decoration: none; }}
.footer-link:hover {{ text-decoration: underline; }}
.footer-note {{ font-size: 0.76rem; color: {MUTED}; margin-top: 4px; line-height: 1.5; }}

/* ── Widgets ── */
[data-testid="stDataFrame"] {{ border: 1px solid {LINE}; border-radius: 10px; overflow: hidden; }}
.stDownloadButton button {{ background: {TEAL}; color: #fff; border: 0; border-radius: 8px; font-weight: 500; }}
.stDownloadButton button:hover {{ background: #0A6068; color: #fff; }}
[data-testid="stPlotlyChart"] {{ background: {PANEL}; border: 1px solid {LINE};
    border-radius: 6px 14px 6px 14px; padding: 6px; }}

:focus-visible {{ outline: 2px solid {TEAL}; outline-offset: 2px; }}
@media (max-width: 640px) {{ .header-title {{ font-size: 1.5rem; }} .metric-value {{ font-size: 1.25rem; }} }}
</style>
"""