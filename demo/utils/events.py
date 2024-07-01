import streamlit as st
from streamlit_elements import sync, mui
from streamlit.components.v1 import html

# import math
import time
import pandas as pd

from .search import doSearch

def chgLayout(_, v):
    if v == "layout2":
        st.session_state.layout = st.session_state.layout2
    else:
        st.session_state.layout = st.session_state.layout1


def chgSearchMode(event):
    # print(event)
    st.session_state["searchMode"] = event.target.checked


def clkChip(keyword: str):
    def callback():
        st.session_state["searchInputText"] = keyword
        doSearch()
        sync()
    return callback


def delChip(keyword):
    def callback():
        st.session_state["searchHistories"].remove(keyword)
        sync()
    return callback


def clkSearchButton():
    st.session_state.need2Search = True
    sync()


def showResults2(ret):
    # ['id', 'JID', 'JTITLE', 'JCHAR', 'JTYPE', 'JDATE', 'JURL', 'JHISURL', 'JPLAINTIFF', 'JDEFENDANT', 'JDESP', 'JFULL', 'ID', 'JSUBJECT', 'JSUBJECTROLE', 'JSCORE', 'JCASESUMMARY']
    columns = [
        {"field": 'id', "headerName": 'No.', "minWidth": 45, "headerAlign":'center', "align": 'center'},
        {"field": 'JSCORE', "headerName": '信貸分數(負面)', "type": 'number', "minWidth": 130, "headerAlign":'center', "align": 'center'},
        {"field": 'JCHAR', "headerName": '裁判字號', "minWidth": 400, "headerAlign":'center', "align": 'left'},        
        {"field": 'JDATE', "headerName": '裁判日期', "type": 'date', "minWidth": 130, "headerAlign":'left', "align": 'left'},
        {"field": 'JTITLE', "headerName": '裁判案由', "minWidth": 150, "headerAlign":'left', "align": 'left'},
        {"field": 'JDESP', "headerName": '簡述', "flex": 1, "minWidth": 1000 , "headerAlign":'center', "align": 'left'},
    ]
    with mui.CardContent(sx={"flex": 1, "minHeight": 0}):
        mui.DataGrid(
            stickyHeader=True,
            rows=ret,
            columns=columns,
            # components={"Toolbar":mui.GridToolbarFilterButton},
            autosizeOnMount=True, #無效
            autoPageSize=True,
            disableSelectionOnClick=True, #disableRowSelectionOnClick=True, #無效 
            onCellDoubleClick=clkDataCell,
            # sx={"overflow": "auto"}
        )


def clkDataCell(params, event, details):
    if params['field'] == "JCHAR":
        jscode = f"""<script type="text/javascript">
                        window.open("{params["row"]["JURL"]}", "_blank");
                        var iframe = document.querySelector('iframe[data-testid="stIFrame"]');
                        if(iframe) iframe.parentNode.removeChild(iframe);
                    </script>
                """
        placeholder = st.empty()
        with placeholder:
            html(jscode)
            time.sleep(0.5)
            placeholder.empty()
    elif params['field'] == "JDESP":
        st.session_state["modal_data"] = params["row"]
        st.session_state["modal"].open()
        time.sleep(0.5)

