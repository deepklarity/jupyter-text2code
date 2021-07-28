# Text2Code for Jupyter notebook
### A proof-of-concept jupyter extension which converts english queries into relevant python code. 


![](jupyter-text2code-demo.gif)

### Blog post with more details:
#### [Data analysis made easy: Text2Code for Jupyter notebook](https://towardsdatascience.com/data-analysis-made-easy-text2code-for-jupyter-notebook-5380e89bb493?source=friends_link&sk=2c46fff2c31f7fe59b667350e4596b18)

### Demo Video:
#### [Text2Code for Jupyter notebook](https://www.youtube.com/watch?v=3gZ7_9W-TJs)

## Supported Operating Systems:
- Ubuntu
- macOS

## Jupyter plugin Installation:
### NOTE: We have renamed the plugin from mopp to jupyter-text2code. Uninstall mopp before installing new jupyter-text2code version.
```
pip uninstall mopp
```

### GPU install
```
git clone https://github.com/deepklarity/jupyter-text2code.git
cd jupyter-text2code
pip install .
```

### CPU-only install
For Mac and other Ubuntu installations not having a nvidia GPU, we need to explicitly set a environment variable at time of install.
```
git clone https://github.com/deepklarity/jupyter-text2code.git
export JUPYTER_TEXT2CODE_MODE="cpu"
cd jupyter-text2code
pip install .
```

## Jupyter plugin Uninstallation:
```
pip uninstall jupyter-text2code
```

## Usage Instructions:

- Open Jupyter notebook
- If installation happened successfully, then for the first time, Universal Sentence Encoder model will be downloaded from `tensorflow_hub`.
- Click on the `Terminal` Icon which appears on the menu (to activate the extension)
- Type "help" to see a list of currently supported commands in the repo
- Watch [Demo video](https://www.youtube.com/watch?v=3gZ7_9W-TJs) for some examples

## Model training:

### Generate training data:
From a list of templates present at `jupyter_text2code/jupyter_text2code_serverextension/data/ner_templates.csv`, generate training data by running the following command:
```
cd scripts && python generate_training_data.py
```
This command will generate data for intent matching and NER(Named Entity Recognition).

### Create intent index faiss
Use the generated data to create a intent-matcher using faiss.

```
cd scripts && python create_intent_index.py
```

### Train NER model
```
cd scripts && python train_spacy_ner.py
```

### Steps to add more intents:
- Add more templates in `ner_templates` with a new intent_id
- Generate training data. Modify `generate_training_data.py` if different generation techniques are needed or if introducing a new entity.
- Train intent index
- Train NER model
- modify `jupyter_text2code/jupyter_text2code_serverextension/__init__.py` with new intent's condition and add actual code for the intent
- Reinstall plugin by running: `pip install .`

### TODO:

- [ ] Publish Docker image
- [ ] Refactor code and make it mode modular, remove duplicate code, etc
- [ ] Add support for Windows
- [ ] Add support for more commands
- [ ] Improve intent detection and NER
- [ ] Explore sentence Paraphrasing to generate higher-quality training data
- [ ] Gather real-world variable names, library names as opposed to randomly generating them
- [ ] Try NER with a transformer-based model
- [ ] With enough data, train a language model to directly do English->code like GPT-3 does, instead of having separate stages in the pipeline
- [ ] Create a survey to collect linguistic data
- [ ] Add Speech2Code support

#### Authored By:

- [Deepak Rawat](https://twitter.com/dsr_ai)
- [Kartik Godawat](https://twitter.com/kartik_godawat)
