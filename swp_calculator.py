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
PASSCODE = "3753"  # രണ്ടിനും ഒരേ പാസ്‌വേഡ് തന്നെ ഉപയോഗിക്കുന്നു
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
    """Calculate effective monthly rate from annual rate"""
    return (1 + annual_rate/100) ** (1/12) - 1

def calculate_inflation_adjusted_swp(principal, monthly_withdrawal, years, inflation_rate, annual_return_rate):
    """Calculate inflation-adjusted SWP with effective interest calculation"""
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
            if current_balance <= 0:
                break
                
            current_balance = current_balance * (1 + monthly_rate)
            withdrawal = min(current_monthly_withdrawal, current_balance)
            current_balance -= withdrawal
            yearly_withdrawal_total += withdrawal
            
            if current_balance <= 0:
                break
        
        total_withdrawn += yearly_withdrawal_total
        
        results.append({
            'Year': year,
            'Monthly_Withdrawal': round(current_monthly_withdrawal, 0),
            'Yearly_Withdrawal': round(yearly_withdrawal_total, 0),
            'Year_End_Balance': round(max(current_balance, 0), 0)
        })
        
        if current_balance <= 0:
            break
    
    return results, total_withdrawn, max(current_balance, 0)

def create_excel_report(data, summary, user_name):
    """Create CLEAN, FUNCTIONAL Excel with PERFECT visibility"""
    import xlsxwriter
    
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        title_format = workbook.add_format({
            'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#1F4E78', 'font_color': 'white', 'border': 1
        })
        
        subtitle_format = workbook.add_format({
            'font_size': 8, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#E7F3FF', 'font_color': '#1F4E78', 'border': 1
        })
        
        section_format = workbook.add_format({
            'bold': True, 'bg_color': '#2E86AB', 'font_color': 'white',
            'align': 'center', 'valign': 'vcenter', 'font_size': 11, 'border': 1
        })
        
        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#4472C4', 'font_color': 'white',
            'align': 'center', 'valign': 'vcenter', 'font_size': 10, 'border': 1
        })
        
        label_format = workbook.add_format({
            'bold': True, 'bg_color': '#F2F2F2', 'border': 1,
            'align': 'center', 'valign': 'vcenter', 'font_size': 10
        })
        
        money_format = workbook.add_format({
            'num_format': '₹#,##0', 'border': 1, 'align': 'center',
            'valign': 'vcenter', 'font_size': 10
        })
        
        percent_format = workbook.add_format({
            'num_format': '0.00"%"', 'border': 1, 'align': 'center',
            'valign': 'vcenter', 'font_size': 10
        })
        
        data_format = workbook.add_format({
            'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10
        })
        
        worksheet = workbook.add_worksheet('SWP Report')
        worksheet.set_column('A:D', 25)
        
        worksheet.merge_range('A1:D1', 'INFLATION-ADJUSTED SWP CALCULATOR REPORT', title_format)
        subtitle = f"Developed by: {DEVELOPER_NAME}  |  Report for: {user_name}"
        worksheet.merge_range('A2:D2', subtitle, subtitle_format)
        worksheet.merge_range('A3:D3', f'Generated on: {datetime.now().strftime("%d-%B-%Y")}', title_format)
        
        worksheet.merge_range('A4:C4', 'INPUT PARAMETERS', section_format)
        worksheet.write('A5', 'Parameter', header_format)
        worksheet.write('B5', 'Value', header_format)
        worksheet.write('C5', 'Description', header_format)
        
        inputs = [
            ['Starting Corpus', summary['investment'], 'Initial lump sum deposited'],
            ['Initial Monthly Withdrawal', summary['monthly_withdrawal'], 'Monthly withdrawal for first year'],
            ['Investment Duration', f"{summary['years']} years", 'Total SWP period in years'],
            ['Expected Inflation Rate', summary['inflation'], 'Annual inflation rate (%)'],
            ['Expected Return Rate', summary['return_rate'], 'Annual ROI on investment (%)']
        ]
        
        for i, (label, value, desc) in enumerate(inputs, start=5):
            worksheet.write(i, 0, label, label_format)
            if 'Rate' in label:
                worksheet.write(i, 1, value, percent_format)
            else:
                worksheet.write(i, 1, value, money_format)
            worksheet.write(i, 2, desc, data_format)
        
        worksheet.merge_range('A11:C11', 'CALCULATION RESULTS', section_format)
        worksheet.write('A12', 'Metric', header_format)
        worksheet.write('B12', 'Amount', header_format)
        worksheet.write('C12', 'Notes', header_format)
        
        results_summary = [
            ['Starting Corpus', summary['investment'], 'Your initial capital'],
            ['Total Withdrawn Amount', summary['total_withdrawn'], 'Sum of all withdrawals'],
            ['Final Balance Remaining', summary['final_balance'], 'Value at end of period']
        ]
        
        for i, (label, value, note) in enumerate(results_summary, start=12):
            worksheet.write(i, 0, label, label_format)
            worksheet.write(i, 1, value, money_format)
            worksheet.write(i, 2, note, data_format)
        
        worksheet.merge_range('A17:D17', 'YEAR-WISE WITHDRAWAL SCHEDULE', section_format)
        worksheet.write('A18', 'Year', header_format)
        worksheet.write('B18', 'Monthly Withdrawal', header_format)
        worksheet.write('C18', 'Yearly Withdrawal', header_format)
        worksheet.write('D18', 'Year-End Balance', header_format)
        
        if data:
            for idx, item in enumerate(data):
                row = 18 + idx
                worksheet.write(row, 0, item['Year'], data_format)
                worksheet.write(row, 1, item['Monthly_Withdrawal'], money_format)
                worksheet.write(row, 2, item['Yearly_Withdrawal'], money_format)
                worksheet.write(row, 3, item['Year_End_Balance'], money_format)
            
    output.seek(0)
    return output

