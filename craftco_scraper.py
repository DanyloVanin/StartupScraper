from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime


# URL of the webpage containing the companies information
url = 'https://craft.co/search?layout=list&order=size_desc&q=&bsizes%5B0%5D=0&bsizes%5B1%5D=100'
base_url = "https://craft.co"

# Set up the Selenium WebDriver with a headless Chrome browser
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

# Navigate to the webpage
driver.get(url)

# Wait for the page to load (you might need to adjust the wait time)
driver.implicitly_wait(10)

# Assuming the button has text "Load More"


# Define the maximum number of times to click the button
max_clicks = 50


def is_accept_button_present():
    try:
        # Check if the button is present in the DOM
        accept_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "hs-eu-confirmation-button"))
        )
        return accept_button is not None
    except Exception as e:
        print(f"Error checking for accept button: {e}")
        return False


def dismiss_cookie_overlay():
    try:
        # Check if the button is present before trying to click
        if is_accept_button_present():
            # Wait for the button to be clickable
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "hs-eu-confirmation-button"))
            )
            # Click the "Accept" button to dismiss the overlay
            accept_button.click()
    except Exception as e:
        print(f"Error accepting cookie: {e}")


def load_more():
    button_text = "Load More"
    try:
        # Wait for the button to be clickable
        button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[text()='{button_text}']"))
        )
        # Click the button
        button.click()
        # Wait for the page to load (you might want to replace this with a more robust wait)
        time.sleep(2)
    except Exception as e:
        print(f"Error clicking button: {e}")


def remove_modal():
    try:
        # Check if the modal is present in the DOM
        modal = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "leadinModal-3012024"))
        )

        # If the modal is found, execute JavaScript to remove it from the DOM
        if modal:
            driver.execute_script('arguments[0].parentNode.removeChild(arguments[0]);', modal)
    except Exception as e:
        print(f"Error removing modal: {e}")



def click_button_and_elsewhere():
    target_button_text = "Load More"
    try:
        # Wait for the target button to be clickable
        target_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[text()='{target_button_text}']"))
        )

        # Click the target button
        target_button.click()

        # Wait for the page to load (you might want to replace this with a more robust wait)
        time.sleep(5)

        # Click anywhere else on the page (replace the XPath with the appropriate selector)
        other_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='_1z_mZ']"))
        )
        other_element.click()

    except Exception as e:
        print(f"Error clicking button and elsewhere: {e}")


# Click the "Load More" button for the fixed amount of times
for _ in range(max_clicks):
    # Dismiss the cookie confirmation overlay if present
    dismiss_cookie_overlay()

    load_more()

    remove_modal()

    time.sleep(5)

# Get the page source after JavaScript has been executed
page_source = driver.page_source

# Parse the HTML content of the page
soup = BeautifulSoup(page_source, 'html.parser')
total_count = 0

# Find the list of companies
companies_list = soup.find('ul', {'class': '_Ux1X', 'data-testid': 'found-companies-cards'})

# Initialize an empty list to store company dictionaries
companies_data = []

# Check if the list is found
if companies_list:
    # Find all company list items
    company_items = companies_list.find_all('li', class_='_2US_W')

    # Loop through each company item
    for company_item in company_items:
        total_count += 1
        # Extract company information
        company_name = company_item.find('h3', class_='_35_BY').text.strip()
        hq_location_tag = company_item.find('div', string='HQ')

        if hq_location_tag:
            hq_location = hq_location_tag.find_next('div', class_='_22Zfj')
            if hq_location:
                hq_location = hq_location.text.strip()
            else:
                hq_location = "Not available"
        else:
            hq_location = "Not available"

        employees_tag = company_item.find('div', string='Employees')

        if employees_tag:
            employees = employees_tag.find_next('div', class_='_22Zfj')
            if employees:
                employees = employees.text.strip()
            else:
                employees = "Not available"
        else:
            employees = "Not available"

        description = company_item.find('div', class_='_2iVCc').text.strip()
        link = f"{base_url}{company_item.find('a')['href']}"

        # Store the extracted information in a dictionary
        company_data = {
            "Company Name": company_name,
            "HQ Location": hq_location,
            "Employees": employees,
            "Description": description,
            "Link": link
        }

        # Append the dictionary to the list
        companies_data.append(company_data)

        # Print or use the extracted information as needed
        print(f"Company Name: {company_name}")
        print(f"HQ Location: {hq_location}")
        print(f"Employees: {employees}")
        print(f"Description: {description}")
        print(f"Link: {link}")
        print("\n")
else:
    print("Companies list not found on the webpage.")

# Save the list of dictionaries as JSON with the current date and time in the file name
current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
json_file_name = f'companies_data_{current_datetime}.json'
with open(json_file_name, 'w', encoding='utf-8') as json_file:
    json.dump(companies_data, json_file, ensure_ascii=False, indent=4)

print(f"Total companies found: {total_count}")

# Close the WebDriver
driver.quit()
