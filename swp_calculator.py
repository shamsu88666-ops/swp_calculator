import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# DEVELOPER CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
DEVELOPER_NAME = "SHAMSUDEEN ABDULLA"
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
        
        # ─────────────────────────────────────────────────────────────────────
        # ESSENTIAL FORMATS ONLY - MINIMAL & CLEAN
        # ─────────────────────────────────────────────────────────────────────
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#1F4E78',
            'font_color': 'white',
            'border': 1
        })
        
        subtitle_format = workbook.add_format({
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#E7F3FF',
            'font_color': '#1F4E78',
            'border': 1
        })
        
        section_format = workbook.add_format({
            'bold': True,
            'bg_color': '#2E86AB',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 11,
            'border': 1
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 10,
            'border': 1
        })
        
        label_format = workbook.add_format({
            'bold': True,
            'bg_color': '#F2F2F2',
            'border': 1,
            'valign': 'vcenter',
            'font_size': 10
        })
        
        money_format = workbook.add_format({
            'num_format': '₹#,##0',
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'font_size': 10
        })
        
        percent_format = workbook.add_format({
            'num_format': '0.00"%"',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 10
        })
        
        data_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 10
        })
        
        note_format = workbook.add_format({
            'italic': True,
            'font_size': 9,
            'valign': 'vcenter',
            'border': 1
        })
        
        # ─────────────────────────────────────────────────────────────────────
        # SINGLE WORKSHEET - MAXIMUM WIDTH COLUMNS
        # ─────────────────────────────────────────────────────────────────────
        worksheet = workbook.add_worksheet('SWP Report')
        
        # === EXTREMELY WIDE COLUMNS - NO #### EVER ===
        worksheet.set_column('A:A', 35)  # Parameters
        worksheet.set_column('B:B', 30)  # Values
        worksheet.set_column('C:C', 40)  # Descriptions
        worksheet.set_column('D:D', 35)  # Year-End Balance (FIXED WIDTH)
        worksheet.set_column('E:E', 12)  # Year
        worksheet.set_column('F:F', 30)  # Monthly
        worksheet.set_column('G:G', 35)  # Yearly
        worksheet.set_column('H:H', 35)  # Balance
        
        # ─────────────────────────────────────────────────────────────────────
        # TITLE SECTION (Merged to visible data range only)
        # ─────────────────────────────────────────────────────────────────────
        worksheet.merge_range('A1:D1', 'INFLATION-ADJUSTED SWP CALCULATOR REPORT', title_format)
        
        subtitle = f"Developed by: {DEVELOPER_NAME}  |  Report for: {user_name}"
        worksheet.merge_range('A2:D2', subtitle, subtitle_format)
        
        worksheet.merge_range('A3:D3', f'Generated on: {datetime.now().strftime("%d-%B-%Y")}', title_format)
        
        # ─────────────────────────────────────────────────────────────────────
        # INPUT PARAMETERS
        # ─────────────────────────────────────────────────────────────────────
        worksheet.merge_range('A4:C4', 'INPUT PARAMETERS', section_format)
        
        worksheet.write('A5', 'Parameter', header_format)
        worksheet.write('B5', 'Value', header_format)
        worksheet.write('C5', 'Description', header_format)
        
        inputs = [
            ['Investment Amount', summary['investment'], 'Initial lump sum deposited'],
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
        
        # ─────────────────────────────────────────────────────────────────────
        # RESULTS SECTION
        # ─────────────────────────────────────────────────────────────────────
        worksheet.merge_range('A11:C11', 'CALCULATION RESULTS', section_format)
        
        worksheet.write('A12', 'Metric', header_format)
        worksheet.write('B12', 'Amount', header_format)
        worksheet.write('C12', 'Notes', header_format)
        
        results_summary = [
            ['Total Invested Amount', summary['investment'], 'Your initial capital'],
            ['Total Withdrawn Amount', summary['total_withdrawn'], 'Sum of all withdrawals'],
            ['Final Balance Remaining', summary['final_balance'], 'Value at end of period']
        ]
        
        for i, (label, value, note) in enumerate(results_summary, start=12):
            worksheet.write(i, 0, label, label_format)
            worksheet.write(i, 1, value, money_format)
            worksheet.write(i, 2, note, data_format)
        
        # ─────────────────────────────────────────────────────────────────────
        # YEAR-WISE TABLE (RE-ADDED AND FIXED)
        # ─────────────────────────────────────────────────────────────────────
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
        
        if data:
            note_row = 19 + len(data)
            worksheet.merge_range(f'A{note_row}:D{note_row}', 
                'Note: All values are rounded to nearest rupee. Withdrawals are inflation-adjusted annually.', note_format)
    
    output.seek(0)
    return output

def main():
    st.set_page_config(
        page_title="Inflation-Adjusted SWP Calculator",
        page_icon="💰",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    if 'dark_theme' not in st.session_state:
        st.session_state.dark_theme = False
    
    st.markdown("""
    <style>
    .appview-container { margin-top: -2rem !important; }
    .block-container { padding-top: 1rem !important; }
    .main-header {
        color: #1E90FF;
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        margin: 0 !important;
        padding: 10px 0;
    }
    .developer-name {
        color: #32CD32;
        font-size: 1.1rem;
        font-weight: 600;
        text-align: center;
        margin: 0 0 8px 0;
    }
    .motivation-quote {
        font-style: italic;
        color: #FF6347;
        font-size: 1.1rem;
        padding: 12px;
        border-left: 5px solid #FFD700;
        background: linear-gradient(135deg, rgba(255,215,0,0.08) 0%, rgba(255,165,0,0.05) 100%);
        border-radius: 8px;
        margin: 15px 0 25px 0;
        text-align: center;
    }
    .result-card {
        background: #1A2233;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #374151;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div class="main-header">Inflation-Adjusted SWP Calculator</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="developer-name">Developed by {DEVELOPER_NAME}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="motivation-quote">{np.random.choice(MOTIVATIONAL_QUOTES)}</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.title("⚙️ Settings")
        theme_toggle = st.toggle("🌙 Dark Mode", value=st.session_state.dark_theme)
        if theme_toggle != st.session_state.dark_theme:
            st.session_state.dark_theme = theme_toggle
            st.rerun()

        # --- ഡെവലപ്പർ സെക്ഷൻ ---
        st.divider()
        st.subheader("🛠️ Developer Area")
        dev_password = st.text_input("Enter Passcode to view logs", type="password")
        
        if dev_password == "3753":
            st.success("Access Granted!")
            if st.session_state.user_data_log:
                df_log = pd.DataFrame(st.session_state.user_data_log)
                st.write("### User Input Logs")
                st.dataframe(df_log, use_container_width=True)
                
                # എക്സൽ ഡൗൺലോഡ്
                towrite = io.BytesIO()
                df_log.to_excel(towrite, index=False, engine='xlsxwriter')
                towrite.seek(0)
                st.download_button(
                    label="📥 Download All Logs as Excel",
                    data=towrite,
                    file_name="SWP_User_Logs.xlsx",
                    mime="application/vnd.ms-excel",
                    use_container_width=True
                )
            else:
                st.info("No user data recorded in this session.")
        elif dev_password != "":
            st.error("Incorrect Passcode!")
    
    col_name, col_spacer = st.columns([2, 1])
    with col_name:
        # ബ്രൗസർ ഓട്ടോഫിൽ ഒഴിവാക്കാൻ autocomplete="off" ചേർത്തു
        user_name = st.text_input("👤 Enter Your Name *", placeholder="Your name for report", autocomplete="off")
    
    col1, col2 = st.columns(2)
    with col1:
        investment_amount = st.number_input("💵 Investment Amount (₹) *", min_value=1000, value=1000000, step=50000)
        monthly_withdrawal = st.number_input("💸 Initial Monthly Withdrawal (₹) *", min_value=100, value=50000, step=1000)
    with col2:
        time_period = st.number_input("⏱️ Time Period (Years) *", min_value=1, max_value=50, value=20)
        inflation_rate = st.number_input("📈 Expected Inflation Rate (% pa) *", min_value=0.0, value=6.0, step=0.1)
        annual_return = st.number_input("📊 Expected Return Rate (% pa) *", min_value=0.0, value=12.0, step=0.1)
    
    if st.button("🧮 Calculate SWP Plan", type="primary", use_container_width=True):
        if not user_name.strip():
            st.error("❌ Please enter your name!")
            st.stop()
        
        # ഡാറ്റ ലോഗ് ചെയ്യുന്നു
        st.session_state.user_data_log.append({
            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'User Name': user_name,
            'Principal': investment_amount,
            'Initial Withdrawal': monthly_withdrawal,
            'Years': time_period,
            'Inflation': inflation_rate,
            'Return Rate': annual_return
        })
            
        results, total_withdrawn, final_balance = calculate_inflation_adjusted_swp(
            investment_amount, monthly_withdrawal, time_period, inflation_rate, annual_return
        )
        
        st.markdown("### 📊 Summary Results")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="result-card"><h4>Invested</h4><h2>₹{int(investment_amount):,}</h2></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="result-card"><h4>Withdrawn</h4><h2>₹{int(total_withdrawn):,}</h2></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="result-card"><h4>Balance</h4><h2>₹{int(final_balance):,}</h2></div>', unsafe_allow_html=True)
        
        st.markdown("### 📅 Year-wise Withdrawal Schedule")
        df_display = pd.DataFrame(results)
        df_display['Monthly_Withdrawal'] = df_display['Monthly_Withdrawal'].apply(lambda x: f'₹{int(x):,}')
        df_display['Yearly_Withdrawal'] = df_display['Yearly_Withdrawal'].apply(lambda x: f'₹{int(x):,}')
        df_display['Year_End_Balance'] = df_display['Year_End_Balance'].apply(lambda x: f'₹{int(x):,}')
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        summary = {
            'investment': int(investment_amount),
            'monthly_withdrawal': int(monthly_withdrawal),
            'years': time_period,
            'inflation': inflation_rate,
            'return_rate': annual_return,
            'total_withdrawn': int(total_withdrawn),
            'final_balance': int(final_balance)
        }
        
        excel_file = create_excel_report(results, summary, user_name)
        st.download_button(
            label="📥 Download Detailed Excel Report",
            data=excel_file,
            file_name=f"SWP_Report_{user_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

if __name__ == "__main__":
    main()
