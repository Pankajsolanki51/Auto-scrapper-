import os
import pandas as pd
import fitz  # PyMuPDF
import re
import ocrmypdf
import csv
from datetime import datetime, timedelta

def sanitize_filename(name, keep_spaces=False):
    if keep_spaces:
        return "".join([c if c.isalnum() or c.isspace() else "_" for c in name])
    else:
        return "".join([c if c.isalnum() else "_" for c in name])

def ocr_pdf(input_pdf, output_pdf):
    try:
        ocrmypdf.ocr(input_pdf, output_pdf, deskew=True, force_ocr=True)
    except Exception as e:
        print(f"Error performing OCR on PDF: {e}")

def extract_text_from_pdf(file_path):
    try:
        pdf_document = fitz.open(file_path)
        text = ''.join([page.get_text() for page in pdf_document])
        pdf_document.close()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ''

def clean_text(text):
    pattern = re.compile(r'[\x00-\x1F\x7F-\x9F]')
    return pattern.sub('', text)

def extract_date_from_folder(year_folder, month_folder, date_folder):
    try:
        return f"{date_folder}-{month_folder}-{year_folder}"
    except Exception as e:
        print(f"Error extracting date from folder names: {e}")
        return ""

def update_csv_with_extracted_data(csv_file, extracted_data):
    new_csv_file = os.path.splitext(csv_file)[0] + '_extracted.csv'
    file_exists = os.path.isfile(new_csv_file)
    with open(new_csv_file, mode='a' if file_exists else 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=extracted_data[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(extracted_data)
    print(f"Text extracted from PDFs and saved in '{new_csv_file}'.")

def log_error(log_file_path, heading, pdf_link, error_message, date):
    file_exists = os.path.isfile(log_file_path)
    with open(log_file_path, mode='a', newline='', encoding='utf-8') as logfile:
        log_writer = csv.writer(logfile)
        if not file_exists:
            log_writer.writerow(['HEADING', 'PDF LINK', 'ERROR', 'DATE'])
        log_writer.writerow([heading, pdf_link, error_message, date])

def read_pdf_links_from_csv(csv_file):
    pdf_links = []
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pdf_links.append(row['PDF LINK'])
    return pdf_links

def find_pdf_file_path(pdf_name, date_folder_path):
    pdf_files = os.listdir(date_folder_path)
    for pdf_file in pdf_files:
        if pdf_name in pdf_file:
            return os.path.join(date_folder_path, pdf_file)
    return None

def check_for_digital_signature(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        for sig in pdf_document.signatures():
            return True
        return False
    except Exception as e:
        print(f"Error checking for digital signature in PDF: {e}")
        return False

def process_pdf(pdf_link, heading, category, date_folder_path, log_file_path, date):
    try:
        first_word = sanitize_filename(heading.split()[0])
        category_sanitized = sanitize_filename(category, keep_spaces=True)
        pdf_name = f"{first_word}_{category_sanitized}_{os.path.basename(pdf_link).split('.')[0]}"
        pdf_file_path = find_pdf_file_path(pdf_name, date_folder_path)

        # print(f"Looking for PDF file at: {pdf_file_path}")

        if pdf_file_path:
            # print(f"Found PDF file: {pdf_file_path}")

            extracted_text = extract_text_from_pdf(pdf_file_path)

            if not extracted_text.strip():
                print(f"No text found in PDF, attempting OCR on: {pdf_file_path}")
                ocr_pdf_path = pdf_file_path.replace('.pdf', '_ocr.pdf')
                ocr_pdf(pdf_file_path, ocr_pdf_path)

                extracted_text = extract_text_from_pdf(ocr_pdf_path)

                if extracted_text.strip():
                    os.remove(ocr_pdf_path)
                else:
                    print(f"Text extraction failed from OCR PDF: {ocr_pdf_path}. Keeping the file for review.")
                    log_error(log_file_path, heading, pdf_link, "Text extraction failed even after OCR", date)

            return extracted_text
        else:
            print(f"PDF file for link {pdf_link} not found in {date_folder_path}")
            log_error(log_file_path, heading, pdf_link, "PDF file not found", date)
            return f"PDF file for link {pdf_link} not found in {date_folder_path}"
    except Exception as e:
        error_message = f"Failed to extract text from {pdf_link}: {str(e)}"
        print(error_message)
        log_error(log_file_path, heading, pdf_link, error_message, date)
        return error_message

def extract_data_from_csv(csv_file_path):
    try:
        df = pd.read_csv(csv_file_path, on_bad_lines='skip')
        if df.empty:
            print(f"No data found in {csv_file_path}")
            return None
        return df
    except Exception as e:
        print(f"Error processing {csv_file_path}: {e}")
        return None

def process_csv_file(csv_file_path, date_folder_path, year_folder, month_folder, date_folder, log_file_path):
    csv_files = [f for f in os.listdir(date_folder_path) if f.lower().endswith('.csv')]

    for csv_file in csv_files:
        if '_extracted.csv' in csv_file:
            print(f"Skipping extracted file: {csv_file}")
            continue
        
        csv_file_path = os.path.join(date_folder_path, csv_file)
        print(f"Processing CSV file: {csv_file_path}")

        extracted_file = os.path.splitext(csv_file)[0] + '_extracted.csv'
        extracted_file_path = os.path.join(date_folder_path, extracted_file)
        
        existing_extracted_data = None
        if os.path.isfile(extracted_file_path):
            # print(f"Extracted file '{extracted_file}' already exists. Checking for already processed entries.")
            try:
                existing_extracted_data = pd.read_csv(extracted_file_path, on_bad_lines='skip')
            except Exception as e:
                print(f"Error reading existing extracted file '{extracted_file}': {e}")
                existing_extracted_data = None

     
        extracted_data = extract_data_from_csv(csv_file_path)
        if extracted_data is not None:
            extracted_rows = []
            date_folder_pdfs_path = os.path.join(date_folder_path, 'PDFs')
            if not os.path.isdir(date_folder_pdfs_path):
                print(f"PDFs directory '{date_folder_pdfs_path}' does not exist.")
                continue
            if 'flag' not in extracted_data.columns:
                extracted_data['flag'] = 0

            for _, row in extracted_data.iterrows():
                pdf_link = row['PDF LINK']
                heading = row['HEADING']
                category = row['CATEGORY']
                flag = row['flag']

                if existing_extracted_data is not None:
                    existing_row = existing_extracted_data[existing_extracted_data['PDF LINK'] == pdf_link]
                    if not existing_row.empty and existing_row.iloc[0]['flag'] == 1:
                        # print(f"PDF link '{pdf_link}' already processed (flag is 1). Skipping.")
                        continue

                extracted_text = process_pdf(pdf_link, heading, category, date_folder_pdfs_path, log_file_path, extract_date_from_folder(year_folder, month_folder, date_folder))

                extracted_row = {
                    'HEADING': heading,
                    'ANNOUNCEMENT': row['ANNOUNCEMENT'],
                    'INSIDER': row['INSIDER'],
                    'PDF LINK': pdf_link,
                    'CATEGORY': category,
                    'Extracted Data': clean_text(extracted_text),
                    'Date': extract_date_from_folder(year_folder, month_folder, date_folder),
                    'flag': 1  
                }
                extracted_rows.append(extracted_row)

            if extracted_rows:
                update_csv_with_extracted_data(csv_file_path, extracted_rows)


def update_csv_with_extracted_data(csv_file, extracted_data):
    new_csv_file = os.path.splitext(csv_file)[0] + '_extracted.csv'
    file_exists = os.path.isfile(new_csv_file)
    with open(new_csv_file, mode='a' if file_exists else 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=extracted_data[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(extracted_data)
    print(f"Text extracted from PDFs and saved in '{new_csv_file}'.")



def process_csv_files(input_path, log_file_path):

    yesterday = datetime.now()
    # day = '04-10-2024'
    # yesterday = datetime.strptime(day, '%d-%m-%Y')
    year_str = yesterday.strftime('%Y')
    month_str = yesterday.strftime('%m')
    day_str = yesterday.strftime('%d')

    year_folder_path = os.path.join(input_path, year_str)
    if os.path.isdir(year_folder_path):
        # print(f"Found year folder: {year_str}")
        month_folder_path = os.path.join(year_folder_path, month_str)
        if os.path.isdir(month_folder_path):
            # print(f"Found month folder: {month_str}")
            date_folder_path = os.path.join(month_folder_path, day_str)
            if os.path.isdir(date_folder_path):
                # print(f"Processing date folder: {day_str}")
                process_csv_file(date_folder_path, date_folder_path, year_str, month_str, day_str, log_file_path)
            else:
                print(f"Date folder '{day_str}' does not exist.")
        else:
            print(f"Month folder '{month_str}' does not exist.")
    else:
        print(f"Year folder '{year_str}' does not exist.")

def main(input_path):
    log_file_path = os.path.join(input_path, "Scheme_extraction_errors_log.csv")
    process_csv_files(input_path, log_file_path)

if __name__ == "__main__":
    input_path = r'D:\Output\BSE DATA' 
    main(input_path)