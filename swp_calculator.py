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

# --- DATA STORAGE ---
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
    """100% Professional Green Theme Design with Auto-Fitting Cells"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # --- PROFESSIONAL GREEN THEME FORMATS ---
        title_fmt = workbook.add_format({
            'bold': True, 'font_size': 18, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#1B5E20', 'font_color': 'white', 'border': 2
        })
        
        info_fmt = workbook.add_format({
            'font_size': 10, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#E8F5E9', 'border': 1, 'italic': True
        })
        
        section_fmt = workbook.add_format({
            'bold': True, 'font_size': 12, 'align': 'left', 'valign': 'vcenter',
            'bg_color': '#2E7D32', 'font_color': 'white', 'border': 1, 'indent': 1
        })
        
        header_fmt = workbook.add_format({
            'bold': True, 'font_size': 11, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#43A047', 'font_color': 'white', 'border': 1
        })
        
        label_fmt = workbook.add_format({
            'bold': True, 'font_size': 10, 'align': 'left', 'valign': 'vcenter',
            'bg_color': '#F1F8E9', 'border': 1, 'indent': 1
        })
        
        data_center_fmt = workbook.add_format({
            'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'border': 1
        })
        
        money_fmt = workbook.add_format({
            'num_format': '₹#,##0', 'font_size': 10, 'align': 'right', 'valign': 'vcenter', 'border': 1
        })
        
        pct_fmt = workbook.add_format({
            'num_format': '0.00"%"', 'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'border': 1
        })

        worksheet = workbook.add_worksheet('SWP Detailed Report')
        
        # COLUMN WIDTHS (Adjusted for perfect fit)
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 22)
        worksheet.set_column('C:C', 22)
        worksheet.set_column('D:D', 45) # Extra wide for descriptions

        # HEADER SECTION
        worksheet.merge_range('A1:D1', 'INFLATION-ADJUSTED SWP DETAILED REPORT', title_fmt)
        worksheet.set_row(0, 30)
        worksheet.merge_range('A2:D2', f"Client Name: {user_name}  |  Report Prepared by: SHAMSUDEEN ABDULLA  |  Date: {datetime.now().strftime('%d-%m-%Y')}", info_fmt)

        # 1. INPUT PARAMETERS
        worksheet.merge_range('A4:D4', '1. INPUT PARAMETERS', section_fmt)
        worksheet.write('A5', 'Parameter', header_fmt)
        worksheet.write('B5', 'Value', header_fmt)
        worksheet.write('C5', 'Status', header_fmt)
        worksheet.write('D5', 'Strategic Description', header_fmt)
        
        inputs = [
            ['Starting Corpus', summary['investment'], 'Initial Deposit', 'The total lump sum amount invested at the beginning.'],
            ['Initial Monthly Withdrawal', summary['monthly_withdrawal'], 'Base Payout', 'The target monthly income required for the first year.'],
            ['Investment Duration', summary['years'], 'Total Years', 'The full time horizon for the systematic withdrawal plan.'],
            ['Expected Inflation Rate', summary['inflation'], 'Annual Increase', 'Projected annual percentage to adjust income for cost of living.'],
            ['Expected Return Rate', summary['return_rate'], 'Annual ROI', 'The estimated annual growth rate of your remaining investment.']
        ]
        
        row = 5
        for l, v, u, d in inputs:
            worksheet.write(row, 0, l, label_fmt)
            if isinstance(v, (int, float)) and l != 'Investment Duration':
                if 'Rate' in l: worksheet.write(row, 1, v, pct_fmt)
                else: worksheet.write(row, 1, v, money_fmt)
            else:
                worksheet.write(row, 1, v, data_center_fmt)
            worksheet.write(row, 2, u, data_center_fmt)
            worksheet.write(row, 3, d, data_center_fmt)
            row += 1

        # 2. CALCULATION SUMMARY
        worksheet.merge_range(row+1, 0, row+1, 3, '2. CALCULATION SUMMARY', section_fmt)
        summary_row = row + 2
        worksheet.write(summary_row, 0, 'Total Estimated Withdrawals', label_fmt)
        worksheet.write(summary_row, 1, summary['total_withdrawn'], money_fmt)
        worksheet.merge_range(summary_row, 2, summary_row, 3, 'Total amount received over the investment period.', data_center_fmt)
        
        worksheet.write(summary_row+1, 0, 'Final Portfolio Balance', label_fmt)
        worksheet.write(summary_row+1, 1, summary['final_balance'], money_fmt)
        worksheet.merge_range(summary_row+1, 2, summary_row+1, 3, 'The remaining capital at the end of the specified years.', data_center_fmt)

        # 3. YEAR-WISE SCHEDULE
        schedule_start = summary_row + 4
        worksheet.merge_range(schedule_start-1, 0, schedule_start-1, 3, '3. YEAR-WISE WITHDRAWAL SCHEDULE', section_fmt)
        
        headers = ['Year', 'Monthly Payout (Adjusted)', 'Annual Total Income', 'Year-End Capital Balance']
        for col, h in enumerate(headers):
            worksheet.write(schedule_start, col, h, header_fmt)

        row = schedule_start + 1
        for item in data:
            worksheet.write(row, 0, f"Year {item['Year']}", label_fmt)
            worksheet.write(row, 1, item['Monthly_Withdrawal'], money_fmt)
            worksheet.write(row, 2, item['Yearly_Withdrawal'], money_fmt)
            worksheet.write(row, 3, item['Year_End_Balance'], money_fmt)
            row += 1

    output.seek(0)
    return output

def main():
    with streamlit_analytics.track():
        st.set_page_config(page_title="SWP Calculator", page_icon="💰", layout="centered")
        
        st.markdown(f'<h1 style="text-align:center;color:#1B5E20;">Inflation-Adjusted SWP Calculator</h1>', unsafe_allow_html=True)
        st.markdown(f'<p style="text-align:center;color:#2E7D32;font-weight:bold;">Developed by {DEVELOPER_NAME}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="text-align:center;font-style:italic;color:#388E3C;">{np.random.choice(MOTIVATIONAL_QUOTES)}</p>', unsafe_allow_html=True)

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
