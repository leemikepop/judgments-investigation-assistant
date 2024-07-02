import requests
from bs4 import BeautifulSoup
import boto3
import timeit

# All available objects and there usage are listed there: https://github.com/okld/streamlit-elements#getting-started
import streamlit as st
from streamlit_elements import elements, dashboard, mui, lazy, sync, html
from utils.events import chgLayout, chgSearchMode, clkChip, delChip, clkAnalyze, clkSearchButton, doSearch, showResults2
from utils.drawer import drawPieChart, drawLineChart
from utils.inference import get_abstract_from_bedrock
from utils.models import MariaDBURID, MyModal

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
    st.session_state.colors = ["hsl(309, 70%, 50%)", "hsl(229, 70%, 50%)",
                               "hsl(78, 70%, 50%)", "hsl(278, 70%, 50%)", "hsl(273, 70%, 50%)"]
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
if 'db' not in st.session_state:
    st.session_state['db'] = MariaDBURID(
        host=st.secrets["DB"]["HOST"], port=3306, user=st.secrets["DB"]["USER"], password=st.secrets["DB"]["PASSWORD"], database=st.secrets["DB"]["DBNAME"])
if "ret" not in st.session_state:  # 搜尋結果
    st.session_state["ret"] = None
if "analyzedData" not in st.session_state:  # 分析結果
    st.session_state["analyzedData"] = None
if "session" not in st.session_state:
    st.session_state["session"] = boto3.Session(
        aws_access_key_id=st.secrets["BEDROCK"]["ACCESS_KEY"],
        aws_secret_access_key=st.secrets["BEDROCK"]["SECRET_KEY"]
    )
if "bedrock_client" not in st.session_state:
    st.session_state["bedrock_client"] = st.session_state["session"].client(
        'bedrock-runtime', region_name='us-east-1')
if 'content' not in st.session_state:
    st.session_state['content'] = None
if 'history' not in st.session_state:
    st.session_state['history'] = None
# 狀態
if "searchMode" not in st.session_state:
    st.session_state["searchMode"] = False
if "need2Search" not in st.session_state:
    st.session_state["need2Search"] = False
if "need2update" not in st.session_state:
    st.session_state['need2update'] = False
if "updateDatas" not in st.session_state:
    st.session_state['updateDatas'] = None
# 使用者輸入
if "searchInputText" not in st.session_state:
    st.session_state["searchInputText"] = ""
if "searchHistories" not in st.session_state:
    st.session_state["searchHistories"] = {
        "閎大營造", "山林水環境工程", "台灣世曦工程顧問", "旺宏電子", "長鴻營造", "欣興電子", "緯創資通"}  # set()


@st.cache_data
def requestJudgs(url):
    response = requests.get(url) if url is not None else None
    if response is not None:
        soup = BeautifulSoup(response.text, 'html.parser')
        div_element = soup.find('div', {'id': 'jud'})
        if div_element:
            td_element = div_element.find(
                'td', {'class': 'tab_linenu'})  # 找到目標td元素
            if td_element:
                td_element.extract()  # 刪除該td元素
            return div_element.text
        else:
            return None
    return None


