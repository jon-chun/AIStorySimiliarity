# INSTRUCTIONS:
# 1. Edit the prompt below to insert REFERENCE_FILM: (title and year)
# 2. Upload the ONE test script 
# 3. Submitting this 

# NOTE: OpenAI gpt-3.5-turbo is limited to 16,385 tokens 
#       our smallest script was 64k or 19,547 tokens (largest 249k ~ 80k tokens)
#       
# NOTE: Could use more expensive model with larger context window


prompt_summarize_narrative_all = f"""
###PERSONA:
You are a world-famous narratologist and successful film scriptwriter.

###REFERENCE_FILM:
Raiders of the Lost Ark (1981 film)

###INSTRUCTIONS:
Think carefully step by step to estimate an overall score between (0-100) based on 
the similarity between the attached ###SCRIPT 
and what you know about the above ###REFERENCE_FILM.
Estimate your overall score using similarity of these narrative elements:

1. Character
2. Plot
3. Setting
4. Theme

and return a consise response in this ###TEMPLATE in JSON format
DO NOT respond with anything beyond the JSON data structure

###TEMPLATE
overall: integer range(0,100)
character: integer range(0,100)
plot: integer range(0,100)
setting: integer range(0,100)
theme: integer range(0,100)

character_score_explanation: string len(100,200)

plot_score_explanation: string len(100,200)

setting_score_explanation: string len(100,200)

theme_score_explanation: string len(100,200)

See the below ###EXAMPLE_RESPONSE:

###EXAMPLE_RESPONSE:

[{
    'overall': 72,
    'character': 50,
    'plot': 80,
    'setting': 90,
    'theme': 75,

    'character_score_explanation': "Raiders of the Lost Ark and National Treasure both feature charismatic and determined protagonists (Indiana Jones and Benjamin Gates) who are scholars and adventurers. Both characters possess a deep respect for history and knowledge and are motivated by a mix of personal and ethical reasons to pursue their quests. However, Indiana Jones is more rugged and physically adept, often relying on his combat skills and resourcefulness, while Benjamin Gates is more cerebral, frequently using his intellect and puzzle-solving abilities. The supporting characters in both films also play crucial roles, but Indy's relationships are often more complex and emotionally charged, whereas Ben's are more collaborative and supportive, particularly with Abigail Chase and Riley Poole. The antagonists in both films are driven by greed and power, yet Belloq from Raiders of the Lost Ark is portrayed with a more intense rivalry and deeper philosophical opposition to Indy compared to Ian Howe's straightforward villainy in National Treasure.",

    'plot_score_explanation': "The plots of Raiders of the Lost Ark and National Treasure revolve around the race to uncover and protect historical artifacts, blending adventure with elements of mystery and suspense. Both films involve a series of clues and puzzles that lead the protagonists to their goals while evading rival treasure hunters. Raiders of the Lost Ark is more action-oriented, with numerous high-stakes chases and confrontations, and a greater emphasis on physical danger and combat. In contrast, National Treasure focuses more on intellectual challenges and historical riddles, with a modern-day setting that incorporates advanced technology and heist elements. The stakes in Raiders of the Lost Ark are tied to supernatural forces and world-altering consequences, while National Treasure has a patriotic undercurrent, emphasizing the protection of national heritage and historical legacy.",

    'setting_score_explanation': "Both Raiders of the Lost Ark and National Treasure feature diverse and exotic settings that play a crucial role in the narrative. Raiders of the Lost Ark spans multiple countries, including Peru, Nepal, and Egypt, immersing the audience in ancient ruins and archaeological sites that enhance the film's adventurous tone. The historical period of the 1930s adds an element of pre-World War II tension and authenticity. In contrast, National Treasure is set in contemporary times, primarily in the United States, with significant scenes in Washington D.C., Philadelphia, and New York. This modern setting incorporates well-known American landmarks and historical sites, creating a sense of national pride and historical intrigue. While Raiders of the Lost Ark emphasizes a more global and historical exploration, National Treasure focuses on the rich historical tapestry within the United States, using familiar locations to ground its narrative in a modern context.",

    'theme_score_explanation': "The themes in Raiders of the Lost Ark and National Treasure both revolve around the importance of history, the preservation of knowledge, and the ethical responsibilities of those who uncover it. Raiders of the Lost Ark explores themes of power and corruption, the supernatural, and the conflict between science and faith. The film delves into the dangers of exploiting ancient artifacts for personal gain and the moral imperative to protect cultural heritage. National Treasure, while sharing the theme of historical preservation, places a stronger emphasis on patriotism and the founding principles of the United States. It highlights the idea of uncovering hidden truths about national identity and heritage, with a more optimistic and educational tone. The interplay between personal ambition and the greater good is a common thread, but Raiders of the Lost Ark presents it with a darker, more cautionary perspective, whereas National Treasure frames it as a journey of discovery and enlightenment.",
}]

###FINAL_INSTRUCTIONS:
DO NOT respond with anything beyond the JSON data structure
""";