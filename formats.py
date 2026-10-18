"""Rich vs Poor Psychology: six different video ANGLES (no forced numbers), plus hook styles and ending styles.
Every video in a run gets a different angle, a different hook style and a different ending style."""

FORMATS = {
    "story": dict(
        kinds=("long", "short"), beats_long=(5, 7), beats_short=(3, 4),
        title_style="a story about two people with the same money moment, one poor mindset and one rich mindset",
        templates=[
            "Two people got the same money. Only one of them is still rich",
            "What the rich do the moment money lands in their hands",
            "Same paycheck, two minds: how one stays stuck and one gets free",
        ],
        outline="Plan {n} story beats following TWO people, one with a poor money mindset and one with a rich money mindset, "
                "who start with the exact same money moment. Each beat is one specific moment in the story. "
                "The last beat shows where the two lives ended up.",
        section="Write this beat of the story (about {w} words): {item}\n"
                "Tell it as a small story with specific details. FIRST what the poor-minded person does and feels, "
                "THEN what the rich-minded person does and feels. Make the viewer see the tiny choice that changes everything.",
        short="tell this moment of the story, the poor-minded person first, then the rich-minded person.",
        hook="Open with the idea that two people got the exact same money and promise to show the moment their lives split.",
        promise="you will show the exact moment their two paths split",
        bgs=["room", "office", "city", "dusk", "day", "money"],
        thumb=["SAME MONEY, NEW LIFE", "THE MOMENT IT SPLITS", "ONE OF THEM WINS", "SAME START, WHO WINS"],
    ),
    "myth": dict(
        kinds=("long", "short"), beats_long=(5, 7), beats_short=(3, 4),
        title_style="one popular money belief that quietly keeps people poor, myth busting",
        templates=[
            "The money lie that quietly keeps people poor",
            "The money advice that sounds smart and keeps you broke",
            "Why the rich never believe what the poor are told about money",
        ],
        outline="Plan {n} beats that expose ONE popular money belief that keeps people poor: the belief in the poor person's own words, "
                "why the brain loves believing it, what it quietly costs, what the rich believe instead, and the shift.",
        section="Write this beat (about {w} words): {item}\n"
                "Keep it about the one belief. Use the poor person's own words when it fits, explain why the brain loves it, "
                "and show what the rich think and do instead. Give one real example.",
        short="say the belief the way a poor person says it, then break it with what the rich do.",
        hook="Open by saying the most dangerous money lies sound exactly like good advice.",
        promise="you will name the one belief that quietly keeps most people stuck",
        bgs=["plain", "night", "office", "money", "city"],
        thumb=["THE BIGGEST LIE", "STOP BELIEVING THIS", "IT SOUNDS SMART", "THEY LIED TO YOU"],
    ),
    "big_idea": dict(
        kinds=("long", "short"), beats_long=(4, 6), beats_short=(3, 3),
        title_style="one hidden psychology idea behind poor thinking and rich thinking",
        templates=[
            "The hidden psychology that decides who stays poor",
            "Why your brain keeps you poor (and how the rich rewired theirs)",
            "The invisible rule behind why some people always have money",
        ],
        outline="Pick ONE powerful money psychology idea that fits the title (for example scarcity thinking, instant reward, identity, "
                "or fear of loss). Plan {n} beats that build that one idea step by step: what it is, how it shows up in a poor life, "
                "how it shows up in a rich life, why the brain does it, and how to break it. "
                "The last beat must change how the viewer sees their own wallet.",
        section="Write this beat of the one big idea (about {w} words): {item}\n"
                "Explain it so a 10 year old gets it, using one vivid everyday comparison. Show how it looks for a poor person and then for a rich person.",
        short="explain this part of the one big idea with one vivid comparison, poor side then rich side.",
        hook="Open with a weird everyday thing nobody connects to money, then say one hidden mechanism sits behind it.",
        promise="you will reveal the one hidden mechanism behind it, and it will change how they look at their own wallet",
        bgs=["plain", "night", "dusk", "day", "room"],
        thumb=["YOUR BRAIN DOES THIS", "THE HIDDEN RULE", "WHY YOU STAY STUCK", "THE REAL REASON"],
    ),
    "scenario": dict(
        kinds=("long", "short"), beats_long=(5, 7), beats_short=(3, 4),
        title_style="'what would you do?' money moments that show if you think poor or rich",
        templates=[
            "What would you do? Money moments that show how you really think",
            "Your answer to this reveals if you think like the rich or the poor",
            "Everyday money choices where the poor and the rich go opposite ways",
        ],
        outline="Plan {n} beats, each one an everyday money moment where a person must choose (a surprise bonus, a friend's wedding, "
                "a big sale, a family request for money). Each beat is the situation in one sentence.",
        section="Write this beat (about {w} words): {item}\n"
                "Describe the situation in two sentences using 'you' so the viewer is inside it. "
                "Say what most poor-minded people choose and the feeling behind it. THEN reveal what the rich choose and the quiet reason.",
        short="put the viewer in the situation, say what the poor choose, then what the rich choose.",
        hook="Open with a 'pick one' challenge that puts the viewer inside a real money choice and promise to reveal what the rich pick.",
        promise="by the end they will know if they think like the rich or the poor",
        bgs=["city", "park", "room", "office", "money", "day"],
        thumb=["WHAT WOULD YOU PICK", "PICK ONE, BE HONEST", "ONLY ONE IS RICH", "YOUR CHOICE SAYS IT"],
    ),
    "warning": dict(
        kinds=("long", "short"), beats_long=(5, 7), beats_short=(3, 4),
        title_style="expensive money habits that feel normal, a warning",
        templates=[
            "The money habits that feel normal and quietly keep you poor",
            "Warning: what you do after payday decides everything",
            "The expensive habits the poor defend and the rich avoid",
        ],
        outline="Plan {n} beats about expensive money habits that feel normal, each with the excuse a poor person tells themselves. "
                "The last beat must be the costliest.",
        section="Write this beat (about {w} words): {item}\n"
                "Name the habit in plain words. Show the excuse the poor person tells themselves. "
                "Show what it really costs over a year. THEN show what the rich do instead.",
        short="name the habit, give the poor person's excuse, then what the rich do instead.",
        hook="Open with a warning tone: you are probably doing at least one of these right now.",
        promise="you will show the habit that costs the most",
        bgs=["night", "money", "city", "dusk", "office"],
        thumb=["STOP DOING THIS", "THIS COSTS YOU", "YOU DO THIS, RIGHT?", "THE COSTLY HABIT"],
    ),
    "truth": dict(
        kinds=("long", "short"), beats_long=(5, 7), beats_short=(3, 4),
        title_style="a direct, honest answer to a question people really search about poor and rich",
        templates=[
            "Why poor people stay poor: the answer nobody likes",
            "Why rich people get richer: it is not what you think",
            "The uncomfortable truth about money nobody tells you",
        ],
        outline="Plan {n} beats that answer the question in the title honestly: start with the surface reason most people give, "
                "go deeper into the psychology underneath, and end with the uncomfortable truth.",
        section="Write this beat (about {w} words): {item}\n"
                "Answer honestly in plain words. Use one concrete example. Contrast how a poor mindset sees it and how a rich mindset sees it.",
        short="give this layer of the honest answer, then contrast poor thinking and rich thinking.",
        hook="Open by asking the question the viewer secretly asks themselves and say the real answer is not what they were told.",
        promise="you will give the real answer, the one most people avoid hearing",
        bgs=["plain", "night", "city", "dusk", "room", "office"],
        thumb=["THE REAL ANSWER", "NOBODY SAYS THIS", "THE UGLY TRUTH", "IT IS NOT LUCK"],
    ),
}

