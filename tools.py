import pandas as pd
from datasets import load_dataset
import urllib.parse

dataset = load_dataset('json', data_files='/mnt/d/T/opendata_judgement/data_company_2463.json')

def decode_url(sample):
    sample["裁判書網址"] = urllib.parse.unquote(sample["裁判書網址"])
    return sample

dataset = dataset['train'].map(decode_url)
dataset = dataset.rename_columns({
    'JID': 'JID',
    'label': 'labels',
    'JTITLE': 'JTITLE',
    '裁判字號': 'Judgment_Number',
    '案件類型': 'Case_Type',
    '裁判日期': 'Judgment_Date',
    '調查對象': 'Investigated_Object',
    '裁判書網址': 'Judgment_URL',
    '摘要': 'Summary',
    'JFULL': 'JFULL',
})

df = pd.DataFrame(dataset)
new_order = ['JID', 'labels', 'JTITLE', 'Judgment_Number', 'Case_Type',
    'Judgment_Date', 'Investigated_Object', 'Judgment_URL', 'Summary', 'JFULL']
df = df.reindex(columns=new_order)
df.to_csv('dataset.csv', index=False, encoding='utf-8')