import requests
import json

def get_youtube_suggestions(query):
    """Fetches real-time autocomplete suggestions from YouTube."""
    try:
        # This is the actual endpoint YouTube uses for its search bar dropdown
        url = f"http://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q={query}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # The suggestions are in the second item of the list
            return data[1] if len(data) > 1 else []
        return []
    except Exception as e:
        print(f"Error fetching YouTube suggestions: {e}")
        return []

def research_topics():
    print("🔍 Researching trends directly from YouTube Autocomplete...")

    # 1. Finance Long Video Topic
    finance_suggestions = get_youtube_suggestions("how to make money online")
    finance_topic = finance_suggestions[0] if finance_suggestions else "Best Passive Income Ideas"

    # 2. Trending Long Video Topic
    general_suggestions = get_youtube_suggestions("trending topics today")
    general_topic = general_suggestions[0] if general_suggestions else "The Future of AI Technology"

    # 3. Finance Short Topic
    finance_short_suggestions = get_youtube_suggestions("quick money tips")
    finance_short_topic = finance_short_suggestions[0] if finance_short_suggestions else "Save Money Fast"

    # 4. Trending Short Topic
    general_short_suggestions = get_youtube_suggestions("viral life hacks")
    general_short_topic = general_short_suggestions[0] if general_short_suggestions else "Life Hack Everyone Should Know"

    # 5. Curious "What If" Short Topic
    curious_suggestions = get_youtube_suggestions("what if you woke up in")
    curious_short_topic = curious_suggestions[0] if curious_suggestions else "What if you woke up in the year 3000?"

    return {
        "long_finance": finance_topic,
        "long_general": general_topic,
        "short_finance": finance_short_topic,
        "short_general": general_short_topic,
        "short_curious": curious_short_topic
    }
