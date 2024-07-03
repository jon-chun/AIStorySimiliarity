prompt_verify_claude35sonnet_characters = """
###REFERENCE_FILM:
Raiders of the Lost Ark (1981)

###TEST_FILM:
Office Space (1999)

###PERSONA:
You are a world-famous narratologist and successful film scriptwriter. 

###ELEMENT_FEATURES
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
You are a world-famous narratologist and successful film scriptwriter 
so precisely and carefully think step by step to
CRITIQUE the similarity scores and corresponding explanations and reasoning for the
similarities between the above ###TEST_ELEMENT and the baseline ###REFERENCE_ELEMENT
using ###ELEMENT_FEATURES then

try to identify any FACTUAL or RESONING ERRORS 

if none, let "accuracy" =100 and "reason"="None" 
else estimate an "accuracy" score (0-100) with a written "reason"

Return your response in JSON form following this ###TEMPLATE as demonstrated in the ###EXAMPLE below

###TEMPLATE

{
    "accuracy_new": integer range(0,100),
    "accuracy_old": integer range(0,100),
    "accuracy_difference": integer range(0,100),
    "factual_errors": list[string len(10,50)],
    "reasoning_errors": string len(200,500)
}

###EXAMPLE:

{
    "accuracy_new": 95,
    "accuracy_old": 100,
    "accuracy_difference": 5,
    "factual_errors": "None",
    "reasoning_errors": "The analysis correctly identifies the strong similarities in Indiana Jones' character across both films. However, it overlooks subtle but important differences in his character arc, social dynamics, and motivations in 'The Last Crusade.' The introduction of the father-son relationship and the personal quest to save his father add new dimensions to the character that aren't reflected in the 100% similarity scores. A more nuanced analysis would acknowledge these differences while still recognizing the high overall consistency of the character."
}
""";