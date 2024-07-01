### ELEMENT_FEATURES
Name: Full name of character
Role: Clarifies the character's function within the story, whether they are driving the action, supporting the protagonist, or creating obstacles.
Backstory: This attribute helps to understand the formative experiences that shaped each character, providing insights into their motivations and behaviors.
Strengths: Highlights unique abilities and proficiencies, distinguishing characters by their specific talents and expertise.
Weaknesses: Humanizes characters by revealing vulnerabilities and personal challenges, making them more relatable and multi-dimensional.
Psychology: Uses personality assessments, such as the Big 5 OCEAN (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism) model, to offer deeper insight into character traits.
Beliefs: Offers a window into the ethical and moral framework guiding each character's decisions, crucial for understanding their actions in moral dilemmas.
Motivations: Describes what drives the character to act, including desires, fears, and goals.
Social Dynamics: Explores the nature of interactions between characters, which can be pivotal in character development and plot progression.
Arc: Summarizes how the character changes or grows for better or worse over the story in response to events, decisions, and actions taken.

### TEMPLATE

{
    "overall": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "backstory": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "strengths": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "weakness": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "psychology": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)  
    },
    "beliefs": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200) 
    },
    "motivations": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "social_dynamics": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    },
    "arc": {
        "similarity": integer range(0,100),
        "reasoning": string len(100,200)
    }
}

### ANALYSIS

**Indiana Jones (Raiders of the Lost Ark) vs. Ben Gates (National Treasure)**

#### Role
- **Similarity**: 90
- **Reasoning**: Both characters serve as the protagonists who drive the action in pursuit of historical treasures. They lead quests and face adversities while seeking valuable artifacts. Indiana Jones is an archaeologist and professor, while Ben Gates is a historian and treasure hunter, creating a close parallel in their roles.

#### Backstory
- **Similarity**: 75
- **Reasoning**: Indiana Jones' backstory is more focused on his professional career and experiences shaping his ethical stance, while Ben Gates' backstory is deeply rooted in family legacy and tradition. Both characters have backgrounds tied to historical pursuits, with a strong family influence in Gates' case.

#### Strengths
- **Similarity**: 85
- **Reasoning**: Both characters share intelligence, resourcefulness, and deep historical knowledge. Indiana Jones has additional combat and survival skills, while Gates' strengths are more academically focused. They both exhibit a high degree of determination and problem-solving abilities.

#### Weaknesses
- **Similarity**: 70
- **Reasoning**: Both characters have weaknesses that can lead to reckless behavior. Indiana's impulsiveness and fear of snakes are more specific, while Gates' obsession with treasure is more directly tied to his motivations. These vulnerabilities make them more relatable and multidimensional.

#### Psychology
- **Similarity**: 85
- **Reasoning**: They share high openness, conscientiousness, and relatively low neuroticism. The main differences are in extraversion (Indiana higher) and agreeableness (Gates higher). Both are driven by curiosity and a sense of adventure, albeit with slightly different personality traits.

#### Beliefs
- **Similarity**: 90
- **Reasoning**: Both strongly value history, preservation, and protecting artifacts from exploitation. Gates has an additional emphasis on familial duty and legacy, while Indiana has a more general ethical stance against the misuse of historical artifacts.

#### Motivations
- **Similarity**: 80
- **Reasoning**: Both are driven by a desire to preserve history and fulfill personal quests. Gates' motivation is more focused on family legacy, while Indiana's includes a thirst for adventure and living up to his father's legacy. Both characters are propelled by a deep-seated passion for historical discovery.

#### Social Dynamics
- **Similarity**: 75
- **Reasoning**: Both characters form alliances and face adversaries. Indiana's relationships are more complex, especially with his father and romantic interests. Gates' dynamics focus more on his team and the main antagonist. Their interactions with other characters are pivotal in driving the plot forward.

#### Arc
- **Similarity**: 85
- **Reasoning**: Both characters evolve to understand deeper values beyond their initial quests. Indiana's arc focuses on his relationship with his father, while Gates' emphasizes valuing relationships and heritage more broadly. They both undergo significant personal growth as a result of their adventures.

### JSON Output

```json
{
    "overall": {
        "similarity": 83,
        "reasoning": "Both characters share similar roles, strengths, and motivations, with slight differences in backstory, psychology, and social dynamics. They are both driven by a passion for history and face similar challenges and growth arcs."
    },
    "backstory": {
        "similarity": 75,
        "reasoning": "Indiana Jones' backstory is more focused on professional experiences, while Ben Gates' is deeply rooted in family legacy and tradition. Both have backgrounds tied to historical pursuits."
    },
    "strengths": {
        "similarity": 85,
        "reasoning": "Both characters share intelligence, resourcefulness, and deep historical knowledge. Indiana has additional combat skills, while Gates' strengths are more academically focused."
    },
    "weakness": {
        "similarity": 70,
        "reasoning": "Both have weaknesses that lead to reckless behavior. Indiana's impulsiveness and fear of snakes are more specific, while Gates' obsession with treasure is more directly tied to his motivations."
    },
    "psychology": {
        "similarity": 85,
        "reasoning": "They share high openness, conscientiousness, and low neuroticism. Differences include higher extraversion in Indiana and higher agreeableness in Gates."
    },
    "beliefs": {
        "similarity": 90,
        "reasoning": "Both value history, preservation, and protecting artifacts. Gates emphasizes familial duty, while Indiana focuses on the ethical stance against misuse of artifacts."
    },
    "motivations": {
        "similarity": 80,
        "reasoning": "Both are driven by a desire to preserve history and fulfill personal quests. Gates is focused on family legacy, while Indiana's includes adventure and living up to his father's legacy."
    },
    "social_dynamics": {
        "similarity": 75,
        "reasoning": "Both form alliances and face adversaries. Indiana's relationships are more complex, while Gates' dynamics focus on his team and antagonist."
    },
    "arc": {
        "similarity": 85,
        "reasoning": "Both characters evolve to understand deeper values. Indiana's arc focuses on his relationship with his father, while Gates emphasizes valuing relationships and heritage more broadly."
    }
}
```