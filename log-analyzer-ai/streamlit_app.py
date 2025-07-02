import streamlit as st
import json
import io
from parser import parse_log_file
from analyser import analyze_entries
import pandas as pd
import matplotlib.pyplot as plt
from ai_utils import style_missing_entries

st.set_page_config(page_title="🌀 Data Health Dashboard", layout="wide")

# Sidebar - File uploader
st.sidebar.markdown("# 🔄 Data Controls")
uploaded_file = st.sidebar.file_uploader("Select a .txt crawl log", type=["txt"])

if uploaded_file:
    st.sidebar.success(f"✅ File Loaded: `{uploaded_file.name}`")
else:
    st.sidebar.info("👈 Please upload a log file")

st.title("🌀 Data Health Dashboard")
st.markdown("Analyze URL ➡ PID ➡ DetailItem consistency from your crawl log files.")

if uploaded_file:
    # Read file content as string stream
    file_obj = io.StringIO(uploaded_file.getvalue().decode("utf-8"))

    # Run parser
    with st.spinner("🔍 Parsing log file..."):
        parsed_data = parse_log_file(file_obj)

    # Analyze parsed content
    with st.spinner("📊 Analyzing entries..."):
        report = analyze_entries(parsed_data)

    # Summary
    st.markdown("## 📌 Summary")
    st.json(report["summary"])

    # Missing entries
    if report.get("missing"):
        st.markdown("## ❌ Missing Entries (With AI Diagnosis)")
        missing_df = pd.DataFrame(report["missing"])
        cols = [col for col in ["url", "pid", "title", "reason", "ai_reason"] if col in missing_df.columns]
        styled_df = style_missing_entries(missing_df[cols])
        st.dataframe(styled_df, use_container_width=True)

        if st.button("🔍 Rerun AI Diagnosis for Missing URLs"):
            from ai_utils import diagnose_missing_url
            with st.spinner("Re-analyzing missing URLs with AI..."):
                for entry in report["missing"]:
                    entry["ai_reason"] = diagnose_missing_url(entry.get("url"), entry.get("reason", ""))
            st.rerun()

    # Matched entries (optional)
    with st.expander("✅ Matched Entries", expanded=False):
        st.dataframe(report["matched"], use_container_width=True)

    # Download report
    st.markdown("## ⬇️ Download Report")
    report_json = json.dumps(report, indent=2)
    st.download_button("Download JSON Report", report_json, file_name="analysis_report.json", mime="application/json")
    
    st.markdown("## 📊 Visual Summary")

    # Convert summary to DataFrame
    summary_df = pd.DataFrame.from_dict(report["summary"], orient="index", columns=["Count"])

    # Show bar chart
    st.bar_chart(summary_df)

    # Pie chart: matched vs missing
    if "matched" in report["summary"] and "missing" in report["summary"]:
        match_data = pd.DataFrame({
            "Status": ["Matched", "Missing"],
            "Count": [
                report["summary"]["matched"],
                report["summary"]["missing"]
            ]
        })

        st.markdown("### 📎 Match vs Missing (Pie Chart)")
        fig, ax = plt.subplots()
        ax.pie(match_data["Count"], labels=match_data["Status"], autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

    