# Full Prompt Structure:
# full_prompt = f"REFERENCE_ELEMENT:\n\n{reference_element} " +
#               f"TEST_ELEMENT:\n\n{test_element} " +
#               prompt_compare_element

prompt_compare_setting = """
###PERSONA:
You are a world-famous narratologist and successful film scriptwriter. 

###ELEMENT_FEATURES
Time Period: Establishes the historical context and influences character behavior, societal norms, technology, and major historical events. Key elements include specific historical era or time frame, including contemporary, historical, and futuristic settings.
Geographical Location: Shapes the environment and specific challenges faced by characters, often serving as a critical component of the plot. Key element include physical locations such as continents, countries, cities, and specific environments like jungles, deserts, and urban areas.
Cultural Context: Enriches the narrative by adding depth to character interactions and conflicts, and significantly impacts the story’s progression. Key elements include cultural, social, and ethnic backdrop, including traditions, customs, social norms, and language.
Social Class: Drives character interactions, conflicts, and personal arcs, highlighting societal issues and adding depth to the narrative. Key elements include hierarchical structure of society, including class divisions based on economic, social, or cultural factors.
Ideology and Belief: Influences character motivations, ethical dilemmas, and conflicts, adding layers of complexity to the narrative. Key elements include dominant belief systems, religions, philosophical views, superstitions, and mythology.
Economic and Political Context: Drives the plot by creating conflicts, influencing character motivations, and providing context for the protagonist’s struggles. Key elements include economic conditions, political climate, type of government, and prevailing economic structures.

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
    "overall": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "time_period": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "geographical_location": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "cultural_context": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "social_class": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)  
    },
    "ideology_and_beliefs": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200) 
    },
    "economic_and_political_context": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    }
}

###EXAMPLE:

{
    "overall": {
        "similarity": 50,
        "reasoning": "Both stories revolve around the protagonists' pursuit of their passions and dreams, encountering obstacles and complex relationships along the way. However, the settings, time periods, and specific conflicts differ significantly, affecting the narratives' overall similarity."
    },
    "time_period": {
        "similarity": 20,
        "reasoning": "The 'Reference Element' is set in 1936, a historical period with its unique context, while the 'Test Element' is set in contemporary Los Angeles, reflecting modern challenges and societal norms. The differing time frames impact the characters' experiences and the plot's progression."
    },
    "geographical_location": {
        "similarity": 30,
        "reasoning": "The 'Reference Element' takes place in various exotic locations, including jungles and remote islands, while the 'Test Element' is primarily set in Los Angeles, an urban environment. The geographical settings influence the nature of the characters' challenges and the story's atmosphere."
    },
    "cultural_context": {
        "similarity": 40,
        "reasoning": "Both stories are influenced by their cultural contexts—archaeology and the Nazi threat in the 'Reference Element' versus the entertainment industry in Los Angeles for the 'Test Element.' While the cultural settings differ, they both deeply impact the characters' lives and pursuits."
    },
    "social_class": {
        "similarity": 60,
        "reasoning": "Both protagonists face challenges related to their social environments: Indiana Jones as an academic and adventurer navigating high-stakes scenarios, and Mia and Sebastian dealing with the competitive entertainment industry. Social class influences their interactions and personal arcs."
    },
    "ideology_and_beliefs": {
        "similarity": 50,
        "reasoning": "The 'Reference Element' involves ideological conflicts related to archaeology and supernatural beliefs, while the 'Test Element' focuses on personal ideologies about artistic integrity and success. Both narratives explore the protagonists' belief systems and their impact on decisions."
    },
    "economic_and_political_context": {
        "similarity": 40,
        "reasoning": "The 'Reference Element' is influenced by the political context of Nazi Germany's ambitions, whereas the 'Test Element' is shaped by the economic realities of pursuing a career in the arts. While both contexts create significant obstacles for the characters, the specifics vary widely."
    }
}
""";