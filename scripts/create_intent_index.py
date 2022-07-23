import re

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
backend_dir = "../jupyter_text2code/jupyter_text2code_serverextension"


def _get_embedding(command):
    command = re.sub('[^A-Za-z0-9 ]+', '', command).lower()
    return list(np.array(model.encode([command])[0]))


# Make intent df
jt2c = pd.read_csv(f'{backend_dir}/data/generated_intents.csv')
naas = pd.read_csv(f'{backend_dir}/data/awesome-notebooks.csv')[['intent_id', 'task', 'st_embedding']]
naas.columns = ['intent_id', 'intent', 'embedding']

jt2c['embedding'] = jt2c['intent'].apply(_get_embedding)
naas['embedding'] = naas['intent'].apply(_get_embedding)
jt2c = jt2c[['intent_id', 'intent', 'embedding']]

intent_df = pd.concat([jt2c, naas], axis=0)
intent_df.to_csv('testing.csv', index=False)

for x, y in zip(intent_df["intent_id"].values, intent_df["embedding"].values):
    if len(y) != 384:
        print(x)

# Make faiss index
db_ids = intent_df['intent_id'].values
db_vectors = np.stack(intent_df["embedding"].values).astype(np.float32)
faiss.normalize_L2(db_vectors)
intent_index = faiss.IndexIDMap(faiss.IndexFlatIP(384))
intent_index.add_with_ids(db_vectors, db_ids)
faiss.write_index(intent_index, f"{backend_dir}/models/intent_index.idx")
