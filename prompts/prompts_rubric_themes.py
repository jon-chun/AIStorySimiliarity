prompt_similarity_themes_referencefilm = f"""
###REFERENCE_FILM:
""";

prompt_similarity_themes_referencefilm = f"""
###TEST_FILM:
""";

prompt_similarity_themes = """
###PERSONA:
You are a world-famous narratologist and successful film scriptwriter.

###RUBRIC:
Main Theme: The central idea or message that permeates the entire narrative and ties all story elements together.
Secondary Themes: Supporting ideas that complement or contrast with the main theme, adding depth and complexity to the narrative.
Tertiary Themes: Minor thematic elements that appear less frequently but contribute to the overall thematic richness of the story.
Resolution Main Theme: How the central theme is concluded or crystallized by the end of the narrative, often reflecting character growth or plot resolution.
Resolution Secondary Themes: The way supporting themes are addressed or resolved in relation to the main theme and overall story arc.
Resolution Tertiary Themes: How minor thematic elements are tied up or integrated into the larger thematic resolution of the story.

###INSTRUCTIONS:
Think carefully step by step to estimate an estimated similarity score between (0-100)
for the features in the above ###RUBRIC
between the above ###TEST_FILM and the above ###REFERENCE_FILM

Based upon these ###RUBRIC similiarities, 
give a FINAL similarity_overall score for these two films
using the following ###TEMPLATE:

and return a response in JSON format using this ###TEMPLATE

###TEMPLATE

[{
    "reference_film": {
        "film_title": string len(,50),
        "features": {
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
        },
    },
    "test_film": {
        "film_title": string len(,50),
        "features": {
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
        },
    },
    "similarity_by_features": {
        "features": {
            "main_theme": integer range(0,100),
            "secondary_themes": integer range(0,100),
            "tertiary_themes": integer range(0,100),
            "resolution_main_them": integer range(0,100),
            "resolution_secondary_themes": integer range(0,100),
            "resolution_tertiary_themes": integer range(0,100),
        },
    },
    "similarity_overall": integer range(0,100)
}] 
""";


"""
##### <PROMPT> #####

###REFERENCE_FILM:
Raiders of the Lost Ark (1981 film)

###TEST_FILM:
National Treasure (2004 film)

###PERSONA:
You are a world-famous narratologist and successful film scriptwriter.

###RUBRIC:
Main Theme: The central idea or message that permeates the entire narrative and ties all story elements together.
Secondary Themes: Supporting ideas that complement or contrast with the main theme, adding depth and complexity to the narrative.
Tertiary Themes: Minor thematic elements that appear less frequently but contribute to the overall thematic richness of the story.
Resolution Main Theme: How the central theme is concluded or crystallized by the end of the narrative, often reflecting character growth or plot resolution.
Resolution Secondary Themes: The way supporting themes are addressed or resolved in relation to the main theme and overall story arc.
Resolution Tertiary Themes: How minor thematic elements are tied up or integrated into the larger thematic resolution of the story.

###INSTRUCTIONS:
Think carefully step by step to estimate an estimated similarity score between (0-100)
for the features in the above ###RUBRIC
between the above ###TEST_FILM and the above ###REFERENCE_FILM

Based upon these ###RUBRIC similiarities, 
give a FINAL similarity_overall score for these two films
using the following ###TEMPLATE:

and return a response in JSON format using this ###TEMPLATE

###TEMPLATE

[{
    "reference_film": {
        "film_title": string len(,50),
        "features": {
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
        },
    },
    "test_film": {
        "film_title": string len(,50),
        "features": {
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
        },
    },
    "similarity_by_features": {
        "features": {
            "main_theme": integer range(0,100),
            "secondary_themes": integer range(0,100),
            "tertiary_themes": integer range(0,100),
            "resolution_main_them": integer range(0,100),
            "resolution_secondary_themes": integer range(0,100),
            "resolution_tertiary_themes": integer range(0,100),
        },
    },
    "similarity_overall": integer range(0,100)
}] 

##### <RESPONSE> #####

[{
    "reference_film": {
        "film_title": "Raiders of the Lost Ark",
        "features": {
            "main_theme": "The pursuit of knowledge and the ethical implications of its use.",
            "secondary_themes": {
                "secondary_theme_0": "The battle between good and evil.",
                "secondary_theme_1": "The value of history and cultural heritage.",
                "secondary_theme_2": "Courage and heroism in the face of danger."
            },
            "tertiary_themes": {
                "tertiary_theme_0": "Romantic relationships as a subplot.",
                "tertiary_theme_1": "The role of faith and belief in the supernatural."
            },
            "resolution_main_theme": "The Ark's power vindicates Jones's belief in its significance, highlighting the importance of knowledge and its responsible use.",
            "resolution_secondary_themes": {
                "resolution_secondary_theme_0": "The destruction of the Nazis underscores the triumph of good over evil.",
                "resolution_secondary_theme_1": "The Ark's placement in a government warehouse signifies the importance of preserving history.",
                "resolution_secondary_theme_2": "Jones's survival and success reinforce the themes of courage and heroism."
            },
            "resolution_tertiary_themes": {
                "resolution_tertiary_theme_0": "The resolution of Jones's romantic subplot with Marion.",
                "resolution_tertiary_theme_1": "The confirmation of the supernatural elements of the Ark."
            }
        }
    },
    "test_film": {
        "film_title": "National Treasure",
        "features": {
            "main_theme": "The pursuit of historical truths and the value of knowledge.",
            "secondary_themes": {
                "secondary_theme_0": "Patriotism and national heritage.",
                "secondary_theme_1": "The importance of family legacy.",
                "secondary_theme_2": "Courage and ingenuity in overcoming obstacles."
            },
            "tertiary_themes": {
                "tertiary_theme_0": "Romantic relationships as a subplot.",
                "tertiary_theme_1": "The ethics of treasure hunting."
            },
            "resolution_main_theme": "The successful discovery of the treasure validates Gates's pursuit of knowledge and highlights the importance of historical truths.",
            "resolution_secondary_themes": {
                "resolution_secondary_theme_0": "The treasure's discovery reinforces the value of national heritage.",
                "resolution_secondary_theme_1": "Gates's family legacy is restored and honored.",
                "resolution_secondary_theme_2": "Gates's cleverness and bravery are rewarded."
            },
            "resolution_tertiary_themes": {
                "resolution_tertiary_theme_0": "The resolution of Gates's romantic subplot with Abigail.",
                "resolution_tertiary_theme_1": "The ethical considerations of treasure hunting are acknowledged."
            }
        }
    },
    "similarity_by_features": {
        "features": {
            "main_theme": 85,
            "secondary_themes": 75,
            "tertiary_themes": 70,
            "resolution_main_theme": 80,
            "resolution_secondary_themes": 75,
            "resolution_tertiary_themes": 70
        }
    },
    "similarity_overall": 76
}]
`
""";