# Buffett Screener

A Python screener that analyzes SEC filings, ranks companies using seven Buffett-inspired indicators, and evaluates historical portfolios against SPY (S&P 500 ETF proxy).
This program compares companies using their financial records (ones that are strictly only available at the cutoff date). It gives each company a score out of 100, selects the highest-scoring companies, and checks what would have happened if you had bought their stocks in the past.

The project uses financial-data retrieval, historical filing filters, transparent 100-point scoring, portfolio selection, and return calculations It is an implementation of Python and company fundamental analysis.

# How It Works

1. The program has a list of 101 companies in `companies.py`. Each company has two useful identifiers:

- A **CIK**, which is its identification number in the SEC's filing system.
- A **ticker**, which is the short name used to look up its stock, such as `AAPL` for Apple.
  The program uses the CIK to find financial reports and the ticker to find stock prices.

2. US public companies submit financial reports to the Securities and Exchange Commission, or SEC. Those reports are available through a system called EDGAR.
   `sec_client.py` requests a company's financial data over the internet. It receives a .JSON response and turns that response into Python dictionaries and lists.
   This gives the rest of the program the numbers to work with.

3. Decide which information was available at the time
   Each analysis has a **cutoff date**. This is the historical date when we pretend to select the stocks.
   For example, suppose the cutoff is September 10, 2022. The program must not use a report published in 2023, even if that report describes an earlier financial year.

Two dates matter:

- The **reporting period** tells us when the company earned the money or held the assets.
- The **filing date** tells us when the report became available.
  The current cutoff rule keeps filings published on or before the cutoff. The simulated purchase happens after that date.

This helps prevent the program from using future information to make a decision in the past. Using future information would make the experiment unfair and potentially make the results look better than they really were.

4. Organize the records
   `financials.py` organizes this information. The goal is to obtain five annual records (5 years of financial information) for each relevant field.

5. Calculate seven indicators
   `metrics.py` contains the calculations. Each indicator answers a different question about the company.

| Indicator                     | Plain-English question                                                              | Maximum points |
| ----------------------------- | ----------------------------------------------------------------------------------- | -------------: |
| Return on equity              | How much profit the company earned compared with its average shareholders' equity   |             20 |
| Net profit margin             | How much of each dollar of sales remained as profit                                 |             15 |
| Margin consistency            | How much the profit margin changed over five years                                  |             10 |
| Liabilities-to-assets ratio   | Company liabilities to assets                                                       |             15 |
| Positive free-cash-flow years | In how many years did operating cash flow exceed spending on property and equipment |             20 |
| Revenue growth                | How quickly did sales grow between the first and last selected years                |             10 |
| Earnings growth               | How quickly did profit grow between the first and last selected years               |             10 |
| **Total**                     |                                                                                     |        **100** |

6. Turn the indicators into a score
   `scoring.py` awards points according to fixed thresholds.

For example, net profit margin earns:

- 15 points if it is at least 15%.
- 8 points if it is at least 10% but below 15%.
- 0 points if it is below 10%.

The seven point contributions add up to a maximum of 100.
These thresholds are choices made for the project.

`screener.py` puts the calculations together in `analyze_company(data, cutoff_date)`.
It returns the company name, financial indicators, point breakdown, and total score as a dictionary.

7. Rank the companies and select the top 10
   `backtest.py` runs the company analysis repeatedly for the same cutoff date.

The program sorts the successful results from highest score to lowest. If scores tie, it uses the company name alphabetically to make the ordering consistent.
It then selects the top 10 and looks up their stock tickers. Those tickers go directly to `returns.py`.

A high score means the company did well under these financial-quality rules. It does not mean the stock is cheap or guaranteed to rise.

8. Simulate buying and selling those stocks
   `returns.py` gets historical stock prices through yfinance.

For each selected stock, it looks for:

- A purchase price at the first available trading-day close after the cutoff.
- A sale price at the first available trading-day close on or after the cutoff's one-year anniversary.

The calculation is:

```text
Stock return = (sale price / purchase price) - 1
```

If the prices are $100 and $120, the return is 20%.
The code requests adjusted price history, which accounts for events such as stock splits and dividends. These adjusted values can differ from the prices originally displayed on those trading days.

