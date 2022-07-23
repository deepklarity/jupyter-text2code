import os
import re
import json
from abc import ABC
from itertools import groupby

import faiss
import spacy
import numpy as np
import pandas as pd
from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
from sentence_transformers import SentenceTransformer

home = os.path.dirname(__file__)

SPACY_MODEL_DIR = os.path.join(home, "models/model-best")
FAISS_INDEX_PATH = os.path.join(home, "models/intent_index.idx")
INTENT_DF_PATH = os.path.join(home, "data/intent_lookup.csv")
HELP_LIST = ['Import all libraries - Example Usage: import all libraries',
             'Use plotly dark theme - Example Usage: use dark theme',
             'Load file into a dataframe - Example Usage: Load train.csv in df',
             'Show n rows of dataframe - Example Usage: Show 10 rows from df',
             'Shape of dataframe - Example Usage: Show shape of df',
             'Describe dataframe - Example Usage: Describe dataframe df',
             'List columns of dataframe - Example Usage: Show columns from df',
             'Correlation matrix of dataframe - Example Usage: Display corelation matrix of df',
             'Histogram of column in dataframe - Example Usage: Plot histogram of category from df',
             'Bar chart of columns from dataframe - Example Usage: Show bar chart of product and amount from df',
             'Pie chart of column - Example Usage: Make pie chart of fruits from df',
             'Group by aggregations of columns in dataframe - Example Usage: group df by country and show sum and mean of population',
             'Line chart of columns in dataframe - Example Usage: Line chart of price and sale from df',
             'Scatter plot of columns in dataframe - Example Usage: Show scatter plot of youtube_likes and episode_duration from df',
             'Heatmap of columns in dataframe - Example Usage: from df make heat map of recording_time and youtube_views',
             'List all files in current directory - Example Usage: List all files in current directory'
             ]
HELP_TEXT = "\n".join([f"# {s}" for s in HELP_LIST])


class CodeGenerator:

    def __init__(self):
        self.nlp = spacy.load(SPACY_MODEL_DIR)
        self.embedding_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
        self.intent_index = faiss.read_index(FAISS_INDEX_PATH)
        self.intent_df = pd.read_csv(INTENT_DF_PATH)
        self.intent_df = self.intent_df.set_index('intent_id')

    def _get_embedding(self, command):
        command = re.sub('[^A-Za-z0-9 ]+', '', command).lower()
        return list(np.array(self.embedding_model.encode([command])[0]))

    def _get_intent(self, query, k_nearest=1):
        query_vector = np.array([self._get_embedding(query)]).astype(np.float32)
        faiss.normalize_L2(query_vector)
        similarities, similarities_ids = self.intent_index.search(query_vector, k_nearest)
        return similarities_ids[0][0], self.intent_df['code'][similarities_ids[0][0]]

    def generate_code(self, query, df_info_dict={}, debug=False):
        intent_id, intent_code = self._get_intent(query)
        if 0 <= intent_id < 10000:   # Existing
            doc = self.nlp(query)
            entities = {key: list(g) for key, g in groupby(sorted(doc.ents, key=lambda x: x.label_), lambda x: x.label_)}
            for entity, labels in entities.items():
                intent_code = re.sub(fr'\${entity.lower()}', lambda _: next(iter(map(lambda x: x.text, labels))), intent_code)
        elif 10000 <= intent_id < 20000:   # Naas
            print("Nothing yet")

        return re.sub(r'\$\w+', 'xxx', intent_code)


print("*" * 20)
print("*" * 20)
print("Loading_jupyter_server_extension. First install will download SentenceTransformers, please wait...")
print("*" * 20)
print("*" * 20)
CG = CodeGenerator()


class JupyterText2CodeHandler(IPythonHandler, ABC):
    def __init__(self, application, request, **kwargs):
        super(JupyterText2CodeHandler, self).__init__(application, request, **kwargs)

    # TODO: Add logger
    def get(self):
        query = self.get_argument('query')

        try:
            status = "success"
            if query.lower() == 'help':
                command = HELP_TEXT
            else:
                df_info = self.get_argument('dataframes_info')
                df_info_dict = json.loads(df_info[1:-1])
                command = CG.generate_code(query, df_info_dict, debug=True)

            response = {"status": status, "message": command}
        except Exception as e:
            response = {"status": "error", "message": str(e)}

        response["message"] = f"#Query: {query}\n\n{response['message']}"
        self.finish(json.dumps(response))


def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """
    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], '/jupyter-text2code')
    web_app.add_handlers(host_pattern, [(route_pattern, JupyterText2CodeHandler)])
    print("loaded_jupyter_server_extension: jupyter-text2code")
