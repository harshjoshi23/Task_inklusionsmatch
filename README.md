README (Simple Version)

# Workshop PDF Parsing & Web Scraping

We have two Python scripts to process the PDF (`Register_2024.pdf`) and collect data about various workshops.

1. **script_pagesplit.py**  
   - Splits the PDF by “Seite - XX -” or “Baden-Württemberg(...)”.  
   - This may produce around 100+ rows. Some might be duplicates or partial entries.  
   - Good if you need to capture **all** text chunks (even if some are repeated).

2. **script_regnr.py**  
   - Splits the PDF by “(Reg.-Nr.)”.  
   - Produces about 60–70 rows, each closer to one unique workshop.  
   - Good if you want a **1:1** mapping of real workshop entries.

### How to Use

1. Place these scripts and the file `Register_2024.pdf` in the same folder.
2. Install Python packages:



3. Run a script:
- `python script_pagesplit.py`  
  - Output: `companies_output_pagesplit.csv`
- `python script_regnr.py`  
  - Output: `companies_output_regnr.csv`

### What the Scripts Do

1. Parse the PDF to get workshop name, services (“offerings”), homepage, and email.  
2. Scrape each homepage (if valid) for updates (“updated_services” and “contact_person”).  
3. Write a CSV with these fields.

### Notes

- Some rows appear as `company_name = "Unknown"` when the PDF text does not match the expected pattern.  
- You can remove them by editing the code to skip “Unknown” entries if desired.

