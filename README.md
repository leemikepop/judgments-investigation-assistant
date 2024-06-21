# judgments-investigation-assistant
Judgments Investigation Assistant 是第五屆T大使-上海商銀企業專班學員們的實作結果。

## 示範影片
![示例影片](https://github.com/leemikepop/judgments-investigation-assistant/blob/main/demo-vedio.webm)

## 安裝虛擬環境

1. 下載專案的壓縮檔或使用 Git Clone 複製專案到本地。

    ```bash
    git clone https://github.com/leemikepop/judgments-investigation-assistant.git
    ```

2. 開啟終端機（Terminal）並切換到專案的目錄。

    ```bash
    cd demo/
    ```

3. 建立並啟用虛擬環境：

   ```bash
   python3 -m venv "demo-env"
   source demo-env/bin/activate
   ```

4. 安裝必要的套件

    ```bash
    pip install -r requirements.txt
    ```
5. 下載資料集到`demo/`資料夾下

    [dataset2_no_JFULL.csv](https://drive.google.com/file/d/1RXb2XytTrLxhzNgKLwkOyqJlkxnJvnVa/view?usp=sharing)
    
6. 運行demo程式

    ```bash
    streamlit run demo_with_streamlit_elements.py
    ```
    在瀏覽器開啟[localhost:8501](localhost:8501)
    第一次運行線上搜尋會比較久，因為`pyppeteer`會先安裝瀏覽器核心

7. 結束程式並退出虛擬環境

    `Ctrl + Z` 中止 `streamlit` 程式
    
    ```bash
    deactivate
    ```