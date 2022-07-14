import os

import fire
import spacy
import srsly
from spacy.tokens import DocBin


class SpaCy3NERTrainer:

    @staticmethod
    def convert(input_path, output_path, lang='en'):
        nlp = spacy.blank(lang)
        db = DocBin()
        for text, annot in srsly.read_json(input_path):
            doc = nlp.make_doc(text)
            ents = []
            for start, end, label in annot["entities"]:
                span = doc.char_span(start, end, label=label)
                if span is None:
                    print("Skipping entity")
                else:
                    ents.append(span)
            doc.ents = ents
            db.add(doc)
        db.to_disk(output_path)

    @staticmethod
    def create_default_config_file(lang='en', pipeline='ner', output='config.cfg', optimize='accuracy'):
        os.system(f'python -m spacy init config --lang {lang} --pipeline {pipeline} --optimize {optimize} {output}')

    @staticmethod
    def train_model(config='config.cfg', output='training/', train='corpus/train.spacy', dev='corpus/dev.spacy', vectors='sm'):
        os.system(f'python -m spacy download en_core_web_{vectors}')
        os.system(f'python -m spacy train {config} --output {output} --paths.train {train} --paths.dev {dev}')


if __name__ == '__main__':
    fire.Fire(SpaCy3NERTrainer)