Each stock starts with 10% of the hypothetical investment (10 stock portfolio). The portfolio's holding-period return is the average of the ten stock returns.

9. Compare the portfolio with SPY
   The program also calculates a return for SPY, an ETF used as a proxy for the S&P 500.
   This provides a reference point of how did the selected companies perform compared with that broad-market investment

The program repeats the process for the configured cutoffs in 2022, 2023, and 2024. Each date gets its own ranking and selected portfolio.

10. Save the results
    The CSV export version writes five files into the `output` folder:

| File                     | What it tells you                                                              |
| ------------------------ | ------------------------------------------------------------------------------ |
| `rankings.csv`           | Which companies ranked highest, their indicator values, and their points       |
| `holdings.csv`           | Which stocks were selected and their purchase dates, sale dates, and returns   |
| `backtest_summary.csv`   | How each portfolio performed compared with SPY                                 |
| `excluded_companies.csv` | Which companies could not be scored and why                                    |
| `overall_summary.csv`    | Average returns across comparable periods and how often the portfolio beat SPY |

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/Digitalsapple/buffett-screener.git
cd buffett-screener
```

### 2. Create an environment and install dependencies

Use Python 3.13, the version used during development. Run these commands in Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install requests pandas yfinance pytest
```

### 3. Set your SEC contact email

The downloader includes this contact in its User-Agent header (Mandatory when using SEC EDGAR API):

```powershell
$env:EMAIL_CONTACT = "your-real-email@example.com"
```

Replace the example with your own email. This setting applies to the CURRENT terminal session; set it again when opening a new terminal.

### 4. Run the complete program

```powershell
.\.venv\Scripts\python.exe returns.py
```

The program ranks companies separately for each cutoff, selects their tickers, calculates subsequent stock returns, compares the portfolios with SPY, and writes CSV files to `output/`.

### macOS / Linux equivalent

```bash
python3 -m venv .venv
.venv/bin/python -m pip install requests pandas yfinance pytest
export EMAIL_CONTACT="your-real-email@example.com"
.venv/bin/python returns.py
```

## How it works - TLDR

1. **Retrieve:** `sec_client.py` downloads Company Facts JSON from SEC EDGAR using a company's CIK identifier.
2. **Select financial records:** `financials.py` filters filings by cutoff, identifies annual records, handles supported tag alternatives, and selects eligible revisions or balances.
3. **Analyze:** `screener.py` calculates the seven indicators and their scores for one company.
4. **Rank:** `backtest.py` ranks successfully scored companies, breaking score ties by company name, and resolves the selected companies to tickers.
5. **Evaluate:** `returns.py` retrieves adjusted historical prices through yfinance, calculates returns, and exports the results.

The configured company count is not a guarantee that all 101 companies can be scored at every historical date. Inspect the ranking and exclusion files for actual coverage.

## Scoring model

The thresholds and weights are project design choices.

| Indicator               | Calculation                                                                 | Points                                                       |
| ----------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Return on equity        | Latest annual net income / average opening and closing shareholders' equity | 20 for >=15%; 10 for >=10% and <15%; otherwise 0             |
| Net profit margin       | Latest annual net income / revenue                                          | 15 for >=15%; 8 for >=10% and <15%; otherwise 0              |
| Margin consistency      | Population standard deviation of five annual net margins                    | 10 for <=3 percentage points; 5 for >3 and <=6; otherwise 0  |
| Liabilities to assets   | Liabilities / assets at the selected year-end                               | 15 for <=50%; 8 for >50% and <=70%; otherwise 0              |
| Positive free cash flow | Count of years with operating cash flow minus capital expenditure >0        | 4 per positive year, up to 20; requires five available years |
| Revenue growth          | Annualized growth between first and last selected revenue observations      | 10 for >=8%; 5 for >=3% and <8%; otherwise 0                 |
| Earnings growth         | Annualized growth between first and last selected net-income observations   | 10 for >=8%; 5 for >=3% and <8%; otherwise 0                 |
| **Maximum**             |                                                                             | **100**                                                      |

Growth uses `(last / first) ** (1 / intervals) - 1`. Five consecutive annual observations represent four growth intervals. Nonpositive growth endpoints produce an unavailable result. ROE is unavailable when either equity balance is nonpositive.

