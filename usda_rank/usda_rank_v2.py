"""
read desp column only
assigned word = []
for row in csv
    record = row.remove special character. slitp(" ").remove stop words
    for word in record:
         if word not in assigned:
              weight = input(word=)

              assigned.append( word )
              record_to_lable = [word, weight]
              final1.csv.write(record_to_label)
"""
import csv
import pandas as pd
import re
from nltk.corpus import stopwords

data_csv = pd.read_csv('nin_usda_combo.csv')
stop_words = set(stopwords.words('english'))

with open("ranked_usda_words_1.csv", "w", newline='') as fr:
    csv_writer = csv.writer(fr)

    assigned_word = []
    for index, row in data_csv.iterrows():

        if row['dataset'] == 'usda':
            descrip = row['Descrip']
            print(descrip)
            ingredient = re.sub('[^\w]', ' ', descrip).lower()
            ingredient = " ".join([k for k in ingredient.split() if len(k) > 1])
            ingredient_token = ingredient.split()
            unique_ingredient = list(set(ingredient_token))
            filtered_ingredient = [one for one in unique_ingredient if not one in stop_words]
            print(filtered_ingredient)
            for word in filtered_ingredient:
                if word not in assigned_word:
                    weight = input(word)
                    assigned_word.append(word)
                    record_to_lable = [word, weight]
                    csv_writer.writerow(record_to_lable)
