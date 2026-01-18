def calculate_effective_monthly_rate(annual_rate):
    """
    വാർഷിക നിരക്ക് മാസിക ഘടനയിലേക്ക് മാറ്റുക
    ഉദാ: 12% annual -> ~0.9489% monthly
    """
    if annual_rate <= -1.0:
        return 0.0
    return (1.0 + annual_rate) ** (1.0 / 12.0) - 1.0

def calculate_inflation_adjusted_swp(principal, monthly_withdrawal, years, inflation_rate, annual_return_rate, deplete_exactly=True):
    """
    ഇൻഫ്ലേഷൻ അഡ്ജസ്റ്റ്ഡ് SWP കാൽക്കുലേറ്റർ
    
    Args:
        principal: ആദ്യ നിക്ഷേപം
        monthly_withdrawal: ആരംഭ മാസിക പിൻവലിക്കൽ
        years: കാലാവധി (വർഷങ്ങളിൽ)
        inflation_rate: വാർഷിക ഇൻഫ്ലേഷൻ നിരക്ക് (ഉദാ: 0.06)
        annual_return_rate: വാർഷിക returns നിരക്ക് (ഉദാ: 0.10)
        deplete_exactly: True എങ്കിൽ അവസാന മാസം പൂർണ്ണ ബാലൻസ് പിൻവലിക്കും
    """
    # മാസിക നിരക്കുകൾ
    monthly_rate = calculate_effective_monthly_rate(annual_return_rate)
    monthly_inflation_rate = calculate_effective_monthly_rate(inflation_rate)
    
    # ഫലങ്ങൾ സംഭരിക്കുക
    results = []
    total_withdrawn = 0.0
    current_balance = float(principal)
    current_monthly_withdrawal = float(monthly_withdrawal)
    
    total_months = years * 12
    yearly_withdrawal_total = 0.0  # വർഷ ആകെ പിൻവലിക്കൽ
    
    for month in range(1, total_months + 1):
        # മാസം തുടങ്ങുമ്പോൾ ഇൻഫ്ലേഷൻ പ്രയോഗിക്കുക
        if month > 1:
            current_monthly_withdrawal *= (1.0 + monthly_inflation_rate)
        
        # പിൻവലിക്കൽ തുക
        if deplete_exactly and month == total_months and current_balance > 0:
            withdrawal = current_balance  # അവസാന മാസം - എല്ലാം
        else:
            withdrawal = min(current_monthly_withdrawal, current_balance)
        
        # വർഷ ആകെക്കൂടിൽ ചേർക്കുക
        yearly_withdrawal_total += withdrawal
        
        # ബാലൻസ് അപ്ഡേറ്റ്
        current_balance -= withdrawal
        total_withdrawn += withdrawal
        
        # ROI പ്രയോഗിക്കുക
        if current_balance > 0:
            current_balance *= (1.0 + monthly_rate)
        
        # വർഷം അവസാനം ഫലങ്ങൾ സംരക്ഷിക്കുക
        if month % 12 == 0:
            year_num = month // 12
            results.append({
                'Year': year_num,
                'Monthly_Withdrawal': round(current_monthly_withdrawal, 2),
                'Yearly_Withdrawal': round(yearly_withdrawal_total, 2),
                'Year_End_Balance': round(max(current_balance, 0.0), 2)
            })
            yearly_withdrawal_total = 0.0  # റീസെറ്റ്
        
        if current_balance <= 0:
            break
    
    return results, total_withdrawn, max(current_balance, 0.0)

def print_results(results, total_withdrawn, final_balance):
    """ഫലങ്ങൾ സുന്ദരമായി പ്രദർശിപ്പിക്കുക"""
    if not results:
        print("No results!")
        return
    
    print("\n" + "=" * 95)
    print(f"{'Year':<6} {'Monthly':<15} {'Yearly':<15} {'Balance':<15}")
    print("=" * 95)
    
    for r in results:
        print(f"{r['Year']:<6} "
              f"₹{r['Monthly_Withdrawal']:>12,.2f} "
              f"₹{r['Yearly_Withdrawal']:>12,.2f} "
              f"₹{r['Year_End_Balance']:>12,.2f}")
    
    print("=" * 95)
    print(f"Total Withdrawn: ₹{total_withdrawn:,.2f}")
    print(f"Final Balance: ₹{final_balance:,.2f}")
    print(f"Total Value: ₹{total_withdrawn + final_balance:,.2f}")

# ഉദാഹരണം
if __name__ == "__main__":
    results, total, balance = calculate_inflation_adjusted_swp(
        principal=10000000,
        monthly_withdrawal=50000,
        years=10,
        inflation_rate=0.06,
        annual_return_rate=0.10,
        deplete_exactly=True
    )
    print_results(results, total, balance)
