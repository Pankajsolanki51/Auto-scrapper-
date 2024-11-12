import schedule
import time
import subprocess
from datetime import datetime
import logging

log_filename = "D:\\CODES\\BSE_AUTO\\scheme_of_arrangement_log.txt"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def run_scripts():
    # Check if the current time is after 6 PM   
    current_time = datetime.now().time()
    cutoff_time = datetime.strptime("23:55","%H:%M").time()
    if current_time >= cutoff_time:  # 6 PM is 18:00 in 24-hour format
        logging.info("Current time is past 11:55 PM. Stopping scheduled tasks.")
        print("Current time is past 11:55 PM. Stopping scheduled tasks.")
        return False  # Signal to stop the scheduler

    scripts = [
        "D:\\CODES\\BSE_AUTO\\SCRAP_DATA.py", 
        "D:\\CODES\\BSE_AUTO\\TEXT_FROM_PDF.py", 
        "D:\\CODES\\BSE_AUTO\\SCHEME_FILTER.py"
    ]

    for script in scripts:
        try:
            subprocess.run(["python", script], check=True)
            logging.info(f"Executed {script} successfully.")
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to execute {script}: {e}")
            
        
        time.sleep(1)

    return True  # Continue scheduling

def scheduled_task():
    # Run scripts and stop if it returns False
    if not run_scripts():
        logging.info("Exiting scheduler.")
        print("Exiting scheduler.")
        return schedule.CancelJob  # Stops all scheduled jobs

schedule.every(5).minutes.do(scheduled_task)
logging.info("Scheduled task set to run every 5 minutes.")
print("Scheduled task to run every 5 minutes.")

while True:
    schedule.run_pending()
    time.sleep(1)

