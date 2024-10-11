import requests
import json
from bs4 import BeautifulSoup
import re

from utils.utilitarians import get_yesterday


class YesterdayEventsScraper:
    def __init__(self):
        self.url = "https://en.wikipedia.org/wiki/Portal:Current_events"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/91.0.4472.124 Safari/537.36",
            "Referer": f"{self.url}",
        }

    def fetch_html_content(self):
        """Fetches the HTML content from Wikipedia's current events page."""
        page_title = 'Portal:Current events'

        params = {
            'action': 'parse',
            'page': page_title,
            'prop': 'text',
            'format': 'json',
            'formatversion': '2'
        }

        try:
            response = requests.get('https://en.wikipedia.org/w/api.php', params=params, headers=self.headers)
            response.raise_for_status()  # Raise an error for bad status codes
            data = response.json()

            if 'error' in data:
                print(f"Error fetching the page: {data['error']['info']}")
                return None
            else:
                html_content = data['parse']['text']
                return html_content
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching the content: {e}")
            return None


    def get_yesterday_events(self):

        yesterday, date_str = get_yesterday()
        html_content = self.fetch_html_content()

        if html_content is None :
            print("Error fetching the html content")
            return None

        soup = BeautifulSoup(html_content, 'html.parser')
        events = self.extract_events_from_soup(soup, date_str)

        if not events:
            print(f"No events found for {date_str}")
            return None

        # Structure the data
        result = {
            yesterday.strftime('%Y_%B_%d'): {
                'Themes': events
            }
        }

        return result

    def extract_events_from_soup(self, soup, target_date):
        events = []
        event_divs = soup.find_all('div', class_='current-events-main')

        for event_div in event_divs:
            # Extract the date from the div
            date_heading = event_div.find('div', class_='current-events-title')
            if date_heading:
                date_text = date_heading.get_text(strip=True)
                date_text = re.sub(r'\s*\(.*?\)', '', date_text)  # Remove any text in parentheses
                date_text = date_text.strip()
                date_text = date_text.replace('\xa0', ' ')  # Replace non-breaking spaces
            else:
                date_text = ''

            if date_text != target_date:
                continue

            date_entry = []

            content_div = event_div.find('div', class_='current-events-content')
            if not content_div:
                continue

            themes = content_div.find_all('p', recursive=False)

            for theme in themes:
                theme_title = theme.get_text(strip=True)
                theme_entry = {
                    'Theme': theme_title,
                    'Sub-Themes': []
                }

                # The next sibling after <p> is a <ul> containing items
                next_sibling = theme.find_next_sibling()

                while next_sibling and next_sibling.name not in ['ul', 'p']:
                    next_sibling = next_sibling.find_next_sibling()

                if next_sibling and next_sibling.name == 'ul':
                    ul = next_sibling
                    # Process the top-level <li> elements as sub-themes
                    for li in ul.find_all('li', recursive=False):
                        sub_theme = self.process_sub_theme_li(li)
                        if sub_theme:
                            theme_entry['Sub-Themes'].append(sub_theme)

                date_entry.append(theme_entry)

            events = date_entry
            break  # Exit the loop after processing the target date

        return events

    def process_sub_theme_li(self, li):
        sub_theme = {}
        a_tag = li.find('a')
        if a_tag:
            sub_theme_name = a_tag.get_text(strip=True)
        else:
            sub_theme_name = li.get_text(strip=True)

        sub_theme['Sub-Theme'] = sub_theme_name
        sub_theme['Headlines'] = []

        # Check if this <li> contains a nested <ul> (headlines)
        sub_ul = li.find('ul')
        if sub_ul:
            for sub_li in sub_ul.find_all('li', recursive=False):
                headline = self.process_headline_li(sub_li)
                if headline:
                    sub_theme['Headlines'].append(headline)
        else:
            # If there is no sub_ul, the li itself is a headline
            headline = self.process_headline_li(li)
            if headline:
                sub_theme['Headlines'].append(headline)

        return sub_theme

    def process_headline_li(self, li):
        a_tag = li.find('a')
        if a_tag:
            headline_text = a_tag.get_text(strip=True)
        else:
            headline_text = li.get_text(strip=True)

        details = li.get_text(separator=' ', strip=True)
        details = details.replace(headline_text, '',1 ).strip()
        details = self.remove_citation_references(details)

        # Remove any external link references in parentheses
        details = re.sub(r'\(\s*.*?\s*\)', '', details).strip()

        return {
            'Headline': headline_text,
            'Details': details
        }

    def remove_citation_references(self, text):
        return re.sub(r'\[\d+\]', '', text).strip()

    def save_json(self, scraped_data):
        with open("../data/yesterday_events.json", "w", encoding='utf-8') as f:
            json.dump(scraped_data, f, indent=4, ensure_ascii=False)


# Example usage:
if __name__ == "__main__":
    scraper = YesterdayEventsScraper()
    scraped_data = scraper.get_yesterday_events()
    if scraped_data:
        # Save the JSON data to a file
        scraper.save_json(scraped_data)
        print("Yesterday's events have been saved to 'data/yesterday_events.json'")
    else:
        print("No data to save.")
