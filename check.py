import sys
import json
import numpy as np
import pandas as pd
from Bio_Epidemiology_NER.bio_recognizer import ner_prediction

pd.set_option('display.max_colwidth', 20)

pa = sys.argv[4]
doc = f"""
    CASE: {pa}
      """

analysed = ner_prediction(corpus=doc, compute='cpu')

if analysed.shape == (0, 0):
    print("Cannot analyse your status: Please be more specific!")
    sys.exit("args: {}".format(analysed.shape))

analysed_filtered_DPBS = analysed[(analysed["entity_group"] == "Diagnostic_procedure") | (analysed["entity_group"] == "Biological_structure")]
analysed_filtered_SSLV = analysed[(analysed["entity_group"] == "Sign_symptom") | (analysed["entity_group"] == "Lab_value")]

sup_1 = pd.read_csv("LabelStatements_1.csv", engine='python')
sup_2 = pd.read_csv("LabelStatements_2.csv", engine="python")

prover_1 = pd.read_csv("ProductOverview_1.csv", engine="python")
prover_2 = pd.read_csv("ProductOverview_2.csv", engine="python")

othing_1 = pd.read_csv("OtherIngredients_1.csv", engine="python")
othing_2 = pd.read_csv("OtherIngredients_2.csv", engine="python")

sup_frame = [sup_1, sup_2]
prover_frame = [prover_1, prover_2]
othing_frame = [othing_1, othing_2]

sup_merged = pd.concat(sup_frame, ignore_index=True, sort=False)
prover_merged = pd.concat(prover_frame, ignore_index=True, sort=False)
othing_merged = pd.concat(othing_frame, ignore_index=True, sort=False)
sup_merged = sup_merged[sup_merged["Statement Type"] == "Other"]

full_merged = pd.merge(prover_merged, sup_merged, how="right", on=["URL", "DSLD ID", "Product Name"])
full_merged = pd.merge(full_merged, othing_merged, how="right", on=["URL", "DSLD ID", "Product Name"])

analysed_df = pd.DataFrame()
for index, row in analysed_filtered_DPBS.iterrows():
    analysed_df = pd.concat([analysed_df, full_merged[full_merged["Statement"].str.contains(row['value'], na=False)]])

if analysed_df.shape == (0, 0):
    print("No supplements available that satisfy your requirements")
    sys.exit("Bailing out of the program.")

if not sys.argv[1]:
    d = {'Supplement Form [LanguaL]': ['Powder', 'Liquid', 'Gummy or Jelly']}
    child_rec = pd.DataFrame(data=d)

    new_df = pd.DataFrame()
    analysed_df_copy = analysed_df.copy()
    for index, row in child_rec.iterrows():
        new_df = pd.concat([new_df, analysed_df[analysed_df["Supplement Form [LanguaL]"].str.contains(row['Supplement Form [LanguaL]'], case=False)]])
    for index, row in new_df.iterrows():
        analysed_df_copy = analysed_df_copy.drop(index, axis=0)

    analysed_df = pd.concat([new_df, analysed_df_copy], axis=0)

if sys.argv[2] != 'Nan':
    age_flag = False
    d = {'Brand Name': ['vega']}
    brand_rec = pd.DataFrame(data=d)

    new_df = pd.DataFrame()
    analysed_df_copy = analysed_df.copy()
    for index, row in brand_rec.iterrows():
        new_df = pd.concat([new_df, analysed_df[analysed_df["Brand Name"].str.contains(row['Brand Name'], case=False)]])

    if 5 <= 6:
        age_flag = True
        d = {'Supplement Form [LanguaL]': ['Liquid', 'Powder', 'Gummy or Jelly']}
        child_rec = pd.DataFrame(data=d)

        new_df_2 = pd.DataFrame()
        for index, row in child_rec.iterrows():
            new_df_2 = pd.concat([new_df_2, new_df[new_df["Supplement Form [LanguaL]"].str.contains(row['Supplement Form [LanguaL]'], case=False)]])

    if age_flag:
        for index, row in new_df_2.iterrows():
            analysed_df_copy = analysed_df_copy.drop(index, axis=0)
        analysed_df = pd.concat([new_df_2, analysed_df_copy], axis=0)
    else:
        for index, row in new_df.iterrows():
            analysed_df_copy = analysed_df_copy.drop(index, axis=0)
        analysed_df = pd.concat([new_df, analysed_df_copy], axis=0)

if sys.argv[3]:
    d = {'Market Status': ['On Market']}
    on_rec = pd.DataFrame(data=d)
    new_df = pd.DataFrame()
    for index, row in on_rec.iterrows():
        new_df = pd.concat([new_df, analysed_df[analysed_df["Market Status"].str.contains(row['Market Status'], case=False)]])
    analysed_df = new_df

inp = sys.argv[5]
inp = inp.replace(" ", "")
inp = inp.split(",")
for item in inp:
    item = item.strip()

allergic_food_dict = {'peanuts': ['peanuts'],
                      'nuts': ['nuts', 'Walnuts', 'almonds', 'cashews', 'pistachios', 'pecans', 'hazelnuts'],
                      'milk': ['cheese', 'butter', 'yogurt', 'milk', 'dairy'],
                      'eggs': ['chicken', 'egg', 'eggs'],
                      'fish': ['fish', 'salmon', 'tuna', 'halibut'],
                      'shellfish': ['shellfish', 'shrimp', 'crab', 'lobster', 'mussel'],
                      'wheat': ['bread', 'wheat', 'pasta', 'baked'],
                      'soy': ['soy', 'tofu'],
                      'mustard': ['mustard', 'mustard seed'],
                      'sesame': ['sesame', 'sesame oil', 'sesame seed'],
                      'celery': ['celery'],
                      'sulfites': ['sulfite'],
                      'lupin': ['lupin'],
                      'mollusks': ['octapus', 'squid', 'cuttlefish'],
                      'kiwi': ['kiwi'],
                      'pineapple': ['pineapple'],
                      'avocado': ['avocado', 'guacamole'],
                      'banana': ['banana'],
                      'strawberries': ['strawberry'],
                      'tomato': ['tomato']}

allergy_list = []

if len(inp) != 0:
    for values in ["milk", "egg", "fish"]:
        for key, val in allergic_food_dict.items():
            if values in val:
                allergy_list+=key

    final_tab_copy = analysed_df.copy()
    flag = True
    for index, row in analysed_df.iterrows():
        for key in allergy_list:
            if flag:
                flag = False
                # Modify the following line:
                final_tab_copy = analysed_df[analysed_df["Other Ingredients"].str.contains(key, case=False, na=False) == False]
            else:
                # Modify the following line:
                final_tab_copy = pd.concat([final_tab_copy, analysed_df[analysed_df["Other Ingredients"].str.contains(key, case=False, na=False) == False]], axis=0)
    analysed_df = final_tab_copy

result = analysed_df.to_json(orient="split")
parsed = json.loads(result)
print(json.dumps(parsed, indent=4))
        