def clkAnalyze():
    if st.session_state["ret"] is not None:
        st.session_state["analyzedData"] = {
            "keyword": st.session_state["searchInputText"]
        }
        df = pd.DataFrame(st.session_state["ret"])
        ## 準備JTITLE圓餅圖資料 ##
        vCountsJTITLE = df["JTITLE"].value_counts()
        pieData = []
        fill = []
        fill_id = ["dots", "lines"]
        JTITLEList = []
        for i, (item, count) in enumerate(vCountsJTITLE.items()):
            if i > 4:
                break
            JTITLEList.append(item)
            pieData.append({
                "id": item,
                "label": item,
                "value": count,
                "color": st.session_state["colors"][count % 5]
            })
            fill.append({
                "match": {"id": item},
                "id": fill_id[count % 2]
            })
        others_data = list(vCountsJTITLE.items())[5:]  # 後面大於4的元素
        if len(others_data) > 0:
            others_item, others_count = zip(*others_data)  # 拆分成兩個列表
            count = sum(others_count)
            pieData.append({
                "id": "其他",
                "label": f"{', '.join(others_item[:3])}, ...",
                "value": count,
                "color": st.session_state["colors"][count % 5]
            })
            fill.append({
                "match": {"id": "其他"},
                "id": fill_id[count % 2]
            })
        if len(pieData) > 0:
            st.session_state["analyzedData"]["pieDataJTITLE"] = [pieData, fill]

        ## 準備JTYPE圓餅圖資料 ##
        vCountsJTYPE = df["JTYPE"].value_counts()
        pieData = []
        fill = []
        fill_id = ["dots", "lines"]
        for i, (item, count) in enumerate(vCountsJTYPE.items()):
            if i > 4:
                break
            pieData.append({
                "id": item,
                "label": item,
                "value": count,
                "color": st.session_state["colors"][count % 5]
            })
            fill.append({
                "match": {"id": item},
                "id": fill_id[count % 2]
            })
        others_data = list(vCountsJTYPE.items())[5:]  # 後面大於4的元素
        if len(others_data) > 0:
            others_item, others_count = zip(*others_data)  # 拆分成兩個列表
            count = sum(others_count)
            pieData.append({
                "id": "其他",
                "label": f"{', '.join(others_item[:3])}, ...",
                "value": count,
                "color": st.session_state["colors"][count % 5]
            })
            fill.append({
                "match": {"id": "其他"},
                "id": fill_id[count % 2]
            })
        if len(pieData) > 0:
            st.session_state["analyzedData"]["pieDataJTYPE"] = [pieData, fill]

        ## 準備折線圖資料 ##
        grouped_df = df[df['JTITLE'].isin(JTITLEList)].groupby('JTITLE')
        lineCharData = []
        for group_name, group_df in grouped_df:
            group_df["YEAR"] = group_df["JDATE"].apply(lambda x: int(x[:4]))
            groups_df_cnt = group_df.groupby(
                "YEAR").size().reset_index(name='COUNT')
            groups_df_cnt = groups_df_cnt.rename(
                columns={"YEAR": "x", "COUNT": "y"})
            lineCharData.append(
                {
                    "id": group_name,
                    "color": "hsl(246, 70%, 50%)",
                    "data": groups_df_cnt.to_dict(orient='records')
                }
            )

        x_values = set()

        for item in lineCharData:
            for data_point in item['data']:
                x_values.add(data_point['x'])

        min_x = min(x_values)
        max_x = max(x_values)

        x_range = list(range(min_x, max_x + 1))

        for item in lineCharData:
            data_points = item['data']
            updated_data = []

            for x_value in x_range:
                y_value = next(
                    (data_point["y"] for data_point in data_points if data_point['x'] == x_value), 0)
                updated_data.append({'x': x_value, "y": y_value})

            item['data'] = updated_data
        st.session_state["analyzedData"]["lineChartDataJTITLE"] = lineCharData
        # print(st.session_state["analyzedData"])

        ## 準備JSUBJECTROLE圓餅圖資料 ##
        vCountsJSUBJECTROLE = df["JSUBJECTROLE"].value_counts()
        print(vCountsJSUBJECTROLE)
        pieData = []
        fill = []
        fill_id = ["dots", "lines"]
        JTITLEList = []
        for i, (item, count) in enumerate(vCountsJSUBJECTROLE.items()):
            print(i, item, count)
            if i > 4:
                break
            JTITLEList.append(item)
            pieData.append({
                "id": item,
                "label": item,
                "value": count,
                "color": st.session_state["colors"][count % 5]
            })
            fill.append({
                "match": {"id": item},
                "id": fill_id[count % 2]
            })
        others_data = list(vCountsJSUBJECTROLE.items())[5:]  # 後面大於4的元素
        if len(others_data) > 0:
            others_item, others_count = zip(*others_data)  # 拆分成兩個列表
            count = sum(others_count)
            pieData.append({
                "id": "其他",
                "label": f"{', '.join(others_item[:3])}, ...",
                "value": count,
                "color": st.session_state["colors"][count % 5]
            })
            fill.append({
                "match": {"id": "其他"},
                "id": fill_id[count % 2]
            })
        if len(pieData) > 0:
            st.session_state["analyzedData"]["pieDataJSUBJECTROLE"] = [pieData, fill]
        sync()
    else:
        st.session_state["analyzedData"] = None


