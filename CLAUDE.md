# SA Tracker

## Primary Application

**`index.html` is the primary application.** It is a standalone, self-contained HTML/CSS/JavaScript portfolio tracker that runs entirely in the browser with no backend. This is the file that matters — focus your work here.

`streamlit_app.py` is a secondary/legacy Python implementation. It exists but is NOT the priority. Do not treat it as the main codebase.

## Architecture

- **index.html** — Single-file frontend app (HTML + embedded JS + CSS). Tracks 13F filings for institutional funds (SA LP, VARA). Uses Chart.js for visualization, localStorage for persistence, and Yahoo Finance for price data. Fetches SEC EDGAR filings via CORS proxies.
- **worker.js** — Optional Cloudflare Workers CORS proxy for fetching Yahoo Finance and SEC data from the browser.
- **streamlit_app.py** — Secondary Python implementation (not the focus).

## Key Concepts

- **Funds**: SA LP (CIK 0002045724) and VARA (CIK 0001963565) — each has its own holdings, CUSIP mappings, and options config in the `FUND_PROFILES` object.
- **13F Filings**: Quarterly SEC filings containing equity holdings. Auto-fetched from SEC EDGAR, parsed from XML. Holdings are stored as defaultHoldings (hardcoded fallback) and in localStorage (live updates).
- **Performance Simulation**: Daily returns calculated from historical prices weighted by 13F-reported portfolio values. Supports Black-Scholes option pricing for call/put positions.
- **Rebalancing Modes**: "Report Date" (uses quarter-end date) vs "Filing Date" (uses SEC filing date) for when holdings become active.

## Adding New 13F Data

When a new 13F is released:
1. Add the quarter's holdings to the fund's `defaultHoldings` in `FUND_PROFILES`
2. Update `defaultQuarterOrder` to include the new quarter
3. Add any new CUSIP→ticker mappings to `cusipToTicker`
4. Add any new company name→ticker mappings to `nameToTicker`
5. Add default IVs for any new option positions to `defaultIVs`

Note: SEC EDGAR filing XML filenames are not standardized. SALP uses names like `SALP_13FQ425.xml` or `SALP13FinfotableQ3.xml`. The auto-fetch code handles this by trying all XML files from the filing index.

## Common Issues

- **CORS**: Browser can't directly fetch SEC/Yahoo APIs. Requires either the Cloudflare worker or public CORS proxies.
- **CUSIP changes**: Companies change CUSIPs after restructurings. Always verify new CUSIPs map to the right ticker.
- **Value format**: SEC 13F values in XML are in full dollars (not thousands) for modern XBRL filings.
- **Missing tickers**: If Yahoo Finance doesn't have price data for a ticker, performance calculation renormalizes weights to exclude it.
