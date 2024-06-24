import streamlit as st
from streamlit_elements.core.callback import ElementsCallbackData
import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import re
import requests
import timeit
import concurrent.futures
import urllib.parse
import random
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
# from .scores import scoreInference


def doSearch():
    if isinstance(st.session_state["searchInputText"], ElementsCallbackData):
        print(st.session_state["searchInputText"])
        st.session_state["searchInputText"] = st.session_state["searchInputText"].target.value

    if st.session_state["searchInputText"]:
        st.session_state["searchHistories"].add(st.session_state["searchInputText"])
        if st.session_state["searchMode"]:
            print("doOnlineSearch()")
            doOnlineSearch()
        else:
            print("doLocalSearch()")
            doLocalSearch()

def doOnlineSearch():
    search_attrs = {
        "case0" : False,
        "case1" : False,
        "case2" : False,
        "case3" : False,
        "case4" : False,
        "year" : None,
        "judgement_char" : None,
        "startNum" : None,
        "endNum" : None,
        "startDay" : None,
        "endDay" : None,
        "judgementTitle" : None,
        "judgementMain" : None,
        "judgementKeyword" : st.session_state["searchInputText"]
    }
    cnt = 0
    for _,attr in search_attrs.items():
        if attr is None or not attr:
            cnt += 1
    if cnt == 14:
        st.warning("搜尋條件不可為空")
        return
    df = concurrentParse(search_attrs)
    df.loc[:,"JDATE"] = pd.to_datetime(df.loc[:,"JDATE"], yearfirst=True, format='%Y-%m-%d').apply(lambda x: x.date())
    # start_time = timeit.default_timer()
    # df["JSCORE"] = scoreInference(df.iloc[:]["JSUMMARY"].to_list())
    # end_time = timeit.default_timer()
    # print("scoreInference time:", end_time - start_time)
    df = df.sort_values(by='JSCORE', ascending=False)
    st.session_state.ret = df
    if st.session_state.ret.shape[0] > 0:
        st.session_state.curr_page = 1
    else:
        st.session_state.curr_page = None
        st.session_state["total_page"] = None
        st.session_state.ret = None

URL = "https://judgment.judicial.gov.tw/FJUD/Default_AD.aspx"
BASEURL = "https://judgment.judicial.gov.tw/FJUD/"
pageUrls = []

# class Node():
#     def __init__(self, title=None, date=None, reason=None, link=None, dscp=None, char=None) -> None:
#         self.title = title 
#         self.date = date
#         self.reason = reason #裁判案由
#         self.link = link
#         self.dscp = dscp #概述
#         self.char = char #民事, 刑事, ...

