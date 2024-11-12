# BSE Data Scraping and Processing Project
This project automates the extraction, processing, and notification of announcements from the Bombay Stock Exchange (BSE) corporate announcements page. It consists of three sequential scripts that handle data extraction, processing, and notification tasks at 5-minute intervals.

## Overview
### Project Components
The project is comprised of three scripts:

- **Script 1: Data Scraping**  
  Collects announcements from the BSE website, organizes them, and downloads associated PDF files.

- **Script 2: PDF Processing**  
  Extracts text from the PDFs, including OCR if needed, and stores extracted information.

- **Script 3: Keyword Search and Notification**  
  Searches the extracted data for specific keywords, checks for recent announcements, and triggers notifications.
