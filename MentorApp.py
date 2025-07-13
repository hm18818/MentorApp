import streamlit as st
from typing import Tuple
import pandas as pd
import datetime
import openai

# Define all categories with keywords and correct email routing
CATEGORY_KEYWORDS = {
    "Bonafide Certificate": {
        "keywords": ["bonafide", "education loan", "passport", "scholarship", "higher studies", "course continuing"],
        "email": "compliance.cse@kiit.ac.in",
        "url": None
    },
    "Railway Concession Pass": {
        "keywords": ["railway pass", "train concession"],
        "email": "compliance.cse@kiit.ac.in",
        "url": None
    },
    "Grade Reports / Certificates": {
        "keywords": ["grade report", "provisional degree", "degree certificate", "conduct certificate", "college leaving"],
        "email": "compliance.cse@kiit.ac.in",
        "url": None
    },
    "Open Electives or Dept Electives": {
        "keywords": ["open elective", "department elective"],
        "email": "compliance.cse@kiit.ac.in",
        "url": None
    },
    "Rank / No Backlog Certificate": {
        "keywords": ["rank certificate", "no backlog certificate"],
        "email": "compliance.cse@kiit.ac.in",
        "url": None
    },
    "GATE / CAT Signature": {
        "keywords": ["gate signature", "cat signature"],
        "email": "compliance.cse@kiit.ac.in",
        "url": None
    },
    "Registration Card": {
        "keywords": ["registration card"],
        "email": "Not Available - Contact Mrs. Tunalata Nayak (8144967820)",
        "url": None
    },
    "Marks/Grades Discrepancy (2022-23, M.Tech, PhD)": {
        "keywords": ["marks", "grades", "answer sheet discrepancy", "2022", "2023", "mtech", "phd"],
        "email": "acoe.cese@kiit.ac.in",
        "url": None
    },
    "Marks/Grades Discrepancy (2024-25)": {
        "keywords": ["marks", "grades", "answer sheet discrepancy", "2024", "2025"],
        "email": "acoe.csit@kiit.ac.in",
        "url": None
    },
    "Correction / Scholarship": {
        "keywords": ["correction", "dob", "name", "address change", "scholarship"],
        "email": "swapna.mohanty@kiit.ac.in",
        "url": None
    },
    "Fee Extension": {
        "keywords": ["fee extension", "academic fee", "hostel fee"],
        "email": "director.admission@kiit.ac.in",
        "url": None
    },
    "Demand Letter for Loan": {
        "keywords": ["demand letter", "loan"],
        "email": "admission@kiit.ac.in",
        "url": None
    },
    "Laptop Issues": {
        "keywords": ["laptop", "laptop delivery", "laptop technical"],
        "email": "laptop.service@kiit.ac.in",
        "url": None
    },
    "Email Group Issues": {
        "keywords": ["group email", "not receiving mail"],
        "email": "helpdesk@kiit.ac.in",
        "url": None
    },
    "Library Issues": {
        "keywords": ["library", "library access", "library books"],
        "email": "beda_sahoo@kiit.ac.in",
        "url": None
    },
    "Fee & SAP": {
        "keywords": ["fee", "sap update", "fee mismatch"],
        "email": "manoj.meher@kiit.ac.in",
        "url": None
    },
    "Hostel Issues": {
        "keywords": ["hostel", "room", "allotment", "accommodation", "kp25"],
        "email": "hostel@kiit.ac.in",
        "url": None
    },
    "Placement / Internship": {
        "keywords": ["placement", "internship", "no objection", "training"],
        "email": "tnp.scs@kiit.ac.in",
        "url": None
    },
    "Sports": {
        "keywords": ["sports", "gym", "fitness", "recreational"],
        "email": "sports.kiit@gmail.com",
        "url": "https://kiit.ac.in/campuslife/sports/"
    },
    "KSAC": {
        "keywords": ["ksac", "student activity", "club"],
        "email": "shyam.behura@kids.ac.in",
        "url": "https://ksac.kiit.ac.in/"
    },
    "Grade Sheet Download": {
        "keywords": ["grade sheet", "download"],
        "email": "slcm.kiit@kiit.ac.in",
        "url": None
    },
    "Guest House": {
        "keywords": ["guest house"],
        "email": "kiitguesthouse@kiit.ac.in",
        "url": None
    },
    "Mentor Info": {
        "keywords": ["mentor", "sap"],
        "email": None,
        "url": "https://kiit.ac.in/sap/know-your-mentor/"
    },
    "Counselling": {
        "keywords": ["counselling", "support", "anxiety", "depression", "stress"],
        "email": "student.counselling@kiit.ac.in",
        "url": "https://kiit.ac.in/student-counselling/"
    },
    "Cyber Helpdesk": {
        "keywords": ["cyber", "phishing", "scam"],
        "email": "cyber.helpline@kiit.ac.in",
        "url": None
    },
    "SAP Helpdesk": {
        "keywords": ["sap help", "student portal"],
        "email": "helpdesksap.eam@kiit.ac.in",
        "url": None
    },
    "Career Placement": {
        "keywords": ["career", "placement"],
        "email": "placement@kiit.ac.in",
        "url": None
    },
    "NCC / NSS / Red Cross": {
        "keywords": ["ncc", "nss", "red cross", "community"],
        "email": "kiit.nss@kiit.ac.in",
        "url": None
    },
    "Student Support": {
        "keywords": ["club", "student support"],
        "email": "studentssupport@kiit.ac.in",
        "url": "https://kiit.ac.in/students/"
    },
    "Grievance Redressal": {
        "keywords": ["grievance", "complaint"],
        "email": "grievance.psp@kiit.ac.in",
        "url": "https://kiit.ac.in/grievance/"
    },
    "Internal Complaints": {
        "keywords": ["sexual harassment", "icc"],
        "email": None,
        "url": "https://kiit.ac.in/internal-complaint-committee/"
    },
    "Anti-Ragging": {
        "keywords": ["ragging"],
        "email": None,
        "url": "https://kiit.ac.in/antiragging/"
    },
    "Other": {
        "keywords": [],
        "email": "Not listed",
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

    # GPT fallback
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
    except Exception as e:
        st.warning("⚠️ Semantic fallback failed. Using default.")
        st.error(f"OpenAI error: {str(e)}")
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
                st.markdown(f"🔗 [Useful Link]({url})" if url and url.startswith("http") else f"📞 Contact Info: {url}")
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
