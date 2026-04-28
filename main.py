import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from io import BytesIO

# Page config
st.set_page_config(
    page_title="SmartInvoice AI 💰",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FIXED CSS - Better colors & visibility
st.markdown("""
<style>
    .main-header {font-size: 3.5rem; color: #1e293b; text-align: center; margin-bottom: 2rem; font-weight: bold;}
    
    /* Fixed Metric Cards - White text on colored background */
    .metric-card {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        padding: 1.5rem; 
        border-radius: 15px; 
        color: white !important;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-card .stMetric > label {
        color: white !important; 
        font-size: 1rem !important;
        font-weight: bold;
    }
    
    .metric-card .stMetric > div > div {
        color: white !important; 
        font-size: 2.2rem !important;
        font-weight: bold;
    }
    
    /* Revenue card */
    .revenue-card {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        padding: 1.5rem; 
        border-radius: 15px; 
        color: white !important;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Overdue card - Red */
    .overdue-card {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        padding: 1.5rem; 
        border-radius: 15px; 
        color: white !important;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Sidebar improvements */
    .sidebar .sidebar-content {background-color: #f8fafc;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">💰 SmartInvoice AI</h1>', unsafe_allow_html=True)
st.markdown("─" * 80)

# Sidebar
st.sidebar.header("🎛️ Controls")
date_range = st.sidebar.date_input(
    "📅 Date Range",
    value=(datetime.now().date() - timedelta(days=30), datetime.now().date())
)

status_filter = st.sidebar.multiselect(
    "🔍 Filter Status",
    options=['Paid', 'Pending', 'Overdue', 'Draft'],
    default=['Paid', 'Pending', 'Overdue', 'Draft']
)

# Load data
@st.cache_data
def load_data():
    np.random.seed(42)
    n = 1000
    dates = pd.date_range('2024-01-01', periods=n, freq='D')
    
    data = {
        'invoice_id': [f'INV-{i:06d}' for i in range(1, n+1)],
        'date': np.random.choice(dates, n),
        'customer': np.random.choice(['Acme Corp', 'Tech Ltd', 'Global Inc', 'Future Tech', 'Innovate LLC'], n),
        'amount': np.random.lognormal(8, 1, n).round(2),
        'status': np.random.choice(['Paid', 'Pending', 'Overdue', 'Draft'], n, p=[0.6, 0.25, 0.1, 0.05]),
        'category': np.random.choice(['Services', 'Products', 'Consulting', 'Subscription'], n)
    }
    df = pd.DataFrame(data)
    df['amount'] = df['amount'].clip(50, 25000)
    df['due_date'] = df['date'] + pd.Timedelta(days=30)
    df['days_overdue'] = np.maximum(0, (pd.Timestamp.now() - df['due_date']).dt.days)
    return df.sort_values('date', ascending=False)

df = load_data()
df_filtered = df[
    (df['date'] >= pd.Timestamp(date_range[0])) & 
    (df['date'] <= pd.Timestamp(date_range[1])) &
    (df['status'].isin(status_filter))
].copy()

# FIXED Metrics - Now clearly visible!
col1, col2, col3, col4 = st.columns(4, gap="large")

# Total Invoices
with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    total = len(df_filtered)
    st.metric("📊 Total Invoices", f"{total:,}")
    st.markdown('</div>', unsafe_allow_html=True)

# Revenue
with col2:
    st.markdown('<div class="revenue-card">', unsafe_allow_html=True)
    revenue = df_filtered['amount'].sum()
    st.metric("💵 Total Revenue", f"₹{revenue:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

# Paid
with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    paid = len(df_filtered[df_filtered['status']=='Paid'])
    pct = paid/total*100 if total > 0 else 0
    st.metric("✅ Paid", f"{paid:,}", f"{pct:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)

# Overdue
with col4:
    st.markdown('<div class="overdue-card">', unsafe_allow_html=True)
    overdue = len(df_filtered[df_filtered['status']=='Overdue'])
    st.metric("⚠️ Overdue", overdue, delta=f"{overdue}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("─" * 80)

# Charts
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📊 Revenue by Status")
    status_rev = df_filtered.groupby('status')['amount'].sum().reset_index()
    fig1 = px.pie(status_rev, values='amount', names='status', hole=0.4)
    fig1.update_traces(textposition='inside', textinfo='percent+label')
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("📈 Revenue Trend")
    df_filtered['month'] = df_filtered['date'].dt.to_period('M')
    monthly = df_filtered.groupby('month')['amount'].sum().reset_index()
    monthly['month'] = monthly['month'].astype(str)
    fig2 = px.line(monthly, x='month', y='amount', markers=True, 
                   title="Monthly Revenue")
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

# Tables
st.subheader("📋 Invoice Details")
tab1, tab2, tab3 = st.tabs(["👀 All Invoices", "⚠️ Overdue", "⏳ Pending"])

with tab1:
    st.dataframe(
        df_filtered[['invoice_id', 'date', 'customer', 'amount', 'status']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "amount": st.column_config.NumberColumn("Amount", format="₹%.2f")
        }
    )

with tab2:
    overdue_df = df_filtered[df_filtered['status']=='Overdue'].sort_values('days_overdue', ascending=False)
    if not overdue_df.empty:
        st.dataframe(overdue_df[['invoice_id', 'customer', 'amount', 'days_overdue']], 
                    use_container_width=True)
    else:
        st.success("🎉 No overdue invoices!")

with tab3:
    pending_df = df_filtered[df_filtered['status']=='Pending']
    if not pending_df.empty:
        st.dataframe(pending_df[['invoice_id', 'customer', 'amount', 'due_date']], 
                    use_container_width=True)
    else:
        st.success("🎉 No pending invoices!")

# Export
with st.expander("💾 Download Data"):
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        "📥 Download CSV",
        csv,
        f"smartinvoices_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        "text/csv",
        use_container_width=True
    )

# Footer
st.markdown("─" * 80)
st.markdown("### 🤖 *SmartInvoice AI - Professional Invoice Dashboard | Made with ❤️ in Streamlit*")
