prompt_similarity_characters_referencefilm = f"""
###REFERENCE_FILM:
""";

prompt_similarity_characters_referencefilm = f"""
###TEST_FILM:
""";

prompt_similarity_characters = """
###PERSONA:
You are a world-famous narratologist and successful film scriptwriter.

###RUBRIC:
Name: Full name of character
Role: Clarifies the character's function within the story, whether they are driving the action, supporting the protagonist, or creating obstacles.
Backstory: This attribute helps to understand the formative experiences that shaped each character, providing insights into their motivations and behaviors.
Strengths: Highlights unique abilities and proficiencies, distinguishing characters by their specific talents and expertise.
Weaknesses: Humanizes characters by revealing vulnerabilities and personal challenges, making them more relatable and multi-dimensional.
Psychology: Uses personality assessments, such as the Big 5 OCEAN (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism) model, to offer deeper insight into character traits.
Beliefs: Offers a window into the ethical and moral framework guiding each character's decisions, crucial for understanding their actions in moral dilemmas.
Motivations: Describes what drives the character to act, including desires, fears, and goals.
SocialDynamics: Explores the nature of interactions between characters, which can be pivotal in character development and plot progression.
Arc: Summarizes how the character changes or grows for better or worse over the story in response to events, decisions, and actions taken


###INSTRUCTIONS:
Think carefully step by step to estimate an estimated similarity score between (0-100)
for features of the most similiar characters in the above ###RUBRIC
between the above ###TEST_FILM and the above ###REFERENCE_FILM

Based upon these ###RUBRIC similiarities, 
give a FINAL similarity_overall score for these two films
and return the valid JSON structure using the following ###TEMPLATE by
populating the JSON structure in ###EXAMPLE
(Be sure to use double quotes and trailing commas)

###TEMPLATE

{
    "reference_film": {
        "film_title": string len(,50),
        "features": {
            "role": string len(100,200),
            "backstory": string len(100,200),
            "strengths": string len(100,200),
            "weakness": string len(100,200),
            "psychology": string len(100,200),
            "beliefs": string len(100,200),
            "motivations": string len(100,200),
            "sodial_dynamics": string len(100,200),
            "arc": string len(100,200)
        },
    },
    "test_film": {
        "film_title": string len(,50),
        "features": {
            "role": string len(100,200),
            "backstory": string len(100,200),
            "strengths": string len(100,200),
            "weakness": string len(100,200),
            "psychology": string len(100,200),
            "beliefs": string len(100,200),
            "motivations": string len(100,200),
            "sodial_dynamics": string len(100,200),
            "arc": string len(100,200)
        },
    },
    "similarity_by_features": {
        "role": integer range(0,100),
        "backstory": integer range(0,100),
        "strengths": integer range(0,100),
        "weakness": integer range(0,100),
        "psychology": integer range(0,100),
        "beliefs": integer range(0,100),
        "motivations": integer range(0,100),
        "sodial_dynamics": integer range(0,100),
        "arc": integer range(0,100)
    },
    "similarity_overall" : integer range(0,100)
}


###EXAMPLE: (populate this JSON datastructure with your values)

{
    "reference_film": {
        "film_title": "",
        "features": {
            "role": "",
            "backstory": "",
            "strengths": "",
            "weakness": "",
            "psychology": "",
            "beliefs": "",
            "motivations": "",
            "sodial_dynamics": "",
            "arc": ""
        }
    },
    "test_film": {
        "film_title": "",
        "features": {
            "role": "",
            "backstory": "",
            "strengths": "",
            "weakness": "",
            "psychology": "",
            "beliefs": "",
            "motivations": "",
            "sodial_dynamics": "",
            "arc": ""
        }
    },
    "similarity_by_features": {
        "role": 0,
        "backstory": 0,
        "strengths": 0,
        "weakness": 0,
        "psychology": 0,
        "beliefs": 0,
        "motivations": 0,
        "sodial_dynamics": 0,
        "arc": 0
    },
    "similarity_overall": 0
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
Name: Full name of character
Role: Clarifies the character's function within the story, whether they are driving the action, supporting the protagonist, or creating obstacles.
Backstory: This attribute helps to understand the formative experiences that shaped each character, providing insights into their motivations and behaviors.
Strengths: Highlights unique abilities and proficiencies, distinguishing characters by their specific talents and expertise.
Weaknesses: Humanizes characters by revealing vulnerabilities and personal challenges, making them more relatable and multi-dimensional.
Psychology: Uses personality assessments, such as the Big 5 OCEAN (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism) model, to offer deeper insight into character traits.
Beliefs: Offers a window into the ethical and moral framework guiding each character's decisions, crucial for understanding their actions in moral dilemmas.
Motivations: Describes what drives the character to act, including desires, fears, and goals.
SocialDynamics: Explores the nature of interactions between characters, which can be pivotal in character development and plot progression.
Arc: Summarizes how the character changes or grows for better or worse over the story in response to events, decisions, and actions taken


###INSTRUCTIONS:
Think carefully step by step to estimate an overall similarity score between (0-100)
for the most similiar characters in the above ###RUBRIC
between the above ###TEST_FILM and the above ###REFERENCE_FILM

Based upon these ###RUBRIC similiarities, 
give a FINAL similarity_overall score for these two films
using the following ###TEMPLATE:

and return a response in Python Dictionary format using this ###TEMPLATE

###TEMPLATE

{
    "reference_film": {
        "film_title": string len(,50),
        "features": {
            "role": string len(100,200),
            "backstory": string len(100,200),
            "strengths": string len(100,200),
            "weakness": string len(100,200),
            "psychology": string len(100,200),
            "beliefs": string len(100,200),
            "motivations": string len(100,200),
            "sodial_dynamics": string len(100,200),
            "arc": string len(100,200)
        },
    },
    "test_film": {
        "film_title": string len(,50),
        "features": {
            "role": string len(100,200),
            "backstory": string len(100,200),
            "strengths": string len(100,200),
            "weakness": string len(100,200),
            "psychology": string len(100,200),
            "beliefs": string len(100,200),
            "motivations": string len(100,200),
            "sodial_dynamics": string len(100,200),
            "arc": string len(100,200)
        },
    },
    "similarity_by_features": {
        "role": string len(100,200),
        "backstory": string len(100,200),
        "strengths": string len(100,200),
        "weakness": string len(100,200),
        "psychology": string len(100,200),
        "beliefs": string len(100,200),
        "motivations": string len(100,200),
        "sodial_dynamics": string len(100,200),
        "arc": string len(100,200)
    },
    "similarity_overall" : range(0,100)
}

##### <RESPONSE> #####
{
    "reference_film": {
        "film_title": "Raiders of the Lost Ark",
        "features": {
            "role": "Indiana Jones serves as the protagonist, driving the action through his quest to find the Ark of the Covenant.",
            "backstory": "Indiana Jones is an archaeologist and adventurer with a storied past, driven by a passion for uncovering ancient artifacts.",
            "strengths": "Indiana Jones is highly intelligent, resourceful, and physically capable, with skills in archaeology and combat.",
            "weakness": "Indiana Jones can be reckless and is often driven by personal ambition, sometimes placing himself and others in danger.",
            "psychology": "Indiana Jones is high in Openness, Conscientiousness, and Extraversion, with moderate Agreeableness and low Neuroticism.",
            "beliefs": "Indiana Jones has a strong belief in the historical and cultural value of artifacts.",
            "motivations": "Indiana Jones is driven by a passion for archaeology and the thrill of adventure.",
            "sodial_dynamics": "Indiana Jones often works alone but can rally others to his cause, with relationships complicated by his singular focus.",
            "arc": "Indiana Jones learns to balance his professional ambitions with personal relationships and moral considerations."
        }
    },
    "test_film": {
        "film_title": "National Treasure",
        "features": {
            "role": "Benjamin Franklin Gates serves as the protagonist, driving the action through his quest to find the hidden treasure.",
            "backstory": "Benjamin Franklin Gates is a descendant of a long line of treasure hunters, motivated by a family legacy and a desire to vindicate his family's name.",
            "strengths": "Benjamin Franklin Gates is highly intelligent, resourceful, and determined, with skills in history and cryptography.",
            "weakness": "Benjamin Franklin Gates can be overly obsessed with his quest, which strains personal relationships.",
            "psychology": "Benjamin Franklin Gates is high in Openness, Conscientiousness, and Extraversion, with moderate Agreeableness and low Neuroticism.",
            "beliefs": "Benjamin Franklin Gates has a strong belief in the importance of history and family legacy.",
            "motivations": "Benjamin Franklin Gates is driven by a desire to prove his family's honor and uncover historical truths.",
            "sodial_dynamics": "Benjamin Franklin Gates is the leader of the group, often in conflict with others over the risks of their quest but ultimately inspiring loyalty.",
            "arc": "Benjamin Franklin Gates grows from being an isolated treasure hunter to understanding the value of teamwork and personal relationships."
        }
    },
    "similarity_by_features": {
        "role": "Both characters serve as protagonists driving the action, though their specific quests differ. (Similarity Score: 90)",
        "backstory": "Both characters have a rich backstory involving a legacy of adventure and exploration. (Similarity Score: 85)",
        "strengths": "Both characters are highly intelligent and resourceful, with specialized knowledge relevant to their quests. (Similarity Score: 90)",
        "weakness": "Both characters exhibit personal flaws that make them relatable, though these flaws manifest differently (obsession vs. recklessness). (Similarity Score: 80)",
        "psychology": "Both characters are similar in their adventurous spirit, dedication, and ability to lead, with slight variations in agreeableness. (Similarity Score: 85)",
        "beliefs": "Both characters value history and legacy, though their exact motivations may differ slightly. (Similarity Score: 85)",
        "motivations": "Both characters are driven by a mix of personal and professional desires, seeking validation through their discoveries. (Similarity Score: 85)",
        "sodial_dynamics": "Both characters have complex social interactions, often leading and inspiring others while facing conflicts. (Similarity Score: 80)",
        "arc": "Both characters grow through their adventures, learning to balance personal and professional goals. (Similarity Score: 85)"
    },
    "similarity_overall": 84
}

""";