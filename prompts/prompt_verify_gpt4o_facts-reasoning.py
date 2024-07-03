# NOTE: for OpenAI ChatUI, pasting JSON is INLINE (not as an attachement)

prompt_str = """
###REFERENCE_FILM:
Raiders of the Lost Ark (1981)

###TEST_FILM:
Office Space (1999)

###PERSONA:
You are a world-famous narratologist and successful film scriptwriter. 

###SIMILARITY SCORES:
0. 'overall'
1. 'characters'
2. 'plot'
3. 'setting'
4. 'themes'

###INSTRUCTIONS:
You are a world-famous narratologist and successful film scriptwriter 
so precisely and carefully think step by step to
CRITIQUE the above ###INPUT_JSON containing 5 similarity scores and corresponding reasoning for each
similarities between the above ###REFERENCE_FILM and above ###TEST_FILM

If any FACTUAL or REASONING errors exist in the above ###INPUT_JSON data, enumerate them in using the below ###TEMPLATE
and use them to estimate an 'accuracy' score (0-100) for each SIMILARITY_SCORE 

if none exist, let "accuracy" =100 and "reason"="None" 
else estimate an "accuracy" score (0-100) with a written "reason"

Return your response in JSON form following this ###TEMPLATE as demonstrated in the ###EXAMPLE below

###TEMPLATE

{
    "accuracy_overall_score": integer range(0,100),
    "accuracy_characters_score": integer range(0,100),
    "accuracy_plot_score": integer range(0,100),
    "accuracy_setting_score": integer range(0,100),
    "accuracy_themes_score": integer range(0,100),
    "factual_errors": list[string len(10,50)],
    "reasoning_errors": string len(200,500)
}
""";