def main():
    # Streamlit Analytics ട്രാക്കിംഗ് തുടങ്ങുന്നു
    with streamlit_analytics.track():
        st.set_page_config(
            page_title="Inflation-Adjusted SWP Calculator",
            page_icon="💰",
            layout="centered"
        )
        
        st.markdown("""
        <style>
        .main-header { color: #1E90FF; font-size: 2.5rem; font-weight: 800; text-align: center; }
        .developer-name { color: #32CD32; font-size: 1.1rem; font-weight: 600; text-align: center; }
        .motivation-quote { font-style: italic; color: #FF6347; font-size: 1.1rem; padding: 12px; border-left: 5px solid #FFD700; background: rgba(255,215,0,0.05); text-align: center; border-radius: 8px; }
        .result-card { background: #1A2233; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #374151; }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f'<div class="main-header">Inflation-Adjusted SWP Calculator</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="developer-name">Developed by {DEVELOPER_NAME}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="motivation-quote">{np.random.choice(MOTIVATIONAL_QUOTES)}</div>', unsafe_allow_html=True)
        
        # --- DEVELOPER AREA IN SIDEBAR ---
        with st.sidebar:
            st.title("🛠️ Settings")
            st.write("Only for Admin")
            dev_password = st.text_input("Enter Passcode", type="password")
            
            if dev_password == PASSCODE:
                st.success("Access Granted!")
                
                # Option 1: View User Logs
                if st.checkbox("Show User Logs"):
                    if st.session_state.user_data_log:
                        df_log = pd.DataFrame(st.session_state.user_data_log)
                        st.dataframe(df_log)
                        towrite = io.BytesIO()
                        df_log.to_excel(towrite, index=False, engine='xlsxwriter')
                        towrite.seek(0)
                        st.download_button("📥 Download Logs", towrite, "Logs.xlsx", use_container_width=True)
                    else:
                        st.info("No logs yet.")
                
                # Option 2: View App Analytics (Traffic, Clicks etc)
                if st.checkbox("Show App Analytics"):
                    st.write("---")
                    st.subheader("📊 Traffic Analytics")
                    # ഇന്റർഫേസിൽ തന്നെ അനലിറ്റിക്സ് സെക്ഷൻ കാണിക്കുന്നു
                    streamlit_analytics.display_sections()
            
            elif dev_password != "":
                st.error("Wrong Passcode")
        
        # --- INPUTS ---
        col_name, col_spacer = st.columns([2, 1])
        with col_name:
            user_name = st.text_input("👤 Enter Your Name *", placeholder="Your name", autocomplete="off")
        
        col1, col2 = st.columns(2)
        with col1:
            investment_amount = st.number_input("💵 Starting Corpus (₹) *", min_value=1000, value=1000000)
            monthly_withdrawal = st.number_input("💸 Initial Monthly Withdrawal (₹) *", min_value=100, value=50000)
        with col2:
            time_period = st.number_input("⏱️ Time Period (Years) *", min_value=1, max_value=50, value=20)
            inflation_rate = st.number_input("📈 Expected Inflation Rate (% pa) *", value=6.0)
            annual_return = st.number_input("📊 Expected Return Rate (% pa) *", value=12.0)
        
        st.divider()
        calc_btn = st.button("🧮 Calculate SWP Plan", type="primary", use_container_width=True)
        st.link_button("💬 Contact Developer on WhatsApp", WHATSAPP_LINK, use_container_width=True)
        st.divider()

        if calc_btn:
            if not user_name.strip():
                st.error("❌ Enter your name!")
                st.stop()
            
            st.session_state.user_data_log.append({
                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'User': user_name, 'Principal': investment_amount, 'Withdrawal': monthly_withdrawal
            })
                
            results, total_withdrawn, final_balance = calculate_inflation_adjusted_swp(
                investment_amount, monthly_withdrawal, time_period, inflation_rate, annual_return
            )
            
            st.markdown("### 📊 Summary Results")
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="result-card"><h4>Starting Corpus</h4><h2>₹{int(investment_amount):,}</h2></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="result-card"><h4>Withdrawn</h4><h2>₹{int(total_withdrawn):,}</h2></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="result-card"><h4>Balance</h4><h2>₹{int(final_balance):,}</h2></div>', unsafe_allow_html=True)
            
            st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
            
            summary = {
                'investment': int(investment_amount), 'monthly_withdrawal': int(monthly_withdrawal),
                'years': time_period, 'inflation': inflation_rate, 'return_rate': annual_return,
                'total_withdrawn': int(total_withdrawn), 'final_balance': int(final_balance)
            }
            
            excel_file = create_excel_report(results, summary, user_name)
            st.download_button("📥 Download Excel Report", excel_file, f"SWP_{user_name}.xlsx", use_container_width=True)

if __name__ == "__main__":
    main()
