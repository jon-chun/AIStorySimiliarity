prompt_extract_characters = f"""
###PERSONA:
You are a world-famous narratologist and successful film scriptwriter.

###INSTRUCTIONS:
Think carefully step by step to order to analyze the attached MOVIE SCRIPT to
identify all the main characters (e.g. protagonist, sidekick, antagonists, henchman) and
for each main character, give a detailed description using this ###CHARACTER_OUTLINE 


###CHARACTER_OUTLINE
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

and return a response in JSON format using this ###TEMPLATE

###TEMPLATE

[{
    "name": string len(,50) {
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
    "name": string len(,50) {
        "role": ...


See the below ###EXAMPLE

###EXAMPLE

[{
    "dr_henry_walton_indiana_jones_jr": {
        "role": "Protagonist. Indiana Jones is the main character driving the action, as an adventurous archaeologist and professor seeking to recover important historical artifacts.",
        "backstory": "Indiana Jones, known as 'Indy,' is a well-traveled archaeologist with a Ph.D. He is a professor at Marshall College but often embarks on dangerous expeditions to recover artifacts, motivated by a strong sense of preserving history and cultural heritage. He has a complicated relationship with his father, Dr. Henry Jones, Sr., who is also an archaeologist.",
        "strengths": "Highly knowledgeable in archaeology, skilled in hand-to-hand combat, proficient with a whip, multilinguistic, and resourceful in escaping dangerous situations.",
        "weaknesses": "Fear of snakes (ophidiophobia), sometimes overly confident, can be reckless in pursuit of artifacts, strained personal relationships.",
        "psychology": "High openness to experience, conscientious, moderately extraverted, agreeable, low neuroticism. Indy is curious, adventurous, responsible, and often displays a rugged charm.",
        "beliefs": "Strong belief in the preservation of history and cultural heritage, a sense of duty to protect ancient artifacts from falling into the wrong hands.",
        "motivations": "Driven by a passion for archaeology and history, a desire to outwit his rivals, particularly Belloq, and a commitment to preventing powerful artifacts from being misused.",
        "social_dynamics": "Indy often works alone but collaborates with trusted allies like Marcus Brody and Sallah. He has a tumultuous relationship with Marion Ravenwood, which evolves over the story.",
        "arc": "Indiana Jones starts as a confident, somewhat solitary adventurer but grows to recognize the importance of allies and relationships, particularly with Marion. He also evolves in his understanding of the artifacts he seeks, appreciating their cultural significance beyond their immediate value."
    },
    "marion_ravenwood": {
        "role": "Sidekick and romantic interest. Marion assists Indy in his quest and has a personal history with him, adding emotional depth to the story.",
        "backstory": "Marion is the daughter of Abner Ravenwood, Indy's former mentor. She has a history with Indy, having been romantically involved with him years earlier. After her father's disappearance, she took over his bar in Nepal.",
        "strengths": "Strong-willed, resourceful, capable in combat, particularly with makeshift weapons, and resilient in the face of danger.",
        "weaknesses": "Can be impulsive and headstrong, has unresolved issues with Indy from their past relationship.",
        "psychology": "High openness and extraversion, moderate conscientiousness and agreeableness, low neuroticism. Marion is adventurous, assertive, and emotionally resilient.",
        "beliefs": "Values independence and self-reliance, has a deep-seated sense of loyalty to her father's legacy.",
        "motivations": "Initially driven by financial survival and personal grievances against Indy, she gradually aligns her goals with Indy's quest to secure the Ark.",
        "social_dynamics": "Her interactions with Indy are initially contentious but evolve into a partnership based on mutual respect and affection. She is also protective and caring towards those she considers allies.",
        "arc": "Marion's arc involves reconciling her past with Indy and finding a renewed sense of purpose. She transforms from a bar owner struggling to make ends meet to a vital partner in Indy's quest."
    },
    ...

}]
""";

# Make JSON a separate step since some models have trouble with malformed JSON output (e.g. using illegal single quotes around keys)
prompt_reformat_to_json = f"""
Terrific, can you please reformat the Outlines for each character in a valid Python nested dictionary with 
A. keys=f"{{key_reformat(Name)}}" and 
B. values=a nested dictionary with keys()=('role','backstory','strengths','weaknesses','psychology','beliefs','motivations','social_dynamics','arc') and values()=corresponding text strings

key_reformat should make all text legal Python key values using (string).replace(' ','_').lower()

""";