# def chgPage(_, value):
#     # print(event)
#     # print(value)
#     st.session_state["curr_page"] = value
#     st.session_state["pageText"] = value
#     sync()


# def chgPageNum(value):
#     if value > 0 and value <= st.session_state["total_page"]:
#         st.session_state["curr_page"] = value
#     else:
#         st.session_state["pageText"] = None


# def keyPressPage(event):
#     print(event)
#     if event.which == 13:
#         st.session_state["pageKeyPressed"] = True
#         sync("pageText")


# def showResults(ret):
#     ROWs_PER_PAGE = 10
#     total_rows = ret.shape[0]
#     st.session_state["total_page"] = math.ceil(total_rows/ROWs_PER_PAGE)
#     start_index = (st.session_state["curr_page"] - 1) * ROWs_PER_PAGE
#     end_index = min(st.session_state["curr_page"] * ROWs_PER_PAGE, total_rows)
#     with mui.CardContent(sx={"flex": 1, "minHeight": 0, "overflow": "auto"}):

#         with mui.Table(aria_label="simple table"):
#             with mui.TableHead():
#                 with mui.TableRow(variant="head"):
#                     mui.TableCell("NO.", align="center")
#                     mui.TableCell("負面分數", align="center")
#                     mui.TableCell("裁判字號", align="center")
#                     mui.TableCell("裁判日期", align="center")
#                     mui.TableCell("裁判案由", align="center")
#             with mui.TableBody():
#                 for index in range(start_index, end_index):
#                     data = ret.iloc[index]
#                     # sx={"& td": { "border-top": 0 }, "& a": { "border-top": 0 }}
#                     with mui.TableRow():
#                         mui.TableCell(f"{index+1}", rowspan=2)
#                         # mui.TableCell(f"{data['JSCORE']:.2f}", rowspan=2)
#                         with mui.TableCell(rowspan=2):
#                             with mui.Typography(sx={"height": 75, "width": 75}, align="center"):
#                                 nivo.Pie(
#                                     colors={"scheme": 'set1'},
#                                     data=[
#                                         {
#                                             "id": "score",
#                                             "label": "score",
#                                             "value": int(data['JSCORE'] * 100),
#                                             # "color": "hsl(0, 100%, 60%)"
#                                         }
#                                     ],
#                                     margin={"top": 10, "right": 10,
#                                             "bottom": 10, "left": 10},
#                                     borderWidth=0,
#                                     innerRadius=0.5,
#                                     padAngle=5,
#                                     cornerRadius=3,
#                                     activeOuterRadiusOffset=8,
#                                     arcLabelsRadiusOffset=-1,
#                                     enableArcLinkLabels=False,
#                                     startAngle=0,
#                                     endAngle=int(360*data['JSCORE']),
#                                     isInteractive=False
#                                 )
#                         mui.TableCell(f"{data['JCHAR']}", align="left", component="a", href=data["JURL"], target="_blank", sx={
#                                       "color": 'blue', "fontWeight": 'bold'})
#                         mui.TableCell(f"{data['JDATE']}", align="center")
#                         mui.TableCell(f"{data['JTITLE']}", align="center")
#                     with mui.TableRow():
#                         mui.TableCell(data['JSUMMARY'][:250]+'...' if len(data['JSUMMARY']) > 250 else data['JSUMMARY'],
#                                       colspan=3, sx={"color": 'gray'}, onClick=clkSummary(data["JURL"]))
