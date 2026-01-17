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
    import xlsxwriter
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        title_format = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'bg_color': '#1F4E78', 'font_color': 'white', 'border': 1})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#4472C4', 'font_color': 'white', 'align': 'center', 'border': 1})
        money_format = workbook.add_format({'num_format': '₹#,##0', 'border': 1, 'align': 'center'})
        data_format = workbook.add_format({'border': 1, 'align': 'center'})
        
        worksheet = workbook.add_worksheet('SWP Report')
        worksheet.set_column('A:D', 25)
        worksheet.merge_range('A1:D1', 'SWP CALCULATOR REPORT', title_format)
        
        # Results Table
        worksheet.write('A18', 'Year', header_format)
        worksheet.write('B18', 'Monthly Withdrawal', header_format)
        worksheet.write('C18', 'Yearly Withdrawal', header_format)
        worksheet.write('D18', 'Year-End Balance', header_format)
        
        for idx, item in enumerate(data):
            row = 18 + idx
            worksheet.write(row, 0, item['Year'], data_format)
            worksheet.write(row, 1, item['Monthly_Withdrawal'], money_format)
            worksheet.write(row, 2, item['Yearly_Withdrawal'], money_format)
            worksheet.write(row, 3, item['Year_End_Balance'], money_format)
    output.seek(0)
    return output

def main():
    # വായനക്കാർക്ക് പ്രശ്നമില്ലാതെ ട്രാക്കിംഗ് നടക്കാൻ ഇതാവശ്യമാണ്
    with streamlit_analytics.track():
        st.set_page_config(page_title="SWP Calculator", page_icon="💰", layout="centered")
        
        st.markdown("""
        <style>
        .main-header { color: #1E90FF; font-size: 2.5rem; font-weight: 800; text-align: center; }
        .developer-name { color: #32CD32; font-size: 1.1rem; font-weight: 600; text-align: center; }
        .result-card { background: #1A2233; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #374151; }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f'<div class="main-header">Inflation-Adjusted SWP Calculator</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="developer-name">Developed by {DEVELOPER_NAME}</div>', unsafe_allow_html=True)
        
        # --- SIDEBAR ADMIN AREA ---
        with st.sidebar:
            st.title("🛠️ Admin Settings")
            dev_password = st.text_input("Enter Passcode", type="password")
            if dev_password == PASSCODE:
                st.success("Access Granted!")
                show_logs = st.checkbox("Show User Logs")
                if show_logs:
                    if st.session_state.user_data_log:
                        st.table(pd.DataFrame(st.session_state.user_data_log))
                    else:
                        st.info("No logs found.")
                
                show_analytics = st.checkbox("Show App Analytics")
                if show_analytics:
                    # AttributeError ഒഴിവാക്കാൻ സുരക്ഷിതമായ രീതി
                    try:
                        streamlit_analytics.display_sections()
                    except:
                        st.info("Analytics dashboard is loading. If not visible, use '?analytics=on' in URL.")

        # --- APP UI ---
        user_name = st.text_input("👤 Your Name", placeholder="Enter name")
        col1, col2 = st.columns(2)
        with col1:
            investment = st.number_input("Starting Corpus (₹)", min_value=1000, value=1000000)
            withdrawal = st.number_input("Monthly Withdrawal (₹)", min_value=100, value=50000)
        with col2:
            years = st.number_input("Years", min_value=1, value=20)
            inflation = st.number_input("Inflation (%)", value=6.0)
            returns = st.number_input("Return Rate (%)", value=12.0)
        
        if st.button("Calculate SWP", type="primary", use_container_width=True):
            if not user_name:
                st.error("Please enter your name")
            else:
                st.session_state.user_data_log.append({
                    'Time': datetime.now().strftime("%H:%M:%S"),
                    'User': user_name, 'Amt': investment
                })
                res, total_w, final_b = calculate_inflation_adjusted_swp(investment, withdrawal, years, inflation, returns)
                
                st.markdown("### Summary")
                c1, c2, c3 = st.columns(3)
                c1.metric("Principal", f"₹{investment:,}")
                c2.metric("Total Withdrawn", f"₹{int(total_w):,}")
                c3.metric("Final Balance", f"₹{int(final_b):,}")
                
                st.dataframe(pd.DataFrame(res), use_container_width=True)
                
                sum_data = {'investment': investment, 'monthly_withdrawal': withdrawal, 'years': years, 'inflation': inflation, 'return_rate': returns, 'total_withdrawn': total_w, 'final_balance': final_b}
                excel = create_excel_report(res, sum_data, user_name)
                st.download_button("📥 Download Report", excel, f"SWP_{user_name}.xlsx")

        st.divider()
        st.link_button("💬 WhatsApp Developer", WHATSAPP_LINK, use_container_width=True)

if __name__ == "__main__":
    main()
