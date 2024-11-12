# BSE Data Processing Project

This project automates the extraction, processing, and notification of announcements from the Bombay Stock Exchange (BSE) corporate announcements page. Three scripts run sequentially, each at 5-minute intervals, to handle different stages of data extraction, processing, and notification. This document explains the setup, usage, and flow of each script.

## Overview

The project consists of three scripts:

- **Script 1:** Web scraping to collect announcements and download associated PDF files.
- **Script 2:** Text extraction from PDFs, OCR processing if needed, and storing extracted text.
- **Script 3:** Keyword search, notification, and result storage with email and SMS capabilities.

### Project Workflow

1. **Script 1:** Collects announcements from the BSE website, organizes data in CSV files, and downloads associated PDFs.
2. **Script 2:** Extracts text from PDFs, including OCR if necessary, then stores extracted information in a structured format.
3. **Script 3:** Searches for keywords and triggers notifications if certain keywords appear, such as "Scheme Of Arrangement."

The scripts are run in this specific order to ensure that each stage of data collection and processing is completed before moving to the next step.

## Dependencies

This project requires the following Python libraries:

- `os`
- `time`
- `pandas`
- `requests`
- `selenium`
- `BeautifulSoup`
- `fitz` (PyMuPDF)
- `re`
- `ocrmypdf`
- `csv`
- `twilio` (for SMS and call notifications)
- `smtplib` (for email notifications)

### Installation

Install the required libraries:

```bash
pip install pandas requests selenium BeautifulSoup4 pymupdf ocrmypdf twilio

# Script Details
--------------

### Script 1: `data_scraping.py`

**Purpose:** Scrape announcements from the BSE website, create a folder structure by date, save announcement details to CSV, and download any associated PDFs.

**Steps:**

* Initializes a Selenium WebDriver with headless Chrome.
* Selects the date range for announcements.
* Scrapes announcement details, including heading, content, insider info, PDF link, and category.
* Creates a date-based folder structure and saves the announcements to CSV.
* Downloads PDFs linked in the announcements to a specified folder.

### Script 2: `pdf_processing.py`

**Purpose:** Processes the downloaded PDFs, extracts text, performs OCR if text extraction fails, and logs any errors.

**Steps:**

* Locates the PDFs downloaded in the previous script.
* Attempts to extract text from each PDF.
* If extraction fails, performs OCR on the PDF and retries extraction.
* Logs errors in an error log CSV if both extraction and OCR fail.
* Updates the CSV file with extracted text data.

### Script 3: `keyword_search_and_notification.py`

**Purpose:** Searches extracted data for specific keywords, checks for prior recent announcements, and notifies via SMS, call, or email.

**Steps:**

* Reads extracted text data and checks if any relevant keywords (e.g., "Scheme Of Arrangement") are present.
* Checks if announcements for the company were made in the past six months to avoid duplicate notifications.
* If a new relevant keyword is found, sends notifications via Twilio SMS, call, or email.
* Stores results in an output CSV file for later reference.

## Flowcharts

To help visualize the process flow:

### Script Workflow

#### Script 1: Data Scraping

* **Input:** Date for announcements
* **Process:** Scrape BSE announcements, save to CSV, download PDFs
* **Output:** CSV of announcements, folder of PDFs

#### Script 2: PDF Processing

* **Input:** CSV file of announcements, downloaded PDFs
* **Process:** Extract text from PDFs, perform OCR if needed, save text to CSV
* **Output:** CSV with extracted text

#### Script 3: Keyword Search and Notification

* **Input:** CSV with extracted text, list of keywords
* **Process:** Search keywords, check for recent announcements, send notifications if relevant
* **Output:** Notifications sent, log of actions

### Flowchart Creation

To create the flowcharts, you can use online tools like [Lucidchart](https://www.lucidchart.com), [draw.io](https://app.diagrams.net/), or [Microsoft Visio](https://www.microsoft.com/en-us/microsoft-365/visio/flowchart-software).

#### Flowchart 1: Script 1 Workflow



