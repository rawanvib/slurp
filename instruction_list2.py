import pymongo
import re
import json
from ingredient_parser_v2 import parse_ingredients_v2

def data_for_eval(value,text_data):
    '''
    Create data suitable for eval function
    '''
    dict_word = {}
    for word in value:
        if word in text_data:
            x = word.split("\'")
            new_word = ''.join(x)
            dict_word[new_word] = word
            text_data = text_data.replace(word, new_word)
    edited_data=text_data
    return edited_data, dict_word


def update_instruction_and_ingredient(collection,data):
    '''
    Create a list of instructions and divide each ingredients into name of ingredient, unit and quantity
    '''
    for i in range(len(data)):
        data_recipe = data[i]
        ingredient_text = data_recipe.get("recipe_ingredient_list")
        instructions_data = data_recipe.get('recipe_instructions')

        if ingredient_text is not None:
            ingredient_text = re.sub(r'\s+', ' ', ingredient_text, flags=re.I)
            quote_words = re.findall("\w+[']+\w+", ingredient_text)

            if quote_words:
                ingredient_text, dict_ingredient_word= data_for_eval(quote_words, ingredient_text)
                ingredient_raw = eval(ingredient_text)

                ingredient_list = []
                for in_sentence in ingredient_raw:
                    for word in dict_ingredient_word.keys():
                        in_sentence = in_sentence.replace(word, dict_ingredient_word[word])
                    ingredient_list.append(in_sentence)
            else:
                ingredient_list = eval(ingredient_text)

            ingredient_data = parse_ingredients_v2(ingredient_list)
        else:
            ingredient_data = []

        if len(instructions_data) >3:
            instructions_data = re.sub('\s+', ' ', instructions_data)
            val = re.findall("\w+[']+\w+", instructions_data)

            if val:
                instructions_data, dict_word = data_for_eval(val, instructions_data)
                dict_instructions = eval(instructions_data)
                text = dict_instructions['text']
                for word in dict_word.keys():
                    if word in text:
                        text = text.replace(word, dict_word[word])
            else:
                dict_instructions = eval(instructions_data)
                text = dict_instructions['text']

            instruction_list = text.split('.')
        else:
            instruction_list=[]

        dict_single = {}
        dict_single['ingredients_with_unit_and_quantity'] = ingredient_data
        dict_single['updated_instructions']=instruction_list

        filter_unit = data_recipe['_id']
        filter_data = {'_id': filter_unit}
        collection.update_one(filter_data,{"$set":dict_single})

if __name__ =='__main__':

    my_client = pymongo.MongoClient("mongodb://localhost:27017/")
    my_db = my_client['Slurp']
    my_col = my_db['RecipeCollectionData1']

    db_data = my_col.find({}, {'recipe_instructions': 1, 'recipe_ingredient_list': 1, '_id': 1})
    db_data = list(db_data)

    update_instruction_and_ingredient(my_col,db_data)
