# pip install fuzzywuzzy
# pip install python-Levenshtein
from pymongo import MongoClient
from pandas import DataFrame
from fuzzywuzzy import process

my_client = MongoClient("mongodb://localhost:27017/")
my_db = my_client['Slurp']
my_col = my_db['ReceipeCollectionWithDiet']

data_from_db = my_col.find({})
data_from_db = list(data_from_db)

file1 = open('non_veg_keywords.txt', 'r')
list_non_veg_words = file1.read()
list_non_veg_words = list_non_veg_words.split('\n')
final_non_veg_words = []

for word in list_non_veg_words:
    if word != '':
        word=word.lower()
        final_non_veg_words.append(word)
print(final_non_veg_words)


# list_non_veg_word = ['chickens', 'mutton', 'prawn', 'fish', 'keema', 'egg', 'tangari', 'pasanda', 'lamb',
#                     'beef', 'crab', 'ham', 'hamburger''meen', 'turkey', 'calamari', 'salmon', 'pomfret',
#                     'lobster', 'pork','quail', 'squid', 'ilish', 'meat']


def dict_data(db_data):
    count = 0
    for data in db_data:
        flag_non_veg = False
        title = data.get('recipe_title', '')
        title=title.lower()
        ingredients = data.get('recipe_ingredient_list', '')
        ingredients=ingredients.lower()
        instructions = ' '.join(data.get('updated_instructions', ''))
        instructions=instructions.lower()

        # for word in list_non_veg_word:
        for word in final_non_veg_words:
            fuzzy_word = process.extractOne(word, title.split())
            if word in title.split():
                data['word'] = word+' found in title'
                flag_non_veg = True
                break
            elif fuzzy_word is not None and fuzzy_word[1] > 90:
                flag_non_veg = True
                data['word'] = word+' found in title'
                break
            else:
                fuzzy_word_ingredient = process.extractOne(word, ingredients.split())

                if word in ingredients.split():
                    data['word'] = word+' found in ingredient'
                    flag_non_veg = True
                    break
                elif fuzzy_word_ingredient is not None and fuzzy_word_ingredient[1] > 90:
                    data['word'] = word+' found in ingredient'
                    flag_non_veg = True
                    break
                else:

                    fuzzy_word_instruction = process.extractOne(word, instructions.split())

                    if word in instructions.split():
                        data['word'] = word+' found in instructions'
                        flag_non_veg = True
                        break
                    elif fuzzy_word_instruction is not None and fuzzy_word_instruction[1] > 90:
                        data['word'] = word+' found in instructions'
                        flag_non_veg = True
                        break
                    else:
                        continue

        if flag_non_veg:
            data['diet'] = 'Non-veg'
        else:
            data['diet'] = 'veg'
            data['word'] = ''
        count += 1
        print(count)

    return db_data


documents = dict_data(data_from_db)
df = DataFrame.from_dict(documents)
df.to_csv('5th_june_veg_nonveg.csv', index=False)
