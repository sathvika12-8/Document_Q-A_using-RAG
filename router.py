import re

from employee_data import load_employee_data, employee_query
from rag import policy_query


# ============================================================
# EMPLOYEE QUESTION DETECTION
# ============================================================

def contains_employee_signal(question):

    q = question.lower()

    employee_patterns = [
        r"\bhow many employees\b",
        r"\bnumber of employees\b",
        r"\bemployees in\b",
        r"\bemployee count\b",
        r"\baverage age\b",
        r"\baverage experience\b",
        r"\bjoined in\b",
        r"\bjoining year\b",
        r"\bjoined\b",
        r"\bfemale employees\b",
        r"\bmale employees\b",
        r"\bpayment tier\b",
        r"\bbenched\b",
        r"\bon leave\b",
        r"\bemployees are\b",
        r"\bstaff count\b",
    ]

    return any(
        re.search(pattern, q)
        for pattern in employee_patterns
    )


# ============================================================
# POLICY QUESTION DETECTION
# ============================================================

def contains_policy_signal(question):

    q = question.lower()

    policy_patterns = [
        r"\bpolicy\b",
        r"\bpolicies\b",
        r"\bovertime\b",
        r"\bcredit card\b",
        r"\bacceptable use\b",
        r"\bit security\b",
        r"\bsecurity rules\b",
        r"\bcost monitoring\b",
        r"\bcost control\b",
        r"\bbenefits\b",
        r"\binsurance\b",
        r"\bretirement\b",
        r"\bleave policy\b",
        r"\bworking hours\b",
        r"\bexpenses\b",
        r"\bexpense policy\b",
        r"\bcompany rules\b",
        r"\bcompany rule\b",
        r"\bwhat does .* require\b",
        r"\bwhat does .* cover\b",
        r"\bwhat are the .* rules\b",
    ]

    return any(
        re.search(pattern, q)
        for pattern in policy_patterns
    )


# ============================================================
# EXTRACT EMPLOYEE PART FROM HYBRID QUESTION
# ============================================================

def extract_employee_question(question):

    q = question.strip()

    patterns = [
        r"(how many employees are in [^?]+)",
        r"(how many employees are there in [^?]+)",
        r"(how many female employees are there)",
        r"(how many male employees are there)",
        r"(what is the average employee age)",
        r"(what is the average age)",
        r"(what is the average experience)",
        r"(how many employees joined in \d{4})",
        r"(how many employees joined \w+)",
    ]

    matches = []

    for pattern in patterns:

        found = re.findall(
            pattern,
            q,
            flags=re.IGNORECASE,
        )

        matches.extend(found)

    if matches:
        return matches[0].strip()

    return q


# ============================================================
# REMOVE EMPLOYEE PART FROM POLICY QUESTION
# ============================================================

def extract_policy_question(question):

    q = question.strip()

    patterns = [
        r"\band how many employees are in [^?]+",
        r"\band how many employees are there in [^?]+",
        r"\band how many female employees are there",
        r"\band how many male employees are there",
        r"\band what is the average employee age",
        r"\band what is the average age",
        r"\band what is the average experience",
        r"\bhow many employees are in [^?]+",
        r"\bhow many employees are there in [^?]+",
        r"\bhow many female employees are there",
        r"\bhow many male employees are there",
        r"\bwhat is the average employee age",
        r"\bwhat is the average age",
        r"\bwhat is the average experience",
        r"\bhow many employees joined in \d{4}",
    ]

    cleaned = q

    for pattern in patterns:

        cleaned = re.sub(
            pattern,
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

    cleaned = cleaned.strip()

    # Remove leftover connectors.
    cleaned = re.sub(
        r"\s+(and|also|plus)\s*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    return cleaned.strip(" ,")


# ============================================================
# HYBRID QUERY
# ============================================================

def hybrid_query(question, df):

    employee_question = extract_employee_question(
        question
    )

    policy_question = extract_policy_question(
        question
    )

    employee_answer = employee_query(
        employee_question,
        df,
    )

    policy_answer, sources = policy_query(
        policy_question
    )

    answer_parts = []

    # Policy section
    if policy_answer:
        answer_parts.append(
            f"### 📄 Policy Information\n\n"
            f"{policy_answer}"
        )

    # Employee section
    if employee_answer:
        answer_parts.append(
            f"### 👥 Employee Data\n\n"
            f"{employee_answer}"
        )

    answer = "\n\n".join(answer_parts)

    return answer, sources


# ============================================================
# MAIN ROUTER
# ============================================================

def ask_assistant(question):

    question = question.strip()

    if not question:
        return (
            "Please enter a question.",
            [],
            "Unknown",
        )

    df = load_employee_data()

    employee_signal = contains_employee_signal(
        question
    )

    policy_signal = contains_policy_signal(
        question
    )

    # --------------------------------------------------------
    # HYBRID
    # --------------------------------------------------------

    if employee_signal and policy_signal:

        answer, sources = hybrid_query(
            question,
            df,
        )

        return (
            answer,
            sources,
            "Hybrid",
        )

    # --------------------------------------------------------
    # EMPLOYEE
    # --------------------------------------------------------

    if employee_signal:

        answer = employee_query(
            question,
            df,
        )

        return (
            answer,
            [],
            "Employee",
        )

    # --------------------------------------------------------
    # POLICY
    # --------------------------------------------------------

    if policy_signal:

        answer, sources = policy_query(
            question
        )

        return (
            answer,
            sources,
            "Policy",
        )

    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    answer, sources = policy_query(
        question
    )

    return (
        answer,
        sources,
        "Policy",
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_questions = [
        "How many employees joined in 2017?",
        "How many employees are in Bangalore?",
        "What are the overtime rules?",
        "What does cost monitoring require?",
        "What are the overtime rules and how many employees are in Bangalore?",
        "What are the security rules and how many employees are in Pune?",
        "Does the company provide pet insurance?",
    ]

    for question in test_questions:

        print("\n" + "=" * 70)
        print("QUESTION:", question)

        answer, sources, category = ask_assistant(
            question
        )

        print("CATEGORY:", category)
        print("\nANSWER:")
        print(answer)

        if sources:

            print("\nSOURCES:")

            for source in sources:
                print(
                    f"- {source['document']} "
                    f"(Page {source['page']})"
                )