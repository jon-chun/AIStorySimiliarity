characters_features_count = 9

characters_weights_dict = {
    "characters": {
        "role": int(100*(1/characters_features_count)),
        "backstory": int(100*(1/characters_features_count)),
        "strengths": int(100*(1/characters_features_count)),
        "weaknesses": int(100*(1/characters_features_count)),
        "psychology": int(100*(1/characters_features_count)),
        "beliefs": int(100*(1/characters_features_count)),
        "motivations": int(100*(1/characters_features_count)),
        "social_dynamics": int(100*(1/characters_features_count)),
        "arc": int(100*(1/characters_features_count))
    },
}

plot_features_count = 9

plot_weights_dict = {

    "protagonist_intro": int(100*(1/plot_features_count)),
    "inciting_incidents": int(100*(1/plot_features_count)),
    "rising_action": int(100*(1/plot_features_count)),
    "climax": int(100*(1/plot_features_count)),
    "resolution": int(100*(1/plot_features_count)),
    "consequences": int(100*(1/plot_features_count)),
    "final_outcome": int(100*(1/plot_features_count)),
    "loose_ends": int(100*(1/plot_features_count)),
    "subplots": int(100*(1/plot_features_count))
}

setting_features_count = 6

setting_weights_dict = {
    "time_period": int(100*(1/setting_features_count)),
    "geographical_location": int(100*(1/setting_features_count)),
    "cultural_context": int(100*(1/setting_features_count)),
    "social_class": int(100*(1/setting_features_count)),
    "ideology_and_beliefs": int(100*(1/setting_features_count)),
    "economic_and_political_context": int(100*(1/setting_features_count))
}

themes_features_count = 6

themes_weights_dict = {
    "main_theme": int(100*(1/themes_features_count)),
    "secondary_themes": int(100*(1/themes_features_count)),
    "tertiary_themes": int(100*(1/themes_features_count)),
    "resolution_main_theme": int(100*(1/themes_features_count)),
    "resolution_secondary_themes": int(100*(1/themes_features_count)),
    "resolution_tertiary_themes": int(100*(1/themes_features_count)),
}
