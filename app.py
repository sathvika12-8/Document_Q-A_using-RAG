import streamlit as st
import pandas as pd

from config import (
    EMPLOYEE_FILE,
    DOCUMENTS_DIR,
    VECTORSTORE_DIR,
    OLLAMA_MODEL,
)

from employee_data import load_employee_data
from router import ask_assistant
from rag import rebuild_vectorstore
from UI import (
    inject_css,
    show_hero,
    show_category_badge,
    show_sources,
    metric_card,
    info_card,
    show_footer,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Employee AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# UI
# ============================================================

inject_css()


# ============================================================
# LOAD EMPLOYEE DATA
# ============================================================

@st.cache_data
def get_employee_data():

    return load_employee_data()


df = get_employee_data()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <h2 style="color:#6d28d9;">
            🤖 Employee AI
        </h2>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Workplace Intelligence Assistant"
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "💬 Assistant",
            "👥 Employee Directory",
            "📚 Documents",
            "⚙️ System Status",
        ],
    )

    st.divider()

    st.markdown(
        "**Quick Questions**"
    )

    quick_questions = [
        "How many employees are in Bangalore?",
        "What are the overtime rules?",
        "What benefits are available?",
        "How many employees joined in 2017?",
    ]

    for question in quick_questions:

        if st.button(
            question,
            use_container_width=True,
        ):

            st.session_state["selected_question"] = question

            st.session_state["page"] = "💬 Assistant"

            st.rerun()

    st.divider()

    st.caption(
        f"Employees: {len(df):,}"
    )

    st.caption(
        f"LLM: {OLLAMA_MODEL}"
    )


# ============================================================
# HANDLE PAGE STATE
# ============================================================

if "page" in st.session_state:

    page = st.session_state["page"]


# ============================================================
# ASSISTANT PAGE
# ============================================================

