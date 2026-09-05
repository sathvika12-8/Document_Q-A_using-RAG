# rag.py

import shutil
import re

import streamlit as st
from pypdf import PdfReader

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from ollama import Client

from config import (
    DOCUMENTS_DIR,
    VECTORSTORE_DIR,
    OLLAMA_HOST,
    OLLAMA_MODEL,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K,
)


# ============================================================
# SETTINGS
# ============================================================

# Retrieve more candidates than the final number of context chunks.
RETRIEVAL_K = 10

# Number of chunks actually sent to Ollama.
CONTEXT_K = 6


# ============================================================
# EMBEDDINGS
# ============================================================

@st.cache_resource
def get_embeddings():

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        },
    )


# ============================================================
# OLLAMA
# ============================================================

@st.cache_resource
def get_ollama():

    return Client(
        host=OLLAMA_HOST
    )


# ============================================================
# LOAD PDF DOCUMENTS
# ============================================================

def load_pdf_documents():

    documents = []

    if not DOCUMENTS_DIR.exists():
        return documents

    pdf_files = sorted(
        DOCUMENTS_DIR.glob("*.pdf")
    )

    for pdf_path in pdf_files:

        try:

            reader = PdfReader(
                str(pdf_path)
            )

            for page_number, page in enumerate(
                reader.pages,
                start=1
            ):

                try:
                    text = page.extract_text() or ""
                except Exception:
                    text = ""

                text = text.strip()

                if not text:
                    continue

                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": pdf_path.name,
                            "page": page_number,
                        },
                    )
                )

        except Exception as e:

            print(
                f"Error reading {pdf_path.name}: {e}"
            )

    return documents


# ============================================================
# SPLIT DOCUMENTS
# ============================================================

def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
        ],
    )

    return splitter.split_documents(
        documents
    )


# ============================================================
# CREATE VECTOR STORE
# ============================================================

def create_vectorstore():

    documents = load_pdf_documents()

    if not documents:

        raise ValueError(
            "No PDF documents were found in the documents folder."
        )

    chunks = split_documents(
        documents
    )

    if not chunks:

        raise ValueError(
            "PDF documents were found, but no readable text was extracted."
        )

    embeddings = get_embeddings()

    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    VECTORSTORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    vectorstore.save_local(
        str(VECTORSTORE_DIR)
    )

    print(
        f"Created FAISS index with {len(chunks)} chunks."
    )

    return vectorstore


# ============================================================
# LOAD / CREATE VECTOR STORE
# ============================================================

@st.cache_resource
def get_vectorstore():

    index_file = (
        VECTORSTORE_DIR / "index.faiss"
    )

    pickle_file = (
        VECTORSTORE_DIR / "index.pkl"
    )

    embeddings = get_embeddings()

    if (
        index_file.exists()
        and pickle_file.exists()
    ):

        try:

            vectorstore = FAISS.load_local(
                str(VECTORSTORE_DIR),
                embeddings,
                allow_dangerous_deserialization=True,
            )

            return vectorstore

        except Exception as e:

            print(
                f"Could not load FAISS index: {e}"
            )

    return create_vectorstore()


# ============================================================
# REBUILD VECTOR STORE
# ============================================================

def rebuild_vectorstore():

    if VECTORSTORE_DIR.exists():

        shutil.rmtree(
            VECTORSTORE_DIR
        )

    VECTORSTORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    st.cache_resource.clear()

    return create_vectorstore()


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# QUERY EXPANSION
# ============================================================