async def getiFramesUrls(search_attrs):
    # width, height = 1800, 1300
    # browser = await launch(headless=False, args=[f'--window-size={width},{height}','--disable-infobars'])
    browser = await launch(headless=True,
                            handleSIGINT=False,
                            handleSIGTERM=False,
                            handleSIGHUP=False,
                            args=['--disable-infobars'])
    page = await browser.newPage()
    # await page.setViewport({'width': 1700, 'height': 1280})
    await page.goto(URL)

    if search_attrs["case0"]:
        await page.waitForSelector("#vtype_C")
        checkBox = await page.querySelector('#vtype_C')
        await checkBox.click()
    if search_attrs["case1"]:
        await page.waitForSelector("#vtype_V")
        checkBox = await page.querySelector('#vtype_V')
        await checkBox.click()
    if search_attrs["case2"]:
        await page.waitForSelector("#vtype_M")
        checkBox = await page.querySelector('#vtype_M')
        await checkBox.click()
    if search_attrs["case3"]:
        await page.waitForSelector("#vtype_A")
        checkBox = await page.querySelector('#vtype_A')
        await checkBox.click()
    if search_attrs["case4"]:
        await page.waitForSelector("#vtype_P")
        checkBox = await page.querySelector('#vtype_P')
        await checkBox.click()

    if search_attrs["year"] is not None:
        await page.waitForSelector("#jud_year")
        inputNum_jud_year = await page.querySelector('#jud_year')
        await inputNum_jud_year.type(search_attrs["year"])

    if search_attrs["judgement_char"] is not None:
        await page.waitForSelector("#jud_case")
        input_jud_case = await page.querySelector('#jud_case')
        await input_jud_case.type(search_attrs["judgement_char"])

    if search_attrs["startNum"] is not None:
        await page.waitForSelector("#jud_no")
        inputNum_jud_no = await page.querySelector('#jud_no')
        await inputNum_jud_no.type(search_attrs["startNum"])

    if search_attrs["endNum"] is not None:
        await page.waitForSelector("#jud_no_end")
        inputNum_jud_no_end = await page.querySelector('#jud_no_end')
        await inputNum_jud_no_end.type(search_attrs["endNum"])

    if search_attrs["startDay"] is not None:
        await page.waitForSelector("#dy1")
        inputNum_dy1 = await page.querySelector('#dy1')
        await page.waitForSelector("#dm1")
        inputNum_dm1 = await page.querySelector('#dm1')
        await page.waitForSelector("#dd1")
        inputNum_dd1 = await page.querySelector('#dd1')
        await inputNum_dy1.type(search_attrs["startDay"].year)
        await inputNum_dm1.type(search_attrs["startDay"].month)
        await inputNum_dd1.type(search_attrs["startDay"].day)

    if search_attrs["endDay"] is not None:
        await page.waitForSelector("#dy2")
        inputNum_dy2 = await page.querySelector('#dy2')
        await page.waitForSelector("#dm2")
        inputNum_dm2 = await page.querySelector('#dm2')
        await page.waitForSelector("#dd2")
        inputNum_dd2 = await page.querySelector('#dd2')
        await inputNum_dy2.type(search_attrs["endDay"].year)
        await inputNum_dm2.type(search_attrs["endDay"].month)
        await inputNum_dd2.type(search_attrs["endDay"].day)

    if search_attrs["judgementTitle"] is not None:
        await page.waitForSelector("#jud_title")
        input_jud_title = await page.querySelector('#jud_title')
        await input_jud_title.type(search_attrs["judgementTitle"])

    if search_attrs["judgementMain"] is not None:
        await page.waitForSelector("#jud_jmain")
        input_jud_jmain = await page.querySelector('#jud_jmain')
        await input_jud_jmain.type(search_attrs["judgementMain"])

    if search_attrs["judgementKeyword"] is not None:
        await page.waitForSelector("#jud_kw")
        input_jud_jkw = await page.querySelector('#jud_kw')
        await input_jud_jkw.type(search_attrs["judgementKeyword"])

    await page.waitForSelector("#btnQry")
    search_btn = await page.querySelector('#btnQry')
    await search_btn.click()

    if "Error" in page.url:
        st.warning("失敗")
        await browser.close()
        return

    await page.waitForSelector('#iframe-data')
    iFrame_element = await page.querySelector('#iframe-data')
    frame = await iFrame_element.contentFrame()
    iFrameUrl = await frame.evaluate('document.baseURI')
    await page.goto(iFrameUrl)
    
    try:
        await page.waitForSelector('#hlLast')
        last_link = await page.querySelector("#hlLast")
        last_link = await last_link.getProperty("href")
        results_pages = int(re.search(r"page=(\d+)", last_link.toString()).group(1))
    except Exception as e:
        st.warning(f"{iFrameUrl}", icon="⚠️")
        st.warning(f"請輸入完整裁判字號", icon="⚠️")
        st.warning(e.__str__(), icon="⚠️")
        results_pages = 1

    await browser.close()
    global pageUrls
    pageUrls = [f"{iFrameUrl}&sort=DS&page={p}&ot=in" for p in range(1, min(results_pages + 1, 26))] #最多500筆(25)頁，超過的judical不會顯示。
    print("len of pageUrls: ", len(pageUrls))

