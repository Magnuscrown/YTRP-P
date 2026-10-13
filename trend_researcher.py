import requests
import json
import os
import random

USED_TOPICS_FILE = "used_topics.json"

# --- Big pools of seed queries (each category has ~30 different angles) ---
FINANCE_SEEDS = [
    "how to save money fast",
    "how to invest for beginners",
    "how to protect your money",
    "how to grow your money",
    "best passive income ideas",
    "how to budget your money",
    "emergency fund tips",
    "dividend stocks for beginners",
    "how to pay off debt fast",
    "side hustle ideas",
    "money mistakes to avoid",
    "how to build wealth",
    "index funds explained",
    "how to retire early",
    "compound interest explained",
    "how to negotiate salary",
    "cheap living tips",
    "how to stop overspending",
    "best savings accounts",
    "how to make your first 1000",
    "tax saving tips",
    "how to invest with little money",
    "credit score explained",
    "how to become a millionaire",
    "financial freedom tips",
    "why rich people stay rich",
    "why poor people stay poor",
    "how banks make money",
    "inflation explained",
    "how to buy your first house"
]

GENERAL_SEEDS = [
    "trending topics today",
    "viral questions this week",
    "most searched questions",
    "life hacks everyone should know",
    "why do people",
    "how does work",
    "biggest mysteries explained",
    "psychology facts",
    "habits of successful people",
    "history facts",
    "science explained simply",
    "how things are made",
    "top 10 facts about",
    "things you didn't know",
    "amazing inventions",
    "space facts",
    "ocean mysteries",
    "human body facts",
    "animal facts",
    "food facts",
    "why is the sky blue",
    "how the internet works",
    "how ai works",
    "hidden rules of society",
    "why do we dream",
    "world records",
    "historical mysteries",
    "future technology",
    "ancient civilizations",
    "everyday objects explained"
]

CURIOUS_SEEDS = [
    "what if you woke up in",
    "what if money didn't exist",
    "what if the internet disappeared",
    "what if humans could fly",
    "what if the sun disappeared",
    "what if you could time travel",
    "what if gravity stopped",
    "what if you never slept",
    "what if everyone was rich",
    "what if the oceans dried up",
    "what if ai took over",
    "what if you were the last person on earth",
    "what if you lived underwater",
    "what if trees could talk",
    "what if you could read minds",
    "what if the moon crashed into earth",
    "what if electricity stopped",
    "what if you aged backwards",
    "what if you were invisible",
    "what if there were no laws",
    "what if you lived forever",
    "what if every day was monday",
    "what if you could teleport",
    "what if ants were as big as humans",
    "what if you woke up as an animal",
    "what if all volcanoes erupted",
    "what if you could freeze time",
    "what if the earth stopped spinning",
    "what if you had a photographic memory",
    "what if you never felt pain"
]

def load_used_topics():
    if os.path.exists(USED_TOPICS_FILE):
        try:
            with open(USED_TOPICS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_used_topics(used):
    with open(USED_TOPICS_FILE, "w") as f:
        json.dump(used[-200:], f, indent=2)  # Keep last 200

def get_youtube_suggestions(query):
    try:
        url = f"http://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q={query}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data[1] if len(data) > 1 else []
        return []
    except Exception as e:
        print(f"⚠️ Suggestion fetch failed for '{query}': {e}")
        return []

def pick_unique_topic(seeds, used_topics, label):
    """Pick a random seed, get YouTube suggestions, return first unused one."""
    random.shuffle(seeds)
    
    for seed in seeds[:10]:  # Try up to 10 seeds
        suggestions = get_youtube_suggestions(seed)
        random.shuffle(suggestions)
        
        for suggestion in suggestions:
            s_clean = suggestion.strip().lower()
            if not s_clean:
                continue
            if s_clean in used_topics:
                continue
            # Also make sure it's not too similar to a used one
            if any(s_clean in u or u in s_clean for u in used_topics if len(u) > 15):
                continue
            print(f"✅ [{label}] Picked: {suggestion}")
            return suggestion
    
    # Fallback: return a random seed itself
    fallback = random.choice(seeds)
    print(f"⚠️ [{label}] Using fallback: {fallback}")
    return fallback

def research_topics():
    print("🔍 Researching diverse YouTube trends...")
    used = load_used_topics()
    print(f"📚 Already used: {len(used)} topics")
    
    topics = {
        "long_finance": pick_unique_topic(FINANCE_SEEDS, used, "LONG-FINANCE"),
        "long_general": pick_unique_topic(GENERAL_SEEDS, used, "LONG-GENERAL"),
        "short_finance": pick_unique_topic(FINANCE_SEEDS, used + [topics.get("long_finance", "")], "SHORT-FINANCE") if False else None,
        "short_general": None,
        "short_curious": None,
    }
    
    # Re-run with proper used-list updating to avoid duplicates within the same run
    run_used = used.copy()
    
    topics["long_finance"] = pick_unique_topic(FINANCE_SEEDS, run_used, "LONG-FINANCE")
    run_used.append(topics["long_finance"].lower())
    
    topics["long_general"] = pick_unique_topic(GENERAL_SEEDS, run_used, "LONG-GENERAL")
    run_used.append(topics["long_general"].lower())
    
    topics["short_finance"] = pick_unique_topic(FINANCE_SEEDS, run_used, "SHORT-FINANCE")
    run_used.append(topics["short_finance"].lower())
    
    topics["short_general"] = pick_unique_topic(GENERAL_SEEDS, run_used, "SHORT-GENERAL")
    run_used.append(topics["short_general"].lower())
    
    topics["short_curious"] = pick_unique_topic(CURIOUS_SEEDS, run_used, "SHORT-CURIOUS")
    run_used.append(topics["short_curious"].lower())
    
    # Save the newly used topics
    save_used_topics(run_used)
    
    return topics