# 30 hook techniques and 30 ending techniques. They are only DIRECTIONS: the AI writes fresh words from each script's own idea.
HOOK_STYLES = {
    "scene": "Drop the viewer into one real moment in the first sentence (a card declined at the till, a rent text at 2am).",
    "truth": "Say a painful truth that makes them feel seen, then admit nobody tells people this.",
    "challenge": "Challenge them to watch for something in themselves while they listen, and promise the answer at the end.",
    "contradiction": "Say that what everyone believes about this money topic is backwards.",
    "secret": "Say there is a quiet pattern the rich follow that almost nobody talks about, and hold it back.",
    "question": "Ask one sharp question the viewer cannot answer honestly, then say you will answer it.",
    "story_cut": "Start in the middle of a tiny story and cut it off at the tensest moment, promising to finish it.",
    "identity": "Describe a tiny everyday habit and say what it quietly tells their brain about who they are.",
    "confession": "Start with a confession about believing something wrong about money for years.",
    "warning": "Start with a calm warning that the next minute may feel uncomfortable, and that is the point.",
    "two_people": "Describe two people with the same job and the same pay whose lives look totally different, and ask why.",
    "prediction": "Predict something specific about the viewer's money habits and promise to prove it by the end.",
    "wrong_advice": "Say the advice most people got about money was made for a different kind of person.",
    "tiny_detail": "Point at one tiny detail (what is in someone's cart, how they pay) that reveals everything.",
    "future_self": "Ask them to picture themselves in ten years living with the habit they have today.",
    "unspoken_rule": "Say the rich follow a rule they never say out loud.",
    "mirror": "Say your bank app already shows exactly who you are, and you will show how to read it.",
    "family_dinner": "Say this is the thing nobody dares say at the family dinner table.",
    "quick_test": "Give a quick test to answer in their head, and say the answer reveals their money mindset.",
    "regret": "Say the biggest money regret is not the one people expect.",
    "feeling": "Take them back to the exact feeling of checking their balance and dreading it.",
    "same_job": "Compare a friend who earns the same but keeps more, and ask what they know that you do not.",
    "not_your_fault": "Say it is not your fault, but it is your responsibility, and promise to explain the difference.",
    "countdown_minute": "Say that in the next minute they will see something about their money they cannot unsee.",
    "bucket": "Open with a simple everyday analogy (a bucket with a small hole) and hint it is about their money.",
    "reveals": "Say money does not change people, it reveals them, and ask what it reveals about you.",
    "one_word": "Say one single word separates the poor mindset from the rich mindset, and hold it back.",
    "payday": "Start at 11pm on payday and what the money is already doing.",
    "coffee_watch": "Describe how a rich person and a poor person pay for the same coffee and what that shows.",
    "bold_claim": "Make a bold claim that being broke is a skill people practice daily without knowing.",
}

ENDINGS = {
    "callback": "Go back to the opening moment and give it a new meaning.",
    "question": "End with one question the viewer will want to answer in the comments.",
    "challenge": "End with one small challenge they can do before tomorrow.",
    "truth": "End with one calm, uncomfortable truth, then a soft ask.",
    "next": "Hint at the next video's topic so they want to come back.",
    "punchline": "End with a short two-line punchline that sums up the poor way and the rich way.",
    "mirror": "Ask them to look at their last purchase and ask one honest question about it.",
    "two_lives": "End by picturing the two lives one more time, a year from now, side by side.",
    "one_word": "End on one single word that carries the whole idea.",
    "tomorrow_morning": "End by describing tomorrow morning and the one tiny thing that is different.",
    "letter": "End as if writing one line to the viewer's future self.",
    "final_image": "End on one vivid final image they will remember.",
    "open_loop": "End by leaving one small question open that the next video will answer.",
    "gratitude": "End with genuine thanks for staying and say they are already ahead.",
    "dare": "End with a friendly dare to try the idea for a week and report back in the comments.",
    "whisper": "End quietly, like sharing a secret, with the single most important line.",
    "reversal": "End by flipping the opening idea on its head.",
    "one_thing": "End with the single smallest action that matters most.",
    "rhetorical": "End with a rhetorical question that lingers.",
    "permission": "End by giving them permission to start over from today.",
    "soft_warning": "End with a gentle warning about what happens if nothing changes.",
    "story_finish": "Finish the small story from the opening and show how it ended.",
    "identity_close": "End by telling them who they are becoming if they use this.",
    "comment_bait": "End by asking for one specific answer in the comments, like which habit was the hardest to admit.",
    "share_bait": "End by suggesting they send this to the one person who needs to hear it.",
    "quotable": "End with one short quotable line people would repeat to a friend.",
    "time_jump": "End with a jump forward in time to show the result.",
    "contrast": "End with a one-breath contrast between the poor mindset and the rich mindset.",
    "invitation": "End with a warm invitation to come along and learn more together.",
    "promise": "End with a simple promise about what the channel will keep delivering.",
}
