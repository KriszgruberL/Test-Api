import json

from utils.fill_detail_gemini import ResumeGemini
from utils.scrap_yesterday_events import YesterdayEventsScraper


def main() :
    scraper = YesterdayEventsScraper()
    scraped_data = scraper.get_yesterday_events()
    if scraped_data:
        scraper.save_json(scraped_data)
        print("Yesterday's events have been saved to 'data/yesterday_events.json'")
    else:
        print("No data to save.")


    # Note Gemini doesn't allow the resume of subject it find violent or something. Like the news you know
    # So the code is working but not working
    gemini = ResumeGemini()
    gemini.get_data()
    ai_responses = gemini.ask_gemini()

    if ai_responses:
        # Save to a JSON file
        with open("ai_responses.json", "w", encoding='utf-8') as outfile:
            json.dump(ai_responses, outfile, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()