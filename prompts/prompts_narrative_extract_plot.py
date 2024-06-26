prompt_extract_characters = f"""
###PERSONA:
You are a world-famous narratologist and successful film scriptwriter.

###INSTRUCTIONS:
Think carefully step by step to order to analyze the attached MOVIE SCRIPT to
identify all the plot points with detailed descriptions
and organize them into a JSON response using this ###PLOT_OUTLINE 


###PLOT_OUTLINE
Protagonist Introduction: Introduces the main character, showcasing their core traits, current status, and immediate goals within their environment.
Inciting Incident: Presents a disruptive event that propels the protagonist into the main conflict and introduces the stakes.
Rising Action: Develops the main conflict through a series of escalating challenges, character development, and introduction of key relationships.
Climax: Features the story's turning point where the main conflict reaches peak tension, leading to a critical decision or action by the protagonist.
Resolution: Concludes the main conflict, showing the immediate outcome of the climax and tying up loose ends.
Consequences: Explores the immediate and short-term effects of the climax on the protagonist and other characters.
Final Outcome: Establishes the new status quo for the protagonist and key characters, concluding their arcs.
Loose Ends: Addresses any remaining unanswered questions or unresolved plot points, often hinting at future possibilities.
Subplots: Enrich the main narrative with secondary storylines that develop supporting characters and reflect or contrast with the main themes.

and return a response in JSON format using this ###TEMPLATE

###TEMPLATE

[{
    "protagonist_intro": string len(100,200)
    "inciting_incident": string len(100,200)
    "rising_action": string len(100,200)
    "climax": string len(100,200)
    "resolution": string len(100,200)
    "consequences": string len(100,200)
    "final_outcome": string len(100,200)
    "loose_ends": string len(100,200)
    "subplots": string len(100,200)
}]

See the below ###EXAMPLE

###EXAMPLE

[{
    "protagonist_introduction": "Indiana Jones, a rugged archaeologist, is introduced in the dense jungles of Peru in 1936. He is portrayed as fearless and resourceful, navigating treacherous terrain and ancient traps in pursuit of a golden idol, showcasing his bravery, expertise, and quick thinking.",
    "inciting_incident": "Indy learns from Army Intelligence agents that the Nazis are searching for the Ark of the Covenant, which is believed to grant invincible power to its possessor. This discovery propels him into a race against time to prevent the Nazis from acquiring the Ark.",
    "rising_action": "The main conflict develops as Indy faces a series of escalating challenges: finding the medallion in Nepal, deciphering its significance, traveling to Egypt, and uncovering the Ark’s location. He encounters numerous obstacles, including confrontations with rival archaeologist Belloq, Nazi soldiers, and various traps. Relationships with key characters like Marion Ravenwood and Sallah are further developed.",
    "climax": "The climax occurs when Indy and Marion are captured by the Nazis on a remote island. Belloq performs a ritual to open the Ark, which leads to a terrifying and supernatural event. The wrath of God is unleashed, killing the Nazis and Belloq while Indy and Marion survive by not looking at the Ark during its activation.",
    "resolution": "Following the supernatural destruction of the Nazis, Indy and Marion escape the island with their lives. The Ark is recovered by the United States government and taken to a secretive location for study, but Indy’s desire for further exploration and understanding remains unfulfilled.",
    "consequences": "The immediate aftermath sees Indy and Marion safe but discontent with the government’s secrecy regarding the Ark. Their efforts prevented the Nazis from harnessing its power, but the Ark remains an enigma, stored away in a vast warehouse among countless other artifacts.",
    "final_outcome": "Indy returns to his academic life, but the adventure has rekindled his passion for archaeology and the pursuit of ancient mysteries. Marion stays with him, hinting at a renewed relationship as they look forward to future adventures.",
    "loose_ends": "The government’s handling of the Ark raises questions about what other powerful artifacts are hidden away and what their potential impact could be. The secrecy surrounding the Ark suggests possible future conflicts or adventures involving hidden treasures.",
    "subplots": "Several subplots enrich the main narrative, including Indy’s tumultuous relationship with Marion, who evolves from a bar owner in Nepal to a brave companion. Another subplot involves Sallah’s aid in Cairo, highlighting themes of loyalty and friendship. The rivalry between Indy and Belloq underscores the ethical contrasts in their approaches to archaeology."
}]

""";

# Make JSON a separate step since some models have trouble with malformed JSON output (e.g. using illegal single quotes around keys)
prompt_reformat_to_json = f"""
Terrific, can you please reformat this Outline into a valid Python dictionary with 
A. keys=f"{{key_reformat(feature)}}" and 
B. values= corresponding descriptive text strings

key_reformat should make all text legal Python key values using (string).replace(' ','_').lower()

""";
