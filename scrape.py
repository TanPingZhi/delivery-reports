import os
import requests
from datetime import datetime
from dateutil import parser

# --- CONFIGURATION ---
BASE_DIR = "data"

# Map URLs to their specific destination folders
URL_GROUPS = {
    "stocks": [
        "https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls",
        "https://www.cmegroup.com/delivery_reports/Silver_stocks.xls",
        "https://www.cmegroup.com/delivery_reports/Copper_Stocks.xls",
        "https://www.cmegroup.com/delivery_reports/PA-PL_Stck_Rprt.xls",
        "https://www.cmegroup.com/delivery_reports/Aluminum_Stocks.xls",
        "https://www.cmegroup.com/delivery_reports/Zinc_Stocks.xls",
        "https://www.cmegroup.com/delivery_reports/Lead_Stocks.xls",
    ],
    "notices/metals": [
        "https://www.cmegroup.com/delivery_reports/MetalsIssuesAndStopsReport.pdf",
        "https://www.cmegroup.com/delivery_reports/MetalsIssuesAndStopsMTDReport.pdf",
        "https://www.cmegroup.com/delivery_reports/MetalsIssuesAndStopsYTDReport.pdf",
    ],
    "notices/energy": [
        "https://www.cmegroup.com/delivery_reports/EnergiesIssuesAndStopsReport.pdf",
        "https://www.cmegroup.com/delivery_reports/EnergiesIssuesAndStopsYTDReport.pdf",
    ]
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_server_date(url):
    """
    Tries to get the Last-Modified header from the server.
    Returns a datetime object or None if not found.
    """
    try:
        response = requests.head(url, headers=HEADERS, timeout=10)
        last_modified = response.headers.get("Last-Modified")
        if last_modified:
            return parser.parse(last_modified)
    except Exception as e:
        print(f"Warning: Could not fetch headers for {url}: {e}")
    return None

def download_file(url, folder):
    """
    Downloads file if a version with the server's date (or today's date) doesn't exist.
    """
    # Ensure directory exists
    os.makedirs(folder, exist_ok=True)
    
    filename_raw = os.path.basename(url)
    
    # 1. Determine the date to use for the filename
    server_date = get_server_date(url)
    
    if server_date:
        date_str = server_date.strftime("%Y-%m-%d")
    else:
        # Fallback to today's date if server doesn't report modification time
        date_str = datetime.utcnow().strftime("%Y-%m-%d")

    # 2. Construct the new unique filename: YYYY-MM-DD_OriginalName.ext
    new_filename = f"{date_str}_{filename_raw}"
    filepath = os.path.join(folder, new_filename)

    # 3. Check if this specific version already exists
    if os.path.exists(filepath):
        print(f"Skipping (Already exists): {new_filename}")
        return

    # 4. Download content
    print(f"Downloading new version: {new_filename}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(response.content)
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def main():
    for category, urls in URL_GROUPS.items():
        # Construct path: data/stocks or data/notices/metals
        target_folder = os.path.join(BASE_DIR, category)
        
        print(f"\nProcessing {category}...")
        for url in urls:
            download_file(url, target_folder)

if __name__ == "__main__":
    main()