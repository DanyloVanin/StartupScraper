import time
import json
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm

VERBOSE = False


def standardize_employees(employees_value):
    if employees_value == "Not available":
        return "Not available"

    # Extract the numeric value using regular expression
    match = re.match(r'(\d+)', employees_value)

    if match:
        return int(match.group())
    else:
        return "Not available"



def initialize_driver():
    chrome_options = Options()
    chrome_options.headless = True
    return webdriver.Chrome(options=chrome_options)


def find_element(soup, tag, text):
    element = soup.find(tag, string=text)
    if element:
        return element.find_next('dd').text.strip()
    else:
        return ""


def scrape_key_people(soup):
    key_people_data = []

    # Find the Key People section
    key_people = soup.find('h2', string='Key People')
    if not key_people:
        return key_people_data

    key_people_section = key_people.find_next('ul', class_='CompanyKeyPeopleStyled__List-sc-1jnz2wn-0')

    # Extract information for each key person
    for person in key_people_section.find_all('li', class_='CompanyKeyPeopleStyled__ListItem-sc-1jnz2wn-1'):
        name = \
            person.find('h1', class_='CompanyKeyPeopleStyled__ExecutiveNameAndTitle-sc-1jnz2wn-6').text.strip().split(
                ',')[
                0]
        position = person.find('span', class_='CompanyKeyPeopleStyled__ExecutiveTitle-sc-1jnz2wn-7').text.strip()

        # Extract LinkedIn URL
        linkedin_element = person.find('a', class_='SocialLinksStyled__Link-sc-mf1kmu-2', href=True)
        linkedin = linkedin_element['href'] if linkedin_element else "Not available"

        # Display key people details
        if VERBOSE:
            print(f"\nName: {name}")
            print(f"Position: {position}")
            print(f"LinkedIn: {linkedin}")

        key_people_data.append({
            "Name": name,
            "Position": position,
            "LinkedIn": linkedin
        })

    return key_people_data


def scrape_financial_metrics(soup):
    financial_metrics_data = []

    # Find the financial metrics section
    financial_metrics_section = soup.find('div', class_='CompanyMetricsStyled__List-sc-kk31ed-4')

    # Extract information for each financial metric
    for metric_box in financial_metrics_section.find_all('div', class_='MetricBoxStyled__Wrapper-sc-wp122h-0'):
        title = metric_box.find('p', class_='MetricBoxStyled__Title-sc-wp122h-1').text.strip()
        value = metric_box.find('div', class_='MetricBoxStyled__Value-sc-wp122h-2').text.strip()
        description = metric_box.find('p', class_='MetricBoxStyled__Description-sc-wp122h-3').text.strip()

        # Display financial metrics details
        if VERBOSE:
            print(f"\n{title}: {value}")
            print(f"Date: {description}")

        financial_metrics_data.append({
            "Title": title,
            "Value": value,
            "Date": description
        })

    return financial_metrics_data


def scrape_company_info(soup):
    # Extract relevant information with error handling
    overview = find_element(soup, 'dt', 'Overview')
    company_type = find_element(soup, 'dt', 'Type')
    status = find_element(soup, 'dt', 'Status')
    foundation_year = find_element(soup, 'dt', 'Founded')
    headquarters = find_element(soup, 'dt', 'HQ').rstrip("| view all locations")

    website_element = find_element(soup, 'dt', 'Website')

    # Extracting sectors
    sectors_element = soup.find('dt', string='Sectors')
    if not sectors_element:
        sectors = []
    else:
        sectors_element = sectors_element.find_next('dd')
        sectors = [tag.text.strip() for tag in
                   sectors_element.find_all('li')] if sectors_element != "Not available" else []

    # Display the extracted information
    if VERBOSE:
        print(f"Overview: {overview}")
        print(f"Type: {company_type}")
        print(f"Status: {status}")
        print(f"Foundation Year: {foundation_year}")
        print(f"HQ: {headquarters}")
        print(f"Website: {website_element}")
        print(f"Sectors: {' ; '.join(sectors)}")

    # Extract key people details
    key_people_data = scrape_key_people(soup)

    # Extract financial metrics details
    financial_metrics_data = scrape_financial_metrics(soup)

    # Create a dictionary to store all the data
    company_data = {
        "Overview": overview,
        "Type": company_type,
        "Status": status,
        "FoundationYear": foundation_year,
        "HQ": headquarters,
        "Website": website_element,
        "Sectors": sectors,
        "KeyPeople": key_people_data,
        "FinancialMetrics": financial_metrics_data
    }

    return company_data


def scrape_and_save_company_info(driver, company):
    try:
        link = company.get('Link')
        if link:
            # Load the webpage
            driver.get(link)

            # Wait for dynamic content to load (you may need to adjust the sleep time)
            driver.implicitly_wait(5)

            # Get the page source after JavaScript execution
            page_source = driver.page_source

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')

            # Scrape company info
            company_data = scrape_company_info(soup)

            # Add the company name and the scraper link to the dictionary
            company_data["Scraper Link"] = link
            company_data["Company Name"] = company["Company Name"]
            company_data["Employees"] = standardize_employees(company["Employees"])
            company_data["Description"] = company["Description"]

            # Replace dots with underscores in the company name for the output file
            company_name_cleaned = company["Company Name"].replace(".", "_").replace(" ", "_").lower()

            # Save data to a separate JSON file
            output_file = f'company_data_with_names/{company_name_cleaned}_data.json'
            with open(output_file, 'w', encoding='utf-8') as json_file:
                json.dump(company_data, json_file, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Error scraping company: {company['Company Name']} ({company.get('Link')})")
        print(f"Error message: {str(e)}")


def main():
    # Replace 'input_file.json' with the actual name of your input JSON file
    input_file = 'companies_data_20231117_195834.json'

    with open(input_file, 'r', encoding='utf-8') as json_file:
        companies = json.load(json_file)

    # Create a WebDriver instance
    driver = initialize_driver()

    try:
        # Use tqdm for a progress bar
        for company in tqdm(companies, desc="Scraping Companies"):
            scrape_and_save_company_info(driver, company)
            # time.sleep(1)  # Add a delay to avoid potential issues with rapid scraping
    finally:
        # Close the WebDriver after scraping all URLs
        driver.quit()


if __name__ == "__main__":
    main()
