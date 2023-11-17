import time
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


def find_element(soup, tag, text):
    element = soup.find(tag, string=text)
    if element:
        return element.find_next('dd').text.strip()
    else:
        return "Not available"


def scrape_key_people(soup):
    key_people_data = []

    # Find the Key People section
    key_people_section = soup.find('h2', string='Key People').find_next('ul', class_='CompanyKeyPeopleStyled__List-sc-1jnz2wn-0')

    # Extract information for each key person
    for person in key_people_section.find_all('li', class_='CompanyKeyPeopleStyled__ListItem-sc-1jnz2wn-1'):
        name = person.find('h1', class_='CompanyKeyPeopleStyled__ExecutiveNameAndTitle-sc-1jnz2wn-6').text.strip().split(',')[0]
        position = person.find('span', class_='CompanyKeyPeopleStyled__ExecutiveTitle-sc-1jnz2wn-7').text.strip()

        # Extract LinkedIn URL
        linkedin_element = person.find('a', class_='SocialLinksStyled__Link-sc-mf1kmu-2', href=True)
        linkedin = linkedin_element['href'] if linkedin_element else "Not available"

        # Display key people details
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
        print(f"\n{title}: {value}")
        print(f"Date: {description}")

        financial_metrics_data.append({
            "Title": title,
            "Value": value,
            "Date": description
        })

    return financial_metrics_data


def scrape_company_info(url):
    # Set up Selenium options to run headless (without a visible browser)
    chrome_options = Options()
    chrome_options.headless = True
    # Create a WebDriver instance
    driver = webdriver.Chrome(options=chrome_options)

    # Load the webpage
    driver.get(url)

    # Wait for dynamic content to load (you may need to adjust the sleep time)
    driver.implicitly_wait(10)

    # Get the page source after JavaScript execution
    page_source = driver.page_source

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Extract relevant information with error handling
    overview = find_element(soup, 'dt', 'Overview')
    company_type = find_element(soup, 'dt', 'Type')
    status = find_element(soup, 'dt', 'Status')
    foundation_year = find_element(soup, 'dt', 'Founded')
    headquarters = find_element(soup, 'dt', 'HQ').rstrip("| view all locations")

    website_element = find_element(soup, 'dt', 'Website')

    # Extracting sectors
    sectors_element = soup.find('dt', string='Sectors')
    sectors_element = sectors_element.find_next('dd')
    sectors = [tag.text.strip() for tag in sectors_element.find_all('li')] if sectors_element != "Not available" else []

    # Display the extracted information
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

    # Save data to JSON file
    with open('company_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(company_data, json_file, ensure_ascii=False, indent=2)

    # Close the WebDriver
    driver.quit()


# Replace 'your_website_url' with the actual URL of the webpage
scrape_company_info('https://craft.co/deltatrainer')
