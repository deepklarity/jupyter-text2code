import json
import string
import pickle
import random
from enum import Enum
from random import randint

import fire
import pandas as pd
from tqdm import tqdm


class Entities(Enum):
    VARNAME = "VARNAME"
    COLNAME = "COLNAME"
    FNAME = "FNAME"
    LIBNAME = "LIBNAME"
    CARDINAL = "CARDINAL"
    FUNCTION = "FUNCTION"


class TrainDataGenerator:

    def __init__(self, mode):
        template_file = "../jupyter_text2code/jupyter_text2code_serverextension/data/ner_templates.csv"
        self.templates_df = pd.read_csv(template_file)
        self.mode = mode  # intent or ner

        self.num_templates = self.templates_df.shape[0]
        print("*" * 10)
        print(self.num_templates, " templates loaded")
        print("*" * 10)

    def _get_entity_type(self, entity_str):
        for entity in Entities:
            if entity.value.lower() in entity_str:
                return entity.value
        print("Cannot find entity in db", entity_str)
        return None

    def _get_replacement_word(self, entity_type, debug):
        if entity_type == "VARNAME":
            choices = ["mydf", "df", "zzz", "tempdf"]
            return random.choice(choices)
        elif entity_type == "FUNCTION":
            choices = ["average", "sum", "min", "max", "maximum", "minimum", "mean", "avg", "count"]
            return random.choice(choices)
        elif entity_type == "COLNAME":
            #             choices = ["age", "temperature", "humidity"]
            #             return random.choice(choices)
            # Generate random columns
            col_len = randint(3, 20)
            cols = ''.join(random.choices(string.ascii_lowercase, k=col_len))
            if randint(1, 10) < 4:
                replace = randint(1, len(cols) - 1)
                cols = cols[:replace] + "_" + cols[replace:]
            return cols

        elif entity_type == "FNAME":
            choices = ["train.csv", "train.json", "test.csv", "validation.csv", "data.csv", "data.xls"]
            return random.choice(choices)
        elif entity_type == "LIBNAME":
            choices = ["spacy", "matplotlib", "pandas", "numpy", "seaborn", "plotly", "tensorflow", "torch",
                       "transformers"]
            return random.choice(choices)
        elif entity_type == "CARDINAL":
            return str(randint(1, 100))

    def _replace_var(self, template, entity_dict, intent_id, debug):
        sign_idx = template.find("$")
        if sign_idx == -1:
            print("Error: No symbol $ found to replace")

        start_idx = sign_idx
        entity_str = template.split("$")[1].split()[0]
        entity_type = self._get_entity_type(entity_str)

        # Allow multiple column syntaxes for group by 
        if intent_id not in [12] or entity_type in ["VARNAME", "FNAME", "LIBNAME", "CARDINAL"]:
            replacement_word = self._get_replacement_word(entity_type, debug)
            end_idx = start_idx + len(replacement_word)
            entity_dict["entities"].append((start_idx, end_idx, entity_type))

            template = template[:start_idx] + replacement_word + template[start_idx + len(entity_str) + 1:]
            return template, entity_dict

        n = randint(1, 9)
        if n < 5:
            # One word
            n = 1
        elif n < 8:
            # Two words
            n = 2
        elif n < 10:
            # 3-5 words
            n = randint(3, 5)

        replacement_word_all = ""
        for i in range(n):
            replacement_word = self._get_replacement_word(entity_type, debug)
            end_idx = start_idx + len(replacement_word)
            entity_dict["entities"].append((start_idx, end_idx, entity_type))
            start_idx = end_idx
            replacement_word_all += replacement_word
            if i != n - 1:
                zzz = randint(1, 2)
                if zzz == 1:
                    replacement_word_all += ","
                    start_idx += 1
                elif zzz == 2:
                    replacement_word_all += ", "
                    start_idx += 2

        template = template[:sign_idx] + replacement_word_all + template[sign_idx + len(entity_str) + 1:]

        if debug:
            print("Modified template=>", template)
        return template, entity_dict

    def generate_training_row(self, intent_id=None, debug=False):
        if intent_id:
            try:
                template = self.templates_df[self.templates_df["intent_id"] == intent_id].sample(1)["template"].values[
                    0]
            except:
                print("Intent id ", intent_id, " not found")
        else:
            tmp = self.templates_df.sample(1)
            template = tmp["template"].values[0]
            intent_id = tmp["intent_id"].values[0]
        if debug:
            print("Template=>", template)

        entity_dict = {"entities": []}
        while True:
            if template.find("$") == -1:
                break
            template, entity_dict = self._replace_var(template, entity_dict, intent_id, debug=debug)
        if debug:
            print("Generated text=> ", template)
            print("Entities=>", entity_dict)

        if self.mode.lower() == "ner":
            return template, entity_dict
        else:
            return {"intent_id": intent_id, "intent": template}

    def generate_training_rows(self, n_rows=10, debug=False):
        rows = []
        for _ in tqdm(range(n_rows)):
            rows.append(self.generate_training_row(debug=debug))
        return rows


def ner_data(n_rows=1000):
    tdg = TrainDataGenerator(mode="ner")
    rows = tdg.generate_training_rows(n_rows=n_rows)
    with open('assets/train.json', 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=4)
    # pickle_out = open("ner_train_data.pickle", "wb")
    # pickle.dump(rows, pickle_out)
    # pickle_out.close()
    print("Generated ner data")


def intent_data(n_rows=1000):
    tdg = TrainDataGenerator(mode="intent")
    rows = tdg.generate_training_rows(n_rows=n_rows)
    df_intent = pd.DataFrame(rows)
    df_intent.to_csv("../jupyter_text2code/jupyter_text2code_serverextension/data/generated_intents.csv", index=False)
    print("Generated intent data")


def main(generate_ner_data="yes", generate_intent_data="yes", n_rows=1000):
    if generate_ner_data.lower() == "yes":
        ner_data(n_rows=n_rows)
    if generate_intent_data.lower() == "yes":
        intent_data(n_rows=n_rows)


if __name__ == '__main__':
    fire.Fire(main)
