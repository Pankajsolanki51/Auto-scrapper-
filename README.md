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
