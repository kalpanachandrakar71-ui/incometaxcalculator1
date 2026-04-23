import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Income Tax Calculator", layout="wide")

st.title("💰 Income Tax Calculator (India - IT Act 1961 Simplified)")
st.caption("Compare Old vs New Regime with deductions and charts")

# =========================
# TAX ENGINE
# =========================
def compute_tax(income, slabs):
    tax = 0
    prev = 0
    rows = []

    for limit, rate in slabs:
        if income > prev:
            taxable = min(income, limit) - prev
            tax_amt = taxable * rate
            tax += tax_amt

            rows.append([f"{prev}-{limit if limit != float('inf') else 'Above'}",
                         taxable, rate, tax_amt])
            prev = limit
        else:
            break

    df = pd.DataFrame(rows, columns=["Slab", "Taxable", "Rate", "Tax"])
    return tax, df


# Old Regime Slabs (simplified)
OLD_SLABS = [
    (250000, 0.00),
    (500000, 0.05),
    (1000000, 0.20),
    (float("inf"), 0.30)
]

# New Regime Slabs (simplified)
NEW_SLABS = [
    (300000, 0.00),
    (600000, 0.05),
    (900000, 0.10),
    (1200000, 0.15),
    (1500000, 0.20),
    (float("inf"), 0.30)
]


# =========================
# SIDEBAR INPUTS
# =========================
st.sidebar.header("📊 Income Details")

income = st.sidebar.number_input("Annual Income (₹)", 0, 10000000, 1000000, step=50000)

st.sidebar.subheader("🧾 Deductions")

sec80c = st.sidebar.number_input("Section 80C", 0, 150000, 100000)
sec80d = st.sidebar.number_input("Section 80D", 0, 100000, 25000)
hra = st.sidebar.number_input("HRA Exemption", 0, 500000, 50000)

deductions = sec80c + sec80d + hra
taxable_income = max(0, income - deductions)


# =========================
# CALCULATIONS
# =========================
old_tax, old_df = compute_tax(taxable_income, OLD_SLABS)
new_tax, new_df = compute_tax(taxable_income, NEW_SLABS)

recommended = "Old Regime" if old_tax < new_tax else "New Regime"


# =========================
# LAYOUT
# =========================
col1, col2 = st.columns(2)


# -------------------------
# OLD REGIME
# -------------------------
with col1:
    st.subheader("🏛️ Old Regime")

    st.metric("Taxable Income", f"₹{taxable_income:,.0f}")
    st.metric("Tax Payable", f"₹{old_tax:,.0f}")

    fig_old = go.Figure(go.Bar(
        y=old_df["Slab"],
        x=old_df["Tax"],
        orientation="h",
        marker_color="royalblue"
    ))

    fig_old.update_layout(title="Old Regime Tax Breakdown")
    st.plotly_chart(fig_old, use_container_width=True)

    st.dataframe(old_df, use_container_width=True)


# -------------------------
# NEW REGIME
# -------------------------
with col2:
    st.subheader("🆕 New Regime")

    st.metric("Taxable Income", f"₹{taxable_income:,.0f}")
    st.metric("Tax Payable", f"₹{new_tax:,.0f}")

    fig_new = go.Figure(go.Bar(
        y=new_df["Slab"],
        x=new_df["Tax"],
        orientation="h",
        marker_color="green"
    ))

    fig_new.update_layout(title="New Regime Tax Breakdown")
    st.plotly_chart(fig_new, use_container_width=True)

    st.dataframe(new_df, use_container_width=True)


# =========================
# COMPARISON CHART
# =========================
st.markdown("---")
st.subheader("📊 Tax Comparison Dashboard")

compare = pd.DataFrame({
    "Regime": ["Old", "New"],
    "Tax": [old_tax, new_tax]
})

fig = go.Figure(go.Bar(
    x=compare["Regime"],
    y=compare["Tax"],
    marker_color=["blue", "green"]
))

fig.update_layout(title="Old vs New Regime Tax Comparison")
st.plotly_chart(fig, use_container_width=True)

st.success(f"Recommended Option: {recommended}")


# =========================
# REPORT DOWNLOAD
# =========================
st.markdown("---")
st.subheader("📥 Download Tax Report")

report_text = f"""
INCOME TAX REPORT
Date: {datetime.now()}

Income: {income}
Deductions: {deductions}
Taxable Income: {taxable_income}

Old Regime Tax: {old_tax}
New Regime Tax: {new_tax}
Recommended: {recommended}
"""

st.download_button(
    "Download TXT Report",
    report_text,
    file_name="income_tax_report.txt"
)

csv_data = pd.DataFrame([{
    "Income": income,
    "Deductions": deductions,
    "Taxable Income": taxable_income,
    "Old Tax": old_tax,
    "New Tax": new_tax,
    "Recommended": recommended
}])

st.download_button(
    "Download CSV Report",
    csv_data.to_csv(index=False),
    file_name="income_tax_report.csv"
)


# =========================
# LEAD GENERATION FORM
# =========================
st.sidebar.markdown("---")
st.sidebar.subheader("📩 Tax Saving Consultation")

with st.sidebar.form("lead_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")

    submit = st.form_submit_button("Submit")

    if submit:
        st.session_state["lead"] = {
            "name": name,
            "email": email,
            "time": str(datetime.now())
        }
        st.success("Thanks! Our tax expert will contact you soon.")


# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("Built with Streamlit | Income Tax Act 1961 (Simplified Educational Model)")