An unavailable score remains `None`, rather than becoming zero. A total score requires every component to be available. High scores describe the selected financial-quality criteria; they do not establish that a stock is attractively priced.

## Historical evaluation

Default ranking cutoffs in `returns.py`:

- September 10, 2022
- September 10, 2023
- September 10, 2024

Financial records filed **on or before** the cutoff are eligible. Filings published later are excluded before revision selection. This date convention is paired with purchases after the cutoff.

For each selected ticker:

- Entry: first available trading-day close strictly after the cutoff.
- Exit: first available trading-day close on or after the cutoff's one-year anniversary.
- Prices: adjusted history requested with `auto_adjust=True`.
- Return: `(adjusted exit price / adjusted entry price) - 1`.

## Output files

Each run replaces the corresponding files in `output/`.

| File                     | Contents                                                                                              |
| ------------------------ | ----------------------------------------------------------------------------------------------------- |
| `rankings.csv`           | Cutoff, rank, ticker, company, CIK, total score, selection flag, raw indicators, and component points |
| `holdings.csv`           | Selected holdings with initial weights, entry/exit dates, adjusted prices, and individual returns     |
| `backtest_summary.csv`   | Per-period stock counts, portfolio completeness, portfolio return, SPY return, and difference         |
| `excluded_companies.csv` | Companies excluded from financial scoring, cutoff dates, and reasons                                  |
| `overall_summary.csv`    | Comparable period count, average returns, average difference, and periods outperforming SPY           |

Raw indicator ratios in `rankings.csv` use decimals: `0.15` means 15%. Columns ending in `_pct` use percentage numbers: `15` means 15%. Difference columns use percentage points. Empty values represent unavailable results.

Financial exclusions are distinct from missing market-price data. Review terminal price-data errors as well as the CSV completeness and stock-count fields. Incomplete price histories must not be interpreted as a completed top-10 backtest.

## Project files

| File            | Responsibility                                                                    |
| --------------- | --------------------------------------------------------------------------------- |
| `companies.py`  | Company-name-to-CIK and company-name-to-ticker mappings                           |
| `sec_client.py` | SEC data requests and HTTP error handling                                         |
| `financials.py` | Filing cutoffs, annual-period selection, revisions, and supported accounting tags |
| `metrics.py`    | Financial calculations                                                            |
| `scoring.py`    | Indicator thresholds and point assignments                                        |
| `screener.py`   | Reusable single-company analysis                                                  |
| `backtest.py`   | Company rankings and automatic top-ticker selection                               |
| `returns.py`    | Price retrieval, portfolio comparisons, terminal reports, and CSV exports         |
| `test_logic.py` | Tests for ROE scoring, revision selection, and filing-date filtering              |

## Configuration and debugging

- Edit `cutoff_dates` in `returns.py` to change the evaluation periods.
- Edit `companies` and `tickers` in `companies.py` together when changing the universe.
- Adjust the `top_n` argument of `get_top_tickers()` to change the requested portfolio size.
- Edit `scoring.py` to change scoring thresholds. Record any changes before interpreting new results; tuning on the same historical periods can overfit the test.

## Limitations

- **Selection and survivorship bias:** the universe is a manually selected list of present-day companies, not historical index membership including failed and delisted businesses.
- **Small historical sample:** three periods cannot establish reliable future outperformance.
- **Financial comparability:** tag alternatives, derived equity/liabilities, and differing reporting periods require review. Accounting fields with similar names are not always interchangeable..
- **Inconsistency across sectors:** the model does not estimate intrinsic value, margin of safety, management quality, or competitive advantages. Scoring model is not meaningful for banks as their cash flows are dominated by deposits and loans, and get penalized by Liability to Asset Ratio. Model is designed for non-financial operating companies because financial institutions require sector-specific valuation and balance-sheet metrics.

## Data sources

- [SEC EDGAR Company Facts API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- [SEC developer resources and automated-access guidance](https://www.sec.gov/about/developer-resources)
- [yfinance](https://github.com/ranaroussi/yfinance), used to retrieve Yahoo Finance price history

Follow the data providers' access and usage terms. Use an identifying SEC User-Agent, moderate automated requests, and review data-use restrictions before redistributing downloaded market data.
