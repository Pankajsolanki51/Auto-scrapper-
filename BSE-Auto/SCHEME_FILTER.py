
import os
import pandas as pd
import re
import warnings
import smtplib
from datetime import datetime, timedelta
from twilio.rest import Client
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

warnings.filterwarnings("ignore")
current_time = datetime.now().time()

# Function to read last processed time
def read_last_processed_time(output_dir, target_date):
    tracking_file = os.path.join(output_dir, f"last_processed_time_{target_date}.txt")
    if os.path.isfile(tracking_file):
        with open(tracking_file, 'r') as file:
            last_time = file.read().strip()
            if last_time:
                return last_time
    return None

# Function to update last processed time
def update_last_processed_time(output_dir, target_date, last_time):
    tracking_file = os.path.join(output_dir, f"last_processed_time_{target_date}.txt")
    with open(tracking_file, 'w') as file:
        file.write(last_time if last_time else "No valid last time found")

# Function to make a call via Twilio
def notify_via_call(message):
    account_sid = os.getenv('ACCOUNT_SID')
    auth_token = os.getenv('AUTH_TOKEN')
    from_phone = os.getenv('FROM_PHONE')
    to_phone = os.getenv('TO_PHONE')

    client = Client(account_sid, auth_token)
    call = client.calls.create(
        twiml=f'<Response><Say>{message}</Say></Response>',
        from_=from_phone,
        to=to_phone
    )
    print(f"Call initiated with SID: {call.sid}")

# Function to send email with attachment
def send_email_with_attachment(subject, body, to_email, attachment_path):
    from_email = os.getenv('SENDER_EMAIL')
    from_password = os.getenv('EMAIL_APP_PASSWORD')

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, from_password)

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with open(attachment_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
        msg.attach(part)

    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()
    print("Email sent successfully.")

def search_in_specific_csv(input_root_dir, output_dir, company_names, target_date, previous_announcements_file):
    extracted_data = []
    extracted_file_pattern = re.compile(r'^\d{8}_\d{8}_extracted\.csv$')
    keywords_pattern = r'(Scheme Of Arrangement)'

    try:
        year_folder, month_folder, day_folder = target_date.split('-')
    except ValueError:
        print("Invalid date format. Please provide the date in YYYY-MM-DD format.")
        return

    date_path = os.path.join(input_root_dir, year_folder, month_folder, day_folder)

    if not os.path.isdir(date_path):
        print(f"Date folder '{date_path}' does not exist.")
        return

    csv_file_path = None
    for file_name in os.listdir(date_path):
        if extracted_file_pattern.match(file_name):
            csv_file_path = os.path.join(date_path, file_name)
            break

    if not csv_file_path:
        print(f"No matching extracted CSV file found for date '{target_date}'.")
        return

    last_processed_time = read_last_processed_time(output_dir, target_date)

    try:
        if os.stat(csv_file_path).st_size == 0:
            print(f"The file '{csv_file_path}' is empty.")
            return  

        df = pd.read_csv(csv_file_path)

        if 'HEADING' not in df.columns or 'ANNOUNCEMENT' not in df.columns or 'Extracted Data' not in df.columns:
            print(f"The required columns are missing in '{csv_file_path}'.")
            return

        df['Extracted Time'] = df['INSIDER'].str.extract(r'(\d{2}:\d{2}:\d{2})', expand=False)
        df = df.sort_values('Extracted Time', ascending=False)

        if last_processed_time:
            df = df[df['Extracted Time'].notna() & (df['Extracted Time'] > last_processed_time)]

        if df.empty:
            print(f"No new data to process since the last run on '{target_date}'.")
            return

        highest_time_in_batch = df['Extracted Time'].iloc[0]
        update_last_processed_time(output_dir, target_date, highest_time_in_batch)

        previous_announcements_df = pd.read_csv(previous_announcements_file)
        previous_announcements_df['Date'] = pd.to_datetime(previous_announcements_df['Date'])
        six_months_ago = datetime.now() - timedelta(days=180)
        previous_announcements_df['Company'] = previous_announcements_df['Company'].str.lower()

        for company_name in company_names:
            
            filtered_df = df[df['HEADING'].str.contains(company_name, case=False, na=False)]
            

            filtered_df = filtered_df[
                filtered_df['HEADING'].str.contains(keywords_pattern, case=False, na=False) |
                filtered_df['ANNOUNCEMENT'].str.contains(keywords_pattern, case=False, na=False) |
                filtered_df['Extracted Data'].str.contains(keywords_pattern, case=False, na=False)
            ]

            if not filtered_df.empty:
                filtered_df['Time'] = filtered_df['INSIDER'].str.extract(r'(\d{2}:\d{2}:\d{2})', expand=False)
                final_df = filtered_df[['HEADING', 'PDF LINK', 'Time']].copy()
                final_df['Word'] = 'Scheme Of Arrangement'
                final_df['Date'] = target_date
                extracted_data.append(final_df)

                recent_entry = previous_announcements_df[
                    (previous_announcements_df['Company'] == company_name) & 
                    (previous_announcements_df['Date'] >= six_months_ago)
                ]

                if recent_entry.empty and current_time.hour < 20:
                    notify_via_call(f"Keyword 'Scheme Of Arrangement' found for {company_name} on {target_date}.")
                else:
                    print(f"Skipping call/SMS for {company_name} as it's after 8 PM or announcement is recent.")

        if extracted_data:
            combined_df = pd.concat(extracted_data, ignore_index=True)
            scheme_dir = os.path.join(output_dir, "SCHEME_OF_ARRANGEMENT")
            os.makedirs(scheme_dir, exist_ok=True)
            output_file = os.path.join(scheme_dir, "scheme_of_arrangement.csv")

            if os.path.exists(output_file):
                combined_df.to_csv(output_file, mode='a', header=False, index=False)
            else:
                combined_df.to_csv(output_file, index=False)

            print(f"Data successfully extracted and saved to '{output_file}'.")

            # Send the email with the CSV attachment regardless of the time
            send_email_with_attachment(
                subject="Keyword Found: Scheme Of Arrangement",
                body=f"Data file for the keyword 'Scheme Of Arrangement' is attached.",
                to_email=os.getenv('TO_EMAIL'),  # Replace with actual recipient email
                attachment_path=output_file
            )
        else:
            print(f"No relevant data found for any company on {target_date}.")

    except pd.errors.EmptyDataError:
        print(f"Encountered an empty data error while processing '{csv_file_path}'.")
    except Exception as e:
        print(f"Error processing file {csv_file_path}: {e}")

# Paths and execution
input_root_dir = r"D:\Output\BSE DATA"
output_dir = r"D:\Output"
company_names_file = r"D:\CODES\BSE_AUTO\Companies_F&O.csv"
previous_announcements_file = r"D:\CODES\BSE_AUTO\last_announcements.csv"

company_names_df = pd.read_csv(company_names_file)

if 'Companies' in company_names_df.columns:
    company_names = company_names_df['Companies'].tolist()
    target_date = datetime.today().strftime('%Y-%m-%d')
    search_in_specific_csv(input_root_dir, output_dir, company_names, target_date, previous_announcements_file)
else:
    print("Column 'Companies' not found in the CSV file.")
