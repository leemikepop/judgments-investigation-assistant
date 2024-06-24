import streamlit as st
# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# from transformers import DataCollatorWithPadding
# import torch
# from torch.utils.data import DataLoader, Dataset


# @st.cache_resource
# def load_tokenizer(checkpoint):
#     return AutoTokenizer.from_pretrained(checkpoint)

# @st.cache_resource
# def load_model(checkpoint):
#     classes = ['neg']
#     class2id = {class_:id for id, class_ in enumerate(classes)}
#     id2class = {id:class_ for class_, id in class2id.items()}
#     return AutoModelForSequenceClassification.from_pretrained(checkpoint, num_labels=1, id2label=id2class, label2id=class2id)

# class JDataset(Dataset):
#     def __init__(self, JSUMMARYs, tokenizer):
#         self.JSUMMARYs = JSUMMARYs
#         self.tokenizer = tokenizer

#     def __len__(self):
#         return len(self.JSUMMARYs)

#     def __getitem__(self, index):
#         tokens = self.tokenizer(self.JSUMMARYs[index], truncation=True, padding=True, add_special_tokens=True)
#         return tokens

# def scoreInference(JSUMMARYs):
#     checkpoint = "./bert-base-zhtw-3t-cls-best"
#     tokenizer = load_tokenizer(checkpoint)
#     model = load_model(checkpoint)
#     dataset = JDataset(JSUMMARYs, tokenizer)
#     data_collator = DataCollatorWithPadding(tokenizer)
#     dataloader = DataLoader(
#         dataset, batch_size=1, collate_fn=data_collator, shuffle=False
#     )
#     scores = []
#     for batch in dataloader:
#         with torch.no_grad():
#             score = model(**batch)
#         scores.append(score.logits.item())
#     print(scores)
#     return scores


import boto3
import json
# authentication
if "session" not in st.session_state:
    st.session_state["session"] = boto3.Session(
        aws_access_key_id=st.secrets["BEDROCK"]["ACCESS_KEY"],
        aws_secret_access_key=st.secrets["BEDROCK"]["SECRET_KEY"]
    )
if "bedrock_client" not in st.session_state:
    st.session_state["bedrock_client"] = st.session_state["session"].client('bedrock-runtime', region_name='us-east-1')

@st.cache_data
def get_abstract_from_bedrock(sample, company_name):
    # 若全文長度大於10000，則取主文+綜上取代JFULL並取前10000字
    # if len(sample['JFULL']) > 10000:
    #     # 將摘要黏到 JFULL 前面並取前10000字
    #     jud_content = sample['JSUMMARY'] + sample['JFULL'] 
    #     jud_content = jud_content[:10000]
    # else:
    #     jud_content = sample['JFULL']
    jud_content = sample[:10000]

    prompt = f"""
    <role>
    銀行徵信調查人員
    </role>
    
    <template>
    被告：<system output>\n
    原告：<system output>；\n
    摘要：<system output>\n
    {company_name}的涉案狀況： 
    </template>

    <rule>
    1.被告：說明在此案中被告為哪些公司或哪些人
    2.原告：說明在此案中被告為哪些公司或哪些人
    3.摘要：簡述案情與判決結果，約100字
    4.{company_name}的涉案狀況：須說明兩件事，其一說明{company_name}在此篇判決書中是"原告"或"被告"或"不知道"，其二簡述{company_name}的涉案狀況，約70字，若該公司與此篇判決書無關則輸出"與此案無關"
    5.輸出請嚴格按照<template>中的模板生成對應內容，即文字、空格以及換行需一模一樣。
    6.輸出時絕對不要用html的標籤
    </rule>

    <content>
    {jud_content}
    </content>

    <prompt>
    你是<role>中所述的專業人士，請你根據<content>中的裁判書內容，以及<rule>中的輸出規則，嚴格按照<template>中的模板生成對應內容，謝謝。
    </prompt>
    """

    # Claude 3 Haiku
    messages_API_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": int(500 / 0.75),
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    }
    kwargs = {
        "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
        "contentType": "application/json",
        "accept": "application/json",
        "body": json.dumps(messages_API_body)
    }
    response = st.session_state["bedrock_client"].invoke_model(**kwargs)
    response_body = json.loads(response.get('body').read())
    return response_body['content'][0]['text']  # for Claude 3
