# Text2Code for Jupyter notebook

![](mopp-demo.gif)

### Blog post with more details:
#### [Data analysis made easy: Text2Code for Jupyter notebook](https://towardsdatascience.com/data-analysis-made-easy-text2code-for-jupyter-notebook-5380e89bb493)

### Demo Video:
#### [Text2Code for Jupyter notebook](https://www.youtube.com/watch?v=3gZ7_9W-TJs)

## Jupyter plugin Installation:
```
pip install .
```

## Model training:

### Generate training data:
From a list of templates present at `mopp/mopp_serverextension/data/ner_templates.csv`, generate training data by running the following command:
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
- modify `mopp/mopp_serverextension/__init__.py` with new intent's condition and add actual code for the intent
- Reinstall plugin by running: `pip install .`


#### Authored By:

- [Deepak Rawat](https://twitter.com/deepak_s_rawat)
- [Kartik Godawat](https://twitter.com/kartik_godawat)