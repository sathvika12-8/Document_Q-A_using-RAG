import re
import pandas as pd

from config import EMPLOYEE_FILE


# ============================================================
# LOAD EMPLOYEE DATA
# ============================================================

def load_employee_data():
    """Load employee CSV into a DataFrame."""

    if not EMPLOYEE_FILE.exists():
        return pd.DataFrame()

    return pd.read_csv(EMPLOYEE_FILE)


# ============================================================
# EMPLOYEE QUERY ENGINE
# ============================================================

def employee_query(question, df=None):
    """
    Answer structured employee questions directly using Pandas.
    This avoids using the LLM for numerical questions.
    """

    if df is None:
        df = load_employee_data()

    if df.empty:
        return None

    q = question.lower().strip()

    # --------------------------------------------------------
    # JOINING YEAR
    # IMPORTANT: Check this BEFORE generic employee count.
    # --------------------------------------------------------

    year_match = re.search(
        r"(?:joining|joined)\s*(?:in\s*)?(?:year\s*)?(20\d{2})",
        q
    )

    if year_match:
        year = int(year_match.group(1))

        count = (
            pd.to_numeric(
                df["JoiningYear"],
                errors="coerce"
            )
            .eq(year)
            .sum()
        )

        return (
            f"**{count:,} employees** joined in **{year}**."
        )

    # --------------------------------------------------------
    # CITY
    # --------------------------------------------------------

    cities = {
        "bangalore": "Bangalore",
        "bengaluru": "Bangalore",
        "pune": "Pune",
        "new delhi": "New Delhi",
    }

    for keyword, city in cities.items():

        if keyword in q:

            count = (
                df["City"]
                .astype(str)
                .str.lower()
                .eq(city.lower())
                .sum()
            )

            if (
                "how many" in q
                or "number" in q
                or "employees" in q
                or "people" in q
            ):
                return (
                    f"There are **{count:,} employees** "
                    f"in **{city}**."
                )

    # --------------------------------------------------------
    # GENDER
    # --------------------------------------------------------

    if "female" in q:

        count = (
            df["Gender"]
            .astype(str)
            .str.lower()
            .eq("female")
            .sum()
        )

        return f"There are **{count:,} female employees**."

    if "male" in q:

        count = (
            df["Gender"]
            .astype(str)
            .str.lower()
            .eq("male")
            .sum()
        )

        return f"There are **{count:,} male employees**."

    # --------------------------------------------------------
    # AVERAGE AGE
    # --------------------------------------------------------

    if "average age" in q:

        value = pd.to_numeric(
            df["Age"],
            errors="coerce"
        ).mean()

        return (
            f"The average employee age is "
            f"**{value:.1f} years**."
        )

    # --------------------------------------------------------
    # AVERAGE EXPERIENCE
    # --------------------------------------------------------

    if (
        "average experience" in q
        or "average experience in current domain" in q
    ):

        value = pd.to_numeric(
            df["ExperienceInCurrentDomain"],
            errors="coerce"
        ).mean()

        return (
            "The average experience in the current domain is "
            f"**{value:.1f} years**."
        )

    # --------------------------------------------------------
    # PAYMENT TIER
    # --------------------------------------------------------

    match = re.search(
        r"payment\s*tier\s*(1|2|3)",
        q
    )

    if match:

        tier = match.group(1)

        count = (
            df["PaymentTier"]
            .astype(str)
            .eq(tier)
            .sum()
        )

        return (
            f"There are **{count:,} employees** "
            f"in Payment Tier **{tier}**."
        )

    # --------------------------------------------------------
    # BENCHED
    # --------------------------------------------------------

    if "benched" in q:

        counts = df["EverBenched"].value_counts()

        yes = int(counts.get("Yes", 0))
        no = int(counts.get("No", 0))

        return (
            f"**{yes:,} employees** have been benched, "
            f"while **{no:,}** have not."
        )

    # --------------------------------------------------------
    # LEAVE DATA
    # --------------------------------------------------------

    if "leave" in q and "policy" not in q:

        counts = df["LeaveOrNot"].value_counts()

        leave_yes = int(counts.get(1, 0))
        leave_no = int(counts.get(0, 0))

        return (
            f"**{leave_yes:,} employees** are marked as "
            f"LeaveOrNot = 1, while **{leave_no:,}** "
            f"are marked as LeaveOrNot = 0."
        )

    # --------------------------------------------------------
    # TOTAL EMPLOYEES
    # IMPORTANT: Keep this LAST.
    # --------------------------------------------------------

    if (
        "how many employees" in q
        or "total employees" in q
        or "number of employees" in q
    ):

        return (
            f"There are **{len(df):,} employees** "
            "in the employee dataset."
        )

    return None


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    df = load_employee_data()

    print("Employee records:", len(df))
    print()

    test_questions = [
        "How many employees joined in 2017?",
        "How many employees are in Bangalore?",
        "How many employees are in Pune?",
        "How many male employees are there?",
        "What is the average experience?",
    ]

    for question in test_questions:

        print("Question:", question)

        answer = employee_query(
            question,
            df
        )

        print("Answer:", answer)
        print("-" * 60)