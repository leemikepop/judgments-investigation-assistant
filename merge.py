import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib
import json
import pandas as pd
from collections import Counter
import os
import seaborn as sns
import datetime

USERNAME = "scsb"
PASSWORD = "scsb"
FILENAME = "data_company_2463.json"


def main():
    # 設定頁面資料
    st.set_page_config(
        page_title="上海商銀裁判書小幫手",
        page_icon="scsb_logo.png",
        layout="wide")

    # 初始化設定, 參數設定
    if 'page' not in st.session_state:
        st.session_state.page = 0
    if "searchpage" not in st.session_state:
        st.session_state.searchpage = 0
    if "start_date" not in st.session_state:
        st.session_state.start_date = "20000000"
    if "end_date" not in st.session_state:
        st.session_state.end_date = "20250000"
    if "typelist" not in st.session_state:
        st.session_state.typelist = ["憲法", "民事", "刑事", "行政", "懲戒"]
    if "maintext_search" not in st.session_state:
        st.session_state.maintext_search = None
    if "content_search" not in st.session_state:
        st.session_state.content_search = None
    if "judgement_reason" not in st.session_state:
        st.session_state.judgement_reason = None
    if "company_name" not in st.session_state:
        st.session_state.company_name = None

    # 載入照片Logo
    logo = Image.open("scsb_logo.png")

    # control page
    if st.session_state['page'] == 0: # login
        web_login()
    elif st.session_state['page'] == 1: # search
        web_search(logo)
    elif st.session_state['page'] == 2: # chart
        # 載入資料
        @st.cache_data
        def read_data(filename):
            return pd.read_json(filename, encoding="utf-8")

        data = read_data(FILENAME)
        filter = data["調查對象"].str.contains(st.session_state['company_name'])
        data = data[filter]

        web_search2(logo)
        chart_overall(logo, data)
        



