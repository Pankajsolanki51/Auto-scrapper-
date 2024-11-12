import os
import time
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta


def init_webdriver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    return webdriver.Chrome(service=service, options=options)


def select_date(driver, input_element, date):
    input_element.click()
    day, month, year = date.split("-")
    year_dropdown = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "ui-datepicker-year"))
    )
    year_dropdown.click()
    year_option = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f"//option[@value='{year}']"))
    )
    year_option.click()
    month_dropdown = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "ui-datepicker-month"))
    )
    month_dropdown.click()
    month_option = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f"//option[@value='{int(month) - 1}']"))
    )
    month_option.click()
    day_option = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f"//a[text()='{int(day)}']"))
    )
    day_option.click()


def scrape_page(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    announcements = []
    rows = soup.select('table[ng-repeat="cann in CorpannData.Table"]')

    for row in rows:
        heading = row.select_one('span[ng-bind-html="cann.NEWSSUB"]').get_text(
            strip=True
        )
        announcement = row.select_one(
            'div[id^="more"] span[ng-bind-html="cann.HEADLINE"]'
        ).get_text(strip=True)
        pdf_link_tag = row.select_one('a.tablebluelink[href$=".pdf"]')  #
        if pdf_link_tag:
            pdf_link = "https://www.bseindia.com" + pdf_link_tag["href"]
        else:
            pdf_link = None
        times = row.select('tr[ng-if="cann.TimeDiff"] td b')
        insider_info = ""
        if times:
            insider_info = (
                times[0].get_text(strip=True) + " " + times[1].get_text(strip=True)
            )

        category_tag = row.select_one(
            "td.tdcolumngrey[ng-if=\"cann.CATEGORYNAME != 'NULL' \"]"
        )
        category = category_tag.get_text(strip=True) if category_tag else "N/A"

        announcements.append(
            {
                "HEADING": heading,
                "ANNOUNCEMENT": announcement,
                "INSIDER": insider_info,
                "PDF LINK": pdf_link,
                "CATEGORY": category,
            }
        )

    return announcements


def handle_alert(driver):
    try:
        WebDriverWait(driver, 6).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()

    except TimeoutException:
        pass


def create_folder_structure(base_path, date):
    day, month, year = date.split("-")
    year_folder = os.path.join(base_path, year)
    month_folder = os.path.join(year_folder, month)
    day_folder = os.path.join(month_folder, day)

    if not os.path.exists(year_folder):
        os.makedirs(year_folder)
    if not os.path.exists(month_folder):
        os.makedirs(month_folder)
    if not os.path.exists(day_folder):
        os.makedirs(day_folder)

    return day_folder


def sanitize_filename(name, keep_spaces=False):
    if keep_spaces:
        return "".join([c if c.isalnum() or c.isspace() else "_" for c in name])
    else:
        return "".join([c if c.isalnum() else "_" for c in name])


def get_last_scraped_time(file_path):
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            if not df.empty:

                last_time_str = df["INSIDER"].dropna().str.strip().max()

                last_time_str = (
                    last_time_str.split()[0] + " " + last_time_str.split()[1]
                )

                last_time = datetime.strptime(last_time_str, "%d-%m-%Y %H:%M:%S")
                return last_time
    except Exception as e:
        print(f"Error reading last scraped time: {e}")
    return None

def scrape_data(target_date, output_path):
    print(f"Starting scrape for date: {target_date}")

    day_folder = create_folder_structure(output_path, target_date)
    date_str = target_date.replace("-", "")
    file_name = f"{date_str}_{date_str}.csv"
    file_path = os.path.join(day_folder, file_name)

    last_scraped_time = get_last_scraped_time(file_path)

    driver = init_webdriver()
    driver.get("https://www.bseindia.com/corporates/ann.html")
    time.sleep(5)

    from_date_input = driver.find_element(By.ID, "txtFromDt")
    to_date_input = driver.find_element(By.ID, "txtToDt")

    try:
        select_date(driver, from_date_input, target_date)
        select_date(driver, to_date_input, target_date)
    except TimeoutException as e:
        print(f"Timeout error selecting date: {target_date}. Skipping this date.")
        driver.quit()
        return

    search_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "btnSubmit"))
    )
    driver.execute_script("arguments[0].scrollIntoView();", search_button)
    time.sleep(1)  # Optional sleep
    search_button.click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "tr")))

    all_announcements = []
    page = 1
    while True:
        new_data = scrape_page(driver)
        if last_scraped_time:

            new_data = [
                item
                for item in new_data
                if "INSIDER" in item
                and len(item["INSIDER"].split()) >= 2
                and datetime.strptime(
                    item["INSIDER"].split()[0] + " " + item["INSIDER"].split()[1],
                    "%d-%m-%Y %H:%M:%S",
                )
                > last_scraped_time
            ]

        all_announcements.extend(new_data)
        print(f"Scraping page {page} for date: {target_date}")

        if not new_data:
            break

        try:
            next_button = driver.find_element(By.ID, "idnext")
            if "disabled" in next_button.get_attribute("class"):
                break
            next_button.click()
            time.sleep(7)
        except Exception as e:
            print(f"An error occurred: {e}")
            break
        page += 1

    if all_announcements:
        new_data_df = pd.DataFrame(all_announcements)
        if os.path.exists(file_path):

            existing_data_df = pd.read_csv(file_path)
            combined_df = pd.concat([new_data_df, existing_data_df], ignore_index=True)
            combined_df.to_csv(file_path, index=False)
        else:

            new_data_df.to_csv(file_path, index=False)
        print(f"Data for date: {target_date} has been saved to '{file_path}'")
    else:
        print(f"No new data found for date: {target_date}")

    driver.quit()


