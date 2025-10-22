import pdfplumber
import pandas as pd
import re
import os
from datetime import datetime

# Define the year to assume
current_year = datetime.now().year

# Get all PDF files in the current directory
pdf_dir = '/Users/giocordial/PycharmProjects/credit_card_project/data/'
pdf_files = [os.path.join(pdf_dir, x) for x in os.listdir(pdf_dir) if x.endswith('.pdf')]
# pdf_files = [x for x in os.listdir('/Users/giocordial/PycharmProjects/credit_card_project/data/') if x.endswith('.pdf')]

# Regex pattern for transaction extraction
pattern = re.compile(
    r"""
    (?P<Transaction_Date>[A-Z][a-z]{2}\s\d{1,2})            # e.g. Sep 13
    \s+
    (?P<Post_Date>[A-Z][a-z]{2}\s\d{1,2})                   # e.g. Sep 14
    \s+
    (?P<Description>[A-Z0-9 .#&'()/,-]+)                    # e.g. DOLLARAMA #1286
    \s+
    (?P<Spend_Category>[A-Za-z\s&]+?)                       # e.g. Retail and Grocery
    \s+
    (?P<Amount>\(?-?\d+\.\d{2}\)?)                          # e.g. 2.81
    """,
    re.VERBOSE
)

# Empty list to store all transactions
all_transactions = []

# Loop through each PDF
for pdf_file in pdf_files:
    print(f"Processing {pdf_file}...")
    all_text = ""

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"

    # Clean weird PDF spacing
    all_text = all_text.replace("\xa0", " ")  # remove non-breaking spaces
    all_text = re.sub(r"\s+", " ", all_text)  # normalize whitespace

    # Extract matches
    matches = pattern.findall(all_text)
    print(f"Found {len(matches)} transactions in {pdf_file}")

    # If matches found, append to all_transactions
    for match in matches:
        all_transactions.append((*match, pdf_file))

# Convert to DataFrame if any transactions found
if all_transactions:
    transactions = pd.DataFrame(all_transactions, columns=[
        "Transaction Date", "Post Date", "Description", "Spend Category", "Amount", "Source File"
    ])

    # Clean up amount
    transactions["Amount"] = (
        transactions["Amount"]
        .str.replace(r"[()]", "", regex=True)
        .astype(float)
    )

    # # Add year to date strings and parse to datetime
    # transactions["Transaction Date"] = pd.to_datetime(
    #     transactions["Transaction Date"] + f" {current_year}",
    #     format="%b %d %Y"
    # )
    #
    # transactions["Post Date"] = pd.to_datetime(
    #     transactions["Post Date"] + f" {current_year}",
    #     format="%b %d %Y"
    # )

    # --- Extract year from Source File ---
    def extract_year(filename):
        # Try to find a 4-digit year in the filename
        match = re.search(r"(20\d{2})", os.path.basename(filename))
        if match:
            return int(match.group(1))
        else:
            # Fallback: assume current year if no year found
            return datetime.now().year


    # --- Apply year extraction ---
    transactions["Year"] = transactions["Source File"].apply(extract_year)

    # --- Add year to dates and convert ---
    transactions["Transaction Date"] = pd.to_datetime(
        transactions["Transaction Date"] + " " + transactions["Year"].astype(str),
        format="%b %d %Y",
        errors="coerce"
    )

    transactions["Post Date"] = pd.to_datetime(
        transactions["Post Date"] + " " + transactions["Year"].astype(str),
        format="%b %d %Y",
        errors="coerce"
    )

    # Exclude rows where Spend Category == "MERCI"
    transactions = transactions[transactions["Spend Category"].str.strip().str.upper() != "MERCI"]

    # Save combined data
    # output_dir = "/Users/giocordial/PycharmProjects/credit_card_project/output"
    transactions.to_csv("/Users/giocordial/PycharmProjects/credit_card_project/output/combined_data.csv", index=False)
    print(f"Saved {len(transactions)} total transactions to combined_data.csv")
else:
    print("No transactions found in any PDF.")