# 刷新頁面時要檢查的狀態
if st.session_state["modal"].is_open():
    st.session_state["modal"].title = f"[AI摘要] {st.session_state['modal_data']['JCHAR']}"
    with st.session_state["modal"].container():
        with elements("modal"):
            if not st.session_state["modal_data"]["JSCORE"]:
                url = st.session_state["modal_data"]["JURL"]
                pre_url = st.session_state["modal_data"]["JHISURL"]
                start_time = timeit.default_timer()
                st.session_state['content'] = requestJudgs(url)
                st.session_state['history'] = requestJudgs(pre_url)
                end_time = timeit.default_timer()
                print("parse JFULL time:", end_time - start_time)
                start_time = timeit.default_timer()
                result = get_abstract_from_bedrock(st.session_state["modal_data"]["JID"], st.session_state["searchInputText"]) if st.session_state['content'] is not None else None
                end_time = timeit.default_timer()
                print("inference time:", end_time - start_time)
                result["JID"] = st.session_state['modal_data']["JID"]
                result["JTITLE"] = st.session_state['modal_data']["JTITLE"]
                result["JCHAR"] = st.session_state['modal_data']["JCHAR"]
                result["JTYPE"] = st.session_state['modal_data']["JTYPE"]
                result["JDATE"] = st.session_state['modal_data']["JDATE"]
                result["JURL"] = st.session_state['modal_data']["JURL"]
                result["JFULL"] = st.session_state['modal_data']["JFULL"]
                result["ID"] = st.session_state['modal_data']["ID"]
                st.session_state['need2update'] = True
                st.session_state['updateDatas'] = result
            else:
                result = st.session_state['modal_data']
            if "JSCORE" in result:
                with mui.Typography(sx={"overflow": "auto"}):
                    st.markdown(f"""<b>調查對象：</b>{result["JSUBJECT"]} ({result["JSUBJECTROLE"]})<br/><br/>"""
                                f"""<b>原告：</b>{result["JPLAINTIFF"]}<br/><br/>"""
                                f"""<b>被告：</b>{result["JDEFENDANT"]}<br/><br/>"""
                                f"""<b>風險評分：</b>{result["JSCORE"]} / 100 <br/><br/><br/>"""
                                f"""<b>簡述：</b>{result["JDESP"]}<br/><br/>"""
                                f"""<b>AI摘要：</b>{result["JCASESUMMARY"]}""", unsafe_allow_html=True)
            else:
                mui.Typography("裁判書擷取失敗")

# st.write(st.session_state['updateDatas'])
if st.session_state['need2update']:
    st.session_state['need2update'] = False
    if not st.session_state['db'].connection.is_connected():
        try:
            st.session_state['db'] = MariaDBURID(
                host='3.115.42.166', port=3306, user='tstudent02', password='Scsb@2024', database='tstudent02db')
        except Exception as e:
            st.warning(e)
            st.stop()
    st.session_state['db'].insert_data_on_duplicate_key_update(
        table='Judgments', columns=['JID', 'JTITLE', 'JCHAR', 'JTYPE', 'JDATE', 'JURL', 'JPLAINTIFF', 'JDEFENDANT', 'JDESP', 'JFULL'], values=(st.session_state['updateDatas']['JID'], st.session_state['updateDatas']['JTITLE'], st.session_state['updateDatas']['JCHAR'], st.session_state['updateDatas']['JTYPE'], st.session_state['updateDatas']['JDATE'], st.session_state['updateDatas']['JURL'], st.session_state['updateDatas']['JPLAINTIFF'], st.session_state['updateDatas']['JDEFENDANT'], st.session_state['updateDatas']['JDESP'], None), update_columns=['JPLAINTIFF', 'JDEFENDANT', 'JDESP'], update_values=(st.session_state['updateDatas']['JPLAINTIFF'], st.session_state['updateDatas']['JDEFENDANT'], st.session_state['updateDatas']['JDESP']), cond="")
    if st.session_state['updateDatas']['ID'] is None:
        st.session_state['db'].insert_data_with_conditions('Searchable', columns=['JID', 'JSUBJECT', 'JSUBJECTROLE', 'JSCORE', 'JCASESUMMARY'], values=(st.session_state['updateDatas']['JID'], st.session_state['updateDatas']['JSUBJECT'], st.session_state['updateDatas']['JSUBJECTROLE'], st.session_state['updateDatas']['JSCORE'], st.session_state['updateDatas']['JCASESUMMARY']), cond=f"NOT EXISTS (SELECT 1 FROM Searchable WHERE JID = %s AND JSUBJECT LIKE %s);", cond_values=(st.session_state['updateDatas']['JID'], f"%{st.session_state['updateDatas']['JSUBJECT']}%"))
    else:
        st.session_state['db'].update_data('Searchable', columns=['JSUBJECT', 'JSUBJECTROLE', 'JSCORE', 'JCASESUMMARY'], values=(st.session_state['updateDatas']['JSUBJECT'], st.session_state['updateDatas']['JSUBJECTROLE'], st.session_state['updateDatas']['JSCORE'], st.session_state['updateDatas']['JCASESUMMARY']), condition=f"ID = {st.session_state['updateDatas']['ID']}")
        # st.session_state["need2Search"] = True
    for dict in st.session_state['ret']:
        if dict['JID'] == st.session_state['updateDatas']['JID']:
            dict['JPLAINTIFF'] = st.session_state['updateDatas']['JPLAINTIFF']
            dict['JDEFENDANT'] = st.session_state['updateDatas']['JDEFENDANT']
            dict['JDESP'] = st.session_state['updateDatas']['JDESP']
            dict['JSUBJECTROLE'] = st.session_state['updateDatas']['JSUBJECTROLE']
            dict['JSCORE'] = st.session_state['updateDatas']['JSCORE']
            dict['JCASESUMMARY'] = st.session_state['updateDatas']['JCASESUMMARY']
            break