def expand_query(question):

    """
    Generate useful search terms for common company-policy
    questions.

    This helps when the user's wording differs from the
    wording used inside the PDF.
    """

    q = question.lower()

    queries = [
        question
    ]

    # --------------------------------------------------------
    # Overtime
    # --------------------------------------------------------

    if any(
        word in q
        for word in [
            "overtime",
            "over time",
            "extra hours",
            "extra work",
        ]
    ):

        queries.extend([
            "overtime policy",
            "overtime eligibility",
            "overtime authorization",
            "overtime hours",
            "overtime compensation",
            "employees working overtime",
        ])

    # --------------------------------------------------------
    # Benefits
    # --------------------------------------------------------

    if any(
        word in q
        for word in [
            "benefit",
            "benefits",
            "employee benefits",
        ]
    ):

        queries.extend([
            "employee benefits",
            "benefits eligibility",
            "health benefits",
            "insurance benefits",
            "retirement benefits",
        ])

    # --------------------------------------------------------
    # Security / acceptable use
    # --------------------------------------------------------

    if any(
        word in q
        for word in [
            "security",
            "cybersecurity",
            "acceptable use",
            "it security",
        ]
    ):

        queries.extend([
            "IT acceptable use policy",
            "information security",
            "computer security",
            "system security",
            "acceptable use rules",
        ])

    # --------------------------------------------------------
    # Credit card
    # --------------------------------------------------------

    if any(
        word in q
        for word in [
            "credit card",
            "company card",
            "corporate card",
        ]
    ):

        queries.extend([
            "company credit card policy",
            "corporate credit card rules",
            "credit card usage",
            "credit card expenses",
            "credit card authorization",
        ])

    # --------------------------------------------------------
    # Cost monitoring
    # --------------------------------------------------------

    if any(
        word in q
        for word in [
            "cost",
            "cost monitoring",
            "cost control",
        ]
    ):

        queries.extend([
            "cost monitoring policy",
            "cost control policy",
            "cost management",
            "monitoring and control",
        ])

    # --------------------------------------------------------
    # Leave
    # --------------------------------------------------------

    if "leave" in q:

        queries.extend([
            "employee leave policy",
            "leave rules",
            "leave eligibility",
            "leave requirements",
        ])

    # --------------------------------------------------------
    # Expenses
    # --------------------------------------------------------

    if any(
        word in q
        for word in [
            "expense",
            "expenses",
            "reimbursement",
            "reimburse",
        ]
    ):

        queries.extend([
            "employee expenses",
            "expense reimbursement",
            "business expenses",
            "expense policy",
        ])

    # Remove duplicates while preserving order

    unique_queries = []

    seen = set()

    for query in queries:

        key = normalize_text(
            query
        )

        if key not in seen:

            seen.add(key)

            unique_queries.append(
                query
            )

    return unique_queries


# ============================================================
# QUERY TERMS
# ============================================================

def get_query_terms(question):

    stopwords = {
        "what",
        "are",
        "is",
        "the",
        "a",
        "an",
        "how",
        "does",
        "do",
        "did",
        "can",
        "could",
        "would",
        "should",
        "please",
        "tell",
        "me",
        "about",
        "of",
        "for",
        "to",
        "in",
        "on",
        "and",
        "or",
        "with",
        "this",
        "that",
        "these",
        "those",
        "company",
        "provide",
        "available",
        "does",
        "my",
        "your",
    }

    words = normalize_text(
        question
    ).split()

    return {
        word
        for word in words
        if len(word) >= 3
        and word not in stopwords
    }


# ============================================================
# KEYWORD SCORE
# ============================================================

def keyword_score(question, document):

    query_terms = get_query_terms(
        question
    )

    if not query_terms:
        return 0

    text = normalize_text(
        document.page_content
    )

    score = 0

    for term in query_terms:

        if term in text:

            # Stronger weighting for important terms
            if term in {
                "overtime",
                "benefit",
                "benefits",
                "insurance",
                "security",
                "credit",
                "card",
                "leave",
                "expense",
                "expenses",
                "cost",
                "monitoring",
                "control",
                "policy",
            }:

                score += 3

            else:

                score += 1

    return score


# ============================================================
# RETRIEVE RELEVANT DOCUMENTS
# ============================================================

def retrieve_documents(question):

    vectorstore = get_vectorstore()

    queries = expand_query(
        question
    )

    candidates = []

    # --------------------------------------------------------
    # Semantic retrieval
    # --------------------------------------------------------

    for query in queries:

        try:

            results = (
                vectorstore.similarity_search_with_score(
                    query,
                    k=RETRIEVAL_K
                )
            )

            for document, distance in results:

                candidates.append(
                    {
                        "document": document,
                        "distance": float(distance),
                    }
                )

        except Exception as e:

            print(
                f"Retrieval error for query '{query}': {e}"
            )

    # --------------------------------------------------------
    # Deduplicate documents
    # --------------------------------------------------------

    unique = {}

    for item in candidates:

        document = item["document"]

        source = document.metadata.get(
            "source",
            "Unknown"
        )

        page = document.metadata.get(
            "page",
            "?"
        )

        text_key = (
            source,
            page,
            document.page_content[:200]
        )

        if text_key not in unique:

            unique[text_key] = item

        else:

            # Keep the better semantic score
            if item["distance"] < unique[text_key]["distance"]:

                unique[text_key] = item

    candidates = list(
        unique.values()
    )

    # --------------------------------------------------------
    # Combine semantic + keyword relevance
    # --------------------------------------------------------

    for item in candidates:

        document = item["document"]

        item["keyword_score"] = keyword_score(
            question,
            document
        )

        # Lower FAISS distance is better.
        #
        # Keyword relevance is added as a bonus.
        item["combined_score"] = (
            item["keyword_score"] * 2
            - item["distance"]
        )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    candidates.sort(
        key=lambda x: x["combined_score"],
        reverse=True
    )

    # --------------------------------------------------------
    # Select top context
    # --------------------------------------------------------

    selected = []

    for item in candidates:

        document = item["document"]

        if document not in selected:

            selected.append(
                document
            )

        if len(selected) >= CONTEXT_K:

            break

    return selected


