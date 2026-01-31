import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sales Dashboard", layout="wide")

# --- Custom styling for better margins, padding and typography ---
st.markdown(
        """
        <style>
            .block-container{padding:1.8rem 2.2rem;}
            .sidebar .sidebar-content{padding:1rem 1rem 2rem 1rem;}
            h1, h2, h3 {font-family: 'Segoe UI', Roboto, sans-serif;}
            .footer {color: #6c757d; font-size:12px}
            .big-metric {font-size:20px}
            .stbackground {background-color: #f8f9fa;}
        </style>
        """,
        unsafe_allow_html=True,
)

# -------------------- DATA LOADING --------------------
@st.cache_data
def load_data():
    data = {
        "Date": pd.date_range(start="2020-01-01", periods=100),
        "Product": np.random.choice(["Product A", "Product B", "Product C"], 100),
        "Region": np.random.choice(["North", "South", "East", "West"], 100),
        "Sales": np.random.randint(100, 1000, 100),
        "Profit": np.random.randint(10, 200, 100)
    }
    return pd.DataFrame(data)


df = load_data()
df["Date"] = pd.to_datetime(df["Date"])  # ensure datetime dtype

# -------------------- TITLE --------------------

st.title("📊 Business Sales Analytics Dashboard")

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.header("Filters")

start_date = st.sidebar.date_input("Start Date", df["Date"].min())
end_date = st.sidebar.date_input("End Date", df["Date"].max())

regions = st.sidebar.multiselect(
    "Select Regions",
    df["Region"].unique(),
    default=df["Region"].unique()
)

products = st.sidebar.multiselect(
    "Select Products",
    df["Product"].unique(),
    default=df["Product"].unique()
)

# --- Display options in an expander for a cleaner sidebar ---
with st.sidebar.expander("Display Options", expanded=True):
    chart_type = st.selectbox("Chart type", ["Line", "Area"], index=0)
    freq = st.selectbox("Aggregation", ["Daily", "Weekly", "Monthly"], index=0)
    show_cumulative = st.checkbox("Show cumulative series", value=False)
    show_table = st.checkbox("Show data table", value=True)

# -------------------- FILTER DATA --------------------

filtered_df = df[
    (df["Date"] >= pd.to_datetime(start_date)) &
    (df["Date"] <= pd.to_datetime(end_date)) &
    (df["Region"].isin(regions)) &
    (df["Product"].isin(products))
]

# -------------------- KPI METRICS --------------------
col1, col2, col3 = st.columns([1.2, 1.2, 1])
col1.metric("Total Sales", f"{filtered_df['Sales'].sum():,}")
col2.metric("Total Profit", f"{filtered_df['Profit'].sum():,}")
col3.metric("Avg Sale", f"{filtered_df['Sales'].mean():.2f}")

# -------------------- SALES TREND --------------------
st.subheader("📈 Sales Trend")

# Aggregate according to frequency
tmp = filtered_df.set_index("Date")
if freq == "Daily":
    sales_trend = tmp["Sales"].resample("D").sum()
    profit_trend = tmp["Profit"].resample("D").sum()
elif freq == "Weekly":
    sales_trend = tmp["Sales"].resample("W").sum()
    profit_trend = tmp["Profit"].resample("W").sum()
else:
    sales_trend = tmp["Sales"].resample("M").sum()
    profit_trend = tmp["Profit"].resample("M").sum()

if show_cumulative:
    sales_plot = sales_trend.cumsum()
else:
    sales_plot = sales_trend

fig, ax = plt.subplots(figsize=(8, 3))
if chart_type == "Area":
    ax.fill_between(sales_plot.index, sales_plot.values, color="#4c78a8", alpha=0.3)
    ax.plot(sales_plot.index, sales_plot.values, color="#4c78a8")
else:
    ax.plot(sales_plot.index, sales_plot.values, marker="o", linewidth=2, color="#4c78a8")

ax.set_xlabel("Date")
ax.set_ylabel("Sales")
ax.set_title("Sales Over Time")
fig.tight_layout()
st.pyplot(fig)

# -------------------- TOP PRODUCTS --------------------
st.subheader("🏆 Top Products")

top_products = (
    filtered_df.groupby("Product")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

col_a, col_b = st.columns([1, 1])
with col_a:
    st.bar_chart(top_products)
with col_b:
    st.table(top_products.to_frame("Sales").style.format("{:,}"))

# -------------------- REGION-WISE REVENUE --------------------
st.subheader("🌍 Region-wise Revenue")

region_revenue = filtered_df.groupby("Region")["Sales"].sum()
st.bar_chart(region_revenue)

# -------------------- PROFIT ANALYSIS --------------------
st.subheader("💰 Profit Trend")

# If profit_trend already computed from aggregation step above, use it; otherwise compute
try:
    _ = profit_trend
except NameError:
    profit_trend = filtered_df.set_index("Date")["Profit"].resample("D").sum()

fig2, ax2 = plt.subplots(figsize=(8, 3))
ax2.plot(profit_trend.index, profit_trend.values, color="#ff7f0e", linewidth=2)
ax2.set_xlabel("Date")
ax2.set_ylabel("Profit")
ax2.set_title("Profit Over Time")
fig2.tight_layout()
st.pyplot(fig2)

# -------------------- DATA TABLE --------------------
st.subheader("📄 Filtered Data")
if show_table:
    st.dataframe(filtered_df)

st.download_button(
    label="Download Data as CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='filtered_sales_data.csv',
    mime='text/csv',
)
# -------------------- FOOTER --------------------
st.markdown("---")
st.markdown("Developed by Deepak Saini | [GitHub](https://github.com/Deepaksaini005)")
st.markdown("<div class='footer'> © 2024 All rights reserved.</div>", unsafe_allow_html=True )