if st.session_state.need2Search:
    st.session_state.need2Search = False
    doSearch()

# 側邊欄(選擇版面配置)
with st.sidebar:
    st.header("選擇一個版面配置")
    with elements("sidebar"):
        with mui.RadioGroup(defaultValue="layout2", onChange=chgLayout):
            mui.FormControlLabel(control=mui.Radio, value="layout1", label=html.img(
                src="https://i.imgur.com/4VwKRF2.png"), sx={"margin": '10px', "padding": '20px'})
            mui.FormControlLabel(control=mui.Radio, value="layout2", label=html.img(
                src="https://i.imgur.com/UBLNnGA.png"), sx={"margin": '10px', "padding": '20px'})

# 主體
with elements("demo"):
    with mui.Grid(container=True, direction="row", justifyContent="flex-start", alignItems="center", sx={"padding":3}):
        with mui.Grid(item=True, sx={"width":50}):
            mui.Avatar(src="https://is1-ssl.mzstatic.com/image/thumb/Purple122/v4/6a/29/84/6a298483-8e5d-e8f2-9f58-6397b7d2deca/AppIcon-0-0-1x_U007emarketing-0-0-0-10-0-0-sRGB-0-0-0-GLES2_U002c0-512MB-85-220-0-0.png/246x0w.webp")
        with mui.Grid(item=True, xs=11):
            mui.Typography("司法判決書小幫手", variant="h4")
        
    with dashboard.Grid(st.session_state.layout, draggableHandle=".draggable"):

        ## 搜尋 ##
        with mui.Card(key="searchBar", sx={"display": "flex", "flexDirection": "column"}):

            # 可拖拽表頭 #
            mui.CardHeader(title="🔍搜尋徵信對象")  # , className="draggable"

            # 卡片主體 #
            with mui.CardContent(sx={"flex": 1, "minHeight": 0}):

                # 線上/本地 切換紐 #
                mui.FormControlLabel(control=mui.Switch(
                    defaultChecked=st.session_state["searchMode"], onChange=chgSearchMode), label="啟用網路搜尋", sx={"marginBottom": "10px"})

                # 搜尋框 #
                mui.TextField(defaultValue=st.session_state["searchInputText"], label="徵信對象...", sx={
                              "width": "95%", "marginBottom": "10px"}, onChange=lazy(sync("searchInputText")))

                # 歷史搜尋標籤 #
                with mui.Stack(direction="row", spacing=2):
                    if len(st.session_state["searchHistories"]) > 0:
                        for keyword in st.session_state["searchHistories"].copy():
                            if isinstance(keyword, str):
                                mui.Chip(label=keyword, onClick=clkChip(
                                    keyword), onDelete=delChip(keyword))

                # 搜尋按鈕 #
                mui.Button("搜尋", value="serchOnline", size="large", variant="contained", sx={
                           "marginTop": "10px"}, onClick=clkSearchButton)

        ## 結果 ##
        with mui.Card(key="judgmentsCard", sx={"display": "flex", "flexDirection": "column"}):

            # 卡片可拖拽表頭 #
            if st.session_state["ret"] is not None:
                mui.CardHeader(
                    title=f"🎁裁判書結果 ({st.session_state['searchInputText']}, 共{len(st.session_state['ret'])}筆)", className="draggable")
            else:
                mui.CardHeader(title="🎁裁判書結果 (無)", className="draggable")

            # 篩選區
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
                showResults2(st.session_state["ret"])

            # 頁碼管理處 #
            # if st.session_state["total_page"] is not None:
            #     with mui.Grid(container=True, direction="column", sx={"display":"flex", "alignItems":"center", "justify-content": "center"}):
            #         mui.Pagination(count=st.session_state["total_page"], defaultPage=st.session_state["curr_page"], page=st.session_state["curr_page"], boundaryCount=3, onChange=chgPage, sx={"margin":1})
            #         mui.Input(defaultValue=st.session_state["pageText"], type="number", placeholder="Go to...", size="small", onChange=lazy(sync("pageText")), onKeyPress=keyPressPage, sx={"margin":1, "width":100, "input": { "textAlign": 'center' }})

        ## 分析 ##
        with mui.Card(key="abstractArea", sx={"display": "flex", "flexDirection": "column"}):
            # 分析搜尋結果按鈕 #
            with mui.CardActions():  # sx={"justifyContent": "flex-end"}
                mui.Button("產生圖表", onClick=clkAnalyze, sx={
                           "fontWeight": 'bold', "fontSize": '1.1em'})
            # 如果有分析結果則展示 #
            if st.session_state["analyzedData"] is not None and 'keyword' in st.session_state["analyzedData"]:
                mui.CardHeader(
                    title=f"⚛️分析圖表 ({st.session_state['analyzedData']['keyword']})", className="draggable")
                # 卡片主體 #
                with mui.CardContent(sx={"flex": 1, "minHeight": 0, "overflow": "auto"}):

                    # 圓餅圖 #
                    with mui.Stack(direction="row", spacing=2, sx={"height": 350, "overflow": "auto"}):

                        if "pieDataJTITLE" in st.session_state["analyzedData"]:
                            with mui.Grid(direction="column", sx={"width": "100%", "height": 300}):
                                with mui.Grid(item=True, sx={"width": "95%", "height": 20}):
                                    mui.Typography("裁判案由", align="center", sx={
                                                   "marginRight": 5})
                                with mui.Grid(item=True, sx={"width": "95%", "height": 280}):
                                    drawPieChart("pieDataJTITLE")

                        if "pieDataJTYPE" in st.session_state["analyzedData"]:
                            with mui.Grid(direction="column", sx={"width": "100%", "height": 300}):
                                with mui.Grid(item=True, sx={"width": "100%", "height": 20}):
                                    mui.Typography("裁判類型", align="center", sx={
                                                   "marginRight": 5})
                                with mui.Grid(item=True, sx={"width": "100%", "height": 280}):
                                    drawPieChart("pieDataJTYPE")

                        if "pieDataJSUBJECTROLE" in st.session_state["analyzedData"]:
                            with mui.Grid(direction="column", sx={"width": "100%", "height": 300}):
                                with mui.Grid(item=True, sx={"width": "100%", "height": 20}):
                                    mui.Typography("調查對象關係", align="center", sx={
                                                   "marginRight": 5})
                                with mui.Grid(item=True, sx={"width": "100%", "height": 280}):
                                    drawPieChart("pieDataJSUBJECTROLE")

                    if "lineChartDataJTITLE" in st.session_state["analyzedData"]:
                        with mui.Grid(direction="column", sx={"padding": 2, "minWidth": 800, "width": "100%", "height": 540}):
                            with mui.Grid(item=True, sx={"width": "95%", "height": 20}):
                                mui.Typography("裁判案由(堆疊)", align="center", sx={
                                               "marginRight": 5})
                            with mui.Grid(item=True, sx={"width": "95%", "height": 480}):
                                drawLineChart("lineChartDataJTITLE")
            else:
                mui.CardHeader(title="⚛️分析圖表", className="draggable")
