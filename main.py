from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
print("\U0001F600 Welcome to the Quantum Paystub Downloader!, Please follow the instructions below to download your paystubs."
      "it requires your username and password to login to the quantum portal and download the paystubs.\n"
      "Please make sure you have the latest version of firefox installed on your machine."
      "If you have any issues please contact the developer at:")

download_directory = input( "please type out you download dir exmp: C:\\users\\user\\test\\  : ")
username = input("Enter your username: ")
password = input("Enter your password: ")

firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference("pdfjs.disabled", True)  # Disable the built-in PDF viewer
firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")  # Don't prompt for downloading PDFs
firefox_profile.set_preference("browser.download.folderList", 2)  # Use custom download location
firefox_profile.set_preference("browser.download.dir", download_directory)  # Specify your download directory

# Set up Firefox options
options = Options()
options.profile=firefox_profile

# Initialize WebDriver with the configured profile
driver = webdriver.Firefox(options=options)

login_url = 'https://services.quantum.ca/login.aspx?ln=en-CA'

driver.get(login_url)

username_field = driver.find_element(By.ID, 'ctl00_Main_UserNameTextBox')
password_field = driver.find_element(By.ID, 'ctl00_Main_PasswordTextBox')



username_field.send_keys(username)
password_field.send_keys(password)

login_button = driver.find_element(By.ID, 'ctl00_Main_SignInButton')
login_button.click()

try:
    my_paystub_link = driver.find_element(By.ID, 'ctl00_Main_PaystubsLinkButton')
    my_paystub_link.click()
except NoSuchElementException:
    print("My Paystub link not found")
base_id = "ctl00_Main_PaystubsDataList_ctl"
suffix = "_viewPaystub"
date_suffix = "_DepositDateData"  # Assuming the ID pattern for the date

start_index = 1
end_index = 8

def wait_for_downloads(download_dir):
    """
    Waits for all files in the download directory to finish downloading.
    """
    while any([filename.endswith(".part") for filename in os.listdir(download_dir)]):
        time.sleep(1)  # Wait for downloads to finish

def rename_latest_file(download_dir, new_name):
    """
     Renames the most recently downloaded file in the specified directory.
     """
     # List of all files in the download directory
    files = [os.path.join(download_dir, f) for f in os.listdir(download_dir)]
     # Filter out directories, get files only
    files = [f for f in files if os.path.isfile(f)]
     # Get the latest file based on modification time
    latest_file = max(files, key=os.path.getctime)
     # Construct new filename with the same extension
    new_filename = os.path.join(download_dir, new_name + os.path.splitext(latest_file)[-1])
     # Rename the file
    os.rename(latest_file, new_filename)
    print(f"Renamed file to: {new_filename}")
 
while True:
   for i in range(start_index, end_index + 1):
       # Constructing the full ID dynamically
       full_id = f"{base_id}{i:02d}{suffix}"
       date_id = f"{base_id}{i:02d}{date_suffix}"
       
       try:
           WebDriverWait(driver, 10).until(
           EC.presence_of_element_located((By.ID, date_id))
           )
           sleep(10)
           date_element = driver.find_element(By.ID, date_id)
           date_text = date_element.text  # Extracting date text
           print(f"Processing paystub link with ID: {full_id} for date {date_text}")
           # Find the element by its constructed ID
           paystub_link = driver.find_element(By.ID, full_id)
           print(f"Clicking paystub link with ID: {full_id}")      
           # Click the paystub link
           #driver.execute_script("arguments[0].target='_self';", paystub_link)
           original_window = driver.current_window_handle
           paystub_link.click()
           new_window = [window for window in driver.window_handles if window != original_window][0]
           print("click is done ")
           sleep(6)
           driver.switch_to.window(new_window)
           print("switching to new window")
           print_click=driver.find_element(By.ID, 'ctl00_Main_ReportToolbar1_Menu_DXI10_I')
           print("clicking on the print button")
           print_click.click()
           new_file_name = f"paystub_{date_text}"
   # After clicking the download link, wait for the download to finish
           wait_for_downloads(download_directory)
       # Rename the most recently downloaded file
           sleep(10)
           print("going for rename")
           rename_latest_file(download_directory, new_file_name)
           sleep(5)
           print("switching to original window")
           driver.switch_to.window(original_window)

   
   
       except NoSuchElementException:
           print(f"No paystub link found with ID: {full_id}")
           break
   
   
   try:
       print("Looking for the Next button to click.")
       next_button = WebDriverWait(driver, 10).until(
           EC.element_to_be_clickable((By.ID, "ctl00_Main_FooterNavigateNext"))
       )
       next_button.click()
       print("Clicked the Next button.")
       element_of_interest = driver.find_element(By.ID, "ctl00_Main_PaystubsDataList_ctl01_viewPaystub")


       WebDriverWait(driver, 10).until(
           EC.presence_of_element_located((By.ID, f"{base_id}01{date_suffix}"))
       )
   except (TimeoutException, NoSuchElementException) as e:
       print(str(e))
       break  # Exit the loop if the next page cannot be loaded or the next button is not found

    
