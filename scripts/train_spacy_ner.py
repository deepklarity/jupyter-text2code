#!/usr/bin/env python
# coding: utf8
"""Example of training spaCy's named entity recognizer, starting off with an
existing model or a blank model.
For more details, see the documentation:
* Training: https://spacy.io/usage/training
* NER: https://spacy.io/usage/linguistic-features#named-entities
Compatible with: spaCy v2.0.0+
Last tested with: v2.2.4
"""
from __future__ import unicode_literals, print_function

import plac
import random
import warnings
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding


# training data
import pickle
pickle_in = open("ner_train_data.pickle","rb")
TRAIN_DATA = pickle.load(pickle_in)

# TRAIN_DATA = [
#     ("import xxxxx", {"entities": [(7, 12, "LIBNAME")]}),
#     ("install spacy", {"entities": [(8, 13, "LIBNAME")]}),
#     ("load intent.csv", {"entities": [(5, 15, "FNAME")]}),
#     ("describe df", {"entities": [(9, 11, "VARNAME")]}),
#     ("Get correlation matrix of xxx", {"entities": [(26, 29, "VARNAME")]}),
#     ("load original_data.csv", {"entities": [(5, 22, "FNAME")]}),
#     ("load intent.csv in df", {"entities": [(5, 15, "FNAME"), (19, 21, "VARNAME")]}),
#     ("show 20 rows from df", {"entities": [(5, 7, "CARDINAL"), (18, 20, "VARNAME")]}),
#     ("print 10 rows of df", {"entities": [(6, 8, "CARDINAL"), (17, 19, "VARNAME")]}),
#     ("plot histogram of xxx column in xxxxxx", {"entities": [(18, 21, "COLNAME"), (32, 38, "VARNAME")]}),
#     ("plot histogram of xxxxx column in xxxx", {"entities": [(18, 23, "COLNAME"), (34, 38, "VARNAME")]}),
#     ("plot histogram of xxx column of xxx", {"entities": [(18, 21, "COLNAME"), (32, 35, "VARNAME")]}),
#     ("barplot xxx and xxxxxx columns of mydf", {"entities": [(8, 11, "COLNAME"), (16, 22, "COLNAME"), (34, 38, "VARNAME")]}),
#     ("plot xxxxxx and xxxxx columns of train_df in a bar plot", {"entities": [(5, 11, "COLNAME"), (16, 21, "COLNAME"), (33, 41, "VARNAME")]}),
#     ("piechart of xxx column in df grouped by xxxxxx column", {"entities": [(12, 15, "COLNAME"), (40, 46, "COLNAME"), (26, 28, "VARNAME")]}),
# ]


@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int),
)
def main(model=None, output_dir="../jupyter_text2code/jupyter_text2code_serverextension/models/ner", n_iter=10):
    """Load the model, set up the pipeline and train the entity recognizer."""
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")  # create blank Language class
        print("Created blank 'en' model")

    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last=True)
    # otherwise, get it so we can add labels
    else:
        ner = nlp.get_pipe("ner")

    # add labels
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    # only train NER
    with nlp.disable_pipes(*other_pipes), warnings.catch_warnings():
        # show warnings for misaligned entity spans once
        warnings.filterwarnings("once", category=UserWarning, module='spacy')

        # reset and initialize the weights randomly – but only if we're
        # training a new model
        if model is None:
            nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                    texts,  # batch of texts
                    annotations,  # batch of annotations
                    drop=0.5,  # dropout - make it harder to memorise data
                    losses=losses,
                )
            print("Losses", losses)

    # test the trained model
    # for text, _ in TRAIN_DATA:
    #     doc = nlp(text)
    #     print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
    #     print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        # print("Loading from", output_dir)
        # nlp2 = spacy.load(output_dir)
        # for text, _ in TRAIN_DATA:
        #     doc = nlp2(text)
        #     print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
        #     print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])


if __name__ == "__main__":
    plac.call(main)