import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import streamlit_analytics

# ─────────────────────────────────────────────────────────────────────────────
# DEVELOPER CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
DEVELOPER_NAME = "SHAMSUDEEN ABDULLA"
WHATSAPP_LINK = "https://wa.me/qr/IOBUQDQMM2X3D1"
PASSCODE = "3753" 
# ─────────────────────────────────────────────────────────────────────────────

# --- ഡാറ്റ ശേഖരിക്കാനുള്ള സെഷൻ സ്റ്റേറ്റ് ---
if 'user_data_log' not in st.session_state:
    st.session_state.user_data_log = []

MOTIVATIONAL_QUOTES = [
    "Invest in your future today, for tomorrow's prosperity begins with today's wise decisions.",
    "Financial freedom is not a dream; it's a goal achievable through planning and perseverance.",
    "Every rupee invested wisely today is a seed for tomorrow's financial garden.",
    "Inflation may rise, but so can your wealth—with the right strategy and patience."
]

def calculate_effective_monthly_rate(annual_rate):
    return (1 + annual_rate/100) ** (1/12) - 1

def calculate_inflation_adjusted_swp(principal, monthly_withdrawal, years, inflation_rate, annual_return_rate):
    monthly_rate = calculate_effective_monthly_rate(annual_return_rate)
    results = []
    total_withdrawn = 0
    current_balance = principal
    current_monthly_withdrawal = monthly_withdrawal
    
    for year in range(1, years + 1):
        if year > 1:
            current_monthly_withdrawal = current_monthly_withdrawal * (1 + inflation_rate/100)
        yearly_withdrawal_total = 0
        for month in range(1, 13):
            if current_balance <= 0: break
            current_balance = current_balance * (1 + monthly_rate)
            withdrawal = min(current_monthly_withdrawal, current_balance)
            current_balance -= withdrawal
            yearly_withdrawal_total += withdrawal
            if current_balance <= 0: break
        
        total_withdrawn += yearly_withdrawal_total
        results.append({
            'Year': year,
            'Monthly_Withdrawal': round(current_monthly_withdrawal, 0),
            'Yearly_Withdrawal': round(yearly_withdrawal_total, 0),
            'Year_End_Balance': round(max(current_balance, 0), 0)
        })
        if current_balance <= 0: break
    return results, total_withdrawn, max(current_balance, 0)

