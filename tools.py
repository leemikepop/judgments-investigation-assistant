import pandas as pd
from datasets import load_dataset
import urllib.parse

dataset = load_dataset('json', data_files='/mnt/d/T/opendata_judgement/data_company_4014.json')

def decode_url(sample):
    sample["裁判書網址"] = urllib.parse.unquote(sample["裁判書網址"])
    sample["裁判日期"] = sample["裁判日期"][:8]
    sample["JFULL"] = ""
    return sample


dataset = dataset['train'].map(decode_url)
dataset = dataset.rename_columns({
    'JID': 'JID',
    'label': 'JSCORE',
    'JTITLE': 'JTITLE',
    '裁判字號': 'JCHAR',
    '案件類型': 'JTYPE',
    '裁判日期': 'JDATE',
    '調查對象': 'JOBJECT',
    '裁判書網址': 'JURL',
    '摘要': 'JSUMMARY',
    'JFULL': 'JFULL',
})

df = pd.DataFrame(dataset)
new_order = ['JID', 'JSCORE', 'JTITLE', 'JCHAR', 'JTYPE',
    'JDATE', 'JOBJECT', 'JURL', 'JSUMMARY', 'JFULL']
df = df.reindex(columns=new_order)
df.loc[:,"JDATE"] = pd.to_datetime(df.loc[:,"JDATE"], yearfirst=True, format="%Y%m%d").apply(lambda x: x.date())
df.to_csv('dataset2_no_JFULL.csv', index=False, encoding='utf_8_sig')