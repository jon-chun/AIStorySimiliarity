prompt_extract_characters = f"""
###PERSONA:
You are a world-famous narratologist and successful film scriptwriter.

###INSTRUCTIONS:
Think carefully step by step to order to analyze the attached MOVIE SCRIPT to
identify all the subcomponents related to narrative setting with detailed descriptions
and organize them into a JSON format using this ###SETTING_OUTLINE 


###SETTING_OUTLINE
Time Period: Establishes the historical context and influences character behavior, societal norms, technology, and major historical events. Key elements include specific historical era or time frame, including contemporary, historical, and futuristic settings.
Geographical Location: Shapes the environment and specific challenges faced by characters, often serving as a critical component of the plot. Key element include physical locations such as continents, countries, cities, and specific environments like jungles, deserts, and urban areas.
Cultural Context: Enriches the narrative by adding depth to character interactions and conflicts, and significantly impacts the story’s progression. Key elements include cultural, social, and ethnic backdrop, including traditions, customs, social norms, and language.
Social Class: Drives character interactions, conflicts, and personal arcs, highlighting societal issues and adding depth to the narrative. Key elements include hierarchical structure of society, including class divisions based on economic, social, or cultural factors.
Ideology and Belief: Influences character motivations, ethical dilemmas, and conflicts, adding layers of complexity to the narrative. Key elements include dominant belief systems, religions, philosophical views, superstitions, and mythology.
Economic and Political Context: Drives the plot by creating conflicts, influencing character motivations, and providing context for the protagonist’s struggles. Key elements include economic conditions, political climate, type of government, and prevailing economic structures.

and return a response in JSON format using this ###TEMPLATE

###TEMPLATE

[{
    "time_period": string len(100,200)
    "geographical_location": string len(100,200)
    "cultural_context": string len(100,200)
    "social_class": string len(100,200)
    "ideology_and_beliefs": string len(100,200)
    "economic_and_political_context": string len(100,200)
}]

See the below ###EXAMPLE

###EXAMPLE

[{
    "time_period": "The screenplay is set in the year 1936, a time between the two World Wars. This period is characterized by significant geopolitical tensions, the rise of Nazi Germany, and an era where archaeology and the search for ancient artifacts were popular and often fraught with danger. The characters' behaviors, such as the militaristic and imperial ambitions of the Nazis, reflect the era's historical context and influence the story's conflicts and motivations.",
    "geographical_location": "The story begins in the dense, lush rainforests of Peru, on the eastern slopes of the Andes, known as 'The Eyebrow of the Jungle.' This setting is characterized by rugged canyon walls, thick mist, and hidden ancient temples. The narrative later transitions to various other locations, including a New England college, Shanghai, Nepal, and Cairo, each contributing unique environmental challenges and cultural elements to the plot.",
    "cultural_context": "The cultural backdrop is richly diverse, ranging from the indigenous Quechua-speaking Yagua Indians in Peru to the cosmopolitan mix of Shanghai and the traditional, bustling streets of Cairo. These varied cultural settings highlight differences in traditions, social norms, and languages, providing depth to character interactions and conflicts. The script also touches on the blend of local and foreign influences, such as the Western characters navigating non-Western societies and the interplay of global powers.",
    "social_class": "The narrative explores distinct social hierarchies and class divisions. Indiana Jones, as a university professor and adventurer, interacts with various social strata, from indigenous porters to high-ranking officials and wealthy collectors. The class dynamics are further highlighted by characters like Marion Ravenwood, who runs a bar in Nepal, and the affluent Belloq, who collaborates with Nazis. These interactions underscore themes of power, exploitation, and the pursuit of knowledge or wealth.",
    "ideology_and_beliefs": "The story delves into various belief systems and ideologies. The indigenous characters in Peru believe in ancient curses and superstitions tied to their sacred sites. The Nazis' obsession with the occult and their belief in harnessing supernatural powers for their regime's benefit contrast sharply with Jones' scientific and adventurous approach to archaeology. The narrative also explores themes of loyalty, betrayal, and the moral dilemmas faced by the characters.",
    "economic_and_political_context": "Set against the backdrop of 1930s global politics, the economic and political climate is tense and unstable. The rise of Nazi Germany and its aggressive expansionism play a critical role in driving the plot, particularly in the Nazis' quest for the Ark of the Covenant. The economic conditions of the era are depicted through the struggles of characters like Marion, who runs a bar to survive, and the funding of expeditions by wealthy patrons or governments, reflecting the broader economic disparities and political motivations of the time."
}]

""";

# Make JSON a separate step since some models have trouble with malformed JSON output (e.g. using illegal single quotes around keys)
prompt_reformat_to_json = f"""
Terrific, can you please reformat the Outline into a valid Python dictionary with 
A. keys=f"{{key_reformat(feature)}}" and 
B. values= corresponding descriptive text strings

key_reformat should make all text legal Python key values using (string).replace(' ','_').lower()

""";
