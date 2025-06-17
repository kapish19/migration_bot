import streamlit as st
from utils.database import db
from utils.reports import ReportGenerator
import pandas as pd
from datetime import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load Google AI API Key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_AI_KEY"))

# Configure page
st.set_page_config(
    page_title="Migration Analysis Chatbot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "report_data" not in st.session_state:
    st.session_state.report_data = None

# Sidebar for report configuration

with st.sidebar:
    st.header("Report Generator")

    # Get available countries
    all_countries = [x["_id"] for x in 
        db.migration_data.aggregate([
            {"$group": {"_id": "$Country of Origin"}}
        ])
    ]

    # ✅ Get year range safely
    year_bounds = next(
        db.migration_data.aggregate([
            {"$match": {"Year": {"$ne": None}}},
            {"$group": {
                "_id": None,
                "min": {"$min": "$Year"},
                "max": {"$max": "$Year"}
            }}
        ]),
        None
    )

    if year_bounds:
        min_year = year_bounds["min"]
        max_year = year_bounds["max"]
    else:
        st.error("No valid 'Year' data found in the database.")
        st.stop()

    # Allow user to choose single or multiple countries
    allow_multiple = st.checkbox("Select multiple countries", value=True)

    if allow_multiple:
        selected_countries = st.multiselect(
            "Select countries",
            options=all_countries,
            default=all_countries[:2] if len(all_countries) >= 2 else all_countries
        )
    else:
        selected_country = st.selectbox(
            "Select a country",
            options=all_countries
        )
        selected_countries = [selected_country]  # Normalize to list

    year_range = st.slider(
        "Select year range",
        min_value=min_year,
        max_value=max_year,
        value=(max_year - 5, max_year)
    )

    report_type = st.radio(
        "Report type",
        options=["Hotspot Prediction", "Impact Analysis"],
        index=0
    )

    if st.button("Generate Report"):
        with st.spinner("Collecting data..."):
            filters = {
                "Country of Origin": {"$in": selected_countries},
                "Year": {"$gte": year_range[0], "$lte": year_range[1]}
            }

            data = db.get_raw_data(filters)
            st.session_state.report_data = data

            with st.spinner("Analyzing with Google AI..."):
                if report_type == "Hotspot Prediction":
                    analysis = ReportGenerator.generate_hotspot_prediction(data)
                else:
                    analysis = ReportGenerator.generate_impact_report(data)

                pdf = ReportGenerator.create_pdf(
                    analysis,
                    f"{report_type} - {datetime.now().strftime('%Y-%m-%d')}"
                )

                st.download_button(
                    label="Download PDF Report",
                    data=pdf,
                    file_name=f"migration_{report_type.lower().replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )

# Main chatbot interface
st.title("🌍 Migration Analysis Chatbot")
st.caption("Ask questions about migration patterns and generate AI-powered reports")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about migration trends..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your question..."):
            try:
                stats = db.get_migration_stats()

                ai_prompt = f"""
                The user asked: {prompt}

                Here's some relevant migration data:
                - Refugees by year: {stats['by_year']}
                - Top origin countries: {stats['top_origins']}

                Provide a concise, data-informed response focusing on:
                1. Key trends in the data
                2. Any notable patterns
                3. Professional insights
                """

                model = genai.GenerativeModel("gemini-1.5-pro-latest")
                response = model.generate_content(ai_prompt)

                st.markdown(response.text)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response.text}
                )
            except Exception as e:
                st.error(f"Error processing your request: {str(e)}")

# Data preview
if st.session_state.report_data:
    with st.expander("View Report Data"):
        st.dataframe(
            pd.DataFrame(st.session_state.report_data).sort_values("Year"),
            use_container_width=True
        )
