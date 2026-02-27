# IBKR Portfolio Dashboard v2.0 🚀

## Complete portfolio dashboard with stocks, options, and performance tracking!

---

## 🎯 FEATURES

✅ **Stock Portfolio Tracking**
   - Real-time positions and P&L
   - Automatic updates from IBKR

✅ **Options Portfolio Analysis**
   - Track all options positions
   - Premium collected vs current value
   - Strategy breakdown (puts/calls sold/bought)
   - Expiration tracking

✅ **Performance Since Inception**
   - Historical returns vs S&P 500
   - Interactive performance chart
   - Annual returns breakdown
   - Cumulative growth tracking

✅ **Beautiful Dashboard**
   - Professional design
   - Mobile responsive
   - Interactive charts (Plotly)
   - Auto-updates via GitHub Actions

---

## 📁 SETUP (One-Time - 5 minutes)

### Prerequisites:
1. **Python 3.x** installed
   - Check: `python --version`
   - Download: https://python.org/downloads

2. **Install required packages:**
   ```bash
   pip install pandas openpyxl
   ```

### Download Files:
1. Create folder: `C:\IBKR_Dashboard\` (Windows) or `~/IBKR_Dashboard/` (Mac/Linux)
2. Download these files into that folder:
   - convert_ibkr_to_csv.py
   - convert.bat (Windows) or convert.sh (Mac/Linux)
   - README.txt (this file)

---

## 🚀 WEEKLY WORKFLOW (30 seconds)

### STEP 1: Download from IBKR

#### A. Portfolio File (REQUIRED)
1. Log in to IBKR Account Management
2. Reports → Flex Queries → Portfolio_Weekly
3. Run query → Download as Excel (.xlsx)
4. Save as `Portfolio_Weekly.xlsx`

#### B. Performance File (OPTIONAL - for charts)
1. Performance & Reports → Performance Summary
2. Select "Since Inception"
3. Download as CSV
4. Save as `Denis_Lecchi_Inception_[Date].csv`

### STEP 2: Convert Files

**Option A: One-Click (Windows)**
1. Put both files in `C:\IBKR_Dashboard\`
2. Double-click `convert.bat`
3. Wait 5 seconds ✅

**Option B: One-Click (Mac/Linux)**
1. Put both files in `~/IBKR_Dashboard/`
2. Run: `./convert.sh`
3. Wait 5 seconds ✅

**Option C: Manual**
```bash
cd C:\IBKR_Dashboard
python convert_ibkr_to_csv.py
```

### STEP 3: Files Created

After conversion, you'll have:
- ✅ `portfolio_data.csv` (stocks)
- ✅ `options_data.csv` (options)
- ✅ `performance_data.csv` (monthly returns)
- ✅ `annual_returns.csv` (yearly summary)

### STEP 4: Upload to GitHub

1. Go to: `github.com/denislecchi/portfolio-dashboard`
2. Upload these CSV files (replace old ones)
3. Go to **Actions** → **Update Portfolio Dashboard**
4. Click **Run workflow**
5. Wait 20 seconds
6. Visit: https://denislecchi.github.io/portfolio-dashboard/

**DONE! 🎉**

---

## 📊 WHAT THE DASHBOARD SHOWS

### 1. Performance Section
- **Since Inception Return**: Your total return since Sept 2021
- **S&P 500 Comparison**: How much you beat the market
- **Interactive Chart**: Visual comparison over time

### 2. Current Portfolio
- **Total Value**: Current portfolio worth
- **Unrealized P&L**: Total gains/losses
- **Total Return %**: Overall percentage return
- **Number of Positions**: Stock count

### 3. Annual Returns Table
- Year-by-year breakdown
- Your returns vs S&P 500
- Outperformance metrics

### 4. Stock Holdings
- All current positions
- Quantity, cost basis, market value
- Individual P&L and return %
- Sorted by position size

### 5. Options Portfolio (NEW!)
- All options contracts
- Premium collected
- Current value
- Unrealized P&L
- Strategy (Put/Call Sold/Bought)
- Strike price and expiration

---

## 🔧 TROUBLESHOOTING

### "No module named pandas"
```bash
pip install pandas openpyxl
```

### "No Portfolio*.xlsx file found"
- Make sure `Portfolio_Weekly.xlsx` is in same folder as script
- Check filename matches pattern `Portfolio*.xlsx`

### "Python not recognized"
- Install Python from python.org
- Make sure "Add to PATH" was checked during install

### Options not showing
- Make sure your Portfolio file includes options
- Check that options have AssetClass = "OPT"

### Performance chart not showing
- You need the inception CSV file
- Make sure it's named `*Inception*.csv`
- Place it in same folder as Portfolio file

### Permission denied (Mac/Linux)
```bash
chmod +x convert.sh
```

---

## 📈 DATA SOURCES

### Portfolio File (Portfolio_Weekly.xlsx)
Contains:
- Current stock positions
- Current options positions
- Cost basis and market values
- P&L for all positions

### Performance File (Denis_Lecchi_Inception_[Date].csv)
Contains:
- Historical monthly returns
- S&P 500 benchmark data
- Annual returns
- Cumulative performance

---

## 💡 TIPS & BEST PRACTICES

1. **Weekly Updates**: Download new files every Friday after market close
2. **Keep History**: Save old Performance CSV files for reference
3. **Backup**: Keep copies of CSV files before uploading
4. **Verify**: Check dashboard after upload to ensure data looks correct
5. **Share**: Perfect for Substack followers - share the GitHub Pages link!

---

## 🎓 FOR SUBSTACK PUBLISHING

Your dashboard is perfect for showing followers:
- ✅ Real-time portfolio performance
- ✅ Transparent returns vs S&P 500
- ✅ Professional presentation
- ✅ Options strategy tracking
- ✅ Historical performance proof

**Share link**: `https://denislecchi.github.io/portfolio-dashboard/`

