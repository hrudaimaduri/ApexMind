# app.py — ApexMind UI (Premium Polished + Analysis Zone)

import streamlit as st
import pandas as pd
import time
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

/* Background Gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0d0f15, #111729 40%, #080b13);
    color: #e6edf3;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(20, 20, 30, 0.55);
    backdrop-filter: blur(14px);
}

/* Main block spacing */
.block-container {
    padding-top: 1.8rem;
}

/* Glass Panels */
.glass-card {
    background: rgba(255,255,255,0.04);
    padding: 18px 22px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.12);
    backdrop-filter: blur(10px);
    margin-bottom: 22px;
}

/* Neon Heading */
.neon-title {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(90deg, #9d4edd, #7f5af0, #00d4ff);
    -webkit-background-clip: text;
    color: transparent;
}

/* Section header */
.section-header {
    font-size: 26px;
    font-weight: 600;
    color: #7f5af0;
    margin-bottom: 0.4rem;
}

/* Chat bubbles */
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

/* Buttons */
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

/* Expander */
.streamlit-expanderHeader {
    font-size: 18px !important;
    color: #e4d9ff !important;
}

/* Custom divider */
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
    st.session_state.scores_history: List[Dict[str, float]] = []

if "apex_history" not in st.session_state:
    st.session_state.apex_history: List[Dict[str, Any]] = []

if "last_query_context" not in st.session_state:
    st.session_state.last_query_context: List[Dict[str, Any]] = []


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
    st.sidebar.success("Session cleared (UI state). Long-term logs on disk are preserved.")

st.sidebar.markdown("---")
st.sidebar.info("Mode: RAG + Gemini Flash + Apex Engine")


# ==========================================================
# LAYOUT — 2 COLUMNS (CHAT / METRICS)
# ==========================================================
col_chat, col_right = st.columns([1.8, 1.2])


# ==========================================================
# CHAT COLUMN
# ==========================================================
with col_chat:
    st.markdown("<div class='section-header'>💬 Mindset Coaching Chat</div>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    # Display chat history
    for msg in st.session_state.chat:
        if msg["role"] == "user":
            st.markdown(f"<div class='user-msg'>🧍 <b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='agent-msg'>🤖 <b>Agent:</b> {msg['content']}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Enter your weekly report or question")
    user_input = st.text_area(
        "",
        height=120,
        placeholder="Example: This week I coded 5 days, 3 hours each, solved 10 LeetCode problems but still feel slow..."
    )

    ask = st.button("🚀 Ask ApexMind")

    if ask and user_input.strip():
        with st.spinner("Analyzing your mindset and optimizing your growth path..."):
            # 1) Retrieve context for analysis zone
            context_docs = retrieve_context(user_input, k=5)
            st.session_state.last_query_context = context_docs

            # 2) Get full agent result (RAG + scoring + apex)
            result = ask_agent(user_id=user_id, query=user_input)

        # Save dialogue
        st.session_state.chat.append({"role": "user", "content": user_input})
        st.session_state.chat.append({"role": "agent", "content": result["answer"]})

        # Save metrics
        st.session_state.scores_history.append(result["scores"])
        st.session_state.apex_history.append(result["apex"])

        st.success("Response generated! Scroll down to view analysis.")


# ==========================================================
# RIGHT COLUMN — METRICS + APEX
# ==========================================================
with col_right:
    # Mindset Metrics
    st.markdown("<div class='section-header'>📊 Mindset Metrics</div>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    if st.session_state.scores_history:
        latest_scores = st.session_state.scores_history[-1]
        scores_df = pd.DataFrame(latest_scores.items(), columns=["Trait", "Score"]).set_index("Trait")
        st.dataframe(scores_df, use_container_width=True)
        st.bar_chart(scores_df)
    else:
        st.info("Metrics will appear after your first interaction.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Apex State
    st.markdown("<div class='section-header'>🧠 Apex State</div>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    if st.session_state.apex_history:
        apex = st.session_state.apex_history[-1]

        # Optional: show modes as badges if present
        modes = apex.get("modes", [])
        if modes:
            st.markdown("**Active Modes:**")
            badges = " ".join(
                f"<span style='padding:4px 10px; border-radius:999px; background:rgba(127,90,240,0.2); "
                f"border:1px solid rgba(127,90,240,0.6); margin-right:6px; font-size:12px;'>{m}</span>"
                for m in modes
            )
            st.markdown(badges, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.json(apex)
    else:
        st.info("Apex Engine will activate after your first session.")

    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================================
# FULL-WIDTH MODEL ANALYSIS ZONE (RAG + REASONING TRACE)
# ==========================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-header' style='font-size:30px;'>🧠 Model Analysis Zone — RAG Context & Reasoning</div>",
    unsafe_allow_html=True,
)

st.markdown("""
<div style="background: rgba(255,255,255,0.04); padding: 25px; border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.08); backdrop-filter: blur(10px);
            margin-top: 6px; margin-bottom: 25px;">
""", unsafe_allow_html=True)

if st.session_state.last_query_context:

    # ---------------------------
    # TOP-K RETRIEVED CHUNKS
    # ---------------------------
    st.markdown("### 🔍 Top Retrieved Knowledge Chunks")

    for i, doc in enumerate(st.session_state.last_query_context, start=1):
        # Normalize score for heat visualization
        score = float(doc["score"])
        heat = max(0.0, min(score, 1.0))  # clamp between 0 and 1
        bar_color = f"rgba(127, 90, 240, {0.4 + heat/2})"

        st.markdown(f"""
        <div style="padding: 14px; margin-bottom: 12px; border-radius: 12px;
                    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.12);">

            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:17px; font-weight:600;">#{i} • {doc['source']}</span>
                <span style="font-size:13px; opacity:0.8;">Similarity score: {score:.3f}</span>
            </div>

            <div style="height:8px; width:100%; background:rgba(255,255,255,0.08);
                        border-radius:4px; margin-top:6px; overflow:hidden;">
                <div style="height:100%; width:{heat*100}%; background:{bar_color};"></div>
            </div>

            <details style="margin-top:10px;">
                <summary style="cursor:pointer; font-size:14px; opacity:0.9;">Show full chunk</summary>
                <div style="margin-top:8px; font-size:14px; opacity:0.88;">
                    {doc["content"]}
                </div>
            </details>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # ---------------------------
    # REASONING TRACE SECTION
    # ---------------------------
    st.markdown("### 🧩 Reasoning Trace (How the Agent Uses These Chunks)")

    reasoning_text = """
The agent retrieves the top-ranked chunks using FAISS similarity search over your mindset knowledge base.
Each chunk influences the final response based on:

- Relevance to your current question or weekly report  
- The psychological themes it represents (discipline, ego, clarity, adaptability, strategy, etc.)  
- How actionable the ideas inside it are for performance coaching  
- Balance between challenge (pushing you) and support (keeping you stable)

These chunks become the **context window** used by the language model.
The final coaching answer is then generated by blending:

- Retrieved knowledge (RAG)  
- Your evolving mindset scores and Apex state  
- A transformation-oriented coaching style focused on breaking limits and building systems
"""

    st.markdown(f"""
    <div style="padding:18px; border-radius:12px; background:rgba(255,255,255,0.03);
                border:1px solid rgba(255,255,255,0.12); margin-top:6px;">
        <pre style="white-space:pre-wrap; font-size:14px; opacity:0.9; margin:0;">{reasoning_text}</pre>
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("Ask a question and the model’s RAG context + reasoning will appear here.")

st.markdown("</div>", unsafe_allow_html=True)


# ==========================================================
# FOOTER
# ==========================================================
st.markdown(
    "<br><center><small>ApexMind — Cognitive Ascension System • Kaggle Agents Intensive</small></center>",
    unsafe_allow_html=True,
)
