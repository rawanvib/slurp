'''
sir we can also do one thing ..like initially we can put all words that are already ranked from nin dataset in assigned word....afterall we are checking no if words are in assigned_words......we will get prompted for other words

 if they are already ranked then we wont get propmt for those words
'''
import csv
import pandas as pd
import re
from nltk.corpus import stopwords

data_csv=pd.read_csv('nin_usda_combo.csv')

stop_words = set(stopwords.words('english'))

assigned_word = []
with open("ranked_usda_words_1.csv", "r") as fr:
    reader = csv.reader(fr)

    for data in reader:
        # print(data[0])
        assigned_word.append(data[0])


with open("ranked_usda_words_1.csv", "a", newline='') as fr:
    csv_writer = csv.writer(fr)

    for index, row in data_csv.iterrows():

        if row['dataset']=='usda':
            descrip=row['Descrip']
            ingredient = re.sub('[^\w]', ' ', descrip).lower()

            ingredient = " ".join([k for k in ingredient.split() if len(k) > 1])

            ingredient_token=ingredient.split()
            unique_ingredient = list(set(ingredient_token))
            filtered_ingredient = [one for one in unique_ingredient if not one in stop_words]
            for word in filtered_ingredient:
                if word not in assigned_word:
                    weight=input(word)
                    assigned_word.append(word)
                    record_to_lable = ['new',word,weight]
                    csv_writer.writerow(record_to_lable)
