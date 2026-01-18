import streamlit as st
import pandas as pd
import random
import time
from datetime import date
import io

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Retirement Planner Pro - Final Edition", layout="wide")

# --- CUSTOM CSS (NO CHANGES) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1116 !important; color: #E5E7EB !important; }
    .main { background-color: #0E1116 !important; }
    .input-card {
        background-color: #1A2233 !important; padding: 25px; border-radius: 10px;
        border: 1px solid #374151; color: #E5E7EB !important;
    }
    .result-text { color: #22C55E !important; font-family: 'Courier New', monospace; font-weight: bold; }
    .quote-text { color: #22C55E !important; font-style: italic; font-weight: bold; text-align: center; display: block; margin-top: 20px; }
    .stButton>button {
        background-color: #22C55E !important; color: white !important; width: 100%;
        border: none; font-weight: bold; height: 3.5em; border-radius: 8px;
    }
    .stButton>button:hover { background-color: #16a34a !important; }
    label, p, span, h1, h2, h3 { color: #E5E7EB !important; }
    [data-testid="stMetricLabel"] { color: #9CA3AF !important; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; }
    .dev-container { text-align: center; margin-bottom: 25px; }
    .dev-btn { display: inline-block; padding: 8px 16px; margin: 5px; border-radius: 5px; text-decoration: none !important; font-weight: bold; color: white !important; font-size: 13px; }
    .wa-btn { background-color: #25D366; }
    .fb-btn { background-color: #1877F2; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTIVATION QUOTES ---
all_quotes = [
    "“Investment is not a one-time decision, it is a lifetime habit.”",
    "“Wealth is not created overnight; it grows with consistency.”",
    "“The day you start a SIP, your future begins.”",
    "“SIP to build wealth, SWP to live life.”",
    "“Start today, for the sake of tomorrow.”"
]

# --- CORE LOGIC (ENHANCED FOR ACCURACY) ---
def calculate_retirement_final(c_age, r_age, l_exp, c_exp, inf_rate, c_sav, e_corp, pre_ret_r, post_ret_r, legacy_amount_real):
    months_to_retire = (r_age - c_age) * 12
    retirement_months = (l_exp - r_age) * 12
    
    monthly_inf = (1 + inf_rate/100) ** (1/12) - 1
    monthly_pre_ret = (1 + pre_ret_r/100) ** (1/12) - 1
    monthly_post_ret = (1 + post_ret_r/100) ** (1/12) - 1
    
    expense_at_retirement = c_exp * (1 + monthly_inf) ** months_to_retire
    
    # Corpus Required Calculation
    legacy_nominal = legacy_amount_real * (1 + monthly_inf) ** ((l_exp - c_age) * 12)
    if abs(monthly_post_ret - monthly_inf) > 0.0001:
        pv_expenses = expense_at_retirement * (1 - ((1 + monthly_inf) / (1 + monthly_post_ret)) ** retirement_months) / (monthly_post_ret - monthly_inf)
    else:
        pv_expenses = expense_at_retirement * retirement_months
    
    pv_legacy = legacy_nominal / (1 + monthly_post_ret) ** retirement_months if legacy_nominal > 0 else 0
    corp_req = pv_expenses + pv_legacy
    
    # Current Savings Projection
    future_existing = e_corp * (1 + monthly_pre_ret) ** months_to_retire
    if monthly_pre_ret > 0:
        future_sip = c_sav * (((1 + monthly_pre_ret) ** months_to_retire - 1) / monthly_pre_ret) * (1 + monthly_pre_ret)
    else:
        future_sip = c_sav * months_to_retire
        
    total_savings = future_existing + future_sip
    shortfall = max(0, corp_req - total_savings)
    
    # Required to fill shortfall
    req_sip = 0
    req_lumpsum = 0
    if shortfall > 0 and months_to_retire > 0:
        req_sip = (shortfall * monthly_pre_ret) / (((1 + monthly_pre_ret) ** months_to_retire - 1) * (1 + monthly_pre_ret))
        req_lumpsum = shortfall / ((1 + monthly_pre_ret) ** months_to_retire)
    
    # Detailed Annual Breakdown
    annual_withdrawals = []
    current_balance = corp_req
    total_withdrawn_sum = 0
    
    for year in range(retirement_months // 12):
        monthly_expense_this_year = expense_at_retirement * (1 + monthly_inf) ** (year * 12)
        yearly_withdrawal = round(monthly_expense_this_year * 12)
        total_withdrawn_sum += yearly_withdrawal
        
        for month in range(12):
            current_balance = (current_balance * (1 + monthly_post_ret)) - monthly_expense_this_year
        
        annual_withdrawals.append({
            "Age": r_age + year,
            "Year": year + 1,
            "Annual Withdrawal": yearly_withdrawal,
            "Monthly Amount": round(monthly_expense_this_year),
            "Remaining Corpus": round(max(current_balance, 0))
        })
    
    return {
        "future_exp": round(expense_at_retirement),
        "corp_req": round(corp_req),
        "total_sav": round(total_savings),
        "shortfall": round(shortfall),
        "req_sip": round(req_sip),
        "req_lumpsum": round(req_lumpsum),
        "legacy_real": round(legacy_amount_real),
        "legacy_nominal": round(legacy_nominal),
        "annual_withdrawals": annual_withdrawals,
        "total_withdrawn_sum": total_withdrawn_sum
    }

# --- MAIN APP (USER INTERFACE) ---
st.markdown("<h1 style='text-align: center;'>RETIREMENT PLANNER PRO</h1>", unsafe_allow_html=True)

st.markdown(f"""
    <div class="dev-container">
        <p style='margin-bottom: 5px; font-size: 0.9em; color: #6B7280;'>Developed by Shamsudeen abdulla</p>
        <a href="https://wa.me/qr/IOBUQDQMM2X3D1" target="_blank" class="dev-btn wa-btn">WhatsApp Developer</a>
        <a href="https://www.facebook.com/shamsudeen.abdulla.2025/" target="_blank" class="dev-btn fb-btn">Facebook Profile</a>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="input-card">', unsafe_allow_html=True)
user_name = st.text_input("Name of the User", value="Valued User")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 👤 Personal Information")
    current_age = st.number_input("Current Age", value=30, min_value=0, step=1)
    retire_age = st.number_input("Retirement Age", value=60, min_value=current_age+1, step=1)
    life_exp = st.number_input("Expected Life Expectancy", value=85, min_value=retire_age+1, step=1)
    current_expense = st.number_input("Current Monthly Expense (₹)", value=30000, step=500)

with col2:
    st.markdown("### 💰 Investment Details")
    inf_rate = st.number_input("Inflation Rate (%)", value=6.0, step=0.1)
    existing_corp = st.number_input("Existing Savings (₹)", value=0, step=5000)
    current_sip = st.number_input("Current Monthly SIP (₹)", value=0, step=100)
    pre_ret_rate = st.number_input("Pre-retirement Returns (%)", value=12.0, step=0.1)
    post_ret_rate = st.number_input("Post-retirement Returns (%)", value=8.0, step=0.1)
    legacy_amount = st.number_input("Legacy (Today's Real Value) (₹)", value=0, step=100000)
st.markdown('</div>', unsafe_allow_html=True)

if st.button("Calculate"):
    res = calculate_retirement_final(current_age, retire_age, life_exp, current_expense, inf_rate, current_sip, existing_corp, pre_ret_rate, post_ret_rate, legacy_amount)
    st.session_state.res = res
    st.session_state.user_name = user_name
    
    st.divider()
    r1, r2 = st.columns(2)
    with r1:
        st.metric("Monthly Expense at Retirement", f"₹ {res['future_exp']:,}")
        st.metric("Total Fund Required (Corpus)", f"₹ {res['corp_req']:,}")
    with r2:
        st.metric("Projected Total Savings", f"₹ {res['total_sav']:,}")
        st.metric("Shortfall", f"₹ {res['shortfall']:,}", delta_color="inverse")

    st.write("### Retirement Cashflow Analysis")
    st.dataframe(pd.DataFrame(res["annual_withdrawals"]), use_container_width=True, hide_index=True)

# --- EXCEL DOWNLOAD (PROFESSIONAL DESIGN) ---
if 'res' in st.session_state:
    res = st.session_state.res
    u_name = st.session_state.user_name
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet('Retirement Plan')
        
        # Styles
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#16A34A', 'font_color': 'white', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        normal_fmt = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
        curr_fmt = workbook.add_format({'num_format': '₹ #,##0', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        title_fmt = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
        disclaimer_fmt = workbook.add_format({'italic': True, 'font_color': 'red', 'text_wrap': True, 'border': 1, 'align': 'center', 'valign': 'vcenter'})

        # Disclaimer & Title
        worksheet.merge_range('A1:E4', "DISCLAIMER: This report is a mathematical projection based on inputs. Market results may vary. Consult a financial advisor.", disclaimer_fmt)
        worksheet.merge_range('A6:E6', f'RETIREMENT FINANCIAL REPORT: {u_name.upper()}', title_fmt)

        # Summary Section
        worksheet.merge_range('A8:B8', 'INPUT DETAILS', header_fmt)
        input_list = [["Current Age", current_age], ["Retirement Age", retire_age], ["Life Expectancy", life_exp], ["Monthly Expense", current_expense], ["Inflation Rate (%)", inf_rate]]
        for i, (l, v) in enumerate(input_list):
            worksheet.write(i+9, 0, l, normal_fmt); worksheet.write(i+9, 1, v, normal_fmt)

        worksheet.merge_range('D8:E8', 'PLAN RESULTS', header_fmt)
        res_list = [["Corpus Needed", res['corp_req']], ["Total Withdrawal Sum", res['total_withdrawn_sum']], ["Shortfall", res['shortfall']], ["Extra SIP Needed", res['req_sip']], ["Legacy (Nominal)", res['legacy_nominal']]]
        for i, (l, v) in enumerate(res_list):
            worksheet.write(i+9, 3, l, normal_fmt); worksheet.write(i+9, 4, v, curr_fmt)

        # Main Table
        worksheet.merge_range('A16:E16', 'YEARLY WITHDRAWAL & WEALTH TRACKER', header_fmt)
        headers = ["Age", "Year", "Annual Withdrawal", "Monthly Amount", "Remaining Balance"]
        for c, h in enumerate(headers): worksheet.write(17, c, h, header_fmt)
        
        for r, row in enumerate(res['annual_withdrawals']):
            worksheet.write(r+18, 0, row["Age"], normal_fmt)
            worksheet.write(r+18, 1, row["Year"], normal_fmt)
            worksheet.write(r+18, 2, row["Annual Withdrawal"], curr_fmt)
            worksheet.write(r+18, 3, row["Monthly Amount"], curr_fmt)
            worksheet.write(r+18, 4, row["Remaining Corpus"], curr_fmt)

        # Final Formatting
        worksheet.set_column('A:E', 25) # എല്ലാ കോളങ്ങൾക്കും ഒരേ വീതി

    st.download_button("📥 Download Professional Excel Report", buffer.getvalue(), f"Report_{u_name}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
