#!/usr/bin/env python
# coding: utf-8
import os
import sys
import pandas as pd
import numpy as np
from tqdm import tqdm
import re
import faiss
import tensorflow_hub as hub
import tensorflow as tf

sys.path.append("../")

DATA_DIR = "../jupyter_text2code/jupyter_text2code_serverextension/data"

def get_embedding(command):
    command = re.sub('[^A-Za-z0-9 ]+', '', command).lower()
    command_embedding = list(np.array(embed([command])[0]))
    return command_embedding

# Explicitly persisting TFHUB_CACHE_DIR
root = os.path.expanduser("~")
os.makedirs(os.path.join(root, ".cache", "tfhub_modules"), exist_ok=True)
os.environ["TFHUB_CACHE_DIR"] = os.path.join(root, ".cache", "tfhub_modules")

embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

intent_df = pd.read_csv(DATA_DIR + "/generated_intents.csv")

intent_df["embedding"] = None

embedding_not_found_list = []
for idx, row in tqdm(intent_df.iterrows()):
    intent_df.at[idx, "embedding"] = get_embedding(row["intent"])

intent_df = intent_df.reset_index()

intent_index = faiss.IndexIDMap(faiss.IndexFlatIP(512))
zzz = np.stack(intent_df["embedding"].values).astype(np.float32)
# faiss.normalize_L2(zzz)
intent_index.add_with_ids(zzz, intent_df["intent_id"].values)
# intent_index.add_with_ids(np.stack(intent_df["embedding"].values).astype(np.float32), intent_df["index"].values)
faiss.write_index(intent_index, "../jupyter_text2code/jupyter_text2code_serverextension/models/intent_index.idx")

print("Done")
