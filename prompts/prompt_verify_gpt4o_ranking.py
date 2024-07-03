prompt_str = """
Estimate a similarity score (0-100) for each of the following films 
with the reference film 'Raiders of the Lost Ark' from 1981: 
    
    1. Titanic (1997) 
    2. The Mummy (1999) 
    3. Office Space (1999) 
    4. Laura Croft Tomb Raider (2001) 
    5. Indiana Jones and the Last Crusade (1989) 
    6. National Treasure (2004) 
    7. Indiana Jones and the Temple of Doom (1984) 
    8. La La Land (2016) 
    
Provide your response in decreasing order of similarity in JSON format like: 


{ "1": { 
    "name": "film1_title", 
    "similarity": 90 
  }, 
  "2": { 
    "name":"film2_title", 
    "similarity":85 
  },
  "3": {
    "name":...
  },
  ...

""";