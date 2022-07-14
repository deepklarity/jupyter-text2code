import pandas as pd

backend_dir = "../jupyter_text2code/jupyter_text2code_serverextension"

jt2c = pd.read_csv(f'{backend_dir}/data/ner_templates.csv')[['intent_id', 'template', 'code']]
jt2c.columns = ['intent_id', 'task', 'code']
naas = pd.read_csv(f'{backend_dir}/data/awesome-notebooks.csv')[['intent_id', 'task', 'code']]

lookup_df = pd.concat([jt2c, naas], axis=0)
lookup_df.columns = ['intent_id', 'intent', 'code']
lookup_df = lookup_df.drop_duplicates('intent_id')
lookup_df.to_csv(f'{backend_dir}/data/intent_lookup.csv', index=False)


