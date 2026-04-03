import streamlit as st
import pandas as pd
import re
from io import BytesIO

def searchDate(lines, index):
  recordLength = 12
  for i in range(recordLength):
    date = lines[index+i]
    pattern = r'[A-Z][a-z]+ \d{1,2}, \d{4}'
    if re.search(pattern, date):
      return i
  return -1

#AtlanticCouncil
def get_atlanticCouncil_articles(text):
    lines = text.splitlines()
    index = -1;
    target = "Content"
    if target in lines:
        index = lines.index(target)
    else:
        st.error("キーワード「Content」が見つかりませんでした。")
        return None
    rows = []

    while True:
        resultSearchDate = searchDate(lines,index)
        if resultSearchDate == -1:
            break
        else:
            index += resultSearchDate
        date = lines[index]
        tag = lines[index-2]
        if(tag == "In the News"):
            index += 7
            continue
        title = lines[index+1]
        author = lines[index+2]
        if author.startswith("By"):
            author = author[2:].strip()
            overview = lines[index+4]
            topic1 = lines[index+6]
            topic2 = lines[index+7]
        else:
            author = "N/A"
            overview = lines[index+2]
            topic1 = lines[index+4]
            topic2 = lines[index+5]
        
        rows.append(["", date, title, "","AtlanticCouncil","",f"{topic1}、{topic2}",author,"",overview])
        index += 7
        df = pd.DataFrame(rows, columns=["#", "日付", "レポートタイトル", "URL","Thinktank名","関係国","トピック","執筆者","まとめ翻訳","まとめ翻訳英文"])
    return df
#Brookings
def get_brookings_articles():
    rows = []
    df = pd.DataFrame(rows, columns=["#", "日付", "レポートタイトル", "URL","Thinktank名"])

    return df

#CSIS
def get_csis_articles():
    rows = []
    # DataFrame作成
    df = pd.DataFrame(rows,columns=["#", "日付", "レポートタイトル", "URL","Thinktank名"]).drop_duplicates(subset=['URL'])

    return df

# ------------------------
# パスワード設定
# ------------------------
PASSWORD = st.secrets["password"] 

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ------------------------
# ログイン画面
# ------------------------
if not st.session_state.authenticated:

    st.title("ログイン")

    password_input = st.text_input("パスワードを入力してください", type="password")

    if st.button("ログイン"):
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")

# ------------------------
# ログイン後の画面
# ------------------------
else:

    st.title("Web記事取得ツール")

    st.write("テキストを入力して Web の記事一覧を Excel で取得できます")

    site = st.selectbox(
        "取得するサイトを選択してください",
        #["Brookings", "CSIS"]
        ["AtlanticCouncil"]
    )

    # テキスト入力
    text = st.text_area("Webサイトから取得したテキストを入力してください")

    #st.write("入力された値:", text)

    # ボタン
    if st.button("記事を取得"):

        st.write("取得中です...")

        df = None

        if site == "AtlanticCouncil":
            try:

                df = get_atlanticCouncil_articles(text)

                if df is not None:
                    if len(df) > 0:
                        st.success(f"{len(df)}件の記事を取得しました")
                    else:
                        st.error("記事がありませんでした")

            except Exception as e:
                st.error(str(e))

        elif site == "Brookings":
            try:

                df = get_brookings_articles()

                if len(df) > 0:
                    st.success(f"{len(df)}件の記事を取得しました")
                else:
                    st.error("記事がありませんでした")

            except Exception as e:
                st.error(str(e))


        elif site == "CSIS":
            try:

                df = get_csis_articles()

                if len(df) > 0:
                    st.success(f"{len(df)}件の記事を取得しました")
                else:
                    st.error("記事がありませんでした")

            except Exception as e:
                st.error(str(e))

        
        if df is not None:
            # Excel作成
            output = BytesIO()
            df.to_excel(output, index=False, engine="openpyxl")
            excel_data = output.getvalue()

            if site == "AtlanticCouncil":
                st.download_button(
                    label="Excelダウンロード",
                    data=excel_data,
                    file_name="AtlanticCouncil.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            elif site == "Brookings":
                st.download_button(
                    label="Excelダウンロード",
                    data=excel_data,
                    file_name="Brookings.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            elif site == "CSIS":
                st.download_button(
                    label="Excelダウンロード",
                    data=excel_data,
                    file_name="CSIS.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )