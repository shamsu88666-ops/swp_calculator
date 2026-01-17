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
    """abcd.xlsx മാതൃകയിലുള്ള 100% കൃത്യമായ ഡിസൈൻ"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # ഫോർമാറ്റുകൾ (നിങ്ങൾ നൽകിയ മാതൃക പ്രകാരം)
        title_fmt = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#1F4E78', 'font_color': 'white', 'border': 1})
        subtitle_fmt = workbook.add_format({'font_size': 9, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#E7F3FF', 'font_color': '#1F4E78', 'border': 1})
        section_fmt = workbook.add_format({'bold': True, 'bg_color': '#2E86AB', 'font_color': 'white', 'align': 'center', 'valign': 'vcenter', 'font_size': 11, 'border': 1})
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#4472C4', 'font_color': 'white', 'align': 'center', 'valign': 'vcenter', 'font_size': 10, 'border': 1})
        label_fmt = workbook.add_format({'bold': True, 'bg_color': '#F2F2F2', 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        money_fmt = workbook.add_format({'num_format': '₹#,##0', 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        pct_fmt = workbook.add_format({'num_format': '0.00"%"', 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        data_fmt = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})

        worksheet = workbook.add_worksheet('SWP Report')
        worksheet.set_column('A:A', 35)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 35)
        worksheet.set_column('D:D', 30)

        # Header
        worksheet.merge_range('A1:D1', 'INFLATION-ADJUSTED SWP CALCULATOR REPORT', title_fmt)
        subtitle = f"Developed by: {DEVELOPER_NAME}  |  Report for: {user_name}"
        worksheet.merge_range('A2:D2', subtitle, subtitle_fmt)
        worksheet.merge_range('A3:D3', f'Generated on: {datetime.now().strftime("%d-%B-%Y")}', title_fmt)

        # Inputs Section
        worksheet.merge_range('A4:C4', 'INPUT PARAMETERS', section_fmt)
        worksheet.write('A5', 'Parameter', header_fmt); worksheet.write('B5', 'Value', header_fmt); worksheet.write('C5', 'Description', header_fmt)
        
        inputs = [
            ['Starting Corpus', summary['investment'], 'Initial lump sum deposited'],
            ['Initial Monthly Withdrawal', summary['monthly_withdrawal'], 'Monthly withdrawal for first year'],
            ['Investment Duration', f"{summary['years']} years", 'Total SWP period in years'],
            ['Expected Inflation Rate', summary['inflation'], 'Annual inflation rate (%)'],
            ['Expected Return Rate', summary['return_rate'], 'Annual ROI on investment (%)']
        ]
        for i, (l, v, d) in enumerate(inputs, start=5):
            worksheet.write(i, 0, l, label_fmt)
            if 'Rate' in l: worksheet.write(i, 1, float(v), pct_fmt)
            elif 'Corpus' in l or 'Withdrawal' in l: worksheet.write(i, 1, float(v), money_fmt)
            else: worksheet.write(i, 1, v, data_fmt)
            worksheet.write(i, 2, d, data_fmt)

        # Calculation Results
        worksheet.merge_range('A11:C11', 'CALCULATION RESULTS', section_fmt)
        worksheet.write('A12', 'Metric', header_fmt); worksheet.write('B12', 'Amount', header_fmt); worksheet.write('C12', 'Notes', header_fmt)
        res_sum = [
            ['Total Withdrawn Amount', summary['total_withdrawn'], 'Sum of all monthly withdrawals'],
            ['Final Balance Remaining', summary['final_balance'], 'Value at the end of period']
        ]
        for i, (l, v, n) in enumerate(res_sum, start=12):
            worksheet.write(i, 0, l, label_fmt); worksheet.write(i, 1, float(v), money_fmt); worksheet.write(i, 2, n, data_fmt)

        # Year-wise Schedule
        worksheet.merge_range('A17:D17', 'YEAR-WISE WITHDRAWAL SCHEDULE', section_fmt)
        headers = ['Year', 'Monthly Withdrawal', 'Yearly Withdrawal', 'Year-End Balance']
        for col, h in enumerate(headers): worksheet.write(17, col, h, header_fmt)

        for idx, item in enumerate(data):
            row = 18 + idx
            worksheet.write(row, 0, item['Year'], data_fmt)
            worksheet.write(row, 1, float(item['Monthly_Withdrawal']), money_fmt)
            worksheet.write(row, 2, float(item['Yearly_Withdrawal']), money_fmt)
            worksheet.write(row, 3, float(item['Year_End_Balance']), money_fmt)

    output.seek(0)
    return output

def main():
    with streamlit_analytics.track():
        st.set_page_config(page_title="SWP Calculator", page_icon="💰", layout="centered")
        
        st.markdown(f'<h1 style="text-align:center;color:#1E90FF;">Inflation-Adjusted SWP Calculator</h1>', unsafe_allow_html=True)
        st.markdown(f'<p style="text-align:center;color:#32CD32;font-weight:bold;">Developed by {DEVELOPER_NAME}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="text-align:center;font-style:italic;color:#FF6347;">{np.random.choice(MOTIVATIONAL_QUOTES)}</p>', unsafe_allow_html=True)

        # --- SIDEBAR ---
        with st.sidebar:
            st.title("🛠️ Admin Area")
            pwd = st.text_input("Enter Passcode", type="password")
            if pwd == PASSCODE:
                st.success("Access Granted")
                if st.checkbox("Show Logs"):
                    if st.session_state.user_data_log:
                        st.table(pd.DataFrame(st.session_state.user_data_log))
                    else: st.info("No logs.")
                if st.checkbox("Show Analytics"):
                    try: streamlit_analytics.display_sections()
                    except: st.info("Loading Analytics...")

        # --- UI INPUTS ---
        user_name = st.text_input("👤 Enter Your Name *", placeholder="Your name")
        c1, c2 = st.columns(2)
        with c1:
            inv = st.number_input("💵 Starting Corpus (₹)", min_value=1000, value=1000000)
            withdr = st.number_input("💸 Initial Monthly Withdrawal (₹)", min_value=100, value=50000)
        with c2:
            yrs = st.number_input("⏱️ Time Period (Years)", min_value=1, value=20)
            inf = st.number_input("📈 Expected Inflation Rate (%)", value=6.0)
            ret = st.number_input("📊 Expected Return Rate (%)", value=12.0)

        st.divider()
        if st.button("🧮 Calculate SWP Plan", type="primary", use_container_width=True):
            if not user_name:
                st.error("❌ Please enter your name to generate report")
                st.stop()
            
            st.session_state.user_data_log.append({'Time': datetime.now().strftime("%H:%M"), 'User': user_name, 'Principal': inv})
            
            res, total_w, final_b = calculate_inflation_adjusted_swp(inv, withdr, yrs, inf, ret)
            
            st.markdown("### 📊 summary Results")
            ca, cb, cc = st.columns(3)
            ca.metric("Starting Corpus", f"₹{inv:,}")
            cb.metric("Total Withdrawn", f"₹{int(total_w):,}")
            cc.metric("Final Balance", f"₹{int(final_b):,}")
            
            st.dataframe(pd.DataFrame(res), use_container_width=True, hide_index=True)
            
            summary = {'investment': inv, 'monthly_withdrawal': withdr, 'years': yrs, 'inflation': inf, 'return_rate': ret, 'total_withdrawn': total_w, 'final_balance': final_b}
            excel = create_excel_report(res, summary, user_name)
            st.download_button("📥 Download Full Excel Report", excel, f"SWP_Report_{user_name}.xlsx", use_container_width=True)

        st.divider()
        st.link_button("💬 Contact Developer on WhatsApp", WHATSAPP_LINK, use_container_width=True)

if __name__ == "__main__":
    main()
