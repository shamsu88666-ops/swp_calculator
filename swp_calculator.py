def calculate_inflation_adjusted_swp(principal, monthly_withdrawal, years, inflation_rate, annual_return_rate, deplete_exactly=True):
    """SWP calculator with option to deplete corpus exactly at end of term"""
    monthly_rate = calculate_effective_monthly_rate(annual_return_rate)
    monthly_inflation_rate = calculate_effective_monthly_rate(inflation_rate)
    
    results = []
    total_withdrawn = 0.0
    current_balance = float(principal)
    current_monthly_withdrawal = float(monthly_withdrawal)
    
    total_months = years * 12
    
    for month in range(1, total_months + 1):
        # മാസം തുടങ്ങുമ്പോൾ ഇൻഫ്ലേഷൻ പ്രയോഗിക്കുക
        if month > 1:
            current_monthly_withdrawal *= (1.0 + monthly_inflation_rate)
        
        # പിൻവലിക്കൽ
        if deplete_exactly and month == total_months:
            # അവസാന മാസം - എല്ലാം എടുക്കുക
            withdrawal = current_balance
        else:
            withdrawal = min(current_monthly_withdrawal, current_balance)
        
        current_balance -= withdrawal
        total_withdrawn += withdrawal
        
        # ROI പ്രയോഗിക്കുക
        current_balance *= (1.0 + monthly_rate)
        
        if month % 12 == 0:  # വർഷം അവസാനം
            year_num = month // 12
            results.append({
                'Year': year_num,
                'Monthly_Withdrawal': round(current_monthly_withdrawal, 0),
                'Yearly_Withdrawal': round(withdrawal * (12 - (month - year_num * 12) + 1), 0),  # ശരിയായ ആകെ
                'Year_End_Balance': round(max(current_balance, 0.0), 0)
            })
        
        if current_balance <= 0:
            break
    
    return results, total_withdrawn, max(current_balance, 0.0)
