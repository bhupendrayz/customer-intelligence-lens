"""
Customer 360 Revenue Intelligence — redesigned layout.
Left nav rail · filter popover · KPI strip · bento-style pages.
Requires theme.py in the same folder.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

from theme import (inject_theme, register_plotly_template, HEALTH_COLORS,
                   CHURN_COLORS, PRIO_COLORS, INK, TEAL, AMBER, CORAL, LINE, MUTED, PANEL)

DEV_NAME      = "Bhupendra Yadav"
DEV_ROLE      = "Data Analyst · Business Analytics · ML · Data Engineering"
DEV_GITHUB    = "https://github.com/bhupendrayz"
DEV_LINKEDIN  = "https://www.linkedin.com/in/bhupendra-yadav-02b8471a0/"
DEV_EMAIL     = "yadavbhupendr7972@gmail.com"

st.set_page_config(page_title="Customer 360", page_icon="🔍📈", layout="wide",
                   initial_sidebar_state="expanded")
inject_theme()
TEMPLATE = register_plotly_template()

st.markdown(f"""
<style>
.kpi-strip {{ display:flex; flex-wrap:wrap; background:{PANEL}; border:1px solid {LINE};
  border-radius:6px 18px 6px 18px; overflow:hidden; margin:6px 0 18px; }}
