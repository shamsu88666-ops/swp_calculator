def calculate_inflation_adjusted_swp(principal, monthly_withdrawal, years, inflation_rate, annual_return_rate, deplete_exactly=True):
    """SWP calculator with option to deplete corpus exactly at end of term"""
    monthly_rate = calculate_effective_monthly_rate(annual_return_rate)
    monthly_inflation_rate = calculate_effective_monthly_rate(inflation_rate)
    
    results = []
    total_withdrawn = 0.0
    current_balance = float(principal)
    current_monthly_withdrawal = float(monthly_withdrawal)
    
    total_months = years * 12
    yearly_withdrawal_total = 0.0
    
    for month in range(1, total_months + 1):
        # മാസം തുടങ്ങുമ്പോൾ ഇൻഫ്ലേഷൻ പ്രയോഗിക്കുക
        if month > 1:
            current_monthly_withdrawal *= (1.0 + monthly_inflation_rate)
        
        # പിൻവലിക്കൽ
        if deplete_exactly and month == total_months:
            withdrawal = current_balance
        else:
            withdrawal = min(current_monthly_withdrawal, current_balance)
        
        # വർഷ ആകെക്കൂടിൽ ചേർക്കുക
        yearly_withdrawal_total += withdrawal
        
        current_balance -= withdrawal
        total_withdrawn += withdrawal
        
        # ROI പ്രയോഗിക്കുക
        if current_balance > 0:
            current_balance *= (1.0 + monthly_rate)
        
        # വർഷം അവസാനം
        if month % 12 == 0:
            results.append({
                'Year': month // 12,
                'Monthly_Withdrawal': round(current_monthly_withdrawal, 2),
                'Yearly_Withdrawal': round(yearly_withdrawal_total, 2),
                'Year_End_Balance': round(max(current_balance, 0.0), 2)
            })
            yearly_withdrawal_total = 0.0  # അടுத்த വർഷത്തിനായി റീസെറ്റ് ചെയ്യുക
        
        if current_balance <= 0:
            break
    
    return results, total_withdrawn, max(current_balance, 0.0)