@st.cache_resource
def concurrentParse(search_attrs):
    start_time = timeit.default_timer()
    asyncio.new_event_loop().run_until_complete(getiFramesUrls(search_attrs))
    results = []
    # with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
    #     for r in executor.map(parsePage, pageUrls):
    #         if r is not None:
    #             results.extend(r)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(parsePage, url) for url in pageUrls]
        for future in concurrent.futures.as_completed(futures):
            results.extend(future.result())
    end_time = timeit.default_timer()
    print("search time:", end_time - start_time)

    df = pd.DataFrame(data=results, columns=['JID', 'JSCORE', 'JTITLE', 'JCHAR', 'JTYPE', 'JDATE', 'JOBJECT', 'JURL', 'JSUMMARY', 'JFULL'])
    return df

def parsePage(url):
    session = requests.Session()
    response = session.get(url)
    session.close()
    ret = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.select_one('#jud')
        if table is None:
            return None
        it = iter(table.find_all("tr"))
        next(it)
        for row in it:
            cells = row.find_all("td")
            if len(cells) != 4:
                continue
            a = cells[1].find('a')
            try:
                link = BASEURL + a.get('href')
                link = urllib.parse.unquote(link)
                start_index = link.find("id=") + 3
                end_index = link.find("&ot=")
                JID = link[start_index:end_index]
            except Exception:
                print(a)
                link = None
                JID = None
            # title = a.text.strip().replace(" ", "")
            title = a.text.strip()
            date = cells[2].text.strip()
            if '.' in date:
                year, month, day = date.split('.')
                date = f'{int(year) + 1911}-{month}-{day}'
            reason = cells[3].text.strip()
            next_row = next(it)
            dscp = next_row.find("span", class_="tdCut").text.strip()
            category_map = {"民事": "民事", "刑事": "刑事",
                        "行政": "行政", "懲戒": "懲戒", "憲法": "憲法"}
            char = None
            for key, value in category_map.items():
                if key in title:
                    char = value
                    break
            # ret.append(Node(title, date, reason, link, dscp, char))
            ret.append({'JID': JID,
                        'JSCORE': random.uniform(0, 1),
                        'JTITLE': reason,
                        'JCHAR': title,
                        'JTYPE': char,
                        'JDATE': date,
                        'JOBJECT': None,
                        'JURL': link,
                        'JSUMMARY':dscp,
                        'JFULL': ""
            })
    return ret

from fuzzywuzzy import fuzz

def search_company(df, keyword, threshold):
    similarity_scores = df['JOBJECT'].apply(lambda x: fuzz.ratio(keyword, x))
    filtered_df = df[similarity_scores >= threshold]
    return filtered_df

def doLocalSearch():
    def modify_scores(x):
        if x == 1:
            return x - random.uniform(0.02, 0.25)
        elif x == 0:
            return x + random.uniform(0.02, 0.25)
        return x
    if st.session_state["dataset"] is not None:
        df = search_company(st.session_state["dataset"], st.session_state["searchInputText"], 45)
        df.loc[:, "JSCORE"] = df.loc[:, "JSCORE"].apply(modify_scores)
        df.loc[:,"JDATE"] = pd.to_datetime(df.loc[:,"JDATE"], yearfirst=True).apply(lambda x: x.date())
        df = df.sort_values(by='JSCORE', ascending=False)
        # st.write(df.shape)
        # st.dataframe(df[['JID', 'labels', 'JTITLE', 'Judgment_Number', 'Case_Type',
        #     'Judgment_Date', 'Investigated_Object', 'Judgment_URL']])
        st.session_state.ret = df
        if st.session_state.ret.shape[0] > 0:
            st.session_state.curr_page = 1
        else:
            st.session_state.curr_page = None
            st.session_state["total_page"] = None
            st.session_state.ret = None
    