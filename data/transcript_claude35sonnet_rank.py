prompt_str = """
Estimate a similarity score (0-100) for each of the following films with the reference film 'Raiders of the Lost Ark' from 1981:

1. Titanic (1997)
2. The Mummy (1999)
3. Office Space (1999)
4. Laura Croft Tomb Raider (2001)
5. Indiana Jones and the Last Crusade (1989)
6. National Treasure (2004)
7. Indiana Jones and the Temple of Doom (1984)
8. La La Land (2016)

Provide your response in decreasing order of similarity in JSON format like:

{
  "1": {
    "name": "film1_title",
    "similarity": 90
  },
  "2": {
    "name":"film2_title",
    "similarity":85
  },...
""";

"""
<RESPONSE>
I'll provide similarity scores (0-100) for each film compared to 'Raiders of the Lost Ark' (1981), considering factors like genre, plot elements, tone, and style:

1. Titanic (1997): 15/100
   Very different genre and setting, but shares some adventure elements.

2. The Mummy (1999): 80/100
   Similar adventure-archaeology theme, supernatural elements, and time period.

3. Office Space (1999): 5/100
   Completely different genre, setting, and tone.

4. Lara Croft: Tomb Raider (2001): 70/100
   Adventure-archaeology theme, action sequences, artifact hunting.

5. Indiana Jones and the Last Crusade (1989): 95/100
   Same franchise, character, and overall style.

6. National Treasure (2004): 75/100
   Historical artifact hunt, adventure elements, puzzle-solving.

7. Indiana Jones and the Temple of Doom (1984): 90/100
   Same franchise, character, and style, slight tone difference.

8. La La Land (2016): 5/100
   Entirely different genre, setting, and style.

Would you like me to elaborate on any of these ratings?

{
  "1": {
    "name": "Indiana Jones and the Last Crusade",
    "similarity": 95
  },
  "2": {
    "name": "Indiana Jones and the Temple of Doom",
    "similarity": 90
  },
  "3": {
    "name": "The Mummy",
    "similarity": 75
  },
  "4": {
    "name": "Laura Croft Tomb Raider",
    "similarity": 70
  },
  "5": {
    "name": "National Treasure",
    "similarity": 65
  },
  "6": {
    "name": "Titanic",
    "similarity": 25
  },
  "7": {
    "name": "Office Space",
    "similarity": 5
  },
  "8": {
    "name": "La La Land",
    "similarity": 5
  }
}


""";