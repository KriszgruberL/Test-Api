import json
import time  # Import the time module
import google.generativeai as genai
import env_var

class ResumeGemini:
    def __init__(self):
        genai.configure(api_key=env_var.API_KEY)
        self.model = genai.GenerativeModel("gemini-pro")
        self.data = None

    def get_data(self):
        try:
            with open("../data/yesterday_events.json") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            print("Data file not found.")
        except json.JSONDecodeError:
            print("Error decoding JSON data.")

    def ask_gemini(self):
        if not self.data:
            print("No data to process. Call get_data() first.")
            return

        ai_responses = {}

        for theme in self.data.values():
            for theme_item in theme['Themes']:
                theme_name = theme_item['Theme']  # Define theme_name
                for sub_theme in theme_item['Sub-Themes']:
                    sub_theme_name = sub_theme['Sub-Theme']  # Define sub_theme_name
                    for headline in sub_theme['Headlines']:
                        event_headline = headline['Headline']
                        event_details = headline['Details'].strip()

                        # Combine headline and details for the prompt
                        if event_details:
                            event_text = f"{event_headline}. {event_details}"
                        else:
                            event_text = event_headline

                        # Generate the summary using the AI model
                        prompt = f"Translate in french the following event: '{event_text}' and {event_details}."
                        try:
                            response = self.model.generate_content(prompt)

                            # Check if the response contains valid candidates
                            if response.candidates and response.candidates[0].content:
                                summary = response.candidates[0].content
                            else:
                                # Handle the case where content is filtered
                                print(f"Content filtered for event: '{event_headline}'")
                                summary = "Content not available due to safety policies."
                                # Optional: Log safety ratings
                                safety_ratings = response.candidates[0].safety_ratings
                                print(f"Safety ratings: {safety_ratings}")

                        except Exception as e:
                            print(f"Error generating summary for '{event_headline}': {e}")
                            summary = None

                        ai_responses.setdefault(theme_name, {}).setdefault(sub_theme_name, {})[event_headline] = summary
                        time.sleep(2)  # Sleep after each API call

        return ai_responses  # Return after processing all data

if __name__ == "__main__":
    f = ResumeGemini()
    f.get_data()
    ai_responses = f.ask_gemini()

    if ai_responses:
        # Save to a JSON file
        with open("ai_responses.json", "w", encoding='utf-8') as outfile:
            json.dump(ai_responses, outfile, indent=4, ensure_ascii=False)

        # Or print the responses
        import pprint
        pprint.pprint(ai_responses)
