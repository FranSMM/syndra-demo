"""
Syndra Demo Dashboard
=====================
B2B sales tool for the Syndra Financial Sentiment API.
Deployed on Streamlit Community Cloud. Zero VPS resource consumption.

Stack: Streamlit + Plotly + Requests
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Syndra · Financial Sentiment API",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }
    .positive { color: #16a34a; font-weight: 600; }
    .negative { color: #dc2626; font-weight: 600; }
    .neutral  { color: #6b7280; font-weight: 600; }
    .signal-card {
        background: #f8fafc;
        border-left: 4px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .signal-card.positive-border { border-left-color: #16a34a; }
    .signal-card.negative-border { border-left-color: #dc2626; }
    .signal-card.neutral-border  { border-left-color: #6b7280; }
    .methodology-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 16px;
        margin: 1rem 0;
    }
    .methodology-box h4 {
        margin-top: 0;
        color: #1e40af;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────
API_BASE = st.secrets.get("API_BASE", "https://api.syndradata.com/api/v1")
DEFAULT_TICKER = "NVDA"

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Syndra API Demo")
    st.markdown("---")

    api_key = st.text_input(
        "🔑 API Key",
        type="password",
        placeholder="syndra_xxxxxxxxxxxxxxxx",
        help="Your Syndra API key. Request demo access at syndradata@gmail.com",
    )

    ticker = st.text_input(
        "📈 Ticker Symbol",
        value=DEFAULT_TICKER,
        placeholder="e.g. NVDA, AAPL, TSLA",
    ).upper().strip()

    time_window = st.selectbox(
        "⏱️ Time Window",
        options=["1 day", "3 days", "7 days", "14 days", "30 days"],
        index=1,
        help="Aggregation window for sentiment analysis",
    )

    st.markdown("---")

    if st.button("🚀 Analyze Sentiment", type="primary", use_container_width=True):
        st.session_state["fetch_triggered"] = True

    st.markdown("---")
    st.markdown("#### 📚 Resources")
    st.link_button("API Documentation", "https://api.syndradata.com/docs", use_container_width=True)
    st.link_button("JSON Schema (Gist)", "https://gist.github.com/FranSMM/7f69e0e54352634f5b977e8c0662b23a", use_container_width=True)
    st.link_button("GitHub Repository", "https://github.com/FranSMM/syndra-data-engine", use_container_width=True)

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; font-size:0.8rem; color:#9ca3af;'>"
        "© 2026 Syndra Data Engine<br>"
        "<a href='mailto:syndradata@gmail.com'>syndradata@gmail.com</a>"
        "</div>",
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────────────────────
# MAIN HEADER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("<div class='main-header'>Syndra · Financial Sentiment API</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-header'>"
    "Zero-leakage NLP sentiment analysis for financial markets. "
    "Self-hosted. API-first. No OpenAI dependency."
    "</div>",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# API KEY VALIDATION
# ──────────────────────────────────────────────────────────────────────────────
if not api_key:
    st.warning("👈 Please enter your API Key in the sidebar to begin.")
    st.info(
        "Don't have a key? Request demo access at **syndradata@gmail.com** "
        "or connect with us on [LinkedIn](https://www.linkedin.com/in/francisco-montesinos/)."
    )
    st.stop()

if not ticker:
    st.warning("👈 Please enter a ticker symbol in the sidebar.")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# FETCH FUNCTION WITH CACHE
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_sentiment_data(ticker_symbol: str, api_key: str, window: str):
    """
    Fetches sentiment data from the Syndra API.
    Cached for 5 minutes to protect the VPS from traffic spikes.
    """
    headers = {"X-API-Key": api_key}
    params = {"time_window": window.replace(" ", "")}

    try:
        resp = requests.get(
            f"{API_BASE}/sentiment/{ticker_symbol}",
            headers=headers,
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 401:
            raise ValueError("Invalid API Key. Please check your credentials.")
        elif resp.status_code == 429:
            raise ValueError("Rate limit exceeded. Please wait a minute and try again.")
        elif resp.status_code == 404:
            raise ValueError(f"No data found for ticker '{ticker_symbol}'.")
        else:
            raise ValueError(f"API Error {resp.status_code}: {resp.text}")
    except requests.exceptions.ConnectionError:
        raise ValueError("Unable to connect to Syndra API. Please try again later.")
    except requests.exceptions.Timeout:
        raise ValueError("Request timed out. The API may be under high load.")

# ──────────────────────────────────────────────────────────────────────────────
# FETCH DATA
# ──────────────────────────────────────────────────────────────────────────────
fetch_triggered = st.session_state.get("fetch_triggered", True)

if fetch_triggered:
    with st.spinner(f"🔍 Analyzing sentiment for **{ticker}**..."):
        try:
            data = fetch_sentiment_data(ticker, api_key, time_window)
        except ValueError as e:
            st.error(f"❌ {e}")
            st.stop()
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            st.stop()
else:
    st.info("👈 Click **Analyze Sentiment** in the sidebar to fetch data.")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# RENDER RESULTS
# ──────────────────────────────────────────────────────────────────────────────

# ── KEY METRICS ──
st.markdown("---")
st.markdown("### 📊 Aggregated Sentiment Overview")

col1, col2, col3, col4, col5 = st.columns(5)

sentiment = data.get("aggregated_sentiment", "neutral")
score = data.get("average_score", 0.0)
count = data.get("article_count", 0)
window = data.get("time_window", time_window)

sentiment_class = sentiment.lower()
sentiment_emoji = {"positive": "🟢", "negative": "🔴", "neutral": "⚪"}.get(sentiment_class, "⚪")

with col1:
    st.metric("Articles Analyzed", count)
with col2:
    st.metric("Avg Sentiment Score", f"{score:.4f}")
with col3:
    st.metric("Sentiment Label", f"{sentiment_emoji} {sentiment.title()}")
with col4:
    st.metric("Time Window", window)
with col5:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        number={"font": {"size": 24}},
        gauge={
            "axis": {"range": [-1, 1], "tickwidth": 1},
            "bar": {"color": "#667eea"},
            "bgcolor": "white",
            "borderwidth": 2,
            "bordercolor": "#e5e7eb",
            "steps": [
                {"range": [-1, -0.2], "color": "#fee2e2"},
                {"range": [-0.2, 0.2], "color": "#f3f4f6"},
                {"range": [0.2, 1], "color": "#dcfce7"},
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": score,
            },
        },
    ))
    fig_gauge.update_layout(height=180, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

# ── SCORING METHODOLOGY (MLOps) ──
with st.expander("📖 Understanding the Scoring Methodology", expanded=False):
    st.markdown("""
    <div class="methodology-box">
        <h4>🔬 FinBERT Softmax Classification</h4>
        <p>
        Syndra uses <strong>ProsusAI/finBERT</strong>, a domain-specific BERT model fine-tuned on financial text.
        Unlike regression models, FinBERT outputs <strong>classification probabilities via Softmax</strong>:
        </p>
        <ul>
            <li><code>sentiment_score</code> = <code>P(positive) − P(negative)</code>, ranging from <strong>−1.0 to +1.0</strong></li>
            <li><code>sentiment_label</code> = argmax of [positive, negative, neutral] probabilities</li>
        </ul>
        <p>
        <strong>Why can average_score be low while label is "neutral"?</strong><br>
        When the model detects <em>conflicting vocabulary</em> or <em>low confidence across all classes</em>,
        the score clusters near 0.0 and the label defaults to "neutral". This is <strong>not a bug</strong> —
        it indicates market uncertainty or mixed signals in the news corpus.
        </p>
        <p>
        <strong>💡 For Quants:</strong> Use <code>sentiment_label</code> for discrete event triggers
        and the <strong>moving average of <code>sentiment_score</code></strong> for trend divergence analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── SENTIMENT TIMELINE ──