def web_login():
    # define CSS
    st.markdown("""
        <style>
        .centered {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        .input-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 10px;
        }
        .input-container label {
            margin-right: 10px;
            font-size: 18px;
        }
        .input-container input {
            border: 2px solid #FF4B4B;
            border-radius: 5px;
            padding: 5px;
            width: 200px;
        }
        .stButton button {
            background-color: #FF4B4B;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            display: block;
            margin: 0 auto;
        }
        .header {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .header img {
            margin-right: 10px;
            vertical-align: bottom;
        }
        .label {
        font-size: 16px;
        margin-right: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

    # 頁面内容
    col1, col2, col3 = st.columns([0.8, 0.3, 2.7])

    st.markdown("<div class='header'>", unsafe_allow_html=True)
    col2.markdown("<span style='font-size:6px;'> </span>", unsafe_allow_html=True)
    col2.image("scsb_logo.png", width=50)
    col3.markdown("<h1>上海商銀裁判書小幫手</h1>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        with st.form(key='login_form2'):
            colu0, colu1, colu2, colu3 = st.columns([0.6, 0.4, 1.5, 1])
            colu1.markdown('<h6> </h6>', unsafe_allow_html=True)
            colu1.markdown('<label>帳號</label>', unsafe_allow_html=True)
            username = colu2.text_input("帳號", label_visibility="hidden")
            colu1.markdown('<h5> </h5>', unsafe_allow_html=True)
            colu1.markdown('<label>密碼</label>', unsafe_allow_html=True)
            password = colu2.text_input("密碼", type="password", label_visibility="hidden")
            submit_button = st.form_submit_button(label='登入')

            # 處理表單提交
            if submit_button:
                if username and password:
                    if username == USERNAME and password == PASSWORD:
                        st.session_state['page'] = 1
                        st.experimental_rerun()
                    else:
                        col1, col2, col3 = st.columns([1, 1, 1])
                        col2.error("帳號或密碼錯誤")
                else:
                    col1, col2, col3 = st.columns([1, 1, 1])
                    col2.error("請輸入帳號和密碼")


def web_search(logo):
    # title
    col1, col2, col3 = st.columns([1, 9, 12])
    with col1:
        st.image(logo, width=30)
    with col2:
        st.markdown("<h3 style='text-align: left; color: grey;'>上海商銀裁判書小幫手</h3>",
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Add the search input field with placeholder text
    st.markdown("""
    <style>
        .label {
            font-size: 16px;
            margin-right: 10px;
        }
        .date-range-button {
            background-color: #FF4B4B;
            border: none;
            padding: 10px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            color: white;
        }
        .date-range-button:hover {
            background-color: #f1948a;
        }
    </style>
    """, unsafe_allow_html=True)

    col0, col1, col2, col3 = st.columns([1, 3, 0.1, 0.9])
    company_name = col1.text_input("請輸入公司")
    col2.markdown("<br>", unsafe_allow_html=True)
    search = col2.button(':mag:', help="搜尋")

    if search:
        if company_name == "":
            col1.error("請輸入公司")
        else:
            st.session_state.company_name = company_name
            st.session_state['page'] = 2
            st.experimental_rerun()


def web_search2(logo):
    # title
    col1, col2, col3 = st.columns([1, 9, 12])
    with col1:
        st.image(logo, width=30)
    with col2:
        st.markdown("<h3 style='text-align: left; color: grey;'>上海商銀裁判書小幫手</h3>",
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Add the search input field with placeholder text
    st.markdown("""
    <style>
        .label {
            font-size: 16px;
            margin-right: 10px;
        }
        .date-range-button {
            background-color: #FF4B4B;
            border: none;
            padding: 10px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            color: white;
        }
        .date-range-button:hover {
            background-color: #f1948a;
        }
    </style>
    """, unsafe_allow_html=True)

    col0, col1, col2, col3 = st.columns([1, 3, 0.1, 0.9])
    company_name = col1.text_input("請輸入公司")
    col2.markdown("<br>", unsafe_allow_html=True)
    search = col2.button(':mag:', help="搜尋")

    if search:
        if company_name == "":
            col1.error("請輸入公司")
        else:
            st.session_state.company_name = company_name
            st.session_state['page'] = 2
            st.experimental_rerun()

def chart_overall(logo, data):
    # Define CSS styles
    st.markdown("""
        <style>
            .header-container {
                display: flex;
                align-items: center;
                justify-content: start;
                padding: 10px;
            }
            .header-logo {
                width: 40px;
                height: 40px;
            }
            .label {
                font-size: 16px;
                margin-right: 10px;
            }
            .content-container {
                padding: 20px;
                background-color: #f8f9fa;
            }
            .chart-container {
                display: flex;
                justify-content: space-around;
                background-color: #f8f9fa;
            }
            .chart {
                width: 30%;
                border: 2px solid #c3c3c3;
                padding: 10px;
                border-radius: 10px;
            }
            .chart-title {
                font-size: 18px;
                text-align: center;
            }
            .text-section {
                margin-top: 20px;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 10px;
            }
            .text-section p {
                font-size: 16px;
                line-height: 1.5;
            }
        </style>
    """, unsafe_allow_html=True)

    # form title
    with st.expander("公司總體報表",expanded=True):

        # charts
        company_name = st.session_state['company_name']
        
        st.markdown(f"""<h3 style="text-align: center;">{company_name}</h3>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # draw pie chart
        # 提取字段data
        jtitle_data = data['JTITLE']
        category_data = data['案件類型']
        label_data = data['label']
        time_data = data['裁判日期']
        df = pd.DataFrame(time_data)
        df['年份'] = df['裁判日期'].str[:4]
        time_df = df[['年份']]
        year_counts = df['年份'].value_counts().sort_index()

        # 生成统計data
        jtitle_counter = Counter(jtitle_data)
        category_counter = Counter(category_data)
        label_counter = Counter(label_data)

        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            create_pie_chart(jtitle_counter, '裁判案由')
        with col1:
            # create_pie_chart(category_counter, '案件類型')
            # 長條圖
            # 中文字體
            zhfont1 = matplotlib.font_manager.FontProperties(
                fname=".\SourceHanSerifTC-Medium.otf")
            fig, ax = plt.subplots()
            colors = ['lightpink'] * len(year_counts)
            year_counts.plot(kind='bar', ax=ax, color=colors)
            ax.set_xlabel('年份', fontproperties=zhfont1, fontsize=20, weight='bold')
            ax.set_ylabel('案件數量', fontproperties=zhfont1, fontsize=20, weight='bold')
            ax.set_title('年份-案件數量長條圖', fontproperties=zhfont1, fontsize=20, weight='bold', pad=30)
            ax.xaxis.labelpad = 10
            ax.yaxis.labelpad = 10
            st.pyplot(fig)
        with col3:
            create_pie_chart(label_counter, '信貸分數')


        st.markdown("""<div class="chart-container">""", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 5])
        with col1:
            score = round(data['label'].sum() / len(data),2)
            plot_score(score)

        col2.markdown(f"""
            <br/>
            <div class="text-section">
                <p> {st.session_state['company_name']}近年來在業界的信譽有所下降，因為其多個項目出現嚴重的延誤和質量問題，導致客戶不滿。該公司在財務管理上表現不佳，多次被曝出拖欠供應商和工人工資的情況，並且在成本控制方面也存在明顯不足。由於經營狀況不穩定，長鴻營造難以獲得銀行信貸支持，成為金融機構眼中的高風險對象。這些問題不僅影響了公司的市場競爭力，也對其長期發展構成了重大挑戰。
                </p>
            </div>""", unsafe_allow_html=True)
        

        # download
        csv_data = data.to_csv(index=False).encode("utf-8")
        st.download_button(label="Download", data=csv_data, file_name=f"{company_name}_總體報表.csv",
                           mime="text/csv", )
    # 搜尋系統
    st.header("搜尋系統")
    with st.expander("",expanded=True):
        with st.form("search_system",border=False):

            # 裁判時間範圍
            st.markdown("**裁判時間範圍**")
            date = st.columns(2)
            start_date = date[0].date_input("起始日期",value=datetime.date(2020,1,1))
            end_date = date[1].date_input("結束日期")
            
            # 案件類型
            st.markdown("**案件類型**")
            type = st.columns(5)
            constitution = type[0].checkbox("憲法")
            civil = type[1].checkbox("民事")
            criminal = type[2].checkbox("刑事")
            administrative = type[3].checkbox("行政")
            discipline = type[4].checkbox("懲戒")

            # 關鍵字
            st.markdown("**關鍵字**")
            keyword = st.columns(2)
            maintext_search = keyword[0].text_input("主文搜尋")
            content_search = keyword[1].text_input("內文搜尋")

            # 裁判案由
            st.markdown("**裁判案由**")
            judgement_reason = st.text_input("裁判案由")

            # 搜尋按鈕
            search_button = st.form_submit_button("搜尋")
            if search_button:
                st.session_state.searchpage = 0
                st.session_state.start_date = str(start_date).replace("-","")
                st.session_state.end_date = str(end_date).replace("-","")

                if constitution or civil or criminal or administrative or discipline:
                    st.session_state.typelist = []
                    if constitution: st.session_state.typelist.append("憲法")
                    if civil: st.session_state.typelist.append("民事")
                    if criminal: st.session_state.typelist.append("刑事")
                    if administrative: st.session_state.typelist.append("行政")
                    if discipline: st.session_state.typelist.append("懲戒")
                else:
                    st.session_state.typelist = ["憲法","民事","刑事","行政","懲戒"]

                if maintext_search == "":
                    st.session_state.maintext_search = None
                else:
                    st.session_state.maintext_search = maintext_search
                if content_search == "":
                    st.session_state.content_search = None
                else:
                    st.session_state.content_search = content_search
                if judgement_reason == "":
                    st.session_state.judgement_reason = None
                else:
                    st.session_state.judgement_reason = judgement_reason

    df = data
    # 用表單存在session_state的變數過濾資料
    if st.session_state.start_date or st.session_state.end_date:
        filter_time = (df["裁判日期"].between(st.session_state.start_date,st.session_state.end_date))
        df = df[filter_time]
    if st.session_state.typelist:
        filter_type = (df["案件類型"].isin(st.session_state.typelist))
        df = df[filter_type]
    if st.session_state.maintext_search:
        filter_maintext = (df["摘要"].str.contains(st.session_state.maintext_search))
        df = df[filter_maintext]
    if st.session_state.content_search:
        filter_content = (df["JFULL"].str.contains(st.session_state.content_search))
        df = df[filter_content]
    if st.session_state.judgement_reason:
        filter_reason = (df["JTITLE"] == st.session_state.judgement_reason)
        df = df[filter_reason]


    # 按照分數排列，並且轉換為字典
    df = df.sort_values(by="label", ascending=False)
    data_list = df.to_dict(orient="records")
    page_count = len(data_list)

    #表列資料
    st.header("表列裁判書(依信貸分數排序)")
    searchpage = st.session_state.searchpage
    for i in range(searchpage*10,searchpage*10+10,1):
        if i == page_count:
            break
        with st.container(border=True):
            col1, col2 = st.columns([1,7])
            with col1:
                # 找到分數並印出來
                score = data_list[i]["label"]
                plot_score(score)
            with col2:
                #裁判字號,裁判日期,裁判案由
                data_name = data_list[i]["裁判字號"].replace(" ","")
                data_date = data_list[i]["裁判日期"]
                data_reason = data_list[i]["JTITLE"]
                st.markdown(f"**{data_name}-{data_date}-{data_reason}**")

                #內文
                content = data_list[i]["摘要"][0:200] + "..."
                st.markdown(content)
                
                # 摘要(可能要使用bedrock的api)
                summary = """
                上訴人：國防部政治作戰局\n
                被上訴人：長鴻營造股份有限公司\n
                主文：原判決廢棄。被上訴人在第一審之訴及假執行之聲請均駁回。第一、二審訴訟費用及發回前，第三審訴訟費用均由被上訴人負擔。\n
                負面關鍵字：駁回、施工不當、損害賠償
                """
                toggle = st.toggle("摘要",key=i)
                if toggle:
                    st.info(summary)

    # 上一頁和下一頁

    def pre_page():
        if st.session_state.searchpage == 0:
            st.session_state.searchpage = st.session_state.searchpage
        else:
            st.session_state.searchpage = st.session_state.searchpage - 1

    def next_page():
        if st.session_state.searchpage == page_count//10:
            st.session_state.searchpage = st.session_state.searchpage
        else:
            st.session_state.searchpage  = st.session_state.searchpage + 1


    col = st.columns(7)
    col[2].button("上一頁",on_click=pre_page)
    col[3].text(f"第{st.session_state.searchpage+1}頁,共{page_count//10+1}頁")
    col[4].button("下一頁",on_click=next_page)

