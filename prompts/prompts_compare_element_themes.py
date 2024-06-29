# Full Prompt Structure:
# full_prompt = f"REFERENCE_ELEMENT:\n\n{reference_element} " +
#               f"TEST_ELEMENT:\n\n{test_element} " +
#               prompt_compare_element

prompt_compare_themes = """
###PERSONA:
You are a world-famous narratologist and successful film scriptwriter. 

###ELEMENT_FEATURES
Main Theme: The central idea or message that permeates the entire narrative and ties all story elements together.
Secondary Themes: Supporting ideas that complement or contrast with the main theme, adding depth and complexity to the narrative.
Tertiary Themes: Minor thematic elements that appear less frequently but contribute to the overall thematic richness of the story.
Resolution Main Theme: How the central theme is concluded or crystallized by the end of the narrative, often reflecting character growth or plot resolution.
Resolution Secondary Themes: The way supporting themes are addressed or resolved in relation to the main theme and overall story arc.
Resolution Tertiary Themes: How minor thematic elements are tied up or integrated into the larger thematic resolution of the story.

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
                ...     
{
    "overall": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "main_theme": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "secondary_themes": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "tertiary_themes": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "resolution_main_them": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)  
    },
    "resolution_secondary_them": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200) 
    },
    "resolution_tertiary_them": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    }
}


###EXAMPLE

{
    "overall": {
        "similarity": 70,
        "reasoning": "Both narratives focus on the pursuit of dreams and the obstacles encountered. However, 'Raiders of the Lost Ark' centers on adventure and historical preservation, while 'La La Land' revolves around artistic ambitions and personal sacrifice."
    },
    "main_theme": {
        "similarity": 60,
        "reasoning": "Both films explore the pursuit of significant goals—artifacts in 'Raiders of the Lost Ark' and artistic dreams in 'La La Land.' However, the contexts and motivations differ, with one focused on historical preservation and the other on personal artistic achievement."
    },
    "secondary_themes": {
        "similarity": 75,
        "reasoning": "Themes of personal relationships and conflicts between ideals and reality are present in both films. 'Raiders' focuses on loyalty, betrayal, and resilience, while 'La La Land' emphasizes love, artistic integrity, and nostalgia."
    },
    "tertiary_themes": {
        "similarity": 70,
        "reasoning": "Both narratives include minor themes that enhance the story's depth. 'Raiders' addresses colonialism, gender roles, and environmental awareness, while 'La La Land' explores identity, support systems, and fate."
    },
    "resolution_main_theme": {
        "similarity": 65,
        "reasoning": "Both films resolve their main themes by achieving their goals despite sacrifices. 'Raiders' emphasizes historical preservation and respect for artifacts, while 'La La Land' focuses on the bittersweet success of personal dreams."
    },
    "resolution_secondary_themes": {
        "similarity": 70,
        "reasoning": "Both films resolve secondary themes by highlighting the importance of relationships and integrity. 'Raiders' resolves loyalty and betrayal, while 'La La Land' concludes the love story and artistic integrity conflict."
    },
    "resolution_tertiary_themes": {
        "similarity": 70,
        "reasoning": "Both films address minor themes by the end. 'Raiders' concludes with reflections on colonialism and gender roles, while 'La La Land' wraps up identity, support systems, and fate themes, emphasizing the impact of choices and destiny."
    }
}
""";