st.markdown("---")
st.markdown("### 📈 Sentiment Timeline")

signals = data.get("recent_signals", [])
if signals:
    df = pd.DataFrame(signals)
    df["published_at"] = pd.to_datetime(df["published_at"])
    df = df.sort_values("published_at")

    fig_timeline = px.scatter(
        df,
        x="published_at",
        y="sentiment_score",
        color="sentiment_label",
        color_discrete_map={"positive": "#16a34a", "negative": "#dc2626", "neutral": "#6b7280"},
        hover_data={"title": True, "source": True, "sentiment_score": ":.4f"},
        title=f"Sentiment Score Evolution — {ticker}",
        labels={"published_at": "Published At", "sentiment_score": "Sentiment Score"},
    )
    fig_timeline.update_traces(marker=dict(size=10, opacity=0.8))
    fig_timeline.update_layout(
        height=400,
        xaxis_title="",
        yaxis_title="Sentiment Score",
        yaxis=dict(range=[-1.1, 1.1]),
        legend_title_text="Label",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig_timeline.add_hline(y=0, line_dash="dash", line_color="#9ca3af", opacity=0.5)
    st.plotly_chart(fig_timeline, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        dist = df["sentiment_label"].value_counts().to_dict()
        fig_pie = px.pie(
            names=list(dist.keys()),
            values=list(dist.values()),
            color=list(dist.keys()),
            color_discrete_map={"positive": "#16a34a", "negative": "#dc2626", "neutral": "#6b7280"},
            title="Signal Distribution",
        )
        fig_pie.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        fig_hist = px.histogram(
            df,
            x="sentiment_score",
            nbins=20,
            color="sentiment_label",
            color_discrete_map={"positive": "#16a34a", "negative": "#dc2626", "neutral": "#6b7280"},
            title="Score Distribution",
            labels={"sentiment_score": "Score", "count": "Articles"},
        )
        fig_hist.update_layout(height=300, bargap=0.1)
        st.plotly_chart(fig_hist, use_container_width=True)
else:
    st.info("No recent signals available for this ticker.")

# ── RECENT SIGNALS ──
st.markdown("---")
st.markdown("### 📰 Recent Signals")

if signals:
    for sig in signals[:10]:
        label = sig.get("sentiment_label", "neutral").lower()
        score_s = sig.get("sentiment_score", 0.0)
        title = sig.get("title", "Untitled")
        url = sig.get("url", "#")
        source = sig.get("source", "Unknown")
        published = sig.get("published_at", "N/A")

        border_class = f"{label}-border"
        label_class = label

        st.markdown(f"""
        <div class="signal-card {border_class}">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div style="flex:1;">
                    <a href="{url}" target="_blank" style="text-decoration:none; color:#1e293b; font-weight:600; font-size:1.05rem;">
                        {title}
                    </a>
                    <div style="margin-top:6px; font-size:0.85rem; color:#64748b;">
                        {source} · {published}
                    </div>
                </div>
                <div style="text-align:right; margin-left:16px; min-width:100px;">
                    <div class="{label_class}" style="font-size:1.1rem;">{label.upper()}</div>
                    <div style="font-size:0.9rem; color:#475569; font-weight:500;">{score_s:.4f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if len(signals) > 10:
        st.caption(f"Showing top 10 of {len(signals)} signals. Full data available via API.")
else:
    st.info("No signals to display.")

# ── RAW JSON (for developers) ──
st.markdown("---")
st.markdown("### 🔧 Raw API Response")

with st.expander("View JSON (for integration debugging)", expanded=False):
    st.json(data)
    st.code(f"""
# Python quick-start
data = requests.get(
    "{API_BASE}/sentiment/{ticker}",
    headers={"X-API-Key": "{api_key[:8]}..."},
    params={"time_window": "{time_window.replace(' ', '')}"}
).json()
    """.strip(), language="python")

# ── FOOTER CTA ──
st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:2rem 0;">
    <h3>Ready to integrate Syndra into your pipeline?</h3>
    <p style="color:#6b7280;">
        Self-hosted · Zero data leakage · FinBERT-powered · REST API
    </p>
</div>
""", unsafe_allow_html=True)

col_cta1, col_cta2, col_cta3 = st.columns(3)
with col_cta1:
    st.link_button("📖 Full API Docs", "https://api.syndradata.com/docs", use_container_width=True)
with col_cta2:
    st.link_button("💬 Contact Sales", "mailto:syndradata@gmail.com", use_container_width=True)
with col_cta3:
    st.link_button("⭐ Star on GitHub", "https://github.com/FranSMM/syndra-docs", use_container_width=True)