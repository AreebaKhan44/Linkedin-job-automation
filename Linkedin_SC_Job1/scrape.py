from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
import time
import traceback
import json
import random

# LinkedIn credentials
# Load credentials from JSON file
with open('credentials.json') as f:
    credentials = json.load(f)

# Retrieve LinkedIn credentials from the JSON data
username = credentials.get('linkedin_username')
password = credentials.get('linkedin_password')

chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

if not (username and password):
    print("Error: LinkedIn credentials not found in the JSON file.")
    exit(1)

# Path to the ChromeDriver executable
chromedriver_path = r'chromedriver.exe'

# Initialize the Chrome driver
service = ChromeService(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open LinkedIn login page
driver.get('https://www.linkedin.com/login')

# Log in
email_elem = driver.find_element(By.ID, 'username')
email_elem.send_keys(username)
password_elem = driver.find_element(By.ID, 'password')
password_elem.send_keys(password)
password_elem.send_keys(Keys.RETURN)

# Allow some time for the login process to complete
time.sleep(7)

# Navigate to your connections page
driver.get('https://www.linkedin.com/mynetwork/catch-up/all/')

# Wait for the connections to load
try:
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'nurture-cards-list__item')))
    print("Connections page loaded.")
except TimeoutException:
    print("Timeout while waiting for the connections page to load.")
    driver.quit()
    exit()

# List to store visited profile URLs
visited_profiles = []

# Define a function to handle the click and navigation
def click_profiles_and_navigate_back():
    while True:
        try:
            # Find all connection items
            connection_items = driver.find_elements(By.CLASS_NAME, 'nurture-cards-list__item')
            # If no connection items are found, break the loop
            if not connection_items:
                break
            
            # Iterate over connections in chunks of 8
            for start in range(0, len(connection_items), 8):
                for index in range(start, min(start + 8, len(connection_items))):
                    try:
                        # Re-find the connection items before each click to avoid stale element reference issues
                        connection_items = driver.find_elements(By.CLASS_NAME, 'nurture-cards-list__item')
                        connection_item = connection_items[index]

                        # Skip items with the 'nurture-cards-list__item--divider' class
                        if 'nurture-cards-list__item--divider' in connection_item.get_attribute('class'):
                            continue
                        
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'nurture-cards-list__item')))
                        
                        print("Element text:", connection_item.text)
                        
                        # Locate the profile picture
                        profile_picture = connection_item.find_element(By.CLASS_NAME, 'presence-entity__image')
                        
                        # Click on the profile picture
                        profile_picture.click()
                        print("Clicked on Profile Picture")
                        try:
                            bell_icon_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CLASS_NAME, 'profile-top-card__subscribe-button'))
                            )
                            bell_icon_button.click()
                            print("Clicked on Bell Icon Button")
                            
                            # Wait for the modal to appear and click the "Save" button
                            try:
                                save_button = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Save']]"))
                                )
                                save_button.click()
                                print("Clicked on Save Button in Modal")
                            except TimeoutException:
                                print("Save Button not found in modal. Skipping...")
                            
                        except TimeoutException:
                            print("Bell Icon Button not found. Skipping...")
                        
                        # For demonstration, let's print the URL of the profile page
                        print("Profile URL:", driver.current_url)
                        
                        # Add the profile URL to the visited profiles list
                        visited_profiles.append(driver.current_url)
                        
                        # Go back to the previous page
                        driver.back()
                        print("Went back to Connection List Page")
                        
                        time.sleep(15)  # Increased sleep time to allow for page load
                    
                    except StaleElementReferenceException:
                        # If a stale element reference exception occurs, re-find the elements and retry the action
                        print("Stale element reference exception occurred. Retrying...")
                        traceback.print_exc()
                        break  # Break the inner loop to retry from the outer loop

                    except NoSuchElementException:
                        # Handle the case where an element is not found
                        print("No such element exception occurred. Skipping...")
                        traceback.print_exc()
                        continue  # Continue to the next iteration to skip the current element

                    except Exception as e:
                        traceback.print_exc()
                        print("Error:", e)
                        continue  # Continue to the next iteration to skip the current element in case of other exceptions
                
                # After processing 8 profiles, scroll down to load more profiles
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                time.sleep(15)  # Increased sleep time 
                         
        except Exception as e:
            traceback.print_exc()
            print("Error:", e)
            break  # Break the loop in case of unexpected exceptions

# Call the function to click profiles and navigate back
click_profiles_and_navigate_back()

# Close the WebDriver
driver.quit()

# Save the visited profiles to a JSON file
with open('visited_profiles.json', 'w') as f:
    json.dump(visited_profiles, f)

print("Script completed.")
