import os
import re
import time
import json
from pathlib import Path

import fire
import faiss
import numpy as np
import pandas as pd
import tensorflow_hub as hub
from sentence_transformers import SentenceTransformer

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'


class NaasProcessor(object):
    """code entry class"""

    exclude = ['.github']
    rootdir = 'input/awesome-notebooks-master'
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

    def _get_categories(self, root, exclude):
        for _, dirs, _ in os.walk(root, topdown=True):
            return [d for d in dirs if d not in exclude]

    def _get_files(self, path):
        for _, _, files in os.walk(path, topdown=True):
            return [os.path.join(path, file) for file in files if file.endswith('.ipynb')]

    def _make_tasks_json(self, intent_id=10000):
        tasks = []
        for category in self._get_categories(self.rootdir, self.exclude):
            for file in self._get_files(os.path.join(self.rootdir, category)):
                task = {'category': category}
                with open(file, 'r') as handle:
                    data = json.load(handle)
                    task['intent_id'] = intent_id
                    task['task'] = data['cells'][1]['source'][0][2:-1]
                    task['st_embedding'] = self._get_embedding(task['task'], 'st')
                    task['tf_embedding'] = self._get_embedding(task['task'], 'tf')
                    task['code'] = "\n".join(["".join(cell['source']) for cell in data['cells'] if cell['cell_type'] == 'code'])
                intent_id += 1
                tasks.append(task)
        return tasks

    def create_intent_df_file(self):
        tasks = pd.DataFrame(self._make_tasks_json())
        tasks = tasks.set_index('intent_id')
        tasks.to_csv('data/awesome-notebooks.csv')
        tasks.to_pickle('data/awesome-notebooks.pkl')

    def _get_embedding(self, command, encoder):
        command = re.sub('[^A-Za-z0-9 ]+', '', command).lower()
        if encoder == 'tf':
            return list(np.array(self.embed([command])[0]))
        elif encoder == 'st':
            return list(np.array(self.model.encode([command])[0]))

    def create_naas_faiss_index(self):
        intent_df = pd.read_pickle('data/awesome-notebooks.pkl').reset_index()
        db_ids = intent_df["intent_id"].values

        for prefix, dimension in zip(['tf', 'st'], [512, 384]):
            db_vectors = np.stack(intent_df[f"{prefix}_embedding"].values).astype(np.float32)
            faiss.normalize_L2(db_vectors)
            intent_index = faiss.IndexIDMap(faiss.IndexFlatIP(dimension))
            intent_index.add_with_ids(db_vectors, db_ids)
            faiss.write_index(intent_index, f"data/{prefix}_naas_intent_index.idx")

    def get_intent(self, query, prefix, tasks, k_nearest=1):
        index = faiss.read_index(f"data/{prefix}_intent_index.idx")
        query_vector = np.array([self._get_embedding(query, prefix)]).astype(np.float32)
        faiss.normalize_L2(query_vector)
        similarities, similarities_ids = index.search(query_vector, k_nearest)
        return similarities_ids[0][0], tasks['task'][similarities_ids[0][0]]

    def eval_models(self):
        for prefix in ['tf', 'st']:
            tasks = pd.read_pickle('data/awesome-notebooks.pkl')
            tasks = tasks.set_index('intent_id')
            tasks.drop([i + '_embedding' for i in ['tf', 'st']] + ['code'], axis=1, inplace=True)

            tasks[[f"{prefix}_matched_intent_id", f"{prefix}_matched_intent_text"]] = tasks['task'].apply(lambda x: pd.Series(self.get_intent(x, prefix, tasks)))
            tasks[f"{prefix}_is_intent_matched"] = tasks[f"{prefix}_matched_intent_id"] == tasks["intent_id"]

            tasks[[f"{prefix}_matched_intent_id_shuffled", f"{prefix}_matched_intent_text_shuffled"]] = tasks['task'].apply(lambda x: pd.Series(self.get_intent(self._shuffle_word(x), prefix, tasks)))
            tasks[f"{prefix}_is_intent_matched_shuffled"] = tasks[f"{prefix}_matched_intent_id_shuffled"] == tasks["intent_id"]

            Path("output").mkdir(parents=True, exist_ok=True)
            tasks.to_csv(f'output/{prefix}_eval_df.csv', index=False)

    def speed_benchmark(self, prefix, repetitions):
        tasks = pd.read_pickle('data/awesome-notebooks.pkl')
        tasks = tasks.set_index('intent_id')
        tasks.drop([i + '_embedding' for i in ['tf', 'st']] + ['code'], axis=1, inplace=True)

        start = time.time()

        for i in range(repetitions):
            tasks[[f"{prefix}_matched_intent_id", f"{prefix}_matched_intent_text"]] = tasks['task'].apply(lambda x: pd.Series(self.get_intent(x, prefix, tasks)))
            tasks[f"{prefix}_is_intent_matched"] = tasks[f"{prefix}_matched_intent_id"] == tasks["intent_id"]

            tasks[[f"{prefix}_matched_intent_id_shuffled", f"{prefix}_matched_intent_text_shuffled"]] = tasks['task'].apply(lambda x: pd.Series(self.get_intent(self._shuffle_word(x), prefix, tasks)))
            tasks[f"{prefix}_is_intent_matched_shuffled"] = tasks[f"{prefix}_matched_intent_id_shuffled"] == tasks[ "intent_id"]

        end = time.time()
        return end - start

    def get_benchmark_data(self, repetitions):
        data = pd.DataFrame([[i] for i in range(repetitions + 1)], columns=['repetitions'])
        for prefix in ['tf', 'st']:
            data[f'{prefix}_time_elapsed'] = data['repetitions'].apply(lambda x: self.speed_benchmark(prefix, x))
        Path("output").mkdir(parents=True, exist_ok=True)
        data.to_csv('output/speed_benchmarks.csv', index=False)

    def _shuffle_word(self, sentence):
        sub = sentence.split(' - ', maxsplit=1)
        return "".join([sub[1], ' - ', sub[0]])


if __name__ == '__main__':
    fire.Fire(NaasProcessor)
