import streamlit as st
from typing import Tuple
import pandas as pd
import datetime
import openai
import os

CATEGORY_KEYWORDS = {
    "Railway Concession Pass": {
        "keywords": ["railway pass", "railway concession"],
        "email": "compliance.cse@kiit.ac.in",
        "url": None
    },
    "Head Signature on Application Form": {
        "keywords": ["gate form", "cat form", "application signature"],
        "email": "compliance.cse@kiit.ac.in",
        "url": None
    },
    "Email Group ID Issue": {
        "keywords": ["email group id", "not receiving emails"],
        "email": "helpdesk@kiit.ac.in",
        "url": None
    },
    "Library Access": {
        "keywords": ["library access", "library book", "library fine"],
        "email": "beda_sahoo@kiit.ac.in",
        "url": None
    },
    "Fee & SAP Issues": {
        "keywords": ["fee discrepancy", "sap update", "payment issue"],
        "email": "manoj.meher@kiit.ac.in",
        "url": None
    },
    "Student Activity Centre": {
        "keywords": ["student club", "extracurricular activity"],
        "email": "studentssupport@kiit.ac.in",
        "url": "https://ksac.kiit.ac.in/"
    },
    "Grievance Helpdesk": {
        "keywords": ["grievance", "student complaint"],
        "email": "grievance.psp@kiit.ac.in",
        "url": "https://kiit.ac.in/grievance/"
    },
    "Guest House Booking": {
        "keywords": ["guest house", "stay request"],
        "email": "kiitguesthouse@kiit.ac.in",
        "url": None
    },
    "Other": {
        "keywords": [],
        "email": "deanoffice@kiit.ac.in",
        "url": None
    }
}

history = []

def classify_query(query: str) -> Tuple[str, str, str, str]:
    query_lower = query.lower()
    match_scores = {}
    keyword_map = {}

    for category, data in CATEGORY_KEYWORDS.items():
        match_count = 0
        for keyword in data["keywords"]:
            if keyword in query_lower:
                match_count += 1
                keyword_map[category] = keyword_map.get(category, []) + [keyword]
        if match_count > 0:
            match_scores[category] = match_count

    if match_scores:
        best_category = max(match_scores, key=match_scores.get)
        email = CATEGORY_KEYWORDS[best_category].get("email", "Not listed")
        url = CATEGORY_KEYWORDS[best_category].get("url")
        matched_keywords = ", ".join(keyword_map[best_category])

        st.subheader("🔎 Matching Categories")
        for cat, count in sorted(match_scores.items(), key=lambda x: -x[1]):
            words = ", ".join(keyword_map[cat])
            st.markdown(f"**{cat}** — {count} match(es) → _{words}_")

        return best_category, email, url, matched_keywords

    openai.api_key = st.secrets["OPENAI_API_KEY"]
    categories = list(CATEGORY_KEYWORDS.keys())
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that classifies student queries based on department."},
                {"role": "user", "content": f"Given the following categories: {categories}.\nClassify this query: {query}"}
            ],
            temperature=0.2,
        )
        best_category = response["choices"][0]["message"]["content"].strip()
        if best_category not in CATEGORY_KEYWORDS:
            best_category = "Other"
    except Exception:
        st.warning("Semantic fallback failed. Using default.")
        best_category = "Other"

    email = CATEGORY_KEYWORDS[best_category].get("email", "Not listed")
    url = CATEGORY_KEYWORDS[best_category].get("url")
    return best_category, email, url, "semantic"

def generate_email_to_student(query: str, category: str, email: str) -> str:
    return f"""
Dear Student,

Thank you for reaching out with your concern:

> {query.strip()}

After reviewing your query, it is recommended that you contact the respective department at: {email}

Feel free to let me know if you need any further help.

Regards,
Mentor
"""

def main():
    st.set_page_config(page_title="KIIT Query Router", layout="centered")
    st.title("📩 KIIT Mentee Query Email Routing Tool")
    st.write("Classify a mentee's query and get department email, link, and a ready-to-send response.")

    with st.expander("🗂 Upload CSV of Queries"):
        csv_file = st.file_uploader("Upload a CSV file with a 'Query' column", type="csv")
        if csv_file:
            df = pd.read_csv(csv_file)
            if "Query" in df.columns:
                results = []
                for query in df["Query"]:
                    category, email, url, keyword = classify_query(query)
                    results.append({
                        "Query": query,
                        "Category": category,
                        "Email": email,
                        "Matched Keyword": keyword,
                        "URL": url
                    })
                result_df = pd.DataFrame(results)
                st.dataframe(result_df)
                st.download_button("Download Classified CSV", result_df.to_csv(index=False), "classified_queries.csv")
            else:
                st.error("CSV must contain a column titled 'Query'.")

    st.subheader("🔍 Classify Individual Query")
    query = st.text_area("Enter the query from student:", height=150)

    if st.button("Classify and Suggest"):
        if query.strip():
            category, email, url, keyword = classify_query(query)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history.append({"Timestamp": timestamp, "Query": query, "Category": category, "Email": email, "Keyword": keyword})
            st.success(f"📌 Category: {category}")
            if keyword:
                st.caption(f"🔍 Matched on: '{keyword}'")
            if email:
                st.info(f"📧 Email ID: `{email}`")
            if url:
                st.markdown(f"🔗 [Useful Link]({url})" if url.startswith("http") else f"📞 Contact Info: {url}")
            st.subheader("📩 Ready-to-Copy Reply Email")
            st.text_area("Email Draft:", generate_email_to_student(query, category, email), height=200)
        else:
            st.warning("Please enter a valid query.")

    with st.expander("📜 Session History"):
        if history:
            hist_df = pd.DataFrame(history)
            st.dataframe(hist_df)
            st.download_button("Download History", hist_df.to_csv(index=False), "query_history.csv")
        else:
            st.info("No queries classified yet.")

if __name__ == "__main__":
    main()