# ============================================================
# FORMAT SOURCES
# ============================================================

def format_sources(documents):

    sources = []

    seen = set()

    for document in documents:

        source = document.metadata.get(
            "source",
            "Unknown document"
        )

        page = document.metadata.get(
            "page",
            "?"
        )

        key = (
            source,
            page
        )

        if key in seen:
            continue

        seen.add(key)

        sources.append(
            {
                "document": source,
                "page": page,
            }
        )

    return sources


# ============================================================
# NOT FOUND DETECTION
# ============================================================

def is_not_found_answer(answer):

    if not answer:
        return False

    answer_lower = answer.lower()

    phrases = [
        "could not find this information",
        "couldn't find this information",
        "information is not available",
        "information was not found",
        "not found in the available",
        "not mentioned in the available",
        "not specified in the available",
        "documents do not provide",
        "documents don't provide",
        "documents do not mention",
        "documents don't mention",
        "not stated in the documents",
        "not explicitly stated",
        "not available in the documents",
        "not mentioned in the documents",
        "not specified in the documents",
    ]

    return any(
        phrase in answer_lower
        for phrase in phrases
    )


# ============================================================
# POLICY QUERY
# ============================================================

def policy_query(question):

    try:

        documents = retrieve_documents(
            question
        )

    except Exception as e:

        return (
            f"Unable to retrieve information from the company documents: {e}",
            []
        )

    if not documents:

        return (
            "I could not find this information in the available company documents.",
            []
        )

    # --------------------------------------------------------
    # Build context
    # --------------------------------------------------------

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1
    ):

        source = document.metadata.get(
            "source",
            "Unknown document"
        )

        page = document.metadata.get(
            "page",
            "?"
        )

        text = document.page_content.strip()

        context_parts.append(
            f"""
DOCUMENT {index}

SOURCE: {source}
PAGE: {page}

CONTENT:
{text}
"""
        )

    context = "\n\n".join(
        context_parts
    )

    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    prompt = f"""
You are Employee AI, a workplace document assistant.

Your job is to answer the user's question using the company
documents supplied below.

GROUNDING RULES:

1. Use ONLY the supplied document context.
2. Do NOT use outside knowledge.
3. Do NOT invent company rules.
4. Do NOT guess.
5. Do NOT assume something is true because it sounds reasonable.
6. Answer directly and clearly.
7. When the documents contain the answer, provide the answer.
8. If multiple documents provide relevant information, combine
   them carefully.
9. Do not combine unrelated information.
10. If the documents do not contain enough information to answer
    the question, say exactly:

"I could not find this information in the available company documents."

11. For yes/no questions, only answer yes or no when the
    supplied documents explicitly support that answer.
12. Do not mention FAISS, embeddings, vector databases,
    retrieval, prompts, or internal implementation details.
13. Keep the response concise but useful.
14. If the question asks about rules, summarize the relevant
    rules as bullet points when appropriate.
15. If the documents contain eligibility, requirements,
    restrictions, authorization, or exceptions, include them
    when relevant.

USER QUESTION:
{question}

COMPANY DOCUMENT CONTEXT:
{context}

ANSWER:
"""

    # --------------------------------------------------------
    # Ollama
    # --------------------------------------------------------

    try:

        ollama = get_ollama()

        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": 0,
                "num_predict": 350,
            },
        )

        answer = (
            response["message"]["content"]
            .strip()
        )

    except Exception as e:

        return (
            f"Unable to generate an answer: {e}",
            []
        )

    # --------------------------------------------------------
    # Not found
    # --------------------------------------------------------

    if is_not_found_answer(
        answer
    ):

        return (
            "I could not find this information in the available company documents.",
            []
        )

    # --------------------------------------------------------
    # Sources
    # --------------------------------------------------------

    sources = format_sources(
        documents
    )

    return (
        answer,
        sources
    )


# ============================================================
# DEBUG / TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("EMPLOYEE AI - RAG TEST")
    print("=" * 70)

    test_questions = [
        "What are the overtime rules?",
        "What does the IT Acceptable Use Policy cover?",
        "What are the company credit card rules?",
        "What benefits are available?",
        "What does the cost monitoring policy require?",
        "Does the company provide pet insurance?",
    ]

    for question in test_questions:

        print("\n")
        print("-" * 70)

        print(
            "QUESTION:",
            question
        )

        try:

            answer, sources = policy_query(
                question
            )

            print(
                "\nANSWER:"
            )

            print(
                answer
            )

            print(
                "\nSOURCES:"
            )

            if sources:

                for source in sources:

                    print(
                        f"- {source['document']} "
                        f"(Page {source['page']})"
                    )

            else:

                print(
                    "No sources"
                )

        except Exception as e:

            print(
                "\nERROR:",
                e
            )

    print("\n")
    print("=" * 70)
    print("TEST COMPLETED")
    print("=" * 70)