Add to your Substack bio or include in weekly posts!

---

## 📊 TECHNICAL DETAILS

### Files Overview:

**convert_ibkr_to_csv.py**
- Reads IBKR Excel and CSV files
- Extracts stocks, options, performance data
- Creates 4 CSV files for dashboard

**generate_dashboard.py**
- Reads CSV files
- Generates interactive HTML dashboard
- Creates charts with Plotly.js

**convert.bat / convert.sh**
- One-click wrapper scripts
- Runs converter automatically

### Output Files:

1. **portfolio_data.csv**
   - Columns: Symbol, Quantity, Cost Basis, Market Value, P&L, Currency
   - One row per stock position

2. **options_data.csv**
   - Columns: Symbol, Description, Quantity, Cost Basis, Market Value, P&L, Strategy, Strike, Expiry
   - One row per options contract

3. **performance_data.csv**
   - Columns: Date, Portfolio_Return, SP500_Return, Portfolio_Cumulative, SP500_Cumulative
   - Monthly time series data

4. **annual_returns.csv**
   - Columns: Year, Portfolio_Return, SP500_Return
   - One row per calendar year

---

## 🆘 NEED HELP?

If something doesn't work:

1. **Check Python version**: `python --version` (need 3.7+)
2. **Check packages**: `pip list | grep pandas`
3. **Check file names**: Portfolio*.xlsx and *Inception*.csv
4. **Read error messages**: They usually tell you what's wrong
5. **Try manual mode**: Run `python convert_ibkr_to_csv.py` to see detailed output

---

## 🎯 SUMMARY

**Setup once:**
- Install Python + pandas
- Download converter scripts
- Create folder

**Every week:**
- Download 2 files from IBKR (5 seconds)
- Run converter (5 seconds)
- Upload to GitHub (20 seconds)
- Dashboard updates automatically!

**Total time: 30 seconds per week** ⚡

---

## 📝 VERSION HISTORY

**v2.0** (February 2026)
- ✅ Added options portfolio tracking
- ✅ Added performance charts
- ✅ Added annual returns table
- ✅ Added S&P 500 comparison
- ✅ Interactive Plotly charts

**v1.0** (February 2026)
- ✅ Initial release
- ✅ Basic stock portfolio tracking

---

**Created for**: Denis Lecchi Portfolio Dashboard
**Last updated**: February 2026
**GitHub**: https://github.com/denislecchi/portfolio-dashboard
**Live Dashboard**: https://denislecchi.github.io/portfolio-dashboard/

---

🚀 **Happy tracking!**
