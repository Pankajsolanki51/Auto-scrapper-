# BSE Data Scraping and Processing Project
This project automates the extraction, processing, and notification of announcements from the Bombay Stock Exchange (BSE) corporate announcements page. It consists of three sequential scripts that handle data extraction, processing, and notification tasks at 5-minute intervals.

## Overview
### Project Components
The project is comprised of three scripts:

- **Script 1: SCRAP_DATA.py**  
  Collects announcements from the BSE website, organizes them, and downloads associated PDF files.

- **Script 2: TEXT_FROM_PDF.py**  
  Extracts text from the PDFs, including OCR if needed, and stores extracted information.

- **Script 3: SCHEME_FILTER.py**  
  Searches the extracted data for specific keywords, checks for recent announcements, and triggers notifications.

## Project Workflow

Each script runs in sequence to ensure data consistency across stages. Here’s the overall workflow:

- **Script 1** scrapes announcements and downloads PDFs.
- **Script 2** processes the PDFs, extracts text, and performs OCR if needed.
- **Script 3** searches for keywords and sends notifications if specified keywords (e.g., “Scheme Of Arrangement”) appear.

## Dependencies
To run the scripts, the following Python libraries are required:
### Libraries Used

- **Standard Libraries:** `os`, `time`, `re`, `csv`, `smtplib`
- **Third-party Libraries:** `pandas`, `requests`, `selenium`, `BeautifulSoup4`, `pymupdf` (fitz), `ocrmypdf`, `twilio`

```python
pip install pandas requests selenium BeautifulSoup4 pymupdf ocrmypdf twilio
```
## Script Details

## Script 1: `SCRAP_DATA.py`
- **Purpose:** Scrapes announcements from the BSE website, organizes data into CSV files, and downloads related PDFs.
- **Steps:**
  - Initializes a headless Chrome WebDriver.
  - Sets the date range for announcements.
  - Collects announcement details, such as title, content, insider info, PDF link, and category.
  - Saves announcement details in a CSV, using a date-based folder structure.
  - Downloads associated PDFs into a specified folder
    
## Script 2: `TEXT_FROM_PDF.py`
- **Purpose:** Processes downloaded PDFs by extracting text, performing OCR if needed, and logging errors.
- **Steps:**
  - Reads PDFs downloaded by Script 1.
  - Attempts text extraction from each PDF.
  - If text extraction fails, performs OCR and retries
  - Logs errors in a CSV if both extraction and OCR fail.
  - Saves extracted text data in a structured format.
### Script 3: `SCHEME_FILTER.py`

- **Purpose:** Searches for specific keywords in extracted data and sends notifications via SMS, call, or email if relevant keywords are found.
- **Steps:**
  - Reads extracted text data.
  - Searches for keywords (e.g., “Scheme Of Arrangement”).
  - Checks if a similar announcement was made in the past six months to prevent duplicate notifications.
  - Sends notifications using Twilio if a new keyword is detected.
  - Logs results in an output CSV for reference.
    
 
