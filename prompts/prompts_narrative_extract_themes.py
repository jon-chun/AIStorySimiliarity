prompt_extract_characters = f"""
###PERSONA:
You are a world-famous narratologist and successful film scriptwriter.

###INSTRUCTIONS:
Think carefully step by step to order to analyze the attached MOVIE SCRIPT to
identify all the themes along with detailed descriptions
and organize them with this partially nested JSON ###THEMES_OUTLINE 


###THEMES_OUTLINE
Main Theme: The central idea or message that permeates the entire narrative and ties all story elements together.
Secondary Themes: Supporting ideas that complement or contrast with the main theme, adding depth and complexity to the narrative.
Tertiary Themes: Minor thematic elements that appear less frequently but contribute to the overall thematic richness of the story.
Resolution Main Theme: How the central theme is concluded or crystallized by the end of the narrative, often reflecting character growth or plot resolution.
Resolution Secondary Themes: The way supporting themes are addressed or resolved in relation to the main theme and overall story arc.
Resolution Tertiary Themes: How minor thematic elements are tied up or integrated into the larger thematic resolution of the story.

and return a response in nested JSON format using this ###TEMPLATE

###TEMPLATE
[{
    "main_theme": string len(100,200),
    "secondary_themes": {
        "secondary_theme_0": string len(100,200),
        "secondary_theme_1": string len(100,200),
        ...
    },
    "tertiary_themes": {
        "tertiary_theme_0": string len(100,200),
        "tertiary_theme_1": string len(100,200),
        ...  
    },
    "resolution_main_them": string len(100,200),
    "resolution_secondary_themes": {
        "resolution_secondary_theme_0": string len(100,200),
        "resolution_secondary_theme_1": string len(100,200),
        ...  
    },
    "resolution_tertiary_themes": {
        "resolution_tertiary_theme_0": string len(100,200),
        "resolution_tertiary_theme_1": string len(100,200),
        ...     
    }
}]

See the below ###EXAMPLE

###EXAMPLE

[{
    "main_theme": "The central idea of 'Lara Croft: Tomb Raider' revolves around the pursuit of knowledge and the relentless quest for discovery. Lara Croft embodies the archetype of an adventurer who is driven by a deep-seated need to uncover hidden truths, often at great personal risk. This theme is expressed through her exploration of ancient tombs, her confrontation with formidable foes, and her unwavering commitment to solving historical mysteries.",
    "secondary_themes": {
        "courage_and_resilience": "Throughout the narrative, Lara demonstrates immense courage and resilience, overcoming physical and emotional challenges. Her encounters with traps, enemies, and personal losses highlight her indomitable spirit.",
        "legacy_and_heritage": "The film explores the concept of legacy, particularly through Lara's relationship with her deceased parents and her desire to honor their memory by continuing their work. This theme is intertwined with her personal growth and her understanding of her place in the world.",
        "friendship_and_loyalty": "Lara's interactions with allies like Karak and Carlos showcase themes of friendship and loyalty. These relationships provide emotional support and practical assistance, emphasizing the importance of trust and camaraderie in her dangerous quests."
    },
    "tertiary_themes": {
        "betrayal_and_deception": "The script includes elements of betrayal and deception, particularly from antagonists like Malvern and his henchmen. These minor themes add complexity to the plot and create tension.",
        "technology_vs_tradition": "Lara often uses advanced technology to navigate ancient, traditional environments, highlighting the juxtaposition and sometimes the conflict between modernity and antiquity.",
        "environmental_awareness": "The settings, from the Amazon jungle to Himalayan monasteries, emphasize the beauty and peril of the natural world, subtly promoting an awareness of and respect for the environment."
    },
    "resolution_main_theme": "By the end of the narrative, the central theme of the quest for knowledge is resolved through Lara's successful discoveries and her realization of deeper personal truths. Her journey leads to significant historical findings, but also to a greater understanding of her own identity and purpose.",
    "resolution_secondary_themes": {
        "courage_and_resilience": "Lara's resilience is rewarded as she emerges victorious despite numerous obstacles. Her bravery is acknowledged and solidified, demonstrating her growth as a character.",
        "legacy_and_heritage": "Lara honors her parents' legacy by completing their unfinished work, and she finds a sense of closure and continuity. Her achievements ensure that her family's contributions to history are recognized and preserved.",
        "friendship_and_loyalty": "The bonds of friendship and loyalty are strengthened as Lara and her allies survive and succeed together. These relationships are validated through their mutual support and shared triumphs."
    },
    "resolution_tertiary_themes": {
        "betrayal_and_deception": "The themes of betrayal are resolved as the antagonists' schemes are thwarted, and justice prevails. Lara's ability to navigate deceitful situations underscores her intelligence and adaptability.",
        "technology_vs_tradition": "The successful integration of technology in traditional settings reaffirms the theme that progress can be achieved without abandoning the past. Lara's use of modern tools to unlock ancient secrets bridges the gap between eras.",
        "environmental_awareness": "The story's conclusion, with its varied and vibrant settings, leaves a lasting impression of the world's diverse environments. This subtly encourages respect for nature and an understanding of its importance in our shared heritage."
    }
}]
""";

# Make JSON a separate step since some models have trouble with malformed JSON output (e.g. using illegal single quotes around keys)
prompt_reformat_to_json = f"""
Terrific, can you please reformat this Outline into a valid Python dictionary with 
A. keys=f"{{key_reformat(feature)}}" and 
B. values= corresponding descriptive text strings

key_reformat should make all text legal Python key values using (string).replace(' ','_').lower()

""";