if page == "💬 Assistant":

    show_hero()

    st.markdown(
        "### Ask Employee AI"
    )

    st.write(
        "Ask questions about company policies, "
        "employees, or both."
    )

    # --------------------------------------------------------
    # EXAMPLE QUESTIONS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            """
            **📄 Policy**

            What are the overtime rules?
            """
        )

    with col2:

        st.markdown(
            """
            **👥 Employee**

            How many employees are in Bangalore?
            """
        )

    with col3:

        st.markdown(
            """
            **🔀 Hybrid**

            What are the overtime rules and how many
            employees are in Bangalore?
            """
        )

    st.divider()

    # --------------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------------

    if "messages" not in st.session_state:

        st.session_state.messages = []

    # Display previous messages.

    for message in st.session_state.messages:

        role = message["role"]

        with st.chat_message(role):

            if role == "assistant":

                category = message.get(
                    "category",
                    "",
                )

                if category:

                    show_category_badge(
                        category
                    )

            st.markdown(
                message["content"]
            )

            if role == "assistant":

                show_sources(
                    message.get(
                        "sources",
                        [],
                    )
                )

    # --------------------------------------------------------
    # QUESTION INPUT
    # --------------------------------------------------------

    selected_question = st.session_state.pop(
        "selected_question",
        None,
    )

    prompt = st.chat_input(
        "Ask a question about employees or company policies..."
    )

    if selected_question:

        prompt = selected_question

    if prompt:

        # User message

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        with st.chat_message("user"):

            st.markdown(prompt)

        # Assistant

        with st.chat_message("assistant"):

            with st.spinner(
                "Thinking..."
            ):

                try:

                    answer, sources, category = (
                        ask_assistant(prompt)
                    )

                except Exception as e:

                    answer = (
                        "Sorry, I encountered an error "
                        "while processing your question."
                    )

                    sources = []

                    category = "Error"

                    st.error(
                        f"Technical details: {e}"
                    )

            if category != "Error":

                show_category_badge(
                    category
                )

            st.markdown(answer)

            show_sources(
                sources
            )

        # Save assistant message

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "category": category,
            }
        )

    # --------------------------------------------------------
    # CLEAR CHAT
    # --------------------------------------------------------

    if st.session_state.messages:

        st.divider()

        if st.button(
            "🗑️ Clear Conversation"
        ):

            st.session_state.messages = []

            st.rerun()


# ============================================================
# EMPLOYEE DIRECTORY
# ============================================================

elif page == "👥 Employee Directory":

    show_hero()

    st.markdown(
        "### 👥 Employee Directory"
    )

    st.write(
        "Explore the structured employee dataset."
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    total = len(df)

    avg_age = round(
        df["Age"].mean(),
        1,
    )

    avg_experience = round(
        df["ExperienceInCurrentDomain"].mean(),
        1,
    )

    cities = df["City"].nunique()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card(
            f"{total:,}",
            "Total Employees",
        )

    with col2:
        metric_card(
            avg_age,
            "Average Age",
        )

    with col3:
        metric_card(
            avg_experience,
            "Avg. Domain Experience",
        )

    with col4:
        metric_card(
            cities,
            "Cities",
        )

    st.divider()

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    st.markdown(
        "### 🔎 Filter Employees"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        city_options = [
            "All"
        ] + sorted(
            df["City"].dropna().unique().tolist()
        )

        selected_city = st.selectbox(
            "City",
            city_options,
        )

    with col2:

        education_options = [
            "All"
        ] + sorted(
            df["Education"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_education = st.selectbox(
            "Education",
            education_options,
        )

    with col3:

        gender_options = [
            "All"
        ] + sorted(
            df["Gender"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_gender = st.selectbox(
            "Gender",
            gender_options,
        )

    filtered_df = df.copy()

    if selected_city != "All":

        filtered_df = filtered_df[
            filtered_df["City"] == selected_city
        ]

    if selected_education != "All":

        filtered_df = filtered_df[
            filtered_df["Education"]
            == selected_education
        ]

    if selected_gender != "All":

        filtered_df = filtered_df[
            filtered_df["Gender"]
            == selected_gender
        ]

    st.info(
        f"Showing {len(filtered_df):,} employees"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# DOCUMENTS
# ============================================================

elif page == "📚 Documents":

    show_hero()

    st.markdown(
        "### 📚 Knowledge Base"
    )

    st.write(
        "These PDF documents are used by the "
        "Retrieval-Augmented Generation system."
    )

    pdf_files = sorted(
        DOCUMENTS_DIR.glob("*.pdf")
    )

    # --------------------------------------------------------
    # DOCUMENT METRICS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        metric_card(
            len(pdf_files),
            "PDF Documents",
        )

    with col2:

        vector_status = (
            "Ready"
            if (
                VECTORSTORE_DIR / "index.faiss"
            ).exists()
            else "Not Created"
        )

        metric_card(
            vector_status,
            "Vector Database",
        )

    st.divider()

    # --------------------------------------------------------
    # DOCUMENT LIST
    # --------------------------------------------------------

    if pdf_files:

        for pdf in pdf_files:

            info_card(
                "📄 " + pdf.stem,
                pdf.name,
            )

    else:

        st.warning(
            "No PDF documents found."
        )

    st.divider()

    # --------------------------------------------------------
    # REBUILD BUTTON
    # --------------------------------------------------------

    st.markdown(
        "### 🔄 Rebuild Knowledge Base"
    )

    st.write(
        "Use this after adding, removing, or "
        "replacing PDF documents."
    )

    if st.button(
        "🔄 Rebuild FAISS Vector Database",
        use_container_width=True,
    ):

        with st.spinner(
            "Rebuilding knowledge base..."
        ):

            try:

                rebuild_vectorstore()

                st.success(
                    "Knowledge base rebuilt successfully."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Failed to rebuild knowledge base: {e}"
                )


# ============================================================
# SYSTEM STATUS
# ============================================================

elif page == "⚙️ System Status":

    show_hero()

    st.markdown(
        "### ⚙️ System Status"
    )

    # --------------------------------------------------------
    # COMPONENT STATUS
    # --------------------------------------------------------

    components = {
        "Employee CSV": EMPLOYEE_FILE.exists(),
        "Documents Folder": DOCUMENTS_DIR.exists(),
        "FAISS Index": (
            VECTORSTORE_DIR / "index.faiss"
        ).exists(),
        "FAISS Metadata": (
            VECTORSTORE_DIR / "index.pkl"
        ).exists(),
    }

    for name, status in components.items():

        if status:

            st.success(
                f"✅ {name}: Ready"
            )

        else:

            st.error(
                f"❌ {name}: Missing"
            )

    st.divider()

    # --------------------------------------------------------
    # DATASET DETAILS
    # --------------------------------------------------------

    st.markdown(
        "### 📊 Dataset Information"
    )

    info_card(
        "Employee Records",
        f"{len(df):,} records",
    )

    info_card(
        "Columns",
        ", ".join(df.columns),
    )

    info_card(
        "Cities",
        ", ".join(
            sorted(
                df["City"]
                .dropna()
                .unique()
                .tolist()
            )
        ),
    )

    # --------------------------------------------------------
    # ARCHITECTURE
    # --------------------------------------------------------

    st.markdown(
        "### 🏗️ Architecture"
    )

    st.code(
        """
User
  │
  ▼
Streamlit UI
  │
  ▼
Question Router
  │
  ├───────────────┐
  ▼               ▼
Employee Data    Policy RAG
(Pandas)         │
                 ▼
             FAISS Search
                 │
                 ▼
            Ollama Llama 3.2
                 │
                 ▼
              Answer
        """,
        language="text",
    )

    st.divider()

    st.markdown(
        "### 🔮 Future Architecture"
    )

    st.code(
        """
Power Apps
    │
    ▼
Microsoft Dataverse
    │
    ▼
AI / Copilot Layer
    │
    ▼
RAG + Structured Data
    │
    ▼
Grounded Employee Assistant
        """,
        language="text",
    )


# ============================================================
# FOOTER
# ============================================================

show_footer()