def plot_score(score):
            """
            :param score: float, average score
            :return: none, show score
            """
            x = [score, 1 - score]
            pie = plt.pie(
                x,
                counterclock=False,
                startangle=90,
                colors=["#FF3131", "#C0C0C3"],
                wedgeprops={'linewidth': 3, 'edgecolor': 'w', 'width': 0.5})
            plt.text(0, 0, score, va="center", ha="center", fontsize=42, fontweight='bold', color="#FF3131",
                     fontfamily="Microsoft JhengHei")
            plt.text(0, -1.4, "信貸分數", va="center", ha="center", fontsize=30, fontweight='light', color="black",
                     fontfamily="Microsoft JhengHei")
            st.pyplot(plt, clear_figure=True)

def create_pie_chart(counter, title):
    # 中文字體
    zhfont1 = matplotlib.font_manager.FontProperties(
        fname=".\SourceHanSerifTC-Medium.otf")

    labels = counter.keys()
    sizes = counter.values()
    colors = ['firebrick', 'indianred', 'lightpink', 'lightcoral', 'pink', 'darksalmon', 'salmon', 'mistyrose']
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140,
            textprops={'color': 'k', 'fontsize': 70, 'weight': 'bold', 'fontproperties': zhfont1})
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title(title, fontproperties=zhfont1, fontsize=20, weight='bold', pad=30)
    st.pyplot(plt, clear_figure=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
