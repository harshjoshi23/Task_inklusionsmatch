"""
Better version : 
script_regnr.py
Splits on '(Reg.-Nr.)' to group each recognized workshop into one chunk.
Likely yields closer to one row per actual company block.
"""

import re
import csv
import requests
from bs4 import BeautifulSoup
import PyPDF2

def parse_pdf_regnr(pdf_path):
    data = []
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"

    # Each chunk starts at '(Reg.-Nr.)'
    raw_entries = re.split(r"(?=\(Reg\.-Nr\.)", full_text)

    for entry in raw_entries:
        # Skip segments that don't actually contain '(Reg.-Nr.)'
        if "(Reg.-Nr." not in entry:
            continue

        cleaned = entry.strip()

        # Finding the lines before '(Reg.-Nr.)' as a potential company name
        name_match = re.search(r"^(.*?)\(Reg\.-Nr\.", cleaned, re.DOTALL)
        if name_match:
            raw_name = name_match.group(1).strip()
            raw_name = re.sub(r"Seite\s*-\s*\d+\s*-", "", raw_name).strip()
            if raw_name:
                company_name = raw_name
            else:
                company_name = "Unknown"
        else:
            company_name = "Unknown"

        # Extract 'Auftragsarbeiten / Produkte:' block
        offerings_block = ""
        block_match = re.search(r"Auftragsarbeiten\s*/\s*Produkte:\s*(.*?)\n\n", cleaned, re.DOTALL)
        if block_match:
            offerings_block = block_match.group(1).strip()
        else:
            fallback = re.search(r"Auftragsarbeiten\s*/\s*Produkte:\s*(.*)", cleaned, re.DOTALL)
            if fallback:
                offerings_block = fallback.group(1)[:500].strip()

        # Homepage / Email
        homepage_match = re.search(r"Homepage:\s*(\S+)", cleaned)
        homepage = homepage_match.group(1).strip() if homepage_match else ""

        email_match = re.search(r"E-Mail:\s*([\w\.-]+@[\w\.-]+)", cleaned)
        email = email_match.group(1).strip() if email_match else ""

        data.append({
            "company_name": company_name,
            "offerings_raw": offerings_block,
            "homepage": homepage,
            "email": email
        })

    return data

def scrape_website_for_details(url):
    details = {"updated_services": None, "contact_person": None}
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            div_services = soup.find('div', class_='services-list')
            if div_services:
                details["updated_services"] = div_services.get_text(separator=' ').strip()
            contact = soup.find('p', class_='contact-person')
            if contact:
                details["contact_person"] = contact.get_text(separator=' ').strip()
    except Exception as e:
        print(f"Could not scrape {url}. Error: {e}")
    return details

def main():
    pdf_path = "Register_2024.pdf"
    output_csv_path = "companies_output_regnr.csv"

    print("Parsing PDF with (Reg.-Nr.) split...")
    companies_data = parse_pdf_regnr(pdf_path)
    print(f"Found {len(companies_data)} potential company entries.")

    for idx, company in enumerate(companies_data, start=1):
        url = company.get("homepage", "")
        if url.startswith("http"):
            print(f"[{idx}/{len(companies_data)}] Scraping site: {url}")
            info = scrape_website_for_details(url)
            company["updated_services"] = info["updated_services"]
            company["contact_person"] = info["contact_person"]

    fields = ["company_name","offerings_raw","homepage","email","updated_services","contact_person"]
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(companies_data)

    print(f"\nAll done! Results written to '{output_csv_path}'")

if __name__ == "__main__":
    main()
