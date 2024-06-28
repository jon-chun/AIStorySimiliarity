import os

film_dir_list = [
    "similiarity-by-score_elements_indiana-jones-and-the-last-crusade_1989",
    "similiarity-by-score_elements_indiana-jones-and-the-temple-of-doom_1984",
    "similiarity-by-score_elements_la-la-land_2016",
    "similiarity-by-score_elements_laura-croft-tomb-raider_2001",
    "similiarity-by-score_elements_national-treasure_2014",
    "similiarity-by-score_elements_office-space_1999",
    "similiarity-by-score_elements_raiders-of-the-lost-arc_1981",
    "similiarity-by-score_elements_the-mummy_1999",
    "similiarity-by-score_elements_titanic_1997",
]

def create_directories(dir_list):
    for dir_name in dir_list:
        try:
            os.mkdir(dir_name)
            print(f"Directory '{dir_name}' created successfully")
        except FileExistsError:
            print(f"Directory '{dir_name}' already exists")
        except Exception as e:
            print(f"An error occurred while creating directory '{dir_name}': {e}")

def main():
    
    create_directories(film_dir_list)

if __name__ == '__main__':
    main()

