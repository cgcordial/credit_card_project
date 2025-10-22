import pandas as pd
import plotly.express as px
import streamlit as st

# Load input data
df = pd.read_csv("/Users/giocordial/PycharmProjects/credit_card_project/output/combined_data.csv")

# Convert Transaction Date to datetime
df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])

# Add a Month column (format e.g. Sep 2025)
df['Month'] = df['Transaction Date'].dt.strftime('%b %Y')

# Summarize all amounts based on months
monthly_summary = df.groupby(['Month', 'Spend Category'])['Amount'].sum().reset_index()

print(monthly_summary.head())

st.title("Monthly Spend Report Viewer")

# Month Selector (chronological sort)
months = sorted(
    df['Month'].unique(),
    key=lambda x: pd.to_datetime(x, format='%b %Y')
)
selected_month = st.selectbox("Select a month:", months)

# Filter Data
filtered = df[df['Month'] == selected_month]

# Summary Chart
st.subheader(f"Spending Breakdown for {selected_month}")
fig = px.bar(
    filtered,
    x = "Spend Category",
    y = "Amount",
    color = "Spend Category",
    title = f"Spend by Category - {selected_month}",
)
st.plotly_chart(fig)

# Detailed Table
st.subheader("Transaction Details")
st.dataframe(filtered[['Transaction Date', 'Description', 'Spend Category', 'Amount']])