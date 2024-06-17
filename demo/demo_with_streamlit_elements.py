# import json
import streamlit as st
import math, json
import pandas as pd

# As for Streamlit Elements, we will need all these objects.
# All available objects and there usage are listed there: https://github.com/okld/streamlit-elements#getting-started

from streamlit_elements import elements, dashboard, mui, lazy, sync, nivo, html
from utils.events import chgSearchMode, clkChip, delChip, clkSearchButton, doSearch, chgPage

# Change page layout to make the dashboard take the whole page.

st.set_page_config(
    page_title="裁判書徵信助手-Demo",
    page_icon="🤖",
    # layout="centered",
    layout="wide",
    initial_sidebar_state="collapsed"
)
DATA = [
    { "id": "css", "label": "css", "value": 58, "color": "hsl(309, 70%, 50%)" },
    { "id": "php", "label": "php", "value": 582, "color": "hsl(229, 70%, 50%)" },
    { "id": "ruby", "label": "ruby", "value": 491, "color": "hsl(78, 70%, 50%)" },
    { "id": "scala", "label": "scala", "value": 254, "color": "hsl(278, 70%, 50%)" },
    { "id": "stylus", "label": "stylus", "value": 598, "color": "hsl(273, 70%, 50%)" }]

# You can get random data there, in tab 'data': https://nivo.rocks/bump/
if 'dataset' not in st.session_state:
    try:
        st.session_state.dataset = pd.read_csv('dataset.csv')
    except Exception:
        st.session_state.dataset = None
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

# https://github.com/react-grid-layout/react-grid-layout#grid-item-props
layout = [
    # Editor item is positioned in coordinates x=0 and y=0, and takes 12/12 columns and has a height of 2.
    dashboard.Item("searchBar", 0, 0, 12, 2),
    # Chart item is positioned in coordinates x=0 and y=2, and takes 6/12 columns and has a height of 8.
    dashboard.Item("judgmentsCard", 0, 2, 6, 8),
    # Media item is positioned in coordinates x=6 and y=2, and takes 6/12 columns and has a height of 8.
    dashboard.Item("abstractArea", 6, 2, 6, 8),
]

if st.session_state.need2Search:
    doSearch()
    st.session_state.need2Search = False

with elements("demo"):

    with dashboard.Grid(layout, draggableHandle=".draggable"):

        ## 搜尋 ##
        with mui.Card(key="searchBar", sx={"display": "flex", "flexDirection": "column"}):

            mui.CardHeader(title="🔍搜尋徵信對象", className="draggable")

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
            if st.session_state.ret is not None:
                mui.CardHeader(title=f"🎁裁判書結果({st.session_state.ret.shape[0]}筆結果)", className="draggable")
            else:
                mui.CardHeader(title="🎁裁判書結果", className="draggable")
            if st.session_state.ret is not None:
                ROWs_PER_PAGE = 10
                total_rows = st.session_state.ret.shape[0]
                st.session_state.total_page = math.ceil(total_rows/ROWs_PER_PAGE)
                start_index = (st.session_state.curr_page - 1) * ROWs_PER_PAGE
                end_index = min(st.session_state.curr_page * ROWs_PER_PAGE, total_rows)
                # it = iter(st.session_state.ret)
                with mui.CardContent(sx={"flex": 1, "minHeight": 0, "overflow": "auto"}):
                    with mui.Table(aria_label="simple table"):
                        with mui.TableHead():
                            with mui.TableRow(variant="head"):
                                mui.TableCell("")
                                mui.TableCell("分數")
                                mui.TableCell("裁判字號")
                                mui.TableCell("裁判日期")
                                mui.TableCell("裁判案由")
                        with mui.TableBody():
                            for index in range(start_index, end_index):
                                data = st.session_state.ret.iloc[index]
                                with mui.TableRow():#sx={"& td": { "border-top": 0 }, "& a": { "border-top": 0 }}
                                    mui.TableCell(f"{index+1}", rowspan=2)
                                    mui.TableCell(f"{data['labels']:.2f}", rowspan=2)
                                    mui.TableCell(f"{data['Judgment_Number']}", component="a", href=data["Judgment_URL"], target="_blank", sx={"color": 'blue', "fontSize": '1em', "fontWeight": 'bold' })
                                    mui.TableCell(f"{data['Judgment_Date']}")
                                    mui.TableCell(f"{data['JTITLE']}")
                                    # mui.Typography(data['Summary'][:250]+'...' if len(data['Summary']) > 250 else data['Summary'])
                                with mui.TableRow():
                                    # mui.TableCell("")
                                    # mui.TableCell("")
                                    mui.TableCell(data['Summary'][:250]+'...' if len(data['Summary']) > 250 else data['Summary'], colspan=3, sx={"color": 'gray'})

                    # with mui.List():
                    #     for index in range(start_index, end_index):
                    #         data = st.session_state.ret.iloc[index]
                    #         with mui.ListItem():
                    #             mui.ListItemText(primary=f"{index} / {data['labels']:.2f} / {data['Judgment_Number']} / {data['Judgment_Date']} / {data['JTITLE']}", secondary=data['Summary'][:250]+'...' if len(data['Summary']) > 250 else data['Summary'])

            if st.session_state.total_page is not None:
                with mui.Box(sx={"display":"flex", "alignItems":"center", "justify-content": "center"}):
                    mui.Pagination(count=st.session_state["total_page"], defaultPage=st.session_state["curr_page"], page=st.session_state["curr_page"], variant="outlined", onChange=chgPage)
        
        ## 分析 ##
        with mui.Card(key="abstractArea", sx={"display": "flex", "flexDirection": "column"}):
            nivo.Pie(
                data=DATA,
                margin={"top": 200, "right": 200, "bottom": 200, "left": 200},
                innerRadius=0.5,
                padAngle=0.7,
                cornerRadius=3,
                activeOuterRadiusOffset=8,
                borderWidth=1,
                borderColor={"from": "color", "modifiers": [["darker", 0.8]]},
                enableArcLinkLabels=False,
                # arcLinkLabelsSkipAngle=10,
                # arcLinkLabelsTextColor="grey",
                # arcLinkLabelsThickness=2,
                # arcLinkLabelsColor={"from": "color"},
                arcLabel="id",
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
                fill=[
                    {"match": {"id": "ruby"}, "id": "dots"},
                    {"match": {"id": "php"}, "id": "dots"},
                    {"match": {"id": "scala"}, "id": "lines"},
                    {"match": {"id": "css"}, "id": "dots"},
                    {"match": {"id": "stylus"}, "id": "lines"},
                ],
                # legends=[
                #     {
                #         "anchor": "bottom",
                #         "direction": "row",
                #         "justify": False,
                #         "translateX": 0,
                #         "translateY": 56,
                #         "itemsSpacing": 0,
                #         "itemWidth": 80,
                #         "itemHeight": 20,
                #         "itemTextColor": "#999",
                #         "itemDirection": "left-to-right",
                #         "itemOpacity": 1,
                #         "symbolSize": 5,
                #         "symbolShape": "circle",
                #         "effects": [
                #             {"on": "hover", "style": {"itemTextColor": "#000"}}
                #         ],
                #     }
                # ],
            )
                        
