import streamlit as st


# ============================================================
# PAGE STYLING
# ============================================================

def inject_css():

    st.markdown(
        """
<style>

.stApp {
    background: #f8f7ff;
}

.main {
    padding-top: 1rem;
}

/* ============================================================
   HERO
============================================================ */

.hero {
    background: linear-gradient(
        135deg,
        #6d28d9,
        #7c3aed,
        #9333ea
    );

    padding: 28px 32px;
    border-radius: 20px;
    color: white;
    margin-bottom: 24px;

    box-shadow: 0 8px 25px rgba(109, 40, 217, 0.20);
}

.hero-title {
    font-size: 32px;
    font-weight: 800;
    margin-bottom: 6px;
    color: white;
}

.hero-subtitle {
    font-size: 15px;
    opacity: 0.92;
    line-height: 1.6;
    color: white;
}

/* ============================================================
   INFORMATION CARDS
============================================================ */

.info-card {
    background: white;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #e9e5f8;

    box-shadow: 0 4px 15px rgba(50, 30, 100, 0.06);

    margin-bottom: 16px;
}

.card-title {
    font-size: 18px;
    font-weight: 700;
    color: #4c1d95;
    margin-bottom: 8px;
}

.card-text {
    font-size: 14px;
    color: #4b5563;
    line-height: 1.5;
}

/* ============================================================
   BADGES
============================================================ */

.badge {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 20px;

    font-size: 12px;
    font-weight: 700;

    margin-bottom: 10px;
}

.employee-badge {
    background: #ede9fe;
    color: #6d28d9;
}

.policy-badge {
    background: #f3e8ff;
    color: #7e22ce;
}

.hybrid-badge {
    background: #e0e7ff;
    color: #4338ca;
}

/* ============================================================
   SOURCE CARDS
============================================================ */

.source-card {
    background: #faf9ff;

    border-left: 4px solid #7c3aed;

    padding: 10px 14px;

    margin: 6px 0;

    border-radius: 8px;

    font-size: 13px;

    color: #4b5563;
}

.source-title {
    font-weight: 700;
    color: #4c1d95;
}

/* ============================================================
   METRIC CARDS
============================================================ */

.metric-card {
    background: white;

    padding: 20px;

    border-radius: 16px;

    text-align: center;

    border: 1px solid #e9e5f8;

    box-shadow: 0 4px 15px rgba(50, 30, 100, 0.06);

    min-height: 100px;

    display: flex;
    flex-direction: column;
    justify-content: center;

    margin-bottom: 10px;
}

.metric-number {
    font-size: 28px;
    font-weight: 800;
    color: #6d28d9;
    line-height: 1.2;
    margin-bottom: 6px;
}

.metric-label {
    font-size: 13px;
    color: #6b7280;
}

/* ============================================================
   SIDEBAR
============================================================ */

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e9e5f8;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #4c1d95;
}

/* ============================================================
   BUTTONS
============================================================ */

.stButton > button {
    border-radius: 10px;

    border: 1px solid #ddd6fe;

    background: white;

    color: #6d28d9;

    font-weight: 600;
}

.stButton > button:hover {
    border-color: #7c3aed;
    color: #5b21b6;
    background: #faf9ff;
}

/* ============================================================
   CHAT
============================================================ */

[data-testid="stChatMessage"] {
    border-radius: 14px;
}

/* ============================================================
   FOOTER
============================================================ */

.footer {
    text-align: center;

    color: #9ca3af;

    font-size: 12px;

    padding: 25px 0;
}

/* ============================================================
   DATAFRAME
============================================================ */

[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

</style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HERO
# ============================================================

def show_hero():

    html = """
<div class="hero"><div class="hero-title">Employee AI</div><div class="hero-subtitle">Workplace intelligence powered by Retrieval-Augmented Generation and structured employee data.</div></div>
"""

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


# ============================================================
# CATEGORY BADGE
# ============================================================

def show_category_badge(category):

    if not category:
        return

    category_lower = category.lower()

    if category_lower == "employee":

        st.markdown(
            '<span class="badge employee-badge">👥 Employee Data</span>',
            unsafe_allow_html=True,
        )

    elif category_lower == "policy":

        st.markdown(
            '<span class="badge policy-badge">📄 Policy Knowledge</span>',
            unsafe_allow_html=True,
        )

    elif category_lower == "hybrid":

        st.markdown(
            '<span class="badge hybrid-badge">🔀 Hybrid Query</span>',
            unsafe_allow_html=True,
        )


# ============================================================
# SOURCE DISPLAY
# ============================================================

def show_sources(sources):

    if not sources:
        return

    st.markdown("#### 📚 Sources")

    for source in sources:

        document = source.get(
            "document",
            "Unknown document",
        )

        page = source.get(
            "page",
            "?",
        )

        html = (
            f'<div class="source-card">'
            f'<span class="source-title">📄 {document}</span>'
            f'<br>Page {page}'
            f'</div>'
        )

        st.markdown(
            html,
            unsafe_allow_html=True,
        )


# ============================================================
# METRIC CARD
# ============================================================

def metric_card(number, label):

    html = (
        f'<div class="metric-card">'
        f'<div class="metric-number">{number}</div>'
        f'<div class="metric-label">{label}</div>'
        f'</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


# ============================================================
# INFORMATION CARD
# ============================================================

def info_card(title, text):

    html = (
        f'<div class="info-card">'
        f'<div class="card-title">{title}</div>'
        f'<div class="card-text">{text}</div>'
        f'</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


# ============================================================
# FOOTER
# ============================================================

def show_footer():

    st.markdown(
        '<div class="footer">Employee AI • RAG + Structured Employee Analytics</div>',
        unsafe_allow_html=True,
    )