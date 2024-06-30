# Full Prompt Structure:
# full_prompt = f"REFERENCE_ELEMENT:\n\n{reference_element} " +
#               f"TEST_ELEMENT:\n\n{test_element} " +
#               prompt_compare_element

prompt_compare_plot = """
###PERSONA:
You are a world-famous narratologist and successful film scriptwriter. 

###ELEMENT_FEATURES
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
You are a world-famous narratologist and successful film scriptwriter 
so precisely and carefully think step by step to
COMPARE the similarities between the above ###TEST_ELEMENT and the baseline ###REFERENCE_ELEMENT
using ###ELEMENT_FEATURES then
responds with estimated similarity scores between (0-100) for the similiary of each of the FEATURES
as well as an 'overall' similarity score
ONLY use information provided HERE, 
DO NOT USE information from your memory.

Return your response in JSON form following this ###TEMPLATE as demostrated in the ###EXAMPLE below

###TEMPLATE

{
    "protagonist_introduction": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "inciting_incident": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "rising_action": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "climax": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "resolution": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)  
    },
    "consequences": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200) 
    },
    "final_outcome": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "loose_ends": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "subplots": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    }
}


###EXAMPLE:

{
    "overall": {
        "similarity": 70,
        "reasoning": "Both narratives follow a similar structure with a clear protagonist introduction, an inciting incident that propels the plot, rising action with escalating challenges, a climax with a pivotal conflict, and a resolution with significant consequences. However, the thematic elements and character arcs differ, reflecting distinct genres and settings."
    },
    "protagonist_introduction": {
        "similarity": 60,
        "reasoning": "Both protagonists are introduced in a manner that highlights their dedication and current struggles in their respective fields. However, the settings and professions differ significantly, with Indiana Jones being an archaeologist in an adventurous setting and Sebastian and Mia being artists in a modern urban environment."
    },
    "inciting_incident": {
        "similarity": 70,
        "reasoning": "In both stories, the inciting incident introduces a significant encounter that sets the protagonist on their main journey. Indiana Jones learns about the Nazis' pursuit of the Ark, while Mia and Sebastian meet at a party, leading to their intertwined paths. Both incidents effectively set the stage for the unfolding narrative."
    },
    "rising_action": {
        "similarity": 75,
        "reasoning": "The rising actions in both narratives involve the protagonists facing numerous challenges while pursuing their goals, developing relationships with key characters, and encountering obstacles. The nature of the challenges differs, with Indiana Jones facing physical dangers and Mia and Sebastian dealing with personal and professional dilemmas."
    },
    "climax": {
        "similarity": 65,
        "reasoning": "Both climaxes involve a significant conflict and a turning point in the protagonist's journey. Indiana Jones faces the supernatural wrath of the Ark, while Mia and Sebastian confront the tension between their dreams and relationship. The emotional stakes and resolution of the conflict are crucial in both stories."
    },
    "resolution": {
        "similarity": 70,
        "reasoning": "Both resolutions show the protagonists achieving a form of victory or progress while dealing with the consequences of their choices. Indiana Jones secures the Ark, and Mia secures a major acting role. Both resolutions tie up the main plot but leave the protagonists with mixed feelings about their achievements."
    },
    "consequences": {
        "similarity": 65,
        "reasoning": "The consequences in both stories reflect the immediate effects of the climax. Indiana Jones deals with the secrecy of the Ark's storage, while Mia and Sebastian face the reality of their separate paths. Both stories show the protagonists coping with the aftermath of their actions and decisions."
    },
    "final_outcome": {
        "similarity": 70,
        "reasoning": "Both final outcomes establish a new status quo for the protagonists. Indiana Jones returns to academia with renewed passion, and Mia becomes a successful actress while Sebastian owns a jazz club. Both endings reflect the protagonists' growth and hint at future possibilities."
    },
    "loose_ends": {
        "similarity": 60,
        "reasoning": "Both narratives leave some questions unanswered, hinting at future adventures or unresolved issues. Indiana Jones contemplates the hidden powers in the government warehouse, while Mia and Sebastian's story leaves open the influence they had on each other. These loose ends suggest ongoing impacts and potential new stories."
    },
    "subplots": {
        "similarity": 75,
        "reasoning": "Both stories include enriching subplots that develop secondary characters and themes. Indiana Jones has his relationships with Marion and Sallah, while Mia and Sebastian have their personal and professional challenges. These subplots add depth and complexity to the main narrative."
    }
}
""";