.kpi-cell {{ flex:1 1 150px; padding:16px 20px; border-right:1px solid {LINE}; }}
.kpi-cell:last-child {{ border-right:0; }}
.kpi-label {{ font-size:.78rem; color:{MUTED}; font-weight:500; }}
.kpi-value {{ font-family:'Sora',sans-serif; font-size:1.55rem; font-weight:600; color:{INK}; letter-spacing:-.02em; }}
.kpi-sub {{ font-size:.76rem; color:{MUTED}; }}
.page-title {{ font-family:'Sora',sans-serif; font-size:1.7rem; font-weight:700; letter-spacing:-.02em; color:{INK}; margin:0; }}
.page-sub {{ color:{MUTED}; font-size:.9rem; margin:2px 0 8px; }}
.prio-row {{ display:flex; align-items:center; gap:12px; padding:10px 0; border-bottom:1px solid {LINE}; }}
.prio-row:last-child {{ border-bottom:0; }}
.prio-dot {{ width:10px; height:10px; border-radius:50%; flex:none; }}
.prio-name {{ width:84px; font-weight:600; font-size:.88rem; flex:none; }}
.prio-bar {{ flex:1; background:#E6ECF3; height:8px; border-radius:4px; overflow:hidden; }}
.prio-fill {{ height:100%; border-radius:4px; }}
.prio-meta {{ width:130px; text-align:right; font-size:.8rem; color:{MUTED}; flex:none; }}
.panel {{ background:{PANEL}; border:1px solid {LINE}; border-radius:6px 16px 6px 16px; padding:14px 20px; }}
.plan-card {{ background:{PANEL}; border:1px solid {LINE}; border-radius:6px 14px 6px 14px; padding:14px 16px; height:100%; }}
.plan-n {{ font-family:'Sora',sans-serif; font-size:1.5rem; font-weight:600; }}
.plan-strategy {{ font-size:.8rem; color:{MUTED}; margin-top:8px; line-height:1.45; }}
.badge {{ display:inline-block; padding:3px 10px; border-radius:6px; font-size:.76rem; font-weight:600; color:#fff; margin-right:6px; }}
.id-card {{ background:{INK}; color:#fff; border-radius:6px 18px 6px 18px; padding:22px; border-bottom:4px solid {TEAL}; }}
.id-score {{ font-family:'Sora',sans-serif; font-size:3rem; font-weight:700; line-height:1; }}
[data-testid="stSidebar"] [role="radiogroup"] {{ gap:2px; }}
[data-testid="stSidebar"] [role="radiogroup"] label {{ padding:9px 12px; border-radius:8px; width:100%; }}
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {{ display:none; }}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {{ background:rgba(255,255,255,.07); }}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{ background:{TEAL}; }}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {{ color:#fff; font-weight:600; }}
</style>
""", unsafe_allow_html=True)

# ── Constants & helpers ──────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
if not (ROOT / "data").exists():
    ROOT = ROOT.parent

HEALTH_ORDER = ["Excellent", "Healthy", "Watchlist", "At Risk", "Critical"]
PRIO_ORDER   = ["Priority 1", "Priority 2", "Priority 3", "Priority 4", "Priority 5"]
VALUE_ORDER  = ["Top 10% Value", "High Value", "Mid Value", "Low Value"]
CHURN_ORDER  = ["Low Risk", "Medium Risk", "High Risk", "Critical Risk", "Not Scored"]
RFM_ORDER    = ["Champions", "Loyal Customers", "Big Spenders", "Potential Loyalists",
                "New Customers", "Needs Attention", "At Risk", "Cannot Lose",
                "Low Value", "Hibernating"]

def money(v):
    if pd.isna(v): return "N/A"
    if v >= 1e6: return f"£{v/1e6:.2f}M"
    if v >= 1e3: return f"£{v/1e3:.1f}K"
    return f"£{v:,.2f}"

def num(v):  return "N/A" if pd.isna(v) else f"{int(v):,}"
def pct(v):  return "N/A" if pd.isna(v) else f"{v:.1%}"

def fig_show(fig, h=320, **layout):
    fig.update_layout(height=h, margin=dict(t=8, b=8, l=8, r=8), **layout)
    st.plotly_chart(fig, use_container_width=True)

def heading(t): st.markdown(f'<div class="section-heading">{t}</div>', unsafe_allow_html=True)

def kpi_strip(items):
    cells = "".join(
        f'<div class="kpi-cell"><div class="kpi-label">{l}</div><div class="kpi-value">{v}</div>'
        f'<div class="kpi-sub">{s}</div></div>' for l, v, s in items)
    st.markdown(f'<div class="kpi-strip">{cells}</div>', unsafe_allow_html=True)

def present(order, series):
    return [o for o in order if o in set(series)]

# ── Data ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_all():
    p = ROOT / "data/processed/customer_360.parquet"
    if not p.exists():
        return None, f"Required file not found: {p}"
    d = pd.read_parquet(p)
    need = ["customer_id", "total_revenue", "health_tier", "rfm_segment", "action_priority",
            "customer_health_score", "churn_risk_tier", "final_recommended_action"]
    miss = [c for c in need if c not in d.columns]
    return (None, f"Missing columns: {miss}") if miss else (d, None)

@st.cache_data
def load_txn():
    p = ROOT / "data/processed/clean_transactions.parquet"
    return pd.read_parquet(p) if p.exists() else None

@st.cache_data
def load_fi():
    p = ROOT / "reports/churn_global_feature_importance.csv"
    return pd.read_csv(p) if p.exists() else None

df_all, err = load_all()
if err:
    st.error(err); st.stop()
txn, feat_imp = load_txn(), load_fi()

# ── Sidebar: nav rail ────────────────────────────────────────────────────────
PAGES = ["Overview", "Segments", "Churn & Retention", "Customer Lookup",
         "Revenue & Products", "Action Plan", "About"]
with st.sidebar:
    st.markdown("### Customer 360")
    st.caption("Revenue intelligence for a UK online retailer · values in GBP (£)")
    page = st.radio("Navigate", PAGES, label_visibility="collapsed", key="nav")
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sidebar-contact">
      <div class="sidebar-contact-name">{DEV_NAME}</div>
      <div class="sidebar-contact-role">{DEV_ROLE}</div>
      <div class="sidebar-contact-links">
        <a class="sidebar-link" href="{DEV_LINKEDIN}" target="_blank">LinkedIn</a>
        <a class="sidebar-link" href="{DEV_GITHUB}" target="_blank">GitHub</a>
        <a class="sidebar-link" href="mailto:{DEV_EMAIL}">Email</a>
      </div>
    </div>""", unsafe_allow_html=True)

# ── Top bar: page title (left) + filter popover (right) ──────────────────────
top_l, top_r = st.columns([3, 1])
with top_r:
    with st.popover("Filters", use_container_width=True):
        if st.button("Reset all filters", use_container_width=True):
            for k in [k for k in st.session_state if k.startswith("flt_")]:
                del st.session_state[k]
            st.rerun()
        a, b = st.columns(2)
        with a:
            sel_health  = st.multiselect("Health tier", sorted(df_all["health_tier"].dropna().unique()), key="flt_health")
            sel_churn   = st.multiselect("Churn risk", sorted(df_all["churn_risk_tier"].dropna().unique()), key="flt_churn")
            sel_value   = st.multiselect("Value tier", sorted(df_all["customer_value_tier"].dropna().unique()), key="flt_value")
        with b:
            sel_rfm     = st.multiselect("RFM segment", sorted(df_all["rfm_segment"].dropna().unique()), key="flt_rfm")
            sel_prio    = st.multiselect("Action priority", sorted(df_all["action_priority"].dropna().unique()), key="flt_prio")
            sel_country = st.multiselect("Country", sorted(df_all["country_mode"].dropna().unique()), key="flt_country")
        scored_label = st.selectbox("Model status", ["All customers", "Scored only", "Not scored only"], key="flt_scored")
        r_lo, r_hi = float(df_all["total_revenue"].min()), float(df_all["total_revenue"].max())
        rev_range = st.slider("Revenue (£)", r_lo, r_hi, (r_lo, r_hi), format="£%.0f", key="flt_rev")
        cp_range = st.slider("Churn probability (scored only)", 0.0, 1.0, (0.0, 1.0), 0.01, key="flt_cp")

df = df_all.copy()
for col, sel in [("health_tier", sel_health), ("rfm_segment", sel_rfm), ("churn_risk_tier", sel_churn),
                 ("action_priority", sel_prio), ("customer_value_tier", sel_value), ("country_mode", sel_country)]:
    if sel:
        df = df[df[col].isin(sel)]
if scored_label == "Scored only":      df = df[df["model_scored"] == 1]
elif scored_label == "Not scored only": df = df[df["model_scored"] == 0]
df = df[df["total_revenue"].between(*rev_range)]
unscored = df["model_scored"] == 0
df = df[unscored | df["churn_probability"].between(*cp_range)]

n_active = sum(bool(x) for x in [sel_health, sel_rfm, sel_churn, sel_prio, sel_value, sel_country]) \
    + (scored_label != "All customers") + (rev_range != (r_lo, r_hi)) + (cp_range != (0.0, 1.0))

with top_l:
    st.markdown(f'<div class="page-title">{page}</div>'
                f'<div class="page-sub">{len(df):,} of {len(df_all):,} customers '
                f'({len(df)/len(df_all):.0%}) · {n_active} filter{"s" if n_active != 1 else ""} active</div>',
                unsafe_allow_html=True)

if df.empty:
    st.markdown('<div class="warning-box">No customers match these filters. Open Filters and widen your selection.</div>',
                unsafe_allow_html=True)
    st.stop()

tot_rev = df["total_revenue"].sum()
n = len(df)
scored = df[df["model_scored"] == 1]

# ═════════════════════════ OVERVIEW ═════════════════════════
if page == "Overview":
    hi_risk = df["churn_risk_tier"].isin(["Critical Risk", "High Risk"])
    kpi_strip([
        ("Customers", num(n), f"{num((df['model_scored']==1).sum())} scored by model"),
        ("Revenue", money(tot_rev), f"{money(df['total_revenue'].mean())} per customer"),
        ("VIP customers", num(df["vip_flag"].sum()), f"{df['vip_flag'].mean():.1%} of base"),
        ("Retention targets", num(df["retention_target_flag"].sum()), f"{df['retention_target_flag'].mean():.1%} need attention"),
        ("High + critical risk", num(hi_risk.sum()), f"{money(df.loc[hi_risk,'total_revenue'].sum())} revenue exposed"),
    ])

    left, right = st.columns([1.5, 1])
    with left:
        heading("Revenue by health tier")
        d = df.groupby("health_tier")["total_revenue"].sum().reset_index()
        fig = px.bar(d, y="health_tier", x="total_revenue", orientation="h", color="health_tier",
                     color_discrete_map=HEALTH_COLORS, text=d["total_revenue"].map(money),
                     category_orders={"health_tier": HEALTH_ORDER},
                     labels={"health_tier": "", "total_revenue": "Revenue (£)"})
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_yaxes(autorange="reversed")
        fig_show(fig, 330, showlegend=False)
    with right:
        heading("Where to act first")
        p = df.groupby("action_priority").agg(c=("customer_id", "count"), r=("total_revenue", "sum")).reindex(
            present(PRIO_ORDER, df["action_priority"])).reset_index()
        mx = p["r"].max() or 1
        rows = "".join(
            f'<div class="prio-row"><span class="prio-dot" style="background:{PRIO_COLORS[a]}"></span>'
            f'<span class="prio-name">{a}</span>'
            f'<div class="prio-bar"><div class="prio-fill" style="width:{r/mx*100:.0f}%;background:{PRIO_COLORS[a]}"></div></div>'
            f'<span class="prio-meta">{num(c)} · {money(r)}</span></div>'
            for a, c, r in zip(p["action_priority"], p["c"], p["r"]))
        st.markdown(f'<div class="panel">{rows}</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1.2])
    with c1:
        heading("Churn risk mix")
        d = df["churn_risk_tier"].value_counts().reset_index()
        d.columns = ["tier", "count"]
        fig = px.pie(d, names="tier", values="count", hole=0.55, color="tier", color_discrete_map=CHURN_COLORS,
                     category_orders={"tier": CHURN_ORDER})
        fig.update_traces(textinfo="percent", sort=False)
        fig_show(fig, 300, legend=dict(orientation="h", y=-0.1))
    with c2:
        heading("Customers by value tier")
        d = df["customer_value_tier"].value_counts().reindex(present(VALUE_ORDER, df["customer_value_tier"])).reset_index()
        d.columns = ["tier", "count"]
        fig = px.bar(d, x="count", y="tier", orientation="h", text="count", color_discrete_sequence=[TEAL],
                     labels={"tier": "", "count": "Customers"})
        fig.update_yaxes(autorange="reversed")
        fig_show(fig, 300)
    with c3:
        heading("What stands out")
        eh = df.loc[df["health_tier"].isin(["Excellent", "Healthy"]), "total_revenue"].sum()
        p4 = df.loc[df["action_priority"] == "Priority 4", "total_revenue"].sum()
        notes = [
            f"Excellent and Healthy customers bring in <b>{eh/tot_rev:.0%}</b> of revenue ({money(eh)}). Protect these first.",
            f"<b>{num(df['retention_target_flag'].sum())}</b> customers are retention targets based on churn risk, health or RFM segment.",
            f"Priority 4 (loyalty and upsell) holds <b>{money(p4)}</b>, or {p4/tot_rev:.0%} of revenue.",
        ]
        for t in notes:
            st.markdown(f'<div class="insight-box">{t}</div>', unsafe_allow_html=True)

# ═════════════════════════ SEGMENTS ═════════════════════════
elif page == "Segments":
    heading("Revenue by RFM segment (box size = revenue, colour = average churn probability)")
    t = df.groupby("rfm_segment").agg(rev=("total_revenue", "sum"), cust=("customer_id", "count"),
                                       churn=("churn_probability", "mean")).reset_index()
    t = t[t["rev"] > 0]
    fig = px.treemap(t, path=["rfm_segment"], values="rev", color="churn",
                     color_continuous_scale=[[0, "#2FA37A"], [0.5, AMBER], [1, CORAL]],
                     hover_data={"cust": True, "rev": ":,.0f"})
    fig.update_traces(textinfo="label+value", texttemplate="<b>%{label}</b><br>£%{value:,.0f}")
    fig.update_layout(coloraxis_colorbar=dict(title="Churn"))
    fig_show(fig, 420)

    l, r = st.columns(2)
    with l:
        heading("Health tier within each segment")
        h = df.groupby(["rfm_segment", "health_tier"]).size().reset_index(name="n")
        h = h.pivot(index="rfm_segment", columns="health_tier", values="n").reindex(
            index=present(RFM_ORDER, df["rfm_segment"]), columns=present(HEALTH_ORDER, df["health_tier"])).fillna(0)
        fig = px.imshow(h, text_auto=True, aspect="auto", color_continuous_scale=["#EEF2F6", TEAL])
        fig.update_layout(coloraxis_showscale=False)
        fig_show(fig, 400)
    with r:
        heading("Segment summary")
        s = df.groupby("rfm_segment").agg(Customers=("customer_id", "count"), Revenue=("total_revenue", "sum"),
                                           Avg=("total_revenue", "mean"), Churn=("churn_probability", "mean"),
                                           VIP=("vip_flag", "sum")).reindex(present(RFM_ORDER, df["rfm_segment"])).reset_index()
        s["Revenue"], s["Avg"], s["Churn"] = s["Revenue"].map(money), s["Avg"].map(money), s["Churn"].map(pct)
        s.columns = ["Segment", "Customers", "Revenue", "Avg revenue", "Avg churn", "VIP"]
        st.dataframe(s, hide_index=True, use_container_width=True, height=400)

# ═════════════════════════ CHURN ═════════════════════════
elif page == "Churn & Retention":
    st.markdown('<div class="insight-box">Predictions cover customers active in the observation window '
                '(cutoff 2011-07-01). Later-joining customers are shown as <b>Not Scored</b> and left out of probability charts.</div>',
                unsafe_allow_html=True)
    if scored.empty:
        st.markdown('<div class="warning-box">No scored customers in the current filters.</div>', unsafe_allow_html=True)
        st.stop()
    hi = scored["churn_risk_tier"].isin(["High Risk", "Critical Risk"])
    kpi_strip([
        ("Scored customers", num(len(scored)), f"{len(scored)/n:.0%} of selection"),
        ("Average churn probability", pct(scored["churn_probability"].mean()), "scored customers only"),
        ("High + critical risk", num(hi.sum()), f"{hi.mean():.0%} of scored"),
        ("Revenue at stake", money(scored.loc[hi, "total_revenue"].sum()), "in high and critical tiers"),
    ])
    l, r = st.columns(2)
    with l:
        heading("How likely customers are to churn")
        fig = px.histogram(scored, x="churn_probability", nbins=40, color_discrete_sequence=[TEAL],
                           labels={"churn_probability": "Churn probability"})
        fig.update_layout(bargap=0.05)
        fig_show(fig, 300)
    with r:
        heading("Revenue at stake by risk tier")
        d = df.groupby("churn_risk_tier")["total_revenue"].sum().reindex(present(CHURN_ORDER, df["churn_risk_tier"])).reset_index()
        fig = px.bar(d, x="churn_risk_tier", y="total_revenue", color="churn_risk_tier", color_discrete_map=CHURN_COLORS,
                     text=d["total_revenue"].map(money), labels={"churn_risk_tier": "", "total_revenue": "Revenue (£)"})
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig_show(fig, 300, showlegend=False)

    heading("Health score vs churn probability")
    fig = px.scatter(scored, x="churn_probability", y="customer_health_score", color="health_tier",
                     color_discrete_map=HEALTH_COLORS, category_orders={"health_tier": HEALTH_ORDER},
                     hover_data=["customer_id", "rfm_segment", "total_revenue"], opacity=0.55,
                     labels={"churn_probability": "Churn probability", "customer_health_score": "Health score"})
    fig_show(fig, 340)

    heading("20 customers most likely to churn")
    cols = ["customer_id", "country_mode", "total_revenue", "rfm_segment", "health_tier",
            "churn_probability", "action_priority", "final_recommended_action"]
    top = scored.nlargest(20, "churn_probability")[cols].copy()
    top["total_revenue"] = top["total_revenue"].map(money)
    top["churn_probability"] = top["churn_probability"].map(lambda x: f"{x:.1%}")
    top.columns = ["Customer", "Country", "Revenue", "Segment", "Health", "Churn prob.", "Priority", "Recommended action"]
    st.dataframe(top, hide_index=True, use_container_width=True)

    if feat_imp is not None:
        with st.expander("What drives churn (model coefficients)"):
            fi = pd.concat([feat_imp[feat_imp["coefficient"] > 0].nlargest(8, "abs_coefficient"),
                            feat_imp[feat_imp["coefficient"] < 0].nlargest(8, "abs_coefficient")]).sort_values("coefficient")
            fig = go.Figure(go.Bar(x=fi["coefficient"], y=fi["feature"], orientation="h",
                                   marker_color=[CORAL if c > 0 else "#2FA37A" for c in fi["coefficient"]]))
            fig.update_layout(xaxis_title="Coefficient (positive = higher churn risk)")
            fig_show(fig, 440)

# ═════════════════════════ LOOKUP ═════════════════════════
elif page == "Customer Lookup":
    ids = sorted(df["customer_id"].unique().tolist())
    cid = st.selectbox("Customer", ids, format_func=lambda x: f"Customer {x}")
    c = df[df["customer_id"] == cid].iloc[0]
    is_scored = c["model_scored"] == 1

    left, right = st.columns([1, 2])
    with left:
        badges = ""
        if c["vip_flag"] == 1: badges += f'<span class="badge" style="background:{TEAL}">VIP</span>'
        if c["retention_target_flag"] == 1: badges += f'<span class="badge" style="background:{CORAL}">Retention target</span>'
        if not is_scored: badges += '<span class="badge" style="background:#8A97A8">Not scored</span>'
        st.markdown(f"""
        <div class="id-card">
          <div style="color:#9FB3C8;font-size:.82rem">Customer {cid} · {c['country_mode']}</div>
          <div style="margin:10px 0 14px">{badges}</div>
          <div class="id-score">{c['customer_health_score']:.0f}<span style="font-size:1rem;color:#9FB3C8"> / 100</span></div>
          <div style="color:#C9D6E4;margin-top:4px">Health score · {c['health_tier']}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="insight-box"><b>Recommended action</b><br>{c["final_recommended_action"]}</div>',
                    unsafe_allow_html=True)
        if not is_scored:
            st.markdown('<div class="warning-box">No churn score: this customer joined during the prediction window. '
                        'The health score uses a neutral churn component (15/30).</div>', unsafe_allow_html=True)
    with right:
        kpi_strip([
            ("Total revenue", money(c["total_revenue"]), c["customer_value_tier"]),
            ("Invoices", num(c["total_invoices"]), f"{money(c['average_invoice_value'])} average"),
            ("Last purchase", f"{num(c['recency_days'])} days ago", str(c["last_purchase_date"])[:10]),
        ])
        kpi_strip([
            ("RFM segment", str(c["rfm_segment"]), f"score {c['rfm_score']}"),
            ("Churn probability", pct(c["churn_probability"]) if is_scored else "Not scored", str(c["churn_risk_tier"])),
            ("Action priority", str(c["action_priority"]), ""),
        ])
        r1, r2 = st.columns(2)
        with r1:
            heading("Score profile")
            health_n = float(c["customer_health_score"]) / 20
            safety = (1 - float(c["churn_probability"])) * 5 if is_scored else 2.5
            cats = ["Recency", "Frequency", "Monetary", "Health", "Churn safety"]
            vals = [float(c["r_score"]), float(c["f_score"]), float(c["m_score"]), health_n, safety]
            fig = go.Figure(go.Scatterpolar(r=vals + vals[:1], theta=cats + cats[:1], fill="toself",
                                            fillcolor="rgba(14,124,134,0.18)", line=dict(color=TEAL, width=2)))
            fig.update_layout(polar=dict(radialaxis=dict(range=[0, 5], tickvals=[1, 2, 3, 4, 5])), showlegend=False)
            fig_show(fig, 320)
        with r2:
            heading("Purchase and return details")
            d = {"First purchase": str(c["first_purchase_date"])[:10], "Tenure (days)": num(c["customer_tenure_days"]),
                 "Purchase days": num(c["unique_purchase_days"]),
                 "Days between purchases": f"{c['avg_days_between_purchases']:.1f}",
                 "Purchases per month": f"{c['purchase_frequency_per_month']:.2f}",
                 "Unique products": num(c["unique_products"]), "Max invoice": money(c["max_invoice_value"]),
                 "Total returns": num(c["total_returns"]), "Return rate": f"{c['return_rate']:.1%}"}
            st.dataframe(pd.DataFrame(d.items(), columns=["Metric", "Value"]), hide_index=True,
                         use_container_width=True, height=320)

# ═════════════════════════ REVENUE & PRODUCTS ═════════════════════════
elif page == "Revenue & Products":
    if txn is None:
        st.markdown('<div class="warning-box">clean_transactions.parquet not found, so revenue and product charts are unavailable.</div>',
                    unsafe_allow_html=True)
        st.stop()
    m = txn.groupby("invoice_yearmonth").agg(revenue=("revenue", "sum"), customers=("customer_id", "nunique")).reset_index().sort_values("invoice_yearmonth")
    peak = m.loc[m["revenue"].idxmax()]
    kpi_strip([("Transaction revenue", money(txn["revenue"].sum()), "all clean transactions"),
               ("Peak month", str(peak["invoice_yearmonth"]), money(peak["revenue"])),
               ("Active customers (peak)", num(m["customers"].max()), "in a single month")])

    heading("Monthly revenue")
    fig = px.area(m, x="invoice_yearmonth", y="revenue", color_discrete_sequence=[TEAL],
                  labels={"invoice_yearmonth": "", "revenue": "Revenue (£)"})
    fig.update_traces(line_width=2, fillcolor="rgba(14,124,134,0.15)")
    fig_show(fig, 300)

    l, r = st.columns(2)
    with l:
        heading("Top 10 countries")
        d = txn.groupby("country")["revenue"].sum().nlargest(10).reset_index()
        fig = px.bar(d, y="country", x="revenue", orientation="h", text=d["revenue"].map(money),
                     color_discrete_sequence=[TEAL], labels={"country": "", "revenue": "Revenue (£)"})
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_yaxes(autorange="reversed")
        fig_show(fig, 380)
    with r:
        heading("Top 10 products")
        d = txn.groupby("description")["revenue"].sum().nlargest(10).reset_index()
        d["description"] = d["description"].str[:36]
        fig = px.bar(d, y="description", x="revenue", orientation="h", text=d["revenue"].map(money),
                     color_discrete_sequence=[AMBER], labels={"description": "", "revenue": "Revenue (£)"})
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_yaxes(autorange="reversed")
        fig_show(fig, 380)

    heading("Average order value")
    aov = txn.groupby(["invoice_yearmonth", "invoice_id"])["revenue"].sum().reset_index() \
             .groupby("invoice_yearmonth")["revenue"].mean().reset_index().sort_values("invoice_yearmonth")
    fig = px.line(aov, x="invoice_yearmonth", y="revenue", markers=True, color_discrete_sequence=[CORAL],
                  labels={"invoice_yearmonth": "", "revenue": "Avg order value (£)"})
    fig_show(fig, 260)

# ═════════════════════════ ACTION PLAN ═════════════════════════
elif page == "Action Plan":
    prios = present(PRIO_ORDER, df["action_priority"])
    cols = st.columns(len(prios))
    for col, pr in zip(cols, prios):
        g = df[df["action_priority"] == pr]
        with col:
            st.markdown(f"""
            <div class="plan-card" style="border-top:4px solid {PRIO_COLORS[pr]}">
              <div style="font-weight:600">{pr}</div>
              <div class="plan-n">{num(len(g))}</div>
              <div class="kpi-sub">{money(g['total_revenue'].sum())} · churn {pct(g['churn_probability'].mean())}</div>
              <div class="plan-strategy">{g['final_recommended_action'].iloc[0]}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    l, r = st.columns(2)
    with l:
        heading("Retention-target revenue by health tier")
        d = df[df["retention_target_flag"] == 1].groupby("health_tier")["total_revenue"].sum() \
              .reindex(present(HEALTH_ORDER, df["health_tier"]), fill_value=0).reset_index()
        fig = px.bar(d, x="health_tier", y="total_revenue", color="health_tier", color_discrete_map=HEALTH_COLORS,
                     text=d["total_revenue"].map(money), labels={"health_tier": "", "total_revenue": "Revenue (£)"})
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig_show(fig, 300, showlegend=False)
    with r:
        heading("VIP revenue by segment")
        d = df[df["vip_flag"] == 1].groupby("rfm_segment")["total_revenue"].sum().sort_values().reset_index()
        fig = px.bar(d, y="rfm_segment", x="total_revenue", orientation="h", text=d["total_revenue"].map(money),
                     color_discrete_sequence=[TEAL], labels={"rfm_segment": "", "total_revenue": "Revenue (£)"})
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig_show(fig, 300)

    heading("Customers in a priority")
    pick = st.selectbox("Priority", prios, label_visibility="collapsed")
    g = df[df["action_priority"] == pick].nlargest(25, "total_revenue")[
        ["customer_id", "country_mode", "total_revenue", "rfm_segment", "health_tier", "churn_risk_tier"]].copy()
    g["total_revenue"] = g["total_revenue"].map(money)
    g.columns = ["Customer", "Country", "Revenue", "Segment", "Health", "Churn risk"]
    st.dataframe(g, hide_index=True, use_container_width=True)

    heading("Export")
    d1, d2, d3, d4 = st.columns(4)
    ap = df.groupby("action_priority").agg(customers=("customer_id", "count"), revenue=("total_revenue", "sum"),
                                           avg_churn=("churn_probability", "mean")).reset_index()
    for col, label, data, name in [
        (d1, "Filtered customers", df, "filtered_customers.csv"),
        (d2, "High-risk customers", df[df["churn_risk_tier"].isin(["High Risk", "Critical Risk"])], "high_risk_customers.csv"),
        (d3, "VIP customers", df[df["vip_flag"] == 1], "vip_customers.csv"),
        (d4, "Action plan summary", ap, "action_plan.csv")]:
        with col:
            st.download_button(label, data.to_csv(index=False).encode("utf-8"), name, "text/csv", use_container_width=True)

# ═════════════════════════ ABOUT ═════════════════════════
else:
    st.markdown(f"""
    <div class="header-card">
      <div class="header-title">Customer 360 Revenue Intelligence</div>
      <div class="header-subtitle">Segments customers with RFM scoring, predicts churn with logistic regression,
      explains the drivers with SHAP, and turns the result into a prioritised action plan.</div>
      <div class="header-owner">Built by <b>{DEV_NAME}</b> · {DEV_ROLE}</div>
      <div class="header-links">
        <a class="header-link" href="{DEV_LINKEDIN}" target="_blank">LinkedIn</a>
        <a class="header-link" href="{DEV_GITHUB}" target="_blank">GitHub</a>
        <a class="header-link" href="mailto:{DEV_EMAIL}">Email</a>
      </div>
    </div>""", unsafe_allow_html=True)

    heading("How it was built")
    steps = [
        ("Ingest and audit", "Loaded 1M+ rows from UCI Online Retail II; removed nulls, cancellations, duplicates and zero-price rows."),
        ("Features and EDA", "Built 27 customer-level features. Repeat buyers (72.4%) drive 96.8% of revenue; peak month was Nov 2010."),
        ("RFM segmentation", "Scored recency, frequency and monetary value from 1 to 5 and mapped customers to 10 business segments."),
        ("Churn model", "Time-window labels (cutoff 2011-07-01), logistic regression with ROC-AUC 0.8148, strict leakage checks."),
        ("Explainability", "SHAP on a 1,000-row sample; top drivers are recency, unique purchase days and RFM score."),
        ("Health score", "0–100 score: RFM 40, churn safety 30, revenue 20, engagement 10, mapped to five tiers and five priorities."),
    ]
    a, b = st.columns(2)
    for i, (t, dsc) in enumerate(steps):
        with (a if i % 2 == 0 else b):
            st.markdown(f'<div class="insight-box"><b>{t}</b><br>{dsc}</div>', unsafe_allow_html=True)

    st.markdown('<div class="warning-box">Portfolio project using the public UCI Online Retail II dataset (Dec 2009 – Dec 2011). '
                'All values are in GBP (£); the country filter refers to customer location only.</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="site-footer"><div class="footer-note">© 2026 {DEV_NAME} · Portfolio project for demonstration</div></div>
""", unsafe_allow_html=True)
