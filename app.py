# app.py — ApexMind UI (Final Clean Version)

import streamlit as st
import pandas as pd
import html
from typing import List, Dict, Any

from rag_step4_agent import ask_agent, retrieve_context


# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="ApexMind — Mindset Transformation Agent",
    page_icon="🧠",
    layout="wide",
)


# ==========================================================
# GLOBAL CSS — NEON + GLASS + PREMIUM THEME
# ==========================================================
st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: "Inter", sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0d0f15, #111729 40%, #080b13);
    color: #e6edf3;
}

[data-testid="stSidebar"] {
    background: rgba(20, 20, 30, 0.55);
    backdrop-filter: blur(14px);
}

.block-container {
    padding-top: 1.8rem;
}

.glass-card {
    background: rgba(255,255,255,0.04);
    padding: 18px 22px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.12);
    backdrop-filter: blur(10px);
    margin-bottom: 22px;
}

.neon-title {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(90deg, #9d4edd, #7f5af0, #00d4ff);
    -webkit-background-clip: text;
    color: transparent;
}

.section-header {
    font-size: 26px;
    font-weight: 600;
    color: #7f5af0;
    margin-bottom: 0.4rem;
}

.user-msg {
    background: rgba(255,255,255,0.08);
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 8px;
}

.agent-msg {
    background: rgba(127, 90, 240, 0.18);
    padding: 12px 16px;
    border-left: 4px solid #7f5af0;
    border-radius: 12px;
    margin-bottom: 8px;
}

.stButton>button {
    background: linear-gradient(90deg, #7f5af0, #6246ea);
    color: white;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    border: none;
    font-weight: 600;
    transition: 0.2s ease-in-out;
}

.stButton>button:hover {
    transform: scale(1.03);
    box-shadow: 0 0 20px #7f5af0;
}

.custom-divider {
    border: 0;
    height: 1px;
    background: linear-gradient(to right, #7f5af0, transparent);
    margin: 20px 0;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# SESSION STATE
# ==========================================================
if "chat" not in st.session_state:
    st.session_state.chat: List[Dict[str, Any]] = []

if "scores_history" not in st.session_state:
    st.session_state.scores_history = []

if "apex_history" not in st.session_state:
    st.session_state.apex_history = []

if "last_query_context" not in st.session_state:
    st.session_state.last_query_context = []


# ==========================================================
# HEADER
# ==========================================================
st.markdown("""
<div style="padding: 12px 0px 8px 0px;">
    <div class="neon-title">🧠 ApexMind</div>
    <p style="font-size: 1.12rem; opacity: 0.82; margin-top: 4px;">
        Hybrid RAG × Psychological Profiling × Apex Performance Engine
    </p>
</div>
""", unsafe_allow_html=True)


# ==========================================================
# SIDEBAR
# ==========================================================
st.sidebar.header("👤 User Settings")

user_id = st.sidebar.text_input("User ID", value="test_user")

if st.sidebar.button("🔁 Reset session"):
    st.session_state.chat = []
    st.session_state.scores_history = []
    st.session_state.apex_history = []
    st.session_state.last_query_context = []
    st.sidebar.success("Session reset successfully!")

st.sidebar.markdown("---")
st.sidebar.info("Mode: RAG + Gemini Flash + Apex Engine")


# ==========================================================
# MAIN LAYOUT — CHAT (LEFT) + METRICS (RIGHT)
# ==========================================================
col_chat, col_right = st.columns([1.8, 1.2])


# ==========================================================
# CHAT COLUMN
# ==========================================================
with col_chat:

    st.markdown("<div class='section-header'>💬 Mindset Coaching Chat</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    if st.session_state.chat:
        for msg in st.session_state.chat:
            if msg["role"] == "user":
                st.markdown(f"<div class='user-msg'>🧍 <b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='agent-msg'>🤖 <b>ApexMind:</b> {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='opacity:0.6;'>No messages yet. Start by entering your weekly report.</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Enter your weekly report or question")

    user_input = st.text_area(
        "",
        height=120,
        placeholder="Example: This week I coded 5 days, but my focus dropped quickly..."
    )

    if st.button("🚀 Ask ApexMind"):
        if user_input.strip():

            with st.spinner("Analyzing your mindset..."):
                context_docs = retrieve_context(user_input, k=5)
                st.session_state.last_query_context = context_docs

                result = ask_agent(user_id, user_input)

            st.session_state.chat.append({"role": "user", "content": user_input})
            st.session_state.chat.append({"role": "agent", "content": result["answer"]})

            st.session_state.scores_history.append(result["scores"])
            st.session_state.apex_history.append(result["apex"])

            st.success("Response generated! Scroll to see analysis.")


# ==========================================================
# METRICS COLUMN
# ==========================================================
with col_right:

    st.markdown("<div class='section-header'>📊 Mindset Metrics</div>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    if st.session_state.scores_history:
        df = pd.DataFrame(st.session_state.scores_history[-1].items(), columns=["Trait", "Score"]).set_index("Trait")
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df)
    else:
        st.info("Metrics will appear after your first interaction.")

    st.markdown("</div>", unsafe_allow_html=True)

    # APEX STATE
    st.markdown("<div class='section-header'>🧠 Apex State</div>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    if st.session_state.apex_history:
        apex = st.session_state.apex_history[-1]
        modes = apex.get("modes", [])
        if modes:
            st.markdown("**Active Modes:**")
            for m in modes:
                st.markdown(f"""
                <span style='padding:4px 10px; border-radius:999px; 
                background:rgba(127,90,240,0.2); border:1px solid rgba(127,90,240,0.6);
                font-size:12px; margin-right:6px;'>{m}</span>
                """, unsafe_allow_html=True)

        st.json(apex)
    else:
        st.info("Apex engine activates after your first session.")

    st.markdown("</div>", unsafe_allow_html=True)



# ==========================================================
# MODEL ANALYSIS ZONE (RAG)
# ==========================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='section-header' style='font-size:30px;'>🧠 Model Analysis Zone — RAG Context & Reasoning</div>", unsafe_allow_html=True)

st.markdown("""
<div style="
    background: rgba(255,255,255,0.04);
    padding: 25px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    margin-top: 6px;
    margin-bottom: 25px;">
""", unsafe_allow_html=True)


if st.session_state.last_query_context:

    st.markdown("## 🔍 Top Retrieved Knowledge Chunks")

    for i, doc in enumerate(st.session_state.last_query_context, 1):

        score = float(doc["score"])
        heat = max(0.0, min(score, 1.0))
        bar_color = f"rgba(127, 90, 240, {0.35 + heat/2})"

        safe_text = html.escape(doc["content"]).replace("\\n", "\n")

        st.markdown(f"""
        <div style="padding: 16px; margin-bottom: 15px; border-radius: 14px;
            background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.12);">

            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-size:17px; font-weight:600;">#{i} • {doc['source']}</div>
                <div style="font-size:13px; opacity:0.8;">Similarity: {score:.3f}</div>
            </div>

            <div style="height:8px; background:rgba(255,255,255,0.08);
                        border-radius:4px; margin-top:8px;">
                <div style="height:100%; width:{heat*100}%; background:{bar_color};"></div>
            </div>

            <details style="margin-top:14px;">
                <summary style="font-size:14px; cursor:pointer;">📄 View full chunk</summary>
                <pre style="white-space:pre-wrap; margin-top:12px; opacity:0.88;">{safe_text}</pre>
            </details>

        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    st.markdown("## 🧩 Reasoning Trace — How ApexMind Used These Chunks")

    reasoning = """
ApexMind retrieves the most relevant psychological principles for your situation using FAISS vector search.
Each retrieved chunk influences the final coaching output through:

• Relevance to your weekly report  
• Psychological category (discipline, clarity, strategy, ego, adaptability)  
• Actionable value of the chunk  
• Your Apex performance profile  
• Your mindset score patterns  

ApexMind then blends:
- Retrieved knowledge (RAG)
- Mindset metrics analysis
- Apex Engine mode logic
- Cognitive-behavioral coaching methodology

This produces a precise, practical, and personalized coaching response.
"""

    st.markdown(f"""
    <div style="padding:18px; border-radius:12px; background:rgba(255,255,255,0.03);
                border:1px solid rgba(255,255,255,0.12);">
        <pre style="white-space:pre-wrap; font-size:14px; opacity:0.9;">{reasoning}</pre>
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("Ask a question to view retrieved knowledge and reasoning.")

st.markdown("</div>", unsafe_allow_html=True)


# ==========================================================
# FOOTER
# ==========================================================
st.markdown(
    "<br><center><small>ApexMind — Cognitive Ascension System • Kaggle Agents Intensive</small></center>",
    unsafe_allow_html=True,
)
