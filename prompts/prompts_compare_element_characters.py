# Full Prompt Structure:
# full_prompt = f"REFERENCE_ELEMENT:\n\n{reference_element} " +
#               f"TEST_ELEMENT:\n\n{test_element} " +
#               prompt_compare_element

prompt_compare_characters = """
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
COMPARE the similarities between the above ###TEST_ELEMENT and the baseline ###REFERENCE_ELEMENT
using ###ELEMENT_FEATURES then
responds with estimated similarity scores between (0-100)  for the similiary of each of the FEATURES
as well as an 'overall' similarity score
ONLY use information provided HERE, 
DO NOT USE information from your memory.

Return your response in JSON form following this ###TEMPLATE as demostrated in the ###EXAMPLE below

###TEMPLATE

{
    "overall": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "backstory": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "strengths": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "weakness": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "psychology": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)  
    },
    "beliefs": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200) 
    },
    "motivations": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "social_dynamics": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "arc": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    }
}

###EXAMPLE:

{
    "role": {
        "similarity": 90,
        "reasoning": "Both are protagonists who drive the action in pursuit of historical treasures. They lead quests and face adversities while seeking valuable artifacts. The main difference is that Indiana Jones has a more established background as an archaeologist and professor."
    },
    "backstory": {
        "similarity": 75,
        "reasoning": "Both characters have backgrounds tied to historical pursuits. However, Indiana Jones' backstory is more focused on personal experiences shaping his ethical stance, while Gates' is deeply rooted in family legacy and tradition."
    },
    "strengths": {
        "similarity": 85,
        "reasoning": "Both characters share intelligence, resourcefulness, and deep historical knowledge. Indiana Jones has additional combat and survival skills, while Gates' strengths are more academically focused."
    },
    "weaknesses": {
        "similarity": 70,
        "reasoning": "Both have weaknesses that can lead to reckless behavior. Indiana's impulsiveness and fear of snakes are more specific, while Gates' obsession with treasure is more directly tied to his motivations."
    },
    "psychology": {
        "similarity": 85,
        "reasoning": "They share high openness, conscientiousness, and relatively low neuroticism. The main differences are in extraversion (Indiana higher) and agreeableness (Gates higher)."
    },
    "beliefs": {
        "similarity": 90,
        "reasoning": "Both strongly value history, preservation, and protecting artifacts from exploitation. Gates has an additional emphasis on familial duty."
    },
    "motivations": {
        "similarity": 80,
        "reasoning": "Both are driven by a desire to preserve history and fulfill personal quests. Gates' motivation is more focused on family legacy, while Indiana's includes a thirst for adventure and living up to his father's legacy."
    },
    "social_dynamics": {
        "similarity": 75,
        "reasoning": "Both form alliances and face adversaries. Indiana's relationships are more complex, especially with his father and romantic interests. Gates' dynamics focus more on his team and main antagonist."
    },
    "arc": {
        "similarity": 85,
        "reasoning": "Both characters evolve to understand deeper values beyond their initial quests. Indiana's arc focuses on his relationship with his father, while Gates' emphasizes valuing relationships and heritage more broadly."
    }
}

""";