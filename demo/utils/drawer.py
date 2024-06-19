import streamlit as st
from streamlit_elements import  nivo

def drawPieChart(key):
    nivo.Pie(
        data=st.session_state["analyzedData"][key][0],
        margin={"top": 25, "right": 100, "bottom": 25, "left": 50},
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
        fill=st.session_state["analyzedData"][key][1],
        onClick=clkPieChart
    )

def clkPieChart(event, value):
    print(event)
    print(value)

def drawLineChart(key):
    nivo.Line(
        data=st.session_state["analyzedData"][key],
        margin={ "top": 50, "right": 100, "bottom": 100, "left": 50 },
        xScale={ "type": 'point' },
        yScale={
            "type": 'linear',
            "min": 'auto',
            "max": 'auto',
            "stacked": True, #資料線條會往上堆疊
            "reverse": False,
        },
        yFormat=">(.0d",
        axisTop=None,
        axisRight=None,
        axisBottom={
            "tickSize": 5,
            "tickPadding": 5,
            "tickRotation": 0,
            "legend": '年份',
            "legendOffset": 36,
            "legendPosition": 'middle',
            "truncateTickAt": 0,
        },
        axisLeft={
            "tickSize": 5,
            "tickPadding": 5,
            "tickRotation": 0,
            "legend": '裁判數量',
            "legendOffset": -40,
            "legendPosition": 'middle',
            "truncateTickAt": 0,
        },
        pointSize=10,
        pointColor={ "theme": 'background' },
        pointBorderWidth=2,
        pointBorderColor={ "from": 'serieColor' },
        pointLabel="data.yFormatted",
        pointLabelYOffset=-12,
        enableTouchCrosshair=True,
        useMesh=True,
        legends=[
            {
                "anchor": 'bottom',
                "direction": 'row',
                "justify": False,
                "translateX": 0,
                "translateY": 75,
                "itemsSpacing": 0,
                "itemDirection": 'top-to-bottom', #'left-to-right',
                "itemWidth": 120,
                "itemHeight": 20,
                "itemOpacity": 0.75,
                "symbolSize": 12,
                "symbolShape": 'circle',
                "symbolBorderColor": 'rgba(0, 0, 0, .5)'
            }
        ]
    )