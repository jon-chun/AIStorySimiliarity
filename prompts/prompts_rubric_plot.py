prompt_similarity_plot_referencefilm = f"""
###REFERENCE_FILM:
""";

prompt_similarity_plot_referencefilm = f"""
###TEST_FILM:
""";

prompt_similarity_plot = """
###PERSONA:
You are a world-famous narratologist and successful film scriptwriter.

###RUBRIC:
Protagonist Introduction: Introduces the main character, showcasing their core traits, current status, and immediate goals within their environment.
Inciting Incident: Presents a disruptive event that propels the protagonist into the main conflict and introduces the stakes.
Rising Action: Develops the main conflict through a series of escalating challenges, character development, and introduction of key relationships.
Climax: Features the story's turning point where the main conflict reaches peak tension, leading to a critical decision or action by the protagonist.
Resolution: Concludes the main conflict, showing the immediate outcome of the climax and tying up loose ends.
Consequences: Explores the immediate and short-term effects of the climax on the protagonist and other characters.
Final Outcome: Establishes the new status quo for the protagonist and key characters, concluding their arcs.
Loose Ends: Addresses any remaining unanswered questions or unresolved plot points, often hinting at future possibilities.
Subplots: Enrich the main narrative with secondary storylines that develop supporting characters and reflect or contrast with the main themes.

###INSTRUCTIONS:
Think carefully step by step to estimate an estimated similarity score between (0-100)
for the features in the above ###RUBRIC
between the above ###TEST_FILM and the above ###REFERENCE_FILM

Based upon these ###RUBRIC similiarities, 
give a FINAL similarity_overall score for these two films
using the following ###TEMPLATE:

and return a response in a valid Python Dictionary format using this ###TEMPLATE

###TEMPLATE

{
    "reference_film": {
        "film_title": string len(,50),
        "features": {
            "protagonist_intro": string len(100,200)
            "inciting_incident": string len(100,200)
            "rising_action": string len(100,200)
            "climax": string len(100,200)
            "resolution": string len(100,200)
            "consequences": string len(100,200)
            "final_outcome": string len(100,200)
            "loose_ends": string len(100,200)
            "subplots": string len(100,200)
        },
    },
    "test_film": {
        "film_title": string len(,50),
        "features": {
            "protagonist_intro": string len(100,200)
            "inciting_incident": string len(100,200)
            "rising_action": string len(100,200)
            "climax": string len(100,200)
            "resolution": string len(100,200)
            "consequences": string len(100,200)
            "final_outcome": string len(100,200)
            "loose_ends": string len(100,200)
            "subplots": string len(100,200)
        },
    },
    "similarity_by_features": {
        "film_title": string len(,50),
        "features": {
            "protagonist_intro": integer range(0,100),
            "inciting_incident": integer range(0,100),
            "rising_action": integer range(0,100),
            "climax": integer range(0,100),
            "resolution": integer range(0,100),
            "consequences": integer range(0,100),
            "final_outcome": integer range(0,100),
            "loose_ends": integer range(0,100),
            "subplots": integer range(0,100),
        },
        "similarity_overall" : integer range(0,100)
    },
} 
""";