def download_pdf(pdf_url, download_folder, heading, category):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(pdf_url, headers=headers)
    if response.status_code == 200:
        first_word = sanitize_filename(heading.split("-")[0])
        category_sanitized = sanitize_filename(category, keep_spaces=True)
        pdf_name = f"{first_word}_{category_sanitized}_{os.path.basename(pdf_url)}"
        pdf_path = os.path.join(download_folder, pdf_name)
        with open(pdf_path, "wb") as f:
            f.write(response.content)
        # print(f"Downloaded PDF: {pdf_path}")
    else:
        print(
            f"Failed to fetch PDF from URL: {pdf_url} with status code: {response.status_code}"
        )


def download_pdfs(output_path, target_date):

    day, month, year = target_date.split("-")
    pdf_folder_path = os.path.join(output_path, year, month, day, "PDFs")
    os.makedirs(pdf_folder_path, exist_ok=True)
    existing_pdfs = {f for f in os.listdir(pdf_folder_path) if f.endswith(".pdf")}
    csv_file_name = f"{day}{month}{year}_{day}{month}{year}.csv"
    csv_file_path = os.path.join(output_path, year, month, day, csv_file_name)
    if not os.path.exists(csv_file_path) or os.stat(csv_file_path).st_size == 0:
        print(
            f"CSV file {csv_file_path} does not exist or is empty. Skipping PDF downloads."
        )
        return

    try:
        df = pd.read_csv(csv_file_path)
    except pd.errors.EmptyDataError:
        print(f"CSV file {csv_file_path} is improperly formatted or empty. Skipping.")
        return

    pdf_links = df[["PDF LINK", "HEADING", "CATEGORY"]].dropna()
    print(f"Downloading PDFs for date: {target_date}")

    for _, row in pdf_links.iterrows():

        pdf_name = f"{sanitize_filename(row['HEADING'].split()[0])}_{sanitize_filename(row['CATEGORY'], keep_spaces=True)}_{os.path.basename(row['PDF LINK'])}"

        if pdf_name in existing_pdfs:
            # print(f"Skipping already downloaded PDF: {pdf_name}")
            continue

        download_pdf(row["PDF LINK"], pdf_folder_path, row["HEADING"], row["CATEGORY"])


if __name__ == "__main__":
    output_path = r"D:\Output\BSE DATA"

    yesterday = datetime.now() - timedelta(days=9)
    target_date = yesterday.strftime("%d-%m-%Y")

    scrape_data(target_date, output_path)
    download_pdfs(output_path, target_date)
