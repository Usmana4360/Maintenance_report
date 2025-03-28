import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
from openpyxl import load_workbook
from openpyxl.styles import Font, Border, Side, Alignment
# Configure Google Gemini API Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Excel file setup
EXCEL_FILE = "generated_reports.xlsx"

# Function to generate report using Gemini AI
def generate_report(unit, machine, technician_name, issue):
    """Generates a professional maintenance report using Gemini AI based on technician input."""
    prompt = f"""
    You are an expert electrical maintenance engineer. Your task is to generate a **concise and professional** one-line report based on the details provided by the technician.

    **Details Provided:**
    - **Unit**: {unit}
    - **Machine**: {machine}
    - **Technician Name**: {technician_name}
    - **Issue Reported**: {issue}

    **Instructions:**
    - Write the report in a **clear and professional tone**.
    - Include key details, such as the unit, machine, and issue.
    - Maintain a **formal and technical style**, suitable for maintenance logs.
    - Keep the report **concise (one line only).**

    **Example Output:**
    "Technician {technician_name} diagnosed {issue} on {machine} in {unit}, performed necessary maintenance, and restored functionality."

    Now, generate a similar report based on the given details.
    """
    model = genai.GenerativeModel('gemini-1.5-pro')  # Use latest model
    response = model.generate_content(prompt)
    return response.text.strip()

# Function to save report in Excel
def save_to_excel(unit, machine, technician_name, issue, report):
    """Saves the generated report to an Excel file with structured formatting."""

    columns = ["Date", "Unit", "Machine", "Technician Name", "Issue", "Generated Report"]

    new_data = pd.DataFrame([{
        "Date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Unit": unit,
        "Machine": machine,
        "Technician Name": technician_name,
        "Issue": issue,
        "Generated Report": report
    }])

    if os.path.exists(EXCEL_FILE):
        try:
            existing_data = pd.read_excel(EXCEL_FILE, engine="openpyxl")
            if not all(col in existing_data.columns for col in columns):
                existing_data = existing_data[columns]
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            updated_data = new_data
    else:
        updated_data = new_data

    # Save Data
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="w") as writer:
        updated_data.to_excel(writer, index=False, sheet_name="Work Orders")

    # Formatting Excel File
    wb = load_workbook(EXCEL_FILE)
    ws = wb.active

    # Apply Styling
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    for row in ws.iter_rows():
        for cell in row:
            cell.border = thin_border
            cell.alignment = Alignment(wrap_text=True, vertical="center")

    # Auto-adjust column widths
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter  # Get column letter
        for cell in col:
            try:
                max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        ws.column_dimensions[col_letter].width = max_length + 2  # Add padding

    # Make header bold
    for cell in ws[1]:  
        cell.font = Font(bold=True)

    # Save the formatted file
    wb.save(EXCEL_FILE)

    print("✅ Report successfully saved with proper formatting!")

# Function to load existing reports
def load_reports():
    """Loads existing reports from Excel."""
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    return pd.DataFrame(columns=["Unit", "Machine", "Technician", "Issue", "Report"])

# Streamlit App
st.set_page_config(page_title="AI Maintenance Report Generator", layout="wide")
st.title("🔧 AI-Powered Maintenance Report Generator")

# User Inputs
col1, col2 = st.columns(2)
with col1:
    unit = st.text_input("Enter Unit:", placeholder="e.g., Unit 5")
    technician_name = st.text_input("Enter Technician Name:", placeholder="e.g., John Doe")
with col2:
    machine = st.text_input("Enter Machine Name:", placeholder="e.g., Compressor A1")
    issue = st.text_input("Enter Issue Reported:", placeholder="e.g., High temperature issue")

# Generate Report
if st.button("Generate Report"):
    if unit and machine and technician_name and issue:
        with st.spinner("Generating report..."):
            report = generate_report(unit, machine, technician_name, issue)
            save_to_excel(unit, machine, technician_name, issue, report)
            st.success("✅ Report generated and saved!")
            st.subheader("Generated Report:")
            st.write(report)
    else:
        st.warning("⚠ Please fill in all fields before generating the report.")

# Display Saved Reports
st.subheader("📁 Report History")
df_reports = load_reports()
st.dataframe(df_reports, use_container_width=True)

# Download Excel Button
if os.path.exists(EXCEL_FILE):
    with open(EXCEL_FILE, "rb") as file:
        st.download_button("📥 Download Reports", file, file_name="generated_reports.xlsx", 
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
