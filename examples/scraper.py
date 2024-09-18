import json

from bs4 import BeautifulSoup as bs
from webrider_async import WebRiderAsync


# Initialize WebRiderAsync with random user agents enabled
webrider = WebRiderAsync(random_user_agents=True, file_output=True)

# Whole settings example
# webrider = WebRiderAsync(
#     log_level = 'debug',
#     file_output = False,
#
#     random_user_agents = False,
#     custom_user_agent = None,
#     custom_headers = None,
#     custom_proxies = None,
#
#     concurrent_requests = 20,
#     delay_per_chunk = 0,
#
#     max_retries = 2,
#     delay_before_retry = 1,
#
#     max_wait_for_resp = 15
# )


def start_scraper():
    start_url = 'https://www.vuokraovi.com/vuokra-asunnot'

    # Phase 1: getting pagination pages
    response = webrider.request(start_url)  # request() returns list of responses
    soup = bs(response[0].html, 'html.parser')  # Taking response[0] since we gave only one url to request()

    final_page = soup.select('ul.pagination > li:nth-of-type(8) > a')[0].getText()  # Extracting number of last page
    pagination_pages = [
        f'https://www.vuokraovi.com/vuokra-asunnot?page={str(number)}&pageType='
        for number in range(1, int(final_page) + 1)
    ]  # Creating list of all 2000k pagination pages

    pagination_pages = pagination_pages[:5]   # Limit list of urls in demo purposes

    # Phase 2: getting product pages from pagination urls
    real_estate_urls = []
    pagination_pages_chunks = webrider.chunkify(pagination_pages, 10)  # Explained in Best practices (README.md)
    for urls_chunk in pagination_pages_chunks:
        real_estate_urls += get_pagination(urls_chunk)  # Parsing chunks of 10 pages simultaneously

    real_estate_urls = real_estate_urls[:30]  # Limit list of urls in demo purposes

    # Phase 3: getting product data
    data = []
    real_estate_urls_chunks = webrider.chunkify(real_estate_urls, 10)  # Explained in Best practices (README.md)
    for urls_chunk in real_estate_urls_chunks:
        data.append(get_content(urls_chunk))  # Parsing chunks of 10 pages simultaneously

    webrider.stats()  # Checking stats

    # Save scraped data
    file_path = "data.json"
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    # Function to reset settings if needed to use class for another scraper without initialization
    webrider.update_settings(
        random_user_agents = False,
    )
    webrider.reset_stats()  # Reset stats


def get_pagination(urls):
    responses = webrider.request(urls)  # Make requests to get pagination URLs
    real_estate_urls = []

    for response in responses:
        soup = bs(response.html, 'html.parser')  # Parse each response HTML

        # Extract real estate URLs from the page
        urls = soup.select('div.list-item-container > div.row.top-row > a')
        urls = [url.get('href') for url in urls if url.get('href')]
        urls = ['https://www.vuokraovi.com' + item for item in urls]

        real_estate_urls += urls  # Append the URLs to the list

    return real_estate_urls


def get_content(urls):
    responses = webrider.request(urls)  # Make requests to get content from real estate URLs
    data = []

    for response in responses:
        soup = bs(response.html, 'html.parser')  # Parse each response HTML

        # Extract description from the page
        description = soup.select('div.item-heading > h1')[0].getText()

        # Append the description and URL to the data list
        data.append(
            {
                'description': description,
                'url': response.url,
            }
        )

    return data


if __name__ == "__main__":
    start_scraper()