def create_excel_report(data, summary, user_name):
    """എക്സൽ റിപ്പോർട്ട് 100% കൃത്യതയോടെ നിർമ്മിക്കുന്നു"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # ഫോർമാറ്റുകൾ
        title_fmt = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'bg_color': '#1F4E78', 'font_color': 'white', 'border': 1})
        sec_fmt = workbook.add_format({'bold': True, 'bg_color': '#2E86AB', 'font_color': 'white', 'align': 'center', 'border': 1})
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#4472C4', 'font_color': 'white', 'align': 'center', 'border': 1})
        money_fmt = workbook.add_format({'num_format': '₹#,##0', 'border': 1, 'align': 'center'})
        pct_fmt = workbook.add_format({'num_format': '0.0"%"', 'border': 1, 'align': 'center'})
        label_fmt = workbook.add_format({'bold': True, 'bg_color': '#F2F2F2', 'border': 1})
        data_fmt = workbook.add_format({'border': 1, 'align': 'center'})

        worksheet = workbook.add_worksheet('SWP Report')
        worksheet.set_column('A:D', 30)

        # Header
        worksheet.merge_range('A1:D1', 'INFLATION-ADJUSTED SWP CALCULATOR REPORT', title_fmt)
        worksheet.merge_range('A2:D2', f"Developed by: {DEVELOPER_NAME} | Report for: {user_name}", data_fmt)

        # Input Parameters Section
        worksheet.merge_range('A4:C4', 'INPUT PARAMETERS', sec_fmt)
        worksheet.write('A5', 'Parameter', header_fmt); worksheet.write('B5', 'Value', header_fmt); worksheet.write('C5', 'Description', header_fmt)
        
        inputs = [
            ['Starting Corpus', summary['investment'], 'Initial lump sum'],
            ['Initial Withdrawal', summary['monthly_withdrawal'], 'Monthly first year'],
            ['Duration', f"{summary['years']} years", 'Total period'],
            ['Inflation Rate', summary['inflation'], 'Annual %'],
            ['Return Rate', summary['return_rate'], 'Annual ROI %']
        ]
        for i, (l, v, d) in enumerate(inputs, start=5):
            worksheet.write(i, 0, l, label_fmt)
            if 'Rate' in l: worksheet.write(i, 1, v, pct_fmt)
            elif 'Corpus' in l or 'Withdrawal' in l: worksheet.write(i, 1, v, money_fmt)
            else: worksheet.write(i, 1, v, data_fmt)
            worksheet.write(i, 2, d, data_fmt)

        # Summary Results
        worksheet.merge_range('A12:C12', 'SUMMARY RESULTS', sec_fmt)
        res_sum = [
            ['Total Withdrawn', summary['total_withdrawn']],
            ['Final Balance', summary['final_balance']]
        ]
        for i, (l, v) in enumerate(res_sum, start=12):
            worksheet.write(i, 0, l, label_fmt)
            worksheet.write(i, 1, v, money_fmt)

        # Year-wise Schedule
        worksheet.merge_range('A16:D16', 'YEAR-WISE WITHDRAWAL SCHEDULE', sec_fmt)
        headers = ['Year', 'Monthly Withdrawal', 'Yearly Withdrawal', 'Year-End Balance']
        for col, h in enumerate(headers): worksheet.write(16, col, h, header_fmt)

        for idx, item in enumerate(data):
            row = 17 + idx
            worksheet.write(row, 0, item['Year'], data_fmt)
            worksheet.write(row, 1, item['Monthly_Withdrawal'], money_fmt)
            worksheet.write(row, 2, item['Yearly_Withdrawal'], money_fmt)
            worksheet.write(row, 3, item['Year_End_Balance'], money_fmt)

    output.seek(0)
    return output

def main():
    with streamlit_analytics.track():
        st.set_page_config(page_title="SWP Calculator", page_icon="💰", layout="centered")
        
        st.markdown(f'<h1 style="text-align:center;color:#1E90FF;">Inflation-Adjusted SWP Calculator</h1>', unsafe_allow_html=True)
        st.markdown(f'<p style="text-align:center;color:#32CD32;font-weight:bold;">Developed by {DEVELOPER_NAME}</p>', unsafe_allow_html=True)
        st.info(np.random.choice(MOTIVATIONAL_QUOTES))

        # --- SIDEBAR ---
        with st.sidebar:
            st.title("🛠️ Admin Area")
            pwd = st.text_input("Enter Passcode", type="password")
            if pwd == PASSCODE:
                st.success("Access Granted")
                if st.checkbox("Show Logs"):
                    st.write(pd.DataFrame(st.session_state.user_data_log))
                if st.checkbox("Show Analytics"):
                    try: streamlit_analytics.display_sections()
                    except: st.info("Analytics dash is loading...")

        # --- UI ---
        user_name = st.text_input("👤 Name")
        c1, c2 = st.columns(2)
        with c1:
            inv = st.number_input("Corpus (₹)", min_value=1000, value=1000000)
            withdr = st.number_input("Monthly Withdrawal (₹)", min_value=100, value=50000)
        with c2:
            yrs = st.number_input("Years", min_value=1, value=20)
            inf = st.number_input("Inflation %", value=6.0)
            ret = st.number_input("Return %", value=12.0)

        if st.button("Calculate Plan", type="primary", use_container_width=True):
            if not user_name: st.error("Please enter name"); st.stop()
            
            st.session_state.user_data_log.append({'User': user_name, 'Amt': inv, 'Time': datetime.now().strftime("%H:%M")})
            
            res, total_w, final_b = calculate_inflation_adjusted_swp(inv, withdr, yrs, inf, ret)
            
            st.markdown("### 📊 Result Summary")
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Starting", f"₹{inv:,}")
            col_b.metric("Total Withdrawn", f"₹{int(total_w):,}")
            col_c.metric("Final Balance", f"₹{int(final_b):,}")
            
            st.dataframe(pd.DataFrame(res), use_container_width=True, hide_index=True)
            
            summary = {'investment': inv, 'monthly_withdrawal': withdr, 'years': yrs, 'inflation': inf, 'return_rate': ret, 'total_withdrawn': total_w, 'final_balance': final_b}
            excel = create_excel_report(res, summary, user_name)
            st.download_button("📥 Download Full Excel Report", excel, f"SWP_{user_name}.xlsx", use_container_width=True)

        st.divider()
        st.link_button("💬 WhatsApp Developer", WHATSAPP_LINK, use_container_width=True)

if __name__ == "__main__":
    main()
