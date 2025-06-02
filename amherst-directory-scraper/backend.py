import requests
import time
from cookies import fetch_cookies
from utils import save_to_csv, get_resource_path

# Fetch cookies and CSRF token
def fetch_session_with_cookies(username, password):
    csrf_token, cookies = fetch_cookies(username, password)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "X-CSRF-TOKEN": csrf_token
    }
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    return session, headers

# Scrape data for individual person
def scrape_person_page(session, id, headers):
    base_url = 'https://alumni.engage.amherst.edu/api/alumni_profile/'
    query_string = "?profile=profile&section=Personal"
    modified_url = f"{base_url}{id}{query_string}"
    person_data = {}
    
    try:
        response = session.get(modified_url, headers=headers)
        print(f"Individual's ID: {id} || Status Code: {response.status_code}")
        data = response.json()['data']['profile']['contact_info']
        person_data['email'] = data.get('Email', '')
        person_data['mobile_phone'] = data.get('CellPhone', '')
        person_data['addresses'] = data.get('Addresses', '')
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    
    return person_data

# Make a POST request to search alumni
def search_alumni(session, headers, payload):
    base_url = 'https://alumni.engage.amherst.edu/api/alumni_searches'
    response = session.post(base_url, json=payload, headers=headers)
    search_id = response.json()["search_id"]
    url = f"https://alumni.engage.amherst.edu/api/alumni_searches/{search_id}"
    return response, url

# Iterate over search results and scrape person data
def scrape_search_results(session, headers, url, params, delay):
    data_list = []

    while True:
        time.sleep(delay)
        try:
            response = session.get(url, params=params, headers=headers)
            print(f"Response: {response.status_code}, URL: {url}")
            data = response.json()

            for person in data["data"]:
                person_data = scrape_person_page(session, person["ID"], headers)
                person_data['name'] = person["NameClasses"]
                person_data['academics'] = person["academics"]["AmhMajors"]
                data_list.append(person_data)

            # Check for next page
            if not data["data"]:
                break

            params["page"] += 1
            print(f"Next page: {params['page']}")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break

    return data_list

# Main function to orchestrate the scraping process
def main(payload, username, password):
    # Fetch session and headers
    session, headers = fetch_session_with_cookies(username, password)
    params = {
        "result_format": "paginate",
        "page": 1,
        "limit": 50,
        "order_by": "SortNameClasses,asc"
    }

    response, url = search_alumni(session, headers, payload) # Make POST request to search alumni
    data_list = scrape_search_results(session, headers, url, params, delay=10)  # Scrape data from the search results
    return save_to_csv(data_list, get_resource_path('output.csv')) # Save the data to CSV
