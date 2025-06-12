import os
from openai import OpenAI
from dotenv import load_dotenv
import re

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def safe_strip(value):
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()

def remove_html_tags(text):
    return re.sub(r'<[^>]+>', '', text)

def summarize_db_results(prompt: str, db_results: list) -> str:
    if not db_results:
        return "No results found."

    # ✅ Use OpenAI only for intro
    intro_prompt = f"""User wants to find resorts based on this request: "{prompt}"

Write a friendly and casual 1-2 sentence introduction without listing specific resort names. Just explain what's coming up (a helpful list of resorts)."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You generate short introductions for resort listings."},
                {"role": "user", "content": intro_prompt}
            ],
            temperature=0.6,
            max_tokens=100,
        )

        # 👇 You can comment these print statements in production
        print("Prompt openai tokens:", response.usage.prompt_tokens)  # type: ignore
        print("Completion tokens:", response.usage.completion_tokens)  # type: ignore
        print("Total tokens:", response.usage.total_tokens)  # type: ignore

        intro_text = safe_strip(response.choices[0].message.content)
    except Exception as e:
        print("❌ OpenAI error:", str(e))
        intro_text = "Here are some great resort options that match what you're looking for!"

    # ✅ Format all entries manually
    entries = []
    for row in db_results:
        try:
            name, location, description_html, price, slug = row
        except ValueError:
            continue

        clean_desc = safe_strip(remove_html_tags(description_html))
        price_str = safe_strip(price) if price is not None else "N/A"
        booking_url = f"https://www.go-koala.com/resort/{slug}"

        entry = f"""{name} ({location})  
- 📍 {location}  
- 🏖 {clean_desc}  
- 💰 Starting at ${price_str} per night  
- 🔗 [Book here]({booking_url})"""

        entries.append(entry)

    entries_text = "\n\n".join(entries)
    final_summary = f"{intro_text}\n\n{entries_text}"
    return final_summary
