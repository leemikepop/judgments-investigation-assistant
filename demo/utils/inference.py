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



import json
# authentication
@st.cache_data
def get_abstract_from_bedrock(sample, investigation_subject):
    # 若全文長度大於10000，則取主文+綜上取代JFULL並取前10000字
    # if len(sample['JFULL']) > 10000:
    #     # 將摘要黏到 JFULL 前面並取前10000字
    #     jud_content = sample['JSUMMARY'] + sample['JFULL']
    #     jud_content = jud_content[:10000]
    # else:
    #     jud_content = sample['JFULL']
    jud_content = sample[:10000]
    content = f"""<content>{jud_content}</content>"""
    rule = f"""
    <rule>
    1.原告(plaintiff)：說明在此案中被告為哪些公司或哪些人。
    2.被告(defendant)：說明在此案中被告為哪些公司或哪些人。
    3.調查對象(subject)：<subject>的內容，是我們的調查對象，通常是公司或個人。
    4.摘要(summary)：簡述案情與判決結果，約200字。
    4.調查對象的涉案狀況(case description)：須說明兩件事，其一說明調查對象在此篇判決書中是"原告"或"被告"或"不知道"，其二簡述調查對象的涉案狀況，約100字，若該公司與此篇判決書無關則輸出"與此案無關"
    </rule>
    """
    subject = f"<subject>{investigation_subject}</subject>"
    prompt = f"""
    <prompt>
    你是銀行金融借貸的徵信調查人員正要調查<subject>提及的人物或公司，請你根據<content>中的裁判書內容，使用summarize_judgement工具生成JSON格式的回答。
    </prompt>
    """

    # https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html
    jud_tool = {
        "name": "summarize_judgement",
        "description": "Summarize judgement content.",
        "input_schema": {
            "type": "object",
            "properties": {
            "plaintiff": {
                "type": "string",
                "description": "Identifies the plaintiff(原告) in the judgment document."
            },
            "defendant": {
                "type": "string",
                "description": "Identifies the defendant(被告) in the judgment document."
            },
            "subject": {
                "type": "string",
                "description": "The subject of investigation in this judgment document.",
            },
            "subject_role": {
                "type": "string",
                "description": "The role of the subject of investigation in this judgment document.",
                "enum": ["原告", "被告", "關係人", "無關", "不知道"]
            },
            "chinese_summary": {
                "type": "string",
                "description": "Provides a summary of this judgment document."
            },
            "case_description": {
                "type": "string",
                "description": "Briefly describes the involvement of the subject of investigation in this judgment document."
            },
            "risk_score": {
                "type": "integer",
                "description": "Determines the risk of financial lending by the bank to the subject of investigation, ranging from 1 to 100.",
                "minimum": 1,
                "maximum": 100
            },          
            # "supporting_business_unit": {
            #     "type": "string",
            #     "description": "The internal business unit that this email should be routed to.",
            #     "enum": ["Sales", "Operations", "Customer Service", "Fund Management"]
            # },
            # "customer_names": {
            #     "type": "array",
            #     "description": "An array of customer names mentioned in the email.",
            #     "items": { "type": "string" }
            # },
            # "sentiment_towards_employees": {
            #     "type": "array",
            #     "items": {
            #         "type": "object",
            #         "properties": {
            #             "employee_name": {
            #                 "type": "string",
            #                 "description": "The employee's name."
            #             },
            #             "sentiment": {
            #                 "type": "string",
            #                 "description": "The sender's sentiment towards the employee.",
            #                 "enum": ["Positive", "Neutral", "Negative"]
            #             }
            #         }
            #     }
            # }
            },
            "required": [
                "plaintiff",
                "defendant",
                "subject",
                "subject_role",
                "chinese_summary",
                "case_description",
                "risk_score"
            ]
        }
    }

    # Claude 3 Haiku
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4000,
        "system": rule,
        # "stop_sequences": [""],
        "messages": [
            # {
            #     "role": "assistant",
            #     "content": [
            #         {"type": "text", "text": rule}
            #     ]
            # },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": content},
                    {"type": "text", "text": subject},
                    {"type": "text", "text": prompt},                
                ]
            }
        ],
        "temperature": 0.5,
        # "top_p": 0.999,
        # "top_k ": 500,
        "tools": [jud_tool],
        "tool_choice": {
            "type": "tool",
            "name": "summarize_judgement"
        }
    }
    kwargs = {
        "body": json.dumps(body),
        "contentType": "application/json",
        "accept": "application/json",
        "modelId": 'anthropic.claude-3-sonnet-20240229-v1:0',#"anthropic.claude-3-haiku-20240307-v1:0", #'anthropic.claude-3-5-sonnet-20240620-v1:0'
        # "trace": 'DISABLED', #'ENABLED'|'DISABLED',
        # "guardrailIdentifier":None, #'string',
        # "guardrailVersion":None, #'string'
    }
    response = st.session_state["bedrock_client"].invoke_model(**kwargs) # dict_keys(['ResponseMetadata', 'contentType', 'body'])
    response_body = json.loads(response.get('body').read()) # dict_keys(['id', 'type', 'role', 'model', 'content', 'stop_reason', 'stop_sequence', 'usage'])
    return response_body["content"][0]["input"]  # dict_keys(['plaintiff', 'defendant', 'subject', 'subject_role', 'chinese_summary', 'case_description', 'risk_score'])
