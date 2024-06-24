# import json
# import math
import pandas as pd
import requests
from bs4 import BeautifulSoup
import boto3

# All available objects and there usage are listed there: https://github.com/okld/streamlit-elements#getting-started
import streamlit as st
from streamlit_elements.core.callback import ElementsCallbackData
from streamlit_elements import elements, dashboard, mui, lazy, sync, html
from utils.events import chgLayout, chgSearchMode, clkChip, delChip, clkAnalyze, clkSearchButton, doSearch, chgPage, chgPageNum, keyPressPage, showResults, showResults2
from utils.drawer import drawPieChart, drawLineChart
from utils.inference import get_abstract_from_bedrock
from streamlit_modal import Modal, contextmanager

# import streamlit.components.v1 as components

# 設定
st.set_page_config(
    page_title="裁判書徵信助手-Demo",
    page_icon="🤖",
    # layout="centered",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 版面
if 'layout1' not in st.session_state:
    st.session_state.layout1 = [
        # Editor item is positioned in coordinates x=0 and y=0, and takes 12/12 columns and has a height of 2.
        dashboard.Item("searchBar", 0, 0, 12, 2),
        # Chart item is positioned in coordinates x=0 and y=2, and takes 6/12 columns and has a height of 8.
        dashboard.Item("judgmentsCard", 0, 2, 6, 6),
        # Media item is positioned in coordinates x=6 and y=2, and takes 6/12 columns and has a height of 8.
        dashboard.Item("abstractArea", 6, 2, 6, 6),
    ]
if 'layout2' not in st.session_state:
    st.session_state.layout2 = [
        # Editor item is positioned in coordinates x=0 and y=0, and takes 12/12 columns and has a height of 2.
        dashboard.Item("searchBar", 0, 0, 12, 2),
        # Chart item is positioned in coordinates x=0 and y=2, and takes 6/12 columns and has a height of 8.
        dashboard.Item("judgmentsCard", 0, 2, 12, 6),
        # Media item is positioned in coordinates x=6 and y=2, and takes 6/12 columns and has a height of 8.
        dashboard.Item("abstractArea", 0, 8, 12, 6),
    ]
if 'layout' not in st.session_state:
    # https://github.com/react-grid-layout/react-grid-layout#grid-item-props
    st.session_state["layout"] = st.session_state["layout2"]
if 'colors' not in st.session_state:
    st.session_state.colors = ["hsl(309, 70%, 50%)", "hsl(229, 70%, 50%)", "hsl(78, 70%, 50%)", "hsl(278, 70%, 50%)", "hsl(273, 70%, 50%)"]
import streamlit.components.v1 as components
class MyModal(Modal):
    def open(self):
        st.session_state[f'{self.key}-opened'] = True
    @contextmanager
    def container(self):
        st.markdown(
            f"""
            <style>
            div[data-modal-container='true'][key='{self.key}'] {{
                position: fixed; 
                width: 100vw !important;
                height: 100vh !important;
                left: 0;
                z-index: 999992;
            }}

            div[data-modal-container='true'][key='{self.key}'] > div:first-child {{
                margin: auto;
            }}

            div[data-modal-container='true'][key='{self.key}'] h1 a {{
                display: none
            }}

            div[data-modal-container='true'][key='{self.key}']::before {{
                    position: fixed;
                    content: ' ';
                    left: 0;
                    right: 0;
                    top: 0;
                    bottom: 0;
                    z-index: 1000;
                    background-color: rgba(50,50,50,0.8);
            }}
            div[data-modal-container='true'][key='{self.key}'] > div:first-child {{
                max-width: {self.max_width};
                max-height: 800;
            }}

            div[data-modal-container='true'][key='{self.key}'] > div:first-child > div:first-child {{
                width: unset !important;
                background-color: #fff; /* Will be overridden if possible */
                padding: {self.padding}px;
                margin-top: {2*self.padding}px;
                margin-left: -{2*self.padding}px;
                margin-right: -{2*self.padding}px;
                margin-bottom: -{2*self.padding}px;
                z-index: 1001;
                border-radius: 5px;
            }}
            div[data-modal-container='true'][key='{self.key}'] > div:first-child > div:first-child > div:first-child  {{
                overflow-y: scroll;
                max-height: 80vh;
                overflow-x: hidden;
                max-width: {self.max_width};
            }}
            
            div[data-modal-container='true'][key='{self.key}'] > div > div:nth-child(2)  {{
                z-index: 1003;
                position: absolute;
            }}
            div[data-modal-container='true'][key='{self.key}'] > div > div:nth-child(2) > div {{
                text-align: right;
                padding-right: {self.padding}px;
                max-width: {self.max_width};
            }}

            div[data-modal-container='true'][key='{self.key}'] > div > div:nth-child(2) > div > button {{
                right: 0;
                margin-top: {2*self.padding + 14}px;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        with st.container():
            _container = st.container()
            
            title, close_button = _container.columns([0.9, 0.05])
            if self.title:
                with title:
                    st.header(self.title)
            with close_button:
                close_ = st.button('X', key=f'{self.key}-close')
                if close_:
                    self.close()
            
            _container.divider()

        components.html(
            f"""
            <script>
            // STREAMLIT-MODAL-IFRAME-{self.key} <- Don't remove this comment. It's used to find our iframe
            const iframes = parent.document.body.getElementsByTagName('iframe');
            let container
            for(const iframe of iframes)
            {{
            if (iframe.srcdoc.indexOf("STREAMLIT-MODAL-IFRAME-{self.key}") !== -1) {{
                container = iframe.parentNode.previousSibling;
                container.setAttribute('data-modal-container', 'true');
                container.setAttribute('key', '{self.key}');
                
                // Copy background color from body
                const contentDiv = container.querySelector('div:first-child > div:first-child');
                contentDiv.style.backgroundColor = getComputedStyle(parent.document.body).backgroundColor;
            }}
            }}
            </script>
            """,
            height=0, width=0
        )

        with _container:
            yield _container
if 'modal' not in st.session_state:
    st.session_state["modal"] = MyModal(
        "AI摘要", 
        key="demo-modal",
        # Optional
        padding=10,    # default value
        max_width=1000  # default value
    )
if 'modal_data' not in st.session_state:
    st.session_state["modal_data"] = None
# 資料
if 'dataset' not in st.session_state:
    try:
        st.session_state["dataset"] = pd.read_csv('dataset2_no_JFULL.csv')
    except Exception:
        st.session_state["dataset"] = None
if "ret" not in st.session_state: #搜尋結果
    st.session_state["ret"] = None
if "analyzedData" not in st.session_state: #分析結果
    st.session_state["analyzedData"] = None
if "session" not in st.session_state:
    st.session_state["session"] = boto3.Session(
        aws_access_key_id=st.secrets["BEDROCK"]["ACCESS_KEY"],
        aws_secret_access_key=st.secrets["BEDROCK"]["SECRET_KEY"]
    )
if "bedrock_client" not in st.session_state:
    st.session_state["bedrock_client"] = st.session_state["session"].client(
        'bedrock-runtime', region_name='us-east-1')
# 狀態
if "searchMode" not in st.session_state:
    st.session_state["searchMode"] = False
if "need2Search" not in st.session_state:
    st.session_state["need2Search"] = False
if 'curr_page' not in st.session_state:
    st.session_state["curr_page"] = 1
if 'total_page' not in st.session_state:
    st.session_state["total_page"] = None
if 'pageKeyPressed' not in st.session_state:
    st.session_state["pageKeyPressed"] = False
# 使用者輸入
if "searchInputText" not in st.session_state:
    st.session_state["searchInputText"] = ""
if "searchHistories" not in st.session_state:
    st.session_state["searchHistories"] = {"閎大營造", "山林水環境工程", "台灣世曦工程顧問", "旺宏電子", "長鴻營造", "欣興電子", "緯創資通"} # set()
if 'pageText' not in st.session_state:
    st.session_state["pageText"] = None

@st.cache_data
def requesJudgs(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    div_element = soup.find('div', {'id': 'jud'})
    if div_element:
        td_element = div_element.find('td', {'class': 'tab_linenu'})  # 找到目標td元素
        if td_element:
            td_element.extract()  # 刪除該td元素
        return div_element.text
    else:
        return None

# 刷新頁面時要檢查的狀態
if st.session_state["modal"].is_open():
    st.session_state["modal"].title = f"[AI摘要] {st.session_state['modal_data']['JCHAR']}"
    with st.session_state["modal"].container():
        with elements("modal"):
            url = st.session_state["modal_data"]["JURL"]
            content = requesJudgs(url)
            if content is not None:
                result = get_abstract_from_bedrock(content, st.session_state["searchInputText"])
                with mui.Typography(sx={"overflow":"auto"}):
                    st.markdown(f"""<b>調查對象：</b>{result["subject"]} ({result["subject_role"]})<br/><br/>"""
                                f"""<b>原告：</b>{result["plaintiff"]}<br/><br/>"""
                                f"""<b>被告：</b>{result["defendant"]}<br/><br/>"""
                                f"""<b>風險評分：</b>{result["risk_score"]} / 100 <br/><br/><br/>"""
                                f"""<b>簡述：</b>{result["chinese_summary"]}<br/><br/>"""
                                f"""<b>AI摘要：</b>{result["case_description"]}""", unsafe_allow_html= True)
            else:
                mui.Typography("裁判書擷取失敗")
            
            
            

if st.session_state["pageKeyPressed"] and st.session_state["pageText"]:
    st.session_state["pageKeyPressed"] = False
    try:
        if isinstance(st.session_state["pageText"], ElementsCallbackData):
            st.session_state["pageText"] = st.session_state["pageText"].target.value
        chgPageNum(int(st.session_state["pageText"]))
    except Exception as e:
        print(st.session_state["pageText"])
        print("Exception in `chgPageNum(int(st.session_state.pageText))`")
    st.session_state.pageText = None

if st.session_state.need2Search:
    st.session_state.need2Search = False
    doSearch()    

# 側邊欄(選擇版面配置)
with st.sidebar:
    st.header("選擇一個版面配置")
    with elements("sidebar"):
        with mui.RadioGroup(defaultValue="layout2", onChange=chgLayout):
            mui.FormControlLabel(control=mui.Radio, value="layout1", label=html.img(src="https://i.imgur.com/4VwKRF2.png"), sx={"margin": '10px', "padding": '20px'})
            mui.FormControlLabel(control=mui.Radio, value="layout2", label=html.img(src="https://i.imgur.com/UBLNnGA.png"), sx={"margin": '10px', "padding": '20px'})

#主體
with elements("demo"):

    with dashboard.Grid(st.session_state.layout, draggableHandle=".draggable"):

        ## 搜尋 ##
        with mui.Card(key="searchBar", sx={"display": "flex", "flexDirection": "column"}):

            # 可拖拽表頭 #
            mui.CardHeader(title="🔍搜尋徵信對象")# , className="draggable"

            # 卡片主體 #
            with mui.CardContent(sx={"flex": 1, "minHeight": 0}):

                # 線上/本地 切換紐 #
                mui.FormControlLabel(control=mui.Switch(defaultChecked=st.session_state["searchMode"], onChange=chgSearchMode), label="啟用網路搜尋", sx={"marginBottom":"10px"})
                
                # 搜尋框 #
                mui.TextField(defaultValue=st.session_state["searchInputText"], label="徵信對象...", sx={"width":"95%", "marginBottom":"10px"}, onChange=lazy(sync("searchInputText")))

                # 歷史搜尋標籤 #
                with mui.Stack(direction="row", spacing=2):
                    if len(st.session_state["searchHistories"]) > 0:
                        for keyword in st.session_state["searchHistories"].copy():
                            if isinstance(keyword, str):
                                mui.Chip(label=keyword, onClick=clkChip(keyword), onDelete=delChip(keyword))
                
                # 搜尋按鈕 #
                mui.Button("搜尋", value="serchOnline", size="large", variant="contained", sx={"marginTop":"10px"}, onClick=clkSearchButton)

        ## 結果 ##
        with mui.Card(key="judgmentsCard", sx={"display": "flex", "flexDirection": "column"}):

            # 卡片可拖拽表頭 #
            if st.session_state["ret"] is not None:
                mui.CardHeader(title=f"🎁裁判書結果 (共{st.session_state['ret'].shape[0]}筆)", className="draggable")
            else:
                mui.CardHeader(title="🎁裁判書結果 (無)", className="draggable")

            #篩選區
            # with mui.Grid(container=True, direction="column", gap=2, sx={"paddingLeft":2, "overflow":"auto"}):
            #     mui.Typography("裁判案由", align="left", sx={})
            #     with mui.Stack(direction="row", spacing=2):
            #         if len(st.session_state["searchHistories"]) > 0:
            #             for keyword in st.session_state["searchHistories"].copy():
            #                 if isinstance(keyword, str):
            #                     mui.Chip(label=keyword, onClick=clkChip(keyword), onDelete=delChip(keyword))
                
            # 如果有搜尋結果存在`st.session_state["ret"]`內，展示結果 #
            if st.session_state["ret"] is not None:
                # showResults(st.session_state["ret"])
                showResults2(st.session_state["ret"].copy())

            # 頁碼管理處 #
            if st.session_state["total_page"] is not None:
                with mui.Grid(container=True, direction="column", sx={"display":"flex", "alignItems":"center", "justify-content": "center"}):                    
                    mui.Pagination(count=st.session_state["total_page"], defaultPage=st.session_state["curr_page"], page=st.session_state["curr_page"], boundaryCount=3, onChange=chgPage, sx={"margin":1})
                    mui.Input(defaultValue=st.session_state["pageText"], type="number", placeholder="Go to...", size="small", onChange=lazy(sync("pageText")), onKeyPress=keyPressPage, sx={"margin":1, "width":100, "input": { "textAlign": 'center' }})

        ## 分析 ##
        with mui.Card(key="abstractArea", sx={"display": "flex", "flexDirection": "column"}):
            # 分析搜尋結果按鈕 #
            with mui.CardActions(): #sx={"justifyContent": "flex-end"}
                mui.Button("開始分析", onClick=clkAnalyze, sx={"fontWeight": 'bold', "fontSize": '1.1em'})
            # 如果有分析結果則展示 #
            if st.session_state["analyzedData"] is not None and 'keyword' in st.session_state["analyzedData"]:
                mui.CardHeader(title=f"⚛️🇦🇮分析報表 ({st.session_state['analyzedData']['keyword']})", className="draggable")
                    # 卡片主體 #
                with mui.CardContent(sx={"flex": 1, "minHeight": 0, "overflow": "auto"}):

                    # 圓餅圖 #
                    with mui.Stack(direction="row", spacing=2, sx={"height":350, "overflow": "auto"}):
                        
                        if "pieDataJTITLE" in st.session_state["analyzedData"]:
                            with mui.Grid(direction="column", sx={"width":"100%", "height":300}):
                                with mui.Grid(item=True, sx={"width":"95%", "height":20}):
                                    mui.Typography("裁判案由", align="center", sx={"marginRight":5})
                                with mui.Grid(item=True, sx={"width":"95%", "height":280}):
                                    drawPieChart("pieDataJTITLE")
                        
                        if "pieDataJTYPE" in st.session_state["analyzedData"]:
                            with mui.Grid(direction="column", sx={"width":"100%", "height":300}):
                                with mui.Grid(item=True, sx={"width":"100%", "height":20}):
                                    mui.Typography("裁判類型", align="center", sx={"marginRight":5})
                                with mui.Grid(item=True, sx={"width":"100%", "height":280}):
                                    drawPieChart("pieDataJTYPE")

                    if "lineChartDataJTITLE" in st.session_state["analyzedData"]:
                        with mui.Grid(direction="column", sx={"padding":2, "minWidth": 800, "width":"100%", "height":540}):
                            with mui.Grid(item=True, sx={"width":"95%", "height":20}):
                                mui.Typography("裁判案由(堆疊)", align="center", sx={"marginRight":5})
                            with mui.Grid(item=True, sx={"width":"95%", "height":480}):
                                drawLineChart("lineChartDataJTITLE")
            else:
                mui.CardHeader(title="⚛️🇦🇮分析報表", className="draggable")
            


                        
                        
                
                
                        
