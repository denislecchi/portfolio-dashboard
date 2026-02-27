import pandas as pd
import sys
import os
from pathlib import Path
from datetime import datetime


def extract_performance_data(csv_file):
    """Extract historical performance data from IBKR Inception CSV"""

    print(f"📊 Extracting performance data from {csv_file}...")

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        monthly_data = []
        annual_data = []

        for line in lines:
            if 'Historical Performance Benchmark Comparison,Data,' in line:
                parts = line.strip().split(',')
                if len(parts) >= 11:
                    date_str = parts[2].strip()
                    if date_str.isdigit() and len(date_str) == 6:
                        try:
                            year = date_str[:4]
                            month = date_str[4:6]
                            spx_return = parts[4].strip() if len(parts) > 4 else None
                            portfolio_return = parts[10].strip() if len(parts) > 10 else None
                            if portfolio_return and portfolio_return != '-':
                                port_ret = float(portfolio_return)
                                sp_ret = float(spx_return) if spx_return and spx_return != '-' else 0.0
                                monthly_data.append({
                                    'Date': f"{year}-{month}-01",
                                    'Portfolio_Return': port_ret,
                                    'SP500_Return': sp_ret
                                })
                        except (ValueError, IndexError):
                            pass

            if 'Historical Performance Benchmark Comparison,Data' in line:
                parts = line.strip().split(',')
                if len(parts) >= 11:
                    year_str = parts[2].strip()
                    if year_str.isdigit() and len(year_str) == 4:
                        try:
                            year = int(year_str)
                            spx_return = parts[4].strip()
                            portfolio_return = parts[10].strip()
                            if portfolio_return and portfolio_return != '-':
                                port_ret = float(portfolio_return)
                                sp_ret = float(spx_return) if spx_return and spx_return != '-' else 0.0
                                annual_data.append({
                                    'Year': year,
                                    'Portfolio_Return': port_ret,
                                    'SP500_Return': sp_ret
                                })
                        except (ValueError, IndexError):
                            pass

        monthly_df = pd.DataFrame(monthly_data)
        annual_df = pd.DataFrame(annual_data)

        if not monthly_df.empty:
            monthly_df['Date'] = pd.to_datetime(monthly_df['Date'])
            monthly_df = monthly_df.sort_values('Date').reset_index(drop=True)
            monthly_df['Portfolio_Cumulative'] = (1 + monthly_df['Portfolio_Return']/100).cumprod() * 100 - 100
            monthly_df['SP500_Cumulative'] = (1 + monthly_df['SP500_Return']/100).cumprod() * 100 - 100

        if not annual_df.empty:
            annual_df = annual_df.sort_values('Year').reset_index(drop=True)

        print(f"✅ Extracted {len(monthly_df)} months and {len(annual_df)} years of performance data")
        return monthly_df, annual_df

    except Exception as e:
        print(f"⚠️  Error extracting performance: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame(), pd.DataFrame()


def extract_options_data(xlsx_file):
    """Extract options positions from Portfolio Excel file"""

    print(f"📋 Extracting options from {xlsx_file}...")

    try:
        df = pd.read_excel(xlsx_file, sheet_name=0, header=5)
        options = df[df['AssetClass'] == 'OPT'].copy()

        if options.empty:
            print("⚠️  No options found")
            return pd.DataFrame()

        options_data = options[[
            'Symbol', 'Description', 'Quantity',
            'CostBasisMoney', 'PositionValue',
            'FifoPnlUnrealized', 'CurrencyPrimary'
        ]].copy()

        options_data.columns = [
            'Symbol', 'Description', 'Quantity',
            'Cost Basis', 'Market Value',
            'Unrealized P&L', 'Currency'
        ]

        def parse_option_description(desc):
            try:
                parts = str(desc).split()
                if len(parts) >= 3:
                    expiry = parts[1]
                    strike = parts[2]
                    opt_type = parts[3] if len(parts) > 3 else 'Unknown'
                    return expiry, strike, opt_type
            except:
                pass
            return 'N/A', 'N/A', 'N/A'

        options_data[['Expiry', 'Strike', 'Type']] = options_data['Description'].apply(
            lambda x: pd.Series(parse_option_description(x))
        )

        options_data['Strategy'] = options_data.apply(
            lambda row: f"{row['Type']} Sold" if row['Quantity'] < 0 else f"{row['Type']} Bought",
            axis=1
        )

        options_data['Underlying'] = options_data['Symbol'].str.split().str[0]
        options_data = options_data.dropna(subset=['Symbol'])

        print(f"✅ Found {len(options_data)} options positions")
        return options_data

    except Exception as e:
        print(f"⚠️  Could not extract options: {e}")
        return pd.DataFrame()


def detect_changes(output_dir, current_stocks, current_options):
    """
    Compares current portfolio to last week saved snapshots.
    Returns a formatted string describing all changes.
    """
    changes_lines = []

    # ── STOCKS ──────────────────────────────────────────────────
    prev_stocks_file = os.path.join(output_dir, 'previous_portfolio.csv')

    if os.path.exists(prev_stocks_file):
        prev_stocks = pd.read_csv(prev_stocks_file)

        prev_symbols = set(prev_stocks['Symbol'].astype(str))
        curr_symbols = set(current_stocks['Symbol'].astype(str))

        new_stocks = curr_symbols - prev_symbols
        closed_stocks = prev_symbols - curr_symbols
        common_stocks = curr_symbols & prev_symbols

        for sym in sorted(new_stocks):
            changes_lines.append(f"🆕 **New Stock Position:** {sym}")

        for sym in sorted(closed_stocks):
            changes_lines.append(f"❌ **Closed Stock Position:** {sym}")

        for sym in sorted(common_stocks):
            prev_row = prev_stocks[prev_stocks['Symbol'].astype(str) == sym]
            curr_row = current_stocks[current_stocks['Symbol'].astype(str) == sym]
            if not prev_row.empty and not curr_row.empty:
                prev_qty = float(prev_row['Quantity'].values[0])
                curr_qty = float(curr_row['Quantity'].values[0])
                if curr_qty > prev_qty:
                    changes_lines.append(f"📈 **Increased Stock Position:** {sym} (qty: {prev_qty:.0f} → {curr_qty:.0f})")
                elif curr_qty < prev_qty:
                    changes_lines.append(f"📉 **Reduced Stock Position:** {sym} (qty: {prev_qty:.0f} → {curr_qty:.0f})")
    else:
        changes_lines.append("*(No previous snapshot found — changes will appear from next week)*")

    # ── OPTIONS ─────────────────────────────────────────────────
    prev_options_file = os.path.join(output_dir, 'previous_options.csv')

    if not current_options.empty and os.path.exists(prev_options_file):
        prev_options = pd.read_csv(prev_options_file)

        prev_opt_symbols = set(prev_options['Symbol'].astype(str))
        curr_opt_symbols = set(current_options['Symbol'].astype(str))

        new_opts = curr_opt_symbols - prev_opt_symbols
        closed_opts = prev_opt_symbols - curr_opt_symbols

        for sym in sorted(new_opts):
            row = current_options[current_options['Symbol'].astype(str) == sym].iloc[0]
            changes_lines.append(
                f"🆕 **New Option Trade:** {sym} — {row['Strategy']} | Expiry: {row['Expiry']} | Strike: ${row['Strike']}"
            )

        for sym in sorted(closed_opts):
            row = prev_options[prev_options['Symbol'].astype(str) == sym].iloc[0]
            changes_lines.append(
                f"✅ **Option Closed/Expired:** {sym} — {row['Strategy']} | Expiry: {row['Expiry']} | Strike: ${row['Strike']}"
            )

        # Check quantity changes on existing options
        common_opts = curr_opt_symbols & prev_opt_symbols
        for sym in sorted(common_opts):
            prev_row = prev_options[prev_options['Symbol'].astype(str) == sym]
            curr_row = current_options[current_options['Symbol'].astype(str) == sym]
            if not prev_row.empty and not curr_row.empty:
                prev_qty = float(prev_row['Quantity'].values[0])
                curr_qty = float(curr_row['Quantity'].values[0])
                if curr_qty != prev_qty:
                    changes_lines.append(
                        f"📝 **Adjusted Option:** {sym} (contracts: {prev_qty:.0f} → {curr_qty:.0f})"
                    )

    elif not current_options.empty and not os.path.exists(prev_options_file):
        pass  # First run, no message needed, already covered by stocks message

    if not changes_lines:
        changes_lines.append("↔️ No changes detected this week.")

    return "\n".join(changes_lines)


def generate_substack_draft(output_dir, metrics, changes_text):
    """Generates a ready-to-publish Substack post with live metrics"""
    date_today = datetime.now().strftime('%B %d, %Y')

    draft_content = f"""### **Title: 📊 Weekly Portfolio Update & Options Premium Collected**

**Subtitle:** *Total Return Since Inception: {metrics['inception_ret']}. See our live IBKR dashboard for every trade.*

Welcome to our weekly portfolio update at *The Fat Pitch*.

Unlike most finance writers who deal in hypotheticals, we manage real capital and believe in radical transparency. Every Friday, our automated pipeline pulls our Interactive Brokers (IBKR) data to verify our trades.

Here is our performance as of {date_today}:

### **📈 Performance Snapshot**
* **Since Inception (Oct 2021):** {metrics['inception_ret']} *(Outperforming S&P 500 by {metrics['inception_alpha']})*
* **Year-to-Date ({metrics['current_year']}):** {metrics['ytd_ret']} *(Outperforming S&P 500 by {metrics['ytd_alpha']})*
* **Month-to-Date ({metrics['current_month']}):** {metrics['mtd_ret']} *(Last completed month — Outperforming S&P 500 by {metrics['mtd_alpha']})*

### **🔄 Weekly Portfolio Variation**
Our total portfolio value moved by **{metrics['value_variation']}** this week.
Current Allocations: {metrics['stock_count']} Equities, {metrics['option_count']} Option Contracts

### **📋 What Changed This Week**
{changes_text}

### **💵 Options Strategy: Premium This Week**
This week we collected **{metrics['premium_weekly_delta']}** in new options premium.
Total premium collected since inception: **${metrics['premium_cashed']}**

We continue to sell premium and use cash-secured puts to accumulate shares of high-conviction tech names at our preferred strike prices.

*(Note: We blur exact dollar values for security, but the dashboard reflects our real, percentage-based allocations and true P&L).*

👇 **Click below to see our live dashboard with every stock, option, and performance chart.**

**[🔗 VIEW THE FAT PITCH LIVE PORTFOLIO DASHBOARD HERE](https://ifihadinvested.github.io/portfolio-dashboard/)**

Have questions about our current allocations? Drop a comment below.

— Denis & Alex
"""
    draft_file = os.path.join(output_dir, 'Substack_Draft.txt')
    with open(draft_file, 'w', encoding='utf-8') as f:
        f.write(draft_content)
    print(f"📝 Substack draft saved to: {draft_file}")


def convert_ibkr_to_dashboard(portfolio_xlsx, performance_csv=None):
    """Convert IBKR files to dashboard CSV format"""

    print("="*60)
    print("  IBKR TO DASHBOARD CONVERTER v2.4 (Substack Edition)")
    print("  (Stocks + Options + Performance + Changes + Auto-Draft)")
    print("="*60)
    print()

    output_dir = os.path.dirname(os.path.abspath(portfolio_xlsx))
    metrics = {}

    # 1. EXTRACT STOCKS
    print("📂 Reading portfolio file...")
    df = pd.read_excel(portfolio_xlsx, sheet_name=0, header=5)
    stocks = df[df['AssetClass'] == 'STK'].copy()
    metrics['stock_count'] = len(stocks)
    print(f"✅ Found {len(stocks)} stock positions")

    portfolio = stocks[[
        'Symbol', 'Quantity', 'CostBasisMoney',
        'PositionValue', 'FifoPnlUnrealized', 'CurrencyPrimary'
    ]].copy()
    portfolio.columns = [
        'Symbol', 'Quantity', 'Cost Basis',
        'Market Value', 'Unrealized P&L', 'Currency'
    ]
    portfolio = portfolio.dropna(subset=['Symbol'])

    # Weekly Value Variation
    current_value = portfolio['Market Value'].sum()
    prev_val_file = os.path.join(output_dir, 'previous_value.txt')
    if os.path.exists(prev_val_file):
        with open(prev_val_file, 'r') as f:
            prev_value = float(f.read().strip())
        val_diff = ((current_value - prev_value) / prev_value) * 100
        metrics['value_variation'] = f"{val_diff:+.2f}%"
    else:
        metrics['value_variation'] = "N/A (First Run)"
    with open(prev_val_file, 'w') as f:
        f.write(str(current_value))

    stocks_file = os.path.join(output_dir, 'portfolio_data.csv')
    portfolio.to_csv(stocks_file, index=False)
    print(f"✅ Saved stocks to: {stocks_file}")

    # 2. EXTRACT OPTIONS
    options = extract_options_data(portfolio_xlsx)
    if not options.empty:
        metrics['option_count'] = len(options)
        options_file = os.path.join(output_dir, 'options_data.csv')
        options.to_csv(options_file, index=False)
        print(f"✅ Saved options to: {options_file}")

        sold_options = options[options['Quantity'] < 0]
        premium_cashed = abs(sold_options['Cost Basis'].sum())
        metrics['premium_cashed'] = f"{premium_cashed:,.2f}"

        prev_premium_file = os.path.join(output_dir, 'previous_premium.txt')
        if os.path.exists(prev_premium_file):
            with open(prev_premium_file, 'r') as f:
                prev_premium = float(f.read().strip())
            premium_delta = premium_cashed - prev_premium
            metrics['premium_weekly_delta'] = f"${premium_delta:+,.2f}"
        else:
            metrics['premium_weekly_delta'] = "N/A (First Run)"
        with open(prev_premium_file, 'w') as f:
            f.write(str(premium_cashed))

        print(f"\n📊 Options Summary:")
        print(f"   Total Contracts: {len(options)}")
        print(f"   Total Premium Collected: ${premium_cashed:,.2f}")
        print(f"   Weekly Premium Delta: {metrics['premium_weekly_delta']}")
    else:
        metrics['option_count'] = 0
        metrics['premium_cashed'] = "0.00"
        metrics['premium_weekly_delta'] = "$0.00"

    # 3. DETECT CHANGES (stocks + options vs last week)
    print("\n🔍 Detecting changes vs last week...")
    changes_text = detect_changes(output_dir, portfolio, options)
    print(changes_text)

    # Save current snapshots for next week comparison
    portfolio.to_csv(os.path.join(output_dir, 'previous_portfolio.csv'), index=False)
    if not options.empty:
        options.to_csv(os.path.join(output_dir, 'previous_options.csv'), index=False)
    print("✅ Saved snapshots for next week comparison")

    # 4. EXTRACT PERFORMANCE (YTD / MTD / Inception)
    if performance_csv and os.path.exists(performance_csv):
        monthly_df, annual_df = extract_performance_data(performance_csv)

        if not monthly_df.empty:
            perf_file = os.path.join(output_dir, 'performance_data.csv')
            monthly_df.to_csv(perf_file, index=False)

            total_return = monthly_df['Portfolio_Cumulative'].iloc[-1]
            sp500_inception = monthly_df['SP500_Cumulative'].iloc[-1]
            metrics['inception_ret'] = f"{total_return:+.2f}%"
            metrics['inception_alpha'] = f"{total_return - sp500_inception:+.2f}%"

            last_row = monthly_df.iloc[-1]
            metrics['current_month'] = last_row['Date'].strftime('%b %Y')
            metrics['mtd_ret'] = f"{last_row['Portfolio_Return']:+.2f}%"
            metrics['mtd_alpha'] = f"{(last_row['Portfolio_Return'] - last_row['SP500_Return']):+.2f}%"

            current_year = datetime.now().year
            ytd_rows = monthly_df[monthly_df['Date'].dt.year == current_year]
            if not ytd_rows.empty:
                ytd_port = (1 + ytd_rows['Portfolio_Return']/100).prod() * 100 - 100
                ytd_sp = (1 + ytd_rows['SP500_Return']/100).prod() * 100 - 100
                metrics['ytd_ret'] = f"{ytd_port:+.2f}%"
                metrics['ytd_alpha'] = f"{(ytd_port - ytd_sp):+.2f}%"
                metrics['current_year'] = str(current_year)
            else:
                if not annual_df.empty:
                    last_annual = annual_df.iloc[-1]
                    metrics['ytd_ret'] = f"{last_annual['Portfolio_Return']:+.2f}%"
                    metrics['ytd_alpha'] = f"{(last_annual['Portfolio_Return'] - last_annual['SP500_Return']):+.2f}%"
                    metrics['current_year'] = str(int(last_annual['Year']))
                else:
                    metrics['ytd_ret'] = "N/A"
                    metrics['ytd_alpha'] = "N/A"
                    metrics['current_year'] = str(current_year)

        if not annual_df.empty:
            annual_file = os.path.join(output_dir, 'annual_returns.csv')
            annual_df.to_csv(annual_file, index=False)

        print(f"\n📈 Performance Summary:")
        print(f"   Since Inception : {metrics['inception_ret']} (Alpha: {metrics['inception_alpha']})")
        print(f"   YTD {metrics['current_year']}          : {metrics['ytd_ret']} (Alpha: {metrics['ytd_alpha']})")
        print(f"   MTD {metrics['current_month']}     : {metrics['mtd_ret']} (Alpha: {metrics['mtd_alpha']})")

    else:
        for key in ['inception_ret', 'inception_alpha', 'mtd_ret', 'mtd_alpha', 'ytd_ret', 'ytd_alpha']:
            metrics[key] = "N/A"
        metrics['current_month'] = "Current Month"
        metrics['current_year'] = str(datetime.now().year)

    # 5. GENERATE SUBSTACK DRAFT
    generate_substack_draft(output_dir, metrics, changes_text)

    # 6. SUMMARY
    print(f"\n{'='*60}")
    print(f"✅ CONVERSION COMPLETE!")
    print(f"   portfolio_data.csv      ({metrics['stock_count']} stocks)")
    print(f"   options_data.csv        ({metrics['option_count']} options)")
    print(f"   performance_data.csv")
    print(f"   annual_returns.csv")
    print(f"   Substack_Draft.txt      ← Ready to publish!")
    print(f"   previous_portfolio.csv  ← Snapshot for next week")
    print(f"   previous_options.csv    ← Snapshot for next week")
    print(f"{'='*60}")

    return stocks_file


if __name__ == "__main__":
    print("Looking for IBKR files...")
    print()

    current_dir = Path('.')
    portfolio_files = list(current_dir.glob('Portfolio*.xlsx'))
    performance_files = list(current_dir.glob('*Inception*.csv'))

    if not portfolio_files:
        print("❌ No Portfolio*.xlsx file found!")
        print("\nUsage:")
        print("  1. Put Portfolio_Weekly.xlsx in this folder")
        print("  2. Put Denis_Lecchi_Inception_[Date].csv in this folder (optional)")
        print("  3. Run this script or double-click convert.bat")
        input("\nPress Enter to exit...")
        sys.exit(1)

    portfolio_file = str(portfolio_files[0])
    performance_file = str(performance_files[0]) if performance_files else None

    print(f"📁 Found: {portfolio_file}")
    if performance_file:
        print(f"📁 Found: {performance_file}")
    else:
        print(f"⚠️  No *Inception*.csv file found — skipping performance")
    print()

    try:
        convert_ibkr_to_dashboard(portfolio_file, performance_file)
        print("\nSUCCESS! All files + Substack Draft are ready.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")
