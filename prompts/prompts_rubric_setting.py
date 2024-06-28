prompt_similarity_setting_referencefilm = f"""
###REFERENCE_FILM:
""";

prompt_similarity_setting_testfilm = f"""
###TEST_FILM:
""";

prompt_similarity_setting = """
###PERSONA:
You are a world-famous narratologist and successful film scriptwriter.

###RUBRIC:
Time Period: Establishes the historical context and influences character behavior, societal norms, technology, and major historical events. Key elements include specific historical era or time frame, including contemporary, historical, and futuristic settings.
Geographical Location: Shapes the environment and specific challenges faced by characters, often serving as a critical component of the plot. Key element include physical locations such as continents, countries, cities, and specific environments like jungles, deserts, and urban areas.
Cultural Context: Enriches the narrative by adding depth to character interactions and conflicts, and significantly impacts the story’s progression. Key elements include cultural, social, and ethnic backdrop, including traditions, customs, social norms, and language.
Social Class: Drives character interactions, conflicts, and personal arcs, highlighting societal issues and adding depth to the narrative. Key elements include hierarchical structure of society, including class divisions based on economic, social, or cultural factors.
Ideology and Belief: Influences character motivations, ethical dilemmas, and conflicts, adding layers of complexity to the narrative. Key elements include dominant belief systems, religions, philosophical views, superstitions, and mythology.
Economic and Political Context: Drives the plot by creating conflicts, influencing character motivations, and providing context for the protagonist’s struggles. Key elements include economic conditions, political climate, type of government, and prevailing economic structures.

###INSTRUCTIONS:
Think carefully step by step to estimate an estimated similarity score between (0-100)
for the features in the above ###RUBRIC
between the above ###TEST_FILM and the above ###REFERENCE_FILM

Based upon these ###RUBRIC similiarities, 
give a FINAL similarity_overall score for these two films
and return the valid JSON structure using the following ###TEMPLATE by
populating the JSON structure in ###EXAMPLE
(Be sure to use double quotes and trailing commas)

###TEMPLATE

{
    "reference_film": {
        "film_title": string len(,50),
        "features": {
            "time_period": string len(100,200),
            "geographical_location": string len(100,200),
            "cultural_context": string len(100,200),
            "social_class": string len(100,200),
            "ideology_and_beliefs": string len(100,200),
            "economic_and_political_context": string len(100,200)
        },
    },
    "test_film": {
        "film_title": string len(,50),
        "features": {
            "time_period": string len(100,200),
            "geographical_location": string len(100,200),
            "cultural_context": string len(100,200),
            "social_class": string len(100,200),
            "ideology_and_beliefs": string len(100,200),
            "economic_and_political_context": string len(100,200)
        },
    },
    "similarity_by_features": {
        "film_title": string len(,50),
        "features": {
            "time_period": integer range(0,100),
            "geographical_location": integer range(0,100),
            "cultural_context": integer range(0,100),
            "social_class": integer range(0,100),
            "ideology_and_beliefs": integer range(0,100),
            "economic_and_political_context": integer range(0,100)
        },
    },
    "similarity_overall" : integer range(0,100)
}

###EXAMPLE:

```json
{
    "reference_film": {
        "film_title": "",
        "features": {
            "time_period": "",
            "geographical_location": "",
            "cultural_context": "",
            "social_class": "",
            "ideology_and_beliefs": "",
            "economic_and_political_context": ""
        }
    },
    "test_film": {
        "film_title": "",
        "features": {
            "time_period": "",
            "geographical_location": "",
            "cultural_context": "",
            "social_class": "",
            "ideology_and_beliefs": "",
            "economic_and_political_context": ""
        }
    },
    "similarity_by_features": {
        "film_title": "",
        "features": {
            "time_period": 0,
            "geographical_location": 0,
            "cultural_context": 0,
            "social_class": 0,
            "ideology_and_beliefs": 0,
            "economic_and_political_context": 0
        }
    },
    "similarity_overall": 0
}
```
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
Time Period: Establishes the historical context and influences character behavior, societal norms, technology, and major historical events. Key elements include specific historical era or time frame, including contemporary, historical, and futuristic settings.
Geographical Location: Shapes the environment and specific challenges faced by characters, often serving as a critical component of the plot. Key element include physical locations such as continents, countries, cities, and specific environments like jungles, deserts, and urban areas.
Cultural Context: Enriches the narrative by adding depth to character interactions and conflicts, and significantly impacts the story’s progression. Key elements include cultural, social, and ethnic backdrop, including traditions, customs, social norms, and language.
Social Class: Drives character interactions, conflicts, and personal arcs, highlighting societal issues and adding depth to the narrative. Key elements include hierarchical structure of society, including class divisions based on economic, social, or cultural factors.
Ideology and Belief: Influences character motivations, ethical dilemmas, and conflicts, adding layers of complexity to the narrative. Key elements include dominant belief systems, religions, philosophical views, superstitions, and mythology.
Economic and Political Context: Drives the plot by creating conflicts, influencing character motivations, and providing context for the protagonist’s struggles. Key elements include economic conditions, political climate, type of government, and prevailing economic structures.

###INSTRUCTIONS:
Think carefully step by step to estimate an estimated similarity score between (0-100)
for the features in the above ###RUBRIC
between the above ###TEST_FILM and the above ###REFERENCE_FILM

Based upon these ###RUBRIC similiarities, 
give a FINAL similarity_overall score for these two films
using the following ###TEMPLATE:

and return a response in a valid Python Dictionary format using this ###TEMPLATE

###TEMPLATE

{
    "reference_film": {
        "film_title": string len(,50),
        "features": {
            "time_period": string len(100,200),
            "geographical_location": string len(100,200),
            "cultural_context": string len(100,200),
            "social_class": string len(100,200),
            "ideology_and_beliefs": string len(100,200),
            "economic_and_political_context": string len(100,200)
        },
    },
    "test_film": {
        "film_title": string len(,50),
        "features": {
            "time_period": string len(100,200),
            "geographical_location": string len(100,200),
            "cultural_context": string len(100,200),
            "social_class": string len(100,200),
            "ideology_and_beliefs": string len(100,200),
            "economic_and_political_context": string len(100,200)
        },
    },
    "similarity_by_features": {
        "film_title": string len(,50),
        "features": {
            "time_period": integer range(0,100),
            "geographical_location": integer range(0,100),
            "cultural_context": integer range(0,100),
            "social_class": integer range(0,100),
            "ideology_and_beliefs": integer range(0,100),
            "economic_and_political_context": integer range(0,100)
        },
    }
    "similarity_overall" : integer range(0,100)
} 

##### <RESPONSE> #####

[{
    "reference_film": {
        "film_title": "Raiders of the Lost Ark",
        "features": {
            "time_period": "Set in the 1930s, during the lead-up to World War II, reflecting the geopolitical tensions and technological limitations of the era.",
            "geographical_location": "Primarily set in various international locations including the jungles of South America, Cairo, and a secret Nazi island base.",
            "cultural_context": "Incorporates diverse cultures such as indigenous tribes, Middle Eastern society, and Western colonial presence, highlighting cultural conflicts and cooperation.",
            "social_class": "Depicts a range of social classes from impoverished villagers to wealthy collectors, with a focus on the academic and military elite.",
            "ideology_and_beliefs": "Explores ideologies of the time, including Nazi occultism, archaeological ethics, and the tension between science and superstition.",
            "economic_and_political_context": "Reflects the global economic challenges of the Great Depression and the political machinations of Nazi Germany seeking world domination."
        }
    },
    "test_film": {
        "film_title": "National Treasure",
        "features": {
            "time_period": "Set in contemporary times (2000s), reflecting modern technology, communication methods, and societal norms.",
            "geographical_location": "Primarily set in the United States, with key locations including Washington D.C., Philadelphia, and New York City.",
            "cultural_context": "Focuses on American history and culture, particularly the founding fathers and the revolutionary era, with a modern twist.",
            "social_class": "Depicts a range of social classes from historians and academics to high-ranking government officials and the wealthy elite.",
            "ideology_and_beliefs": "Explores American ideals of freedom, patriotism, and the importance of history, with a focus on the ethical implications of treasure hunting.",
            "economic_and_political_context": "Reflects the political landscape of post-9/11 America, with an emphasis on national security, historical preservation, and governmental authority."
        }
    },
    "similarity_by_features": {
        "film_title": "National Treasure",
        "features": {
            "time_period": 50,
            "geographical_location": 60,
            "cultural_context": 65,
            "social_class": 70,
            "ideology_and_beliefs": 75,
            "economic_and_political_context": 65
        },
        "similarity_overall": 64
    }
}]


""";