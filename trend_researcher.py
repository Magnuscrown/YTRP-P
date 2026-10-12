from youtube_search import YoutubeSearch # For autocomplete suggestions
from yspy import Yspy # For trending videos without API key

def research_topics():
    print("🔍 Researching trends directly from YouTube...")

    # Helper function to get autocomplete suggestions
    def get_suggestions(query):
        try:
            # This uses YouTube's autocomplete feature
            suggestions = YoutubeSearch(query, max_results=5).to_dict()
            return [s['title'] for s in suggestions]
        except Exception as e:
            print(f"Error fetching suggestions for '{query}': {e}")
            return []

    # Helper function to get trending videos
    def get_trending():
        try:
            yspy = Yspy()
            # Fetch trending videos (default: US region, but you can change this)
            trending = yspy.trending(max_results=5)
            return [video['title'] for video in trending]
        except Exception as e:
            print(f"Error fetching trending videos: {e}")
            return []

    # 1. Finance Long Video Topic
    finance_queries = ["how to make money online", "passive income ideas", "best investments 2026"]
    finance_suggestions = []
    for q in finance_queries:
        finance_suggestions.extend(get_suggestions(q))
    finance_topic = finance_suggestions[0] if finance_suggestions else "Best Passive Income Ideas"

    # 2. Trending Long Video Topic (from YouTube Trending feed)
    trending_titles = get_trending()
    general_topic = trending_titles[0] if trending_titles else "The Future of AI Technology"

    # 3. Finance Short Topic
    finance_short_queries = ["quick money tips", "save money fast"]
    finance_short_suggestions = []
    for q in finance_short_queries:
        finance_short_suggestions.extend(get_suggestions(q))
    finance_short_topic = finance_short_suggestions[0] if finance_short_suggestions else "Save Money Fast"

    # 4. Trending Short Topic
    general_short_queries = ["viral life hacks", "trending shorts"]
    general_short_suggestions = []
    for q in general_short_queries:
        general_short_suggestions.extend(get_suggestions(q))
    general_short_topic = general_short_suggestions[0] if general_short_suggestions else "Life Hack Everyone Should Know"

    # 5. Curious "What If" Short Topic
    curious_queries = ["what if scenarios", "what if you woke up in"]
    curious_suggestions = []
    for q in curious_queries:
        curious_suggestions.extend(get_suggestions(q))
    curious_short_topic = curious_suggestions[0] if curious_suggestions else "What if you woke up in the year 3000?"

    return {
        "long_finance": finance_topic,
        "long_general": general_topic,
        "short_finance": finance_short_topic,
        "short_general": general_short_topic,
        "short_curious": curious_short_topic
    }
