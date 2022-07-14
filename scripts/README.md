# `Scripts` dir - A Walk-through

### Note: Make sure to run all the following commands at `/scirpts` level in your terminal

### Preferred Tools:
- Python version: 3.7
- Python environment: conda
- Python package installer: pip

## Processing awesome-notebooks

To start off, run the following command to download the awesome-notebooks repo into the `input/` sub-directory
```
git clone https://github.com/jupyter-naas/awesome-notebooks.git ./input/
```

Then, in order to extract the tasks and code and create a `.pkl` out of it, run the following command
```
python3 process_awesome_notebooks.py create_pkl_file
```

and in order to create the faiss's FlatIndex using the Embeddings from the `.pkl` file, run
```
python3 process_awesome_notebooks.py create_faiss_index
```

and in order to get an intent, run the following command where `<query>` is your query and `<nearest_k>` is the number of nearest neighbours from your query's embedding
```
python3 process_awesome_notebooks.py get_intent <query> <nearest_k>
```

To evaluate the outputs of both tensorflow_hub and sentence_transformers embeddings, run the following command to create 2 `.csv` files, one for each type of encoder
```
python3 process_awesome_notebooks.py eval_models
```
To get speed benchmarks for each encoder over a fixed number of repetitions, run:
```
python3 process_awesome_notebooks.py get_benchmark_data <repetitions>
```

## Training NER model using spaCy v3

To generate training or validation data:
```
python3 generate_training_data.py <number of rows>
```

To convert the `.json` files to `.spacy` objects:
```
python3 train_spacy3_ner.py <input path> <output_path>
```

To create the default config file:
```
python3 train_spacy3_ner.py create_default_config_file
```

To train the NER model:
```
python3 train_spacy3_ner.py train_model
```

You now have a trained NER Model!