import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# DEVELOPER CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
DEVELOPER_NAME = "SHAMSUDEEN ABDULLA"
# നിങ്ങളുടെ യഥാർത്ഥ ഫോൺ നമ്പർ ഇവിടെ നൽകുക (e.g., "919876543210")
WHATSAPP_LINK = "https://wa.me/91XXXXXXXXXX" 

# ഹോസ്പിറ്റൽ ഇൻഡെക്സ് കോഡ് - 100% മാറ്റമില്ലാതെ നിലനിർത്തുന്നു
HOSPITAL_INDEX_CODE = "HIC-2026-STABLE" 
# ─────────────────────────────────────────────────────────────────────────────

if 'user_data_log' not in st.session_state:
    st.session_state.user_data_log = []

MOTIVATIONAL_QUOTES = [
    "Invest in your future today, for tomorrow's prosperity begins with today's wise decisions.",
    "Financial freedom is not a dream; it's a goal achievable through planning and perseverance.",
    "Every rupee invested wisely today is a seed for tomorrow's financial garden."
]

def calculate_effective_monthly_rate(annual_rate: float) -> float:
    """Calculate effective monthly rate with validation"""
    if not 0 <= annual_rate <= 100:
        return 0.0
    return (1 + annual_rate/100) ** (1/12) - 1

def calculate_inflation_adjusted_swp(principal, monthly_withdrawal, years, inflation_rate, annual_return_rate):
    monthly_rate = calculate_effective_monthly_rate(annual_return_rate)
    results = []
    total_withdrawn = 0
    current_balance = principal
    current_monthly_withdrawal = monthly_withdrawal
    
    for year in range(1, years + 1):
        if year > 1:
            current_monthly_withdrawal *= (1 + max(0, inflation_rate)/100)
        
        yearly_withdrawal_total = 0
        for month in range(1, 13):
            if current_balance <= 0:
                current_balance = 0
                break
            
            withdrawal = min(current_monthly_withdrawal, current_balance)
            current_balance -= withdrawal
            current_balance *= (1 + monthly_rate)
            yearly_withdrawal_total += withdrawal
        
        total_withdrawn += yearly_withdrawal_total
        results.append({
            'Year': year,
            'Monthly_Withdrawal': round(current_monthly_withdrawal, 0),
            'Yearly_Withdrawal': round(yearly_withdrawal_total, 0),
            'Year_End_Balance': round(max(current_balance, 0), 0)
        })
        if current_balance <= 0: break
    
    return results, total_withdrawn, max(current_balance, 0)

# Excel Report Generator (മാറ്റമില്ലാതെ തുടരുന്നു)
def create_excel_report(data, summary, user_name):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame(data)
        df.to_excel(writer, index=False, sheet_name='SWP Report')
    output.seek(0)
    return output

def main():
    st.set_page_config(page_title="SWP Calculator Pro", page_icon="💰")
    
    st.markdown(f"<h1 style='text-align: center; color: #1E90FF;'>SWP Calculator</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>Developed by <b>{DEVELOPER_NAME}</b></p>", unsafe_allow_html=True)

    # Sidebar Security
    with st.sidebar:
        st.subheader("🛠️ Admin Access")
        dev_password = st.text_input("Enter Passcode", type="password")
        # st.secrets ഉപയോഗിക്കുന്നത് ശുപാർശ ചെയ്യുന്നു. തൽക്കാലം സുരക്ഷയ്ക്കായി ഇവിടെ മാറ്റം വരുത്തി.
        admin_pass = st.secrets.get("DEV_PASS", "3753") 
        
        if dev_password == admin_pass:
            if st.session_state.user_data_log:
                st.write("User Logs:")
                st.table(pd.DataFrame(st.session_state.user_data_log))
            else:
                st.info("No logs found.")

    user_name = st.text_input("👤 Name", placeholder="Enter your name")
    
    col1, col2 = st.columns(2)
    with col1:
        investment = st.number_input("💵 Corpus (₹)", min_value=1000, value=1000000)
        monthly_out = st.number_input("💸 Monthly Withdrawal (₹)", min_value=100, value=10000)
    with col2:
        years = st.number_input("⏱️ Years", min_value=1, max_value=50, value=20)
        inf_rate = st.number_input("📈 Inflation (%)", min_value=0.0, max_value=20.0, value=6.0)
        ret_rate = st.number_input("📊 Return Rate (%)", min_value=0.0, max_value=30.0, value=12.0)

    if st.button("Calculate Plan", type="primary", use_container_width=True):
        if not user_name:
            st.error("Please enter a name.")
            return

        results, total_w, final_b = calculate_inflation_adjusted_swp(investment, monthly_out, years, inf_rate, ret_rate)
        
        # Summary Display
        st.divider()
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("Total Withdrawn", f"₹{int(total_w):,}")
        res_col2.metric("Final Balance", f"₹{int(final_b):,}")
        res_col3.metric("Duration", f"{len(results)} Years")
        
        st.dataframe(pd.DataFrame(results), use_container_width=True)
        
        # Log entry
        st.session_state.user_data_log.append({
            'Time': datetime.now().strftime("%H:%M:%S"),
            'User': user_name, 'Principal': investment
        })

    st.link_button("💬 WhatsApp Support", WHATSAPP_LINK, use_container_width=True)

if __name__ == "__main__":
    main()
