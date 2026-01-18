import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# DEVELOPER CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
DEVELOPER_NAME = "SHAMSUDEEN ABDULLA"
WHATSAPP_LINK = "https://wa.me/qr/IOBUQDQMM2X3D1"
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
    """Calculate effective monthly rate from annual rate (CAGR basis)"""
    return (1 + annual_rate/100) ** (1/12) - 1

def calculate_inflation_adjusted_swp(principal, monthly_withdrawal, years, inflation_rate, annual_return_rate):
    """Calculate inflation-adjusted SWP with corrected monthly logic"""
    monthly_rate = calculate_effective_monthly_rate(annual_return_rate)
    
    results = []
    total_withdrawn = 0
    current_balance = principal
    current_monthly_withdrawal = monthly_withdrawal
    
    for year in range(1, years + 1):
        if year > 1:
            # ഓരോ വർഷവും ഇൻഫ്ലേഷൻ അനുസരിച്ച് പിൻവലിക്കുന്ന തുക വർദ്ധിപ്പിക്കുന്നു
            current_monthly_withdrawal = current_monthly_withdrawal * (1 + inflation_rate/100)
        
        yearly_withdrawal_total = 0
        
        for month in range(1, 13):
            if current_balance <= 0:
                current_balance = 0
                break
            
            # ലോജിക് തിരുത്തിയത്: മാസത്തിന്റെ തുടക്കത്തിൽ തുക പിൻവലിക്കുന്നു
            withdrawal = min(current_monthly_withdrawal, current_balance)
            current_balance -= withdrawal
            
            # ബാക്കി നിൽക്കുന്ന തുകയ്ക്ക് ആ മാസത്തെ പലിശ (Return) കണക്കാക്കുന്നു
            current_balance = current_balance * (1 + monthly_rate)
            
            yearly_withdrawal_total += withdrawal
        
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
    """Create Excel with formatting"""
    import xlsxwriter
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # ഫോർമാറ്റുകൾ
        title_format = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'bg_color': '#1F4E78', 'font_color': 'white', 'border': 1})
        subtitle_format = workbook.add_format({'font_size': 9, 'align': 'center', 'bg_color': '#E7F3FF', 'font_color': '#1F4E78', 'border': 1})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#4472C4', 'font_color': 'white', 'align': 'center', 'border': 1})
        money_format = workbook.add_format({'num_format': '₹#,##0', 'border': 1, 'align': 'center'})
        data_format = workbook.add_format({'border': 1, 'align': 'center'})
        
        worksheet = workbook.add_worksheet('SWP Report')
        worksheet.set_column('A:D', 25)
        
        worksheet.merge_range('A1:D1', 'INFLATION-ADJUSTED SWP REPORT', title_format)
        worksheet.merge_range('A2:D2', f"User: {user_name} | Date: {datetime.now().strftime('%d-%m-%Y')}", subtitle_format)
        
        # ഇൻപുട്ട് സമ്മറി
        worksheet.write('A4', 'Starting Corpus', header_format)
        worksheet.write('B4', summary['investment'], money_format)
        worksheet.write('C4', 'Total Withdrawn', header_format)
        worksheet.write('D4', summary['total_withdrawn'], money_format)
        
        # ടേബിൾ ഹെഡർ
        headers = ['Year', 'Monthly Withdrawal', 'Yearly Withdrawal', 'Year-End Balance']
        for col_num, header in enumerate(headers):
            worksheet.write(6, col_num, header, header_format)
            
        # ഡാറ്റ ചേർക്കുന്നു
        for row_num, item in enumerate(data, start=7):
            worksheet.write(row_num, 0, item['Year'], data_format)
            worksheet.write(row_num, 1, item['Monthly_Withdrawal'], money_format)
            worksheet.write(row_num, 2, item['Yearly_Withdrawal'], money_format)
            worksheet.write(row_num, 3, item['Year_End_Balance'], money_format)
            
    output.seek(0)
    return output

def main():
    st.set_page_config(page_title="SWP Calculator", page_icon="💰", layout="centered")
    
    st.markdown("""
    <style>
    .main-header { color: #1E90FF; font-size: 2.2rem; font-weight: 800; text-align: center; margin-bottom: 0px; }
    .developer-name { color: #32CD32; font-size: 1rem; font-weight: 600; text-align: center; margin-bottom: 20px; }
    .motivation-quote { font-style: italic; color: #666; font-size: 0.9rem; text-align: center; padding: 10px; border-radius: 5px; background: #f0f2f6; margin-bottom: 20px; }
    .result-card { background: #f8f9fb; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #ddd; color: #333; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header">Inflation-Adjusted SWP Calculator</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="developer-name">Developed by {DEVELOPER_NAME}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="motivation-quote">"{np.random.choice(MOTIVATIONAL_QUOTES)}"</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.subheader("🛠️ Developer Area")
        dev_password = st.text_input("Enter Passcode", type="password")
        if dev_password == "3753":
            if st.session_state.user_data_log:
                df_log = pd.DataFrame(st.session_state.user_data_log)
                st.dataframe(df_log)
            else:
                st.info("No logs yet.")

    # User Inputs
    user_name = st.text_input("👤 Enter Your Name *", placeholder="Your name")
    
    col1, col2 = st.columns(2)
    with col1:
        investment_amount = st.number_input("💵 Starting Corpus (₹)", min_value=1000, value=1000000, step=10000)
        monthly_withdrawal = st.number_input("💸 Initial Monthly Withdrawal (₹)", min_value=100, value=10000, step=500)
    with col2:
        time_period = st.number_input("⏱️ Time Period (Years)", min_value=1, max_value=50, value=20)
        inflation_rate = st.number_input("📈 Inflation Rate (% pa)", value=6.0, step=0.1)
        annual_return = st.number_input("📊 Expected Return Rate (% pa)", value=12.0, step=0.1)
    
    st.divider()
    calc_btn = st.button("🧮 Calculate SWP Plan", type="primary", use_container_width=True)
    st.link_button("💬 Contact Developer on WhatsApp", WHATSAPP_LINK, use_container_width=True)

    if calc_btn:
        if not user_name.strip():
            st.error("❌ Please enter your name to proceed.")
            st.stop()
            
        # ലോജിങ്
        st.session_state.user_data_log.append({
            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'User': user_name, 'Principal': investment_amount, 'Withdrawal': monthly_withdrawal
        })
            
        results, total_withdrawn, final_balance = calculate_inflation_adjusted_swp(
            investment_amount, monthly_withdrawal, time_period, inflation_rate, annual_return
        )
        
        # Results Display
        st.markdown("### 📊 Summary Results")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="result-card"><p>Starting Corpus</p><h3>₹{int(investment_amount):,}</h3></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="result-card"><p>Total Withdrawn</p><h3>₹{int(total_withdrawn):,}</h3></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="result-card"><p>Final Balance</p><h3>₹{int(final_balance):,}</h3></div>', unsafe_allow_html=True)
        
        st.write("#### Yearly Breakdown")
        df_results = pd.DataFrame(results)
        st.dataframe(df_results, use_container_width=True, hide_index=True)
        
        # Excel Download
        summary = {
            'investment': int(investment_amount), 'monthly_withdrawal': int(monthly_withdrawal),
            'years': time_period, 'inflation': inflation_rate, 'return_rate': annual_return,
            'total_withdrawn': int(total_withdrawn), 'final_balance': int(final_balance)
        }
        excel_file = create_excel_report(results, summary, user_name)
        st.download_button("📥 Download Excel Report", excel_file, f"SWP_Report_{user_name}.xlsx", use_container_width=True)

if __name__ == "__main__":
    main()
