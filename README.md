# judgments-investigation-assistant
Judgments Investigation Assistant 是第五屆T大使-上海商銀企業專班學員們的實作結果。

## 示範影片
[<img src="https://img.youtube.com/vi/EPotbISrGYs/0.jpg" width="90%">](https://youtu.be/EPotbISrGYs)

## 安裝虛擬環境

1. 下載專案的壓縮檔或使用 Git Clone 複製專案到本地。

    ```bash
    git clone https://github.com/leemikepop/judgments-investigation-assistant.git
    ```

2. 建立並啟用虛擬環境(建議使用python3.10.9 ~ 3.12.4)：

   ```bash
   python3 -m venv "demo-env-310"
   source demo-env-310/bin/activate //Linux
   demo-env-310\Scripts\activate //Windows
   ```

3. 開啟終端機（Terminal）並切換到專案的目錄。

    ```bash
    cd demo/
    ```

4. 安裝必要的套件

    ```bash
    pip install --default-timeout=100 -r requirements.txt
    ```
    <br>
    如果你使用windows OS，請在虛擬環境中修改這份文件
    
    `demo-env-310\Lib\site-packages\pyppeteer\__init__.py`

    ```python
    # __chromium_revision__ = '1181205' 修改如下
    __chromium_revision__ = '1263111'
    ```

5. 下載資料集到`demo/`資料夾下
    [dataset2_no_JFULL.csv](https://drive.google.com/file/d/1RXb2XytTrLxhzNgKLwkOyqJlkxnJvnVa/view?usp=sharing)
    
    
6.  在 `.streamlit/`下新增`secrets.toml`
    ```toml
    [BEDROCK]
    ACCESS_KEY = 'YOUR_BEDROCK_ACCESS_KEY'
    SECRET_KEY = 'YOUR_BEDROCK_ACCESSSECRET_KEY'
    ```
    
7. 運行demo程式

    ```bash
    streamlit run demo_with_streamlit_elements.py
    ```
    在瀏覽器開啟[localhost:8501](localhost:8501)
    第一次運行線上搜尋會比較久，因為`pyppeteer`會先安裝瀏覽器核心

8. 結束程式並退出虛擬環境

    `Ctrl + Z` 中止 `streamlit` 程式
    
    ```bash
    deactivate
    ```
