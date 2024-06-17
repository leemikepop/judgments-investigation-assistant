# import json
import streamlit as st
import math
import pandas as pd

# As for Streamlit Elements, we will need all these objects.
# All available objects and there usage are listed there: https://github.com/okld/streamlit-elements#getting-started

from streamlit_elements import elements, dashboard, mui, lazy, sync, html, nivo
from utils.events import chgLayout, chgSearchMode, clkChip, delChip, clkAnalyze, clkSearchButton, doSearch, chgPage, chgPageNum, keyPressPage, ElementsCallbackData

# Change page layout to make the dashboard take the whole page.

st.set_page_config(
    page_title="裁判書徵信助手-Demo",
    page_icon="🤖",
    # layout="centered",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# You can get random data there, in tab 'data': https://nivo.rocks/bump/
if 'layout1' not in st.session_state:
    st.session_state.layout1 = [
        # Editor item is positioned in coordinates x=0 and y=0, and takes 12/12 columns and has a height of 2.
        dashboard.Item("searchBar", 0, 0, 12, 2),
        # Chart item is positioned in coordinates x=0 and y=2, and takes 6/12 columns and has a height of 8.
        dashboard.Item("judgmentsCard", 0, 2, 6, 8),
        # Media item is positioned in coordinates x=6 and y=2, and takes 6/12 columns and has a height of 8.
        dashboard.Item("abstractArea", 6, 2, 6, 8),
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
    st.session_state.layout = st.session_state.layout1
if 'dataset' not in st.session_state:
    try:
        st.session_state.dataset = pd.read_csv('dataset.csv')
    except Exception:
        st.session_state.dataset = None
if 'colors' not in st.session_state:
    st.session_state.colors = ["hsl(309, 70%, 50%)", "hsl(229, 70%, 50%)", "hsl(78, 70%, 50%)", "hsl(278, 70%, 50%)", "hsl(273, 70%, 50%)"]
if "pieDataJTITLE" not in st.session_state:
    st.session_state.pieDataJTITLE = None
if "pieDataJTYPE" not in st.session_state:
    st.session_state.pieDataJTYPE = None
if "searchMode" not in st.session_state:
    st.session_state.searchMode = False
if "need2Search" not in st.session_state:
    st.session_state.need2Search = False
if "searchInputText" not in st.session_state:
    st.session_state.searchInputText = ""
if "searchHistories" not in st.session_state:
    st.session_state.searchHistories = {"台灣世曦工程顧問", "旺宏電子", "長鴻營造", "欣興電子", "緯創資通"} # set()
if "ret" not in st.session_state:
    st.session_state.ret = None
if 'curr_page' not in st.session_state:
    st.session_state.curr_page = 1
if 'total_page' not in st.session_state:
    st.session_state.total_page = None
if 'pageText' not in st.session_state:
    st.session_state.pageText = None
if 'pageKeyPressed' not in st.session_state:
    st.session_state.pageKeyPressed = False

if st.session_state.pageKeyPressed and st.session_state.pageText:
    st.session_state.pageKeyPressed = False
    try:
        if isinstance(st.session_state["pageText"], ElementsCallbackData):
            st.session_state["pageText"] = st.session_state["pageText"].target.value
        chgPageNum(int(st.session_state["pageText"]))
    except Exception as e:
        print(st.session_state.pageText)
        print("Exception in `chgPageNum(int(st.session_state.pageText))`")
    st.session_state.pageText = None

if st.session_state.need2Search:
    doSearch()
    st.session_state.need2Search = False

with st.sidebar:
    st.header("選擇一個版面配置")
    with elements("sidebar"):
        with mui.RadioGroup(defaultValue="layout1", onChange=chgLayout):
            mui.FormControlLabel(control=mui.Radio, value="layout1", label=html.img(src="https://i.imgur.com/4VwKRF2.png"), sx={"margin": '10px', "padding": '20px'})
            mui.FormControlLabel(control=mui.Radio, value="layout2", label=html.img(src="https://i.imgur.com/UBLNnGA.png"), sx={"margin": '10px', "padding": '20px'})

with elements("demo"):

    with dashboard.Grid(st.session_state.layout, draggableHandle=".draggable"):

        ## 搜尋 ##
        with mui.Card(key="searchBar", sx={"display": "flex", "flexDirection": "column"}):

            mui.CardHeader(title="🔍搜尋徵信對象")# , className="draggable"

            with mui.CardContent(sx={"flex": 1, "minHeight": 0}):

                mui.FormControlLabel(control=mui.Switch(defaultChecked=False, onChange=chgSearchMode), label="啟用網路搜尋", sx={"marginBottom":"10px"})

                mui.TextField(defaultValue=st.session_state["searchInputText"], label="徵信對象...", sx={"width":"95%", "marginBottom":"10px"}, onChange=lazy(sync("searchInputText")))
                with mui.Stack(direction="row", spacing=2):
                    if len(st.session_state["searchHistories"]) > 0:
                        for keyword in st.session_state["searchHistories"].copy():
                            if isinstance(keyword, str):
                                mui.Chip(label=keyword, onClick=clkChip(keyword), onDelete=delChip(keyword))
                
                mui.Button("搜尋", value="serchOnline", size="large", variant="contained", sx={"marginTop":"10px"}, onClick=clkSearchButton)

        ## 結果 ##
        with mui.Card(key="judgmentsCard", sx={"display": "flex", "flexDirection": "column"}):
            with mui.CardActions(): #sx={"justifyContent": "flex-end"}
                mui.Button("分析搜尋結果🔄", onClick=clkAnalyze, sx={"fontWeight": 'bold', "fontSize": '1.1em'})

            if st.session_state.ret is not None:
                mui.CardHeader(title=f"🎁裁判書結果 (共{st.session_state.ret.shape[0]}筆)", className="draggable")
            else:
                mui.CardHeader(title="🎁裁判書結果", className="draggable")
            if st.session_state.ret is not None:
                ROWs_PER_PAGE = 10
                total_rows = st.session_state.ret.shape[0]
                st.session_state.total_page = math.ceil(total_rows/ROWs_PER_PAGE)
                start_index = (st.session_state.curr_page - 1) * ROWs_PER_PAGE
                end_index = min(st.session_state.curr_page * ROWs_PER_PAGE, total_rows)
                with mui.CardContent(sx={"flex": 1, "minHeight": 0, "overflow": "auto"}):
                    with mui.Table(aria_label="simple table"):
                        with mui.TableHead():
                            with mui.TableRow(variant="head"):
                                mui.TableCell("NO.", align="center")
                                mui.TableCell("負面分數", align="center")
                                mui.TableCell("裁判字號", align="center")
                                mui.TableCell("裁判日期", align="center")
                                mui.TableCell("裁判案由", align="center")
                        with mui.TableBody():
                            for index in range(start_index, end_index):
                                data = st.session_state.ret.iloc[index]
                                with mui.TableRow():#sx={"& td": { "border-top": 0 }, "& a": { "border-top": 0 }}
                                    mui.TableCell(f"{index+1}", rowspan=2)
                                    # mui.TableCell(f"{data['JSCORE']:.2f}", rowspan=2)
                                    with mui.TableCell(rowspan=2):
                                        with mui.Typography(sx={"height":75, "width":75}, align="center"):
                                            nivo.Pie(
                                                colors={"scheme": 'set1'},
                                                data=[
                                                    {
                                                        "id": "score",
                                                        "label": "score",
                                                        "value": int(data['JSCORE'] * 100),
                                                        # "color": "hsl(0, 100%, 60%)"
                                                    }
                                                ],
                                                margin={"top": 10, "right": 10, "bottom": 10, "left": 10},
                                                borderWidth=0,
                                                innerRadius=0.5,
                                                padAngle=5,
                                                cornerRadius=3,
                                                activeOuterRadiusOffset=8,
                                                arcLabelsRadiusOffset=-1,
                                                enableArcLinkLabels=False,
                                                startAngle=0,
                                                endAngle=int(360*data['JSCORE']),
                                                isInteractive=False
                                            )
                                    mui.TableCell(f"{data['JCHAR']}", align="left", component="a", href=data["JURL"], target="_blank", sx={"color": 'blue', "fontWeight": 'bold' })
                                    mui.TableCell(f"{data['JDATE']}", align="center")
                                    mui.TableCell(f"{data['JTITLE']}", align="center")
                                with mui.TableRow():
                                    mui.TableCell(data['JSUMMARY'][:250]+'...' if len(data['JSUMMARY']) > 250 else data['JSUMMARY'], colspan=3, sx={"color": 'gray'})

            if st.session_state.total_page is not None:
                with mui.Grid(container=True, direction="column", sx={"display":"flex", "alignItems":"center", "justify-content": "center"}):                    
                    mui.Pagination(count=st.session_state["total_page"], defaultPage=st.session_state["curr_page"], page=st.session_state["curr_page"], boundaryCount=3, onChange=chgPage, sx={"margin":1})
                    mui.Input(defaultValue=st.session_state["pageText"], type="number", placeholder="Go to...", onChange=lazy(sync("pageText")), onKeyPress=keyPressPage, sx={"margin":1})

        ## 分析 ##
        with mui.Card(key="abstractArea", sx={"display": "flex", "flexDirection": "column"}):
            mui.CardHeader(title="⚛️🇦🇮分析結果", className="draggable")
            with mui.CardContent(sx={"flex": 1, "minHeight": 0}):
                with mui.Stack(direction="row", spacing=2, sx={"height":350, "overflow": "auto"}):
                    if st.session_state["pieDataJTITLE"] is not None:
                        with mui.Grid(direction="column", sx={"width":450, "height":300}):
                            with mui.Grid(item=True, sx={"width":450, "height":20}):
                                mui.Typography("裁判案由", align="center")
                            with mui.Grid(item=True, sx={"width":450, "height":280}):
                                nivo.Pie(
                                    data=st.session_state["pieDataJTITLE"][0],
                                    margin={"top": 25, "right": 25, "bottom": 25, "left": 25},
                                    innerRadius=0.5,
                                    padAngle=2,
                                    cornerRadius=3,
                                    activeOuterRadiusOffset=8,
                                    borderWidth=1,
                                    borderColor={"from": "color", "modifiers": [["darker", 0.8]]},
                                    enableArcLinkLabels=True,
                                    arcLinkLabelsSkipAngle=10,
                                    arcLinkLabelsTextColor="grey",
                                    arcLinkLabelsThickness=2,
                                    arcLinkLabelsDiagonalLength=8,
                                    arcLinkLabelsStraightLength=12,
                                    arcLinkLabelsColor={"from": "color"},
                                    arcLabel="formattedValue",
                                    arcLabelsSkipAngle=10,
                                    arcLabelsTextColor={"from": "color", "modifiers": [["darker", 4]]},
                                    defs=[
                                        {
                                            "id": "dots",
                                            "type": "patternDots",
                                            "background": "inherit",
                                            "color": "rgba(255, 255, 255, 0.3)",
                                            "size": 4,
                                            "padding": 1,
                                            "stagger": True,
                                        },
                                        {
                                            "id": "lines",
                                            "type": "patternLines",
                                            "background": "inherit",
                                            "color": "rgba(255, 255, 255, 0.3)",
                                            "rotation": -45,
                                            "lineWidth": 6,
                                            "spacing": 10,
                                        },
                                    ],
                                    fill=st.session_state["pieDataJTITLE"][1]
                                )
                    
                    if st.session_state["pieDataJTYPE"] is not None:
                        with mui.Grid(direction="column", sx={"width":450, "height":300}):
                            with mui.Grid(item=True, sx={"width":450, "height":20}):
                                mui.Typography("裁判類型", align="center")
                            with mui.Grid(item=True, sx={"width":450, "height":280}):
                                nivo.Pie(
                                    # width=200,
                                    # height=200,
                                    data=st.session_state["pieDataJTYPE"][0],
                                    margin={"top": 25, "right": 25, "bottom": 25, "left": 25},
                                    innerRadius=0.5,
                                    padAngle=2,
                                    cornerRadius=3,
                                    activeOuterRadiusOffset=8,
                                    borderWidth=1,
                                    borderColor={"from": "color", "modifiers": [["darker", 0.8]]},
                                    enableArcLinkLabels=True,
                                    arcLinkLabelsSkipAngle=10,
                                    arcLinkLabelsTextColor="grey",
                                    arcLinkLabelsThickness=2,
                                    arcLinkLabelsDiagonalLength=8,
                                    arcLinkLabelsStraightLength=12,
                                    arcLinkLabelsColor={"from": "color"},
                                    arcLabel="formattedValue",
                                    arcLabelsSkipAngle=10,
                                    arcLabelsTextColor={"from": "color", "modifiers": [["darker", 4]]},
                                    defs=[
                                        {
                                            "id": "dots",
                                            "type": "patternDots",
                                            "background": "inherit",
                                            "color": "rgba(255, 255, 255, 0.3)",
                                            "size": 4,
                                            "padding": 1,
                                            "stagger": True,
                                        },
                                        {
                                            "id": "lines",
                                            "type": "patternLines",
                                            "background": "inherit",
                                            "color": "rgba(255, 255, 255, 0.3)",
                                            "rotation": -45,
                                            "lineWidth": 6,
                                            "spacing": 10,
                                        },
                                    ],
                                    fill=st.session_state["pieDataJTYPE"][1]
                                )


                        
                        
                
                
                        
