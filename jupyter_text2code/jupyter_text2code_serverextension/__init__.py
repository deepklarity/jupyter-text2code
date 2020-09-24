import json
import os
import re

import faiss
import numpy as np
import pandas as pd
import spacy
# from sentence_transformers import SentenceTransformer
import tensorflow_hub as hub
from notebook.base.handlers import IPythonHandler
from notebook.utils import url_path_join

home = os.path.dirname(__file__)

# Explicitly persisting TFHUB_CACHE_DIR
root = os.path.expanduser("~")
os.makedirs(os.path.join(root, ".cache", "tfhub_modules"), exist_ok=True)
os.environ["TFHUB_CACHE_DIR"] = os.path.join(root, ".cache", "tfhub_modules")

SPACY_MODEL_DIR = os.path.join(home, "models/ner")
FAISS_INDEX_PATH = os.path.join(home, "models/intent_index.idx")
INTENT_DF_PATH = os.path.join(home, "data/ner_templates.csv")
SYNONYMS_MAPPING = {'mean': ('average', 'avg', 'avg.'), 'sum': ('add')}
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


class CodeGenerator():

    def __init__(self):
        self.nlp = spacy.load(SPACY_MODEL_DIR)
        # self.embedding_model = SentenceTransformer('bert-base-nli-stsb-mean-tokens')
        self.embedding_model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
        self.intent_index = faiss.read_index(FAISS_INDEX_PATH)
        self.intent_df = pd.read_csv(INTENT_DF_PATH)
        self.intent_df = self.intent_df

    def _get_embedding(self, command):
        command = re.sub('[^A-Za-z0-9 ]+', '', command).lower()
        #     command_embedding = self.embedding_model.encode(command)[0]
        command_embedding = list(np.array(self.embedding_model([command])[0]))
        return command_embedding

    def _get_intent(self, query, k=1):
        query_vector = self._get_embedding(query)
        zzz = np.array([query_vector]).astype(np.float32)
        # faiss.normalize_L2(zzz)
        top_k = self.intent_index.search(zzz, k)
        results = []
        return {"idx": top_k[1][0][0], "similarity": top_k[0][0][0]}

    def _get_fname_entities(self, entities):
        """Get all entities of type FNAME"""
        return [x["text"] for x in entities if x["type"] == "FNAME"]

    def _get_varname_entities(self, entities):
        """Get all entities of type VARNAME"""
        return [x["text"] for x in entities if x["type"] == "VARNAME"]

    def _get_numeric_entities(self, entities):
        """Get all entities of type CARDINAL"""
        return [x["text"] for x in entities if x["type"] == "CARDINAL"]

    def _get_col_entities(self, entities):
        """Get all entities of type COLNAME"""
        return [x["text"] for x in entities if x["type"] == "COLNAME"]

    def _get_entities(self, entities, type):
        """Get all entities by type"""
        return [x["text"] for x in entities if x["type"] == type]

    def _lib_import(self, entity_text, debug=False):
        """
        Generates code for importing a library.
        TODO: Match popular libaries and map. like scikit-learn>sklearn, matplotlib > pyplot as plt
        """
        return "import " + entity_text

    def _all_lib_import(self, debug=False):
        """
        Generates code for importing a preset of libraries
        """
        text = '''
import pandas as pd
import numpy as np
import os
import plotly.express as px
import matplotlib.pyplot as plt
pd.options.plotting.backend = 'plotly'
        '''
        return text

    def _lib_install(self, entity_text, debug=False):
        """
        Generate code for installing a library
        TODO: Match popular libaries and map. like scikit-learn>sklearn, matplotlib > pyplot as plt
        """
        return "!pip install " + entity_text

    def _load_df(self, entities, debug=False):
        """
        Load a file into a df.
        expects one entity to be a file and another optional entity
        eg:"Load train.csv" or "Load train.csv in traindf"
        """
        code = ""
        fname_entities = self._get_fname_entities(entities)
        varname_entities = self._get_varname_entities(entities)
        if not varname_entities:
            if debug:
                print("Error: ", "Didn't detect the variablename")
            varname_entities = ["xxx"]
            code += "#Couldn't extract variable name, replacing with default\n"
        if not fname_entities:
            if debug:
                print("Error: ", "Didn't detect the filename")
            fname_entities = "xxx"
            code += "#Couldn't extract file name, replacing with default\n"

        var_name = varname_entities[0]  # Assuming only one varname
        fname = fname_entities[0]  # Assuming only 1 fname here
        code = var_name + " = pd.read_csv('" + fname + "')"
        return code

    def _show_df(self, entities, debug=False):
        code = ""
        varname_entities = self._get_varname_entities(entities)
        numeric_entities = self._get_numeric_entities(entities)
        if not varname_entities:
            if debug:
                print("Error: ", "Didn't detect the variablename")
            varname_entities = ["xxx"]
            code += "#Couldn't extract variable name, replacing with default\n"

        if not numeric_entities:
            code += varname_entities[0] + ".head()"
        else:
            code += varname_entities[0] + ".head(" + str(numeric_entities[0]) + ")"
        return code

    def _list_cols(self, entities, debug=False):
        """
        List all columns of the dataframe
        """
        code = ""
        varname_entities = self._get_varname_entities(entities)
        if not varname_entities:
            if debug:
                print("Error: ", "Didn't detect the variablename")
            varname_entities = ["xxx"]
            code += "#Couldn't extract variable name, replacing with default\n"
        code += varname_entities[0] + ".columns"
        return code

    def _describe_df(self, entities, debug=False):
        """
        Describe the dataframe
        """
        code = ""
        varname_entities = self._get_varname_entities(entities)
        if not varname_entities:
            if debug:
                print("Error: ", "Didn't detect the variablename")
            varname_entities = ["xxx"]
            code += "#Couldn't extract variable name, replacing with default\n"
        code += varname_entities[0] + ".describe()"
        return code

    def _plot_hist(self, entities, debug=False):
        """
        Generate histogram of a column
        """
        code = ""
        varname_entities = self._get_varname_entities(entities)
        col_entities = self._get_col_entities(entities)
        if not varname_entities:
            if debug:
                print("Error: ", "Didn't detect the variablename")
            varname_entities = ["xxx"]
            code += "#Couldn't extract variable name, replacing with default\n"
        if not col_entities:
            if debug:
                print("Error: ", "Didn't detect the column name")
            col_entities = ["xxx", "yyy"]
            code += "#Couldn't extract column names, replacing with default\n"

        col_entities_str = json.dumps(col_entities)
        code += varname_entities[0] + ".plot.hist(x=" + col_entities_str + ")"
        return code

    def _get_corr_matrix(self, entities, debug=False):
        """
        Get the correlation matrix for a dataframe
        TODO: Wrap around plotly to plot correlation matrix
        """
        code = ""
        varname_entities = self._get_varname_entities(entities)
        if not varname_entities:
            if debug:
                print("Error: ", "Didn't detect the variablename")
            varname_entities = ["xxx"]
            code += "#Couldn't extract variable name, replacing with default\n"
        code += varname_entities[0] + ".corr()"
        return code

    def _get_shape(self, entities, debug=False):
        """
        Get df shape
        """
        code = ""
        varname_entities = self._get_varname_entities(entities)
        if not varname_entities:
            if debug:
                print("Error: ", "Didn't detect the variablename")
            varname_entities = ["xxx"]
            code += "#Couldn't extract variable name, replacing with default\n"
        code += varname_entities[0] + ".shape"
        return code

    def _bar_plot(self, entities, debug=False):
        """
        Plot barplot for two columns in a df
        """
        code = ""
        varname_entities = self._get_varname_entities(entities)
        col_entities = self._get_col_entities(entities)
        if not varname_entities:
            if debug:
                print("Error: ", "Didn't detect the variablename")
            varname_entities = ["xxx"]
            code += "#Couldn't extract variable name, replacing with default\n"
        if len(col_entities) < 2:
            if debug:
                print("Error: ", "Didn't detect the column name")
            col_entities = ["xxx", "yyy"]
            code += "#Couldn't extract column names, replacing with default\n"

        code += "px.bar(x='" + col_entities[0] + "',y='" + col_entities[1] + "',data_frame=" + varname_entities[0] + ",title='CustomTitle', labels=" \
                + "{'" + col_entities[0] + "':'" + col_entities[0] + "','" + col_entities[1] + "':'" + col_entities[1] + "'})"

        return code

    def _pie_plot(self, entities, debug=False):
        """
        Plot piechart of a column in df
        """
        code = ""
        varname_entities = self._get_varname_entities(entities)
        col_entities = self._get_col_entities(entities)
        if not varname_entities:
            if debug:
                print("Error: ", "Didn't detect the variablename")
            varname_entities = ["xxx"]
            code += "#Couldn't extract variable name, replacing with default\n"
        if not col_entities:
            if debug:
                print("Error: ", "Didn't detect the column name")
            col_entities = ["xxx"]
            code += "#Couldn't extract column name, replacing with default\n"

        code += "tmp = " + varname_entities[0] + "['" + col_entities[0] + "'].value_counts(dropna=False)\n" + \
                "px.pie(tmp,values=tmp.values,names=tmp.index,title='CustomTitle')"
        return code

    def _list_dir(self, entities, debug=False):
        return "!ls ."

    def _line_plot(self, entities, debug=False):
        """
        Line plot of two columns in df
        """
        code = ""
        varname_entities = self._get_varname_entities(entities)
        col_entities = self._get_col_entities(entities)
        if not varname_entities:
            if debug:
                print("Error: ", "Didn't detect the variablename")
            varname_entities = ["xxx"]
            code += "#Couldn't extract variable name, replacing with default\n"
        if len(col_entities) < 2:
            if debug:
                print("Error: ", "Didn't detect the column name")
            col_entities = ["xxx", "yyy"]
            code += "#Couldn't extract column names, replacing with default\n"

        code += varname_entities[0] + ".plot.line(x='" + col_entities[0] + "', y='" + col_entities[1] + "', color=None, title='CustomTitle', labels=" \
                + "{'" + col_entities[0] + "':'" + col_entities[0] + "', '" + col_entities[1] + "':'" + col_entities[1] + "'})"
        return code

    def _scatter_plot(self, entities, debug=False):
        """
        Line plot of two columns in df
        """
        code = ""
        varname_entities = self._get_varname_entities(entities)
        col_entities = self._get_col_entities(entities)
        if not varname_entities:
            if debug:
                print("Error: ", "Didn't detect the variablename")
            varname_entities = ["xxx"]
            code += "#Couldn't extract variable name, replacing with default\n"
        if len(col_entities) < 2:
            if debug:
                print("Error: ", "Didn't detect the column name")
            col_entities = ["xxx", "yyy"]
            code += "#Couldn't extract column names, replacing with default\n"

        code += varname_entities[0] + ".plot.scatter(x='" + col_entities[0] + "', y='" + col_entities[1] + "', color=None, size=None, title='CustomTitle', labels=" \
                + "{'" + col_entities[0] + "':'" + col_entities[0] + "', '" + col_entities[1] + "':'" + col_entities[1] + "'})"
        return code

    def _heatmap(self, entities, debug=False):
        code = ""
        varname_entities = self._get_varname_entities(entities)
        col_entities = self._get_col_entities(entities)
        if not varname_entities:
            if debug:
                print("Error: ", "Didn't detect the variablename")
            varname_entities = ["xxx"]
            code += "#Couldn't extract variable name, replacing with default\n"
        if len(col_entities) < 2:
            if debug:
                print("Error: ", "Didn't detect the column name")
            col_entities = ["xxx", "yyy"]
            code += "#Couldn't extract column names, replacing with default\n"

        code += varname_entities[0] + ".plot(kind='density_heatmap', x='" + col_entities[0] + "', y='" + col_entities[1] + "', title='CustomTitle', labels=" \
                + "{'" + col_entities[0] + "':'" + col_entities[0] + "', '" + col_entities[1] + "':'" + col_entities[1] + "'})"
        return code

    def _aggregation(self, entities, debug=False):
        """
        Aggregation
        """
        code = ""
        varname_entities = self._get_entities(entities, 'VARNAME')
        col_entities = self._get_entities(entities, 'COLNAME')
        func_entities = self._get_entities(entities, 'FUNCTION')
        if not varname_entities:
            if debug:
                print("Error: ", "Didn't detect the variablename")
            varname_entities = ["xxx"]
            code += "#Couldn't extract variable name, replacing with default\n"
        if not col_entities:
            if debug:
                print("Error: ", "Didn't detect the column name")
            col_entities = ["xxx"]
            code += "#Couldn't extract column name, replacing with default\n"
        if not func_entities:
            if debug:
                print("Error: ", "Didn't detect the function")
            func_entities = ["xxx"]
            code += "#Couldn't extract function name, replacing with default\n"

        split_idx = -1
        for e in entities:
            if e['type'] == 'COLNAME':
                split_idx += 1
            elif e['type'] == 'FUNCTION':
                break

        quote_cols = [f"'{c}'" for c in col_entities]
        quote_funcs = [f"'{c}'" for c in func_entities]
        if len(quote_cols) == 1:
            code += f"{varname_entities[0]}.groupby([{','.join(quote_cols)}]).agg([{','.join(quote_funcs)}])"
        else:
            code += f"{varname_entities[0]}[[{','.join(quote_cols)}]].groupby([{','.join(quote_cols[:split_idx + 1])}]).agg([{','.join(quote_funcs)}])"
        return code

    def _dark_theme(self, entities, debug=False):
        code = "import plotly.io as pio\npio.templates.default = 'plotly_dark'"
        return code

    def synonym_key(self, value, debug=False):
        for k, v in SYNONYMS_MAPPING.items():
            if value in v:
                if debug:
                    print(f"Use {k} for synonym {value}")
                return k
        return value

    def generate_code(self, query, df_info_dict={}, debug=False):
        intent = self._get_intent(query)
        intent_str = self.intent_df[self.intent_df["intent_id"] == intent["idx"]]["template"].values[0]
        if debug:
            print("Intent:", intent_str, " Intent_id:", intent["idx"], " Similarity", intent["similarity"])
        doc = self.nlp(query)
        if debug:
            print("Entities:")
            for ent in doc.ents:
                print(ent.text, ent.start_char, ent.end_char, ent.label_)
            print("-" * 10)

        df_columns = set()
        for columns in df_info_dict.values():
            df_columns.update(columns)

        entities = []
        for ent in doc.ents:
            if len(df_columns) > 0 and ent.label_ == 'COLNAME' and ent.text not in df_columns:
                if debug:
                    print(f"{ent.text} wrongly detected as COLNAME")
            else:
                if ent.label_ == 'FUNCTION':
                    text = self.synonym_key(ent.text, debug=debug)
                else:
                    text = ent.text
                entities.append({"text": text, "type": ent.label_})

        # Switch case for intents:
        if intent["idx"] == 0:
            # Import a lib
            return self._lib_import(entities[0]["text"], debug=debug)
        if intent["idx"] == 1:
            # All imports
            return self._all_lib_import(debug=debug)
        if intent["idx"] == 2:
            # Load file into df
            return self._load_df(entities, debug=debug)
        if intent["idx"] == 3:
            # Show x rows of df
            return self._show_df(entities, debug=debug)
        if intent["idx"] == 4:
            # Plot histogram of a column
            return self._plot_hist(entities, debug=debug)
        if intent["idx"] == 5:
            # Get correlation matrix of df
            return self._get_corr_matrix(entities, debug=debug)
        if intent["idx"] == 6:
            # Print shape of df
            return self._get_shape(entities, debug=debug)
        if intent["idx"] == 7:
            # Bar plot
            return self._bar_plot(entities, debug=debug)
        if intent["idx"] == 8:
            # Pie plot
            return self._pie_plot(entities, debug=debug)
        if intent["idx"] == 9:
            # Install a package
            return self._lib_install(entities[0]["text"], debug=debug)
        if intent["idx"] == 10:
            # List all columns of a df
            return self._list_cols(entities, debug=debug)
        if intent["idx"] == 11:
            # Describe df
            return self._describe_df(entities, debug=debug)
        if intent["idx"] == 12:
            # Aggregation
            return self._aggregation(entities, debug=debug)
        if intent["idx"] == 13:
            # Line plot
            return self._line_plot(entities, debug=debug)
        if intent["idx"] == 14:
            # Scatter plot
            return self._scatter_plot(entities, debug=debug)
        if intent["idx"] == 15:
            # Heatmap
            return self._heatmap(entities, debug=debug)
        if intent["idx"] == 16:
            return self._list_dir(entities, debug=debug)
        if intent["idx"] == 17:
            # Dark theme
            return self._dark_theme(entities, debug=debug)


print("*" * 20)
print("*" * 20)
print("loading_jupyter_server_extension: jupyter-text2code. First install will download universal-sentence-encoder, please wait...")
print("*" * 20)
print("*" * 20)
CG = CodeGenerator()


class JupyterText2CodeHandler(IPythonHandler):
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