"""
##### <PROMPT> #####

###REFERENCE_FILM:
Raiders of the Lost Ark (1981 film)

###TEST_FILM:
National Treasure (2004 film)

###PERSONA:
You are a world-famous narratologist and successful film scriptwriter.

###RUBRIC:
Protagonist Introduction: Introduces the main character, showcasing their core traits, current status, and immediate goals within their environment.
Inciting Incident: Presents a disruptive event that propels the protagonist into the main conflict and introduces the stakes.
Rising Action: Develops the main conflict through a series of escalating challenges, character development, and introduction of key relationships.
Climax: Features the story's turning point where the main conflict reaches peak tension, leading to a critical decision or action by the protagonist.
Resolution: Concludes the main conflict, showing the immediate outcome of the climax and tying up loose ends.
Consequences: Explores the immediate and short-term effects of the climax on the protagonist and other characters.
Final Outcome: Establishes the new status quo for the protagonist and key characters, concluding their arcs.
Loose Ends: Addresses any remaining unanswered questions or unresolved plot points, often hinting at future possibilities.
Subplots: Enrich the main narrative with secondary storylines that develop supporting characters and reflect or contrast with the main themes.

###INSTRUCTIONS:
Think carefully step by step to estimate an estimated similarity score between (0-100)
for the features in the above ###RUBRIC
between the above ###TEST_FILM and the above ###REFERENCE_FILM

Based upon these ###RUBRIC similiarities, 
give a FINAL similarity_overall score for these two films
using the following ###TEMPLATE:

and return a response in valid Python Dictionary format using this ###TEMPLATE

###TEMPLATE

[{
    "reference_film": {
        "film_title": string len(,50),
        "features": {
            "protagonist_intro": string len(100,200)
            "inciting_incident": string len(100,200)
            "rising_action": string len(100,200)
            "climax": string len(100,200)
            "resolution": string len(100,200)
            "consequences": string len(100,200)
            "final_outcome": string len(100,200)
            "loose_ends": string len(100,200)
            "subplots": string len(100,200)
        },
    },
    "test_film": {
        "film_title": string len(,50),
        "features": {
            "protagonist_intro": string len(100,200)
            "inciting_incident": string len(100,200)
            "rising_action": string len(100,200)
            "climax": string len(100,200)
            "resolution": string len(100,200)
            "consequences": string len(100,200)
            "final_outcome": string len(100,200)
            "loose_ends": string len(100,200)
            "subplots": string len(100,200)
        },
    },
    "similarity_by_features": {
        "film_title": string len(,50),
        "features": {
            "protagonist_intro": integer range(0,100),
            "inciting_incident": integer range(0,100),
            "rising_action": integer range(0,100),
            "climax": integer range(0,100),
            "resolution": integer range(0,100),
            "consequences": integer range(0,100),
            "final_outcome": integer range(0,100),
            "loose_ends": integer range(0,100),
            "subplots": integer range(0,100),
        },
        "similarity_overall" : integer range(0,100)
    },
}] 

##### <RESPONSE> #####

[{
    "reference_film": {
        "film_title": "Raiders of the Lost Ark",
        "features": {
            "protagonist_intro": "Indiana Jones is introduced as a daring archaeologist, skillfully retrieving a golden idol from a perilous jungle temple.",
            "inciting_incident": "Indiana Jones learns of the Nazis' plan to find the Ark of the Covenant, prompting him to embark on a mission to stop them.",
            "rising_action": "Indiana Jones faces various challenges including rivals, traps, and Nazi antagonists as he seeks the Ark, developing key relationships with Marion and Sallah.",
            "climax": "Indiana Jones and Marion are captured by the Nazis who open the Ark, unleashing supernatural forces that destroy the Nazis.",
            "resolution": "Indiana Jones ensures the Ark is safely secured in a government warehouse, preventing its misuse.",
            "consequences": "The climax results in the loss of many lives, but Indiana Jones is vindicated in his beliefs about the Ark's power.",
            "final_outcome": "Indiana Jones returns to his academic life, with his adventurous spirit undiminished and a sense of having protected a vital artifact.",
            "loose_ends": "Questions about the true power of the Ark and potential future threats remain, hinting at further adventures.",
            "subplots": "Subplots include Indiana Jones's complex relationships with Marion and his academic rivalries, enriching his character and motivations."
        }
    },
    "test_film": {
        "film_title": "National Treasure",
        "features": {
            "protagonist_intro": "Benjamin Franklin Gates is introduced as a passionate historian and treasure hunter, dedicated to uncovering secrets of the past.",
            "inciting_incident": "Gates discovers a clue suggesting the existence of a vast hidden treasure and decides to steal the Declaration of Independence to find it.",
            "rising_action": "Gates faces escalating challenges from rivals and the authorities while deciphering clues, forming key alliances with Abigail and Riley.",
            "climax": "Gates and his team find the hidden treasure after a series of intense trials, just as the antagonist threatens to claim it.",
            "resolution": "Gates secures the treasure and ensures it is preserved for historical and public benefit, escaping legal repercussions.",
            "consequences": "The discovery of the treasure brings historical validation and personal vindication to Gates and his family.",
            "final_outcome": "Gates achieves fame and recognition, solidifying his family's legacy and hinting at future quests.",
            "loose_ends": "Future adventures are suggested with unresolved mysteries and potential new clues.",
            "subplots": "Subplots include Gates's evolving relationship with Abigail and the tension with his former ally, Ian, adding depth to the main narrative."
        }
    },
    "similarity_by_features": {
        "film_title": "National Treasure",
        "features": {
            "protagonist_intro": 85,
            "inciting_incident": 80,
            "rising_action": 85,
            "climax": 80,
            "resolution": 75,
            "consequences": 70,
            "final_outcome": 80,
            "loose_ends": 70,
            "subplots": 75
        },
        "similarity_overall": 78
    }
}]

""";