import requests
from bs4 import BeautifulSoup
import csv
import re

HTML_FILE = "amherst-directory-scraper/Amherst College_ Alumni Directory_ Basic Search.html"

'''This function reads the individual's personal page. The page often has details such
as address, email, and phone number.'''
# Function to scrape individual person page
def scrape_person_page(id):
    # Sample URL: https://alumni.engage.amherst.edu/api/alumni_profile/{id}?profile=profile&section=Personal
    base_url = 'https://alumni.engage.amherst.edu/api/alumni_profile/'
    id = id
    query_string = "?profile=profile&section=Personal"

    # Construct the full URL for the API request
    modified_url = f"{base_url}{id}{query_string}"
    print(f"Individual's URL: {modified_url}")

    headers = parse_headers() # Headers necessary for GET request

    # Constructs the JSON list
    person_data = {
        'email': '',
        'mobile_phone': '',
        'addresses': ''
    }

    try:
        # GET request to json file endpoint
        response = requests.get(modified_url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()['data']['profile']['contact_info']
            person_data['email'] = data.get('Email', '')
            person_data['mobile_phone'] = data.get('CellPhone', '')
            person_data['addresses'] = data.get('Addresses', '')
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    return person_data

'''This function reads the downloaded HTML file, and scrapes through the 
individual names processed on the page. This page often has details such 
as name, year, and major. The page also contains links to access the 
individual's personal information.'''
# Main scraping function
def scrape_main_page(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    data_list = []
    rows = soup.find_all('li', class_='list-group-item')

    for row in rows:
        person = row.find('a')
        if person:
            name = person.get_text(strip=True)
            href = person.get('href')
            id = re.search(r'/profile/(\d+)/', href).group(1)

            # Extract major, if present
            major_text = 'nothing'
            strong_tag = row.find('strong')
            if strong_tag and "Majors:" in strong_tag.get_text():
                major_text = strong_tag.next_sibling.strip()

            print(f'name: {name}, id: {id}, major: {major_text}')

            # Scrape individual person's page
            person_data = scrape_person_page(id)
            person_data['name'] = name
            person_data['major'] = major_text

            data_list.append(person_data)

    return data_list

# Save to CSV
def save_to_csv(data_list, filename):
    keys = data_list[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data_list)


# Turning headers.txt into a Python dictionary
def parse_headers():
    filename = 'amherst-directory-scraper/headers.txt' # Replace with the actual file path for headers
    headers = {}
    with open(filename, 'r') as file:
        for line in file:
            # Strip whitespace and check if the line is not empty
            line = line.strip()
            if line:
                # Split on the first ':', in case the value contains ':'
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()
    return headers

# Example usage
data_list = scrape_main_page(HTML_FILE)
save_to_csv(data_list, 'output.csv')

print("Data successfully saved to 'output.csv'")
