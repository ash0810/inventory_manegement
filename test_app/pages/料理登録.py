import streamlit as st
import sqlite3
import pandas as pd

st.title('作るメニューと個数を入力するページ')
st.caption('消費する材料の個数を計算してデータベースを編集する')

# データベースファイルのパスを指定
db_path = "C:/zaiko/inventory_manegement/test_app/発注管理.db"  # 保存先のディレクトリを指定

# データベース内にテーブルを作成
def create_ryouri_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ryouri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            quantity INTEGER
        )
    """)
    conn.commit()
    conn.close()

# 作る料理とその個数を入力
if "ryouri_info_list" not in st.session_state:
    st.session_state["ryouri_info_list"] = []

with st.form(key='ryouri_info'):
    kinds = st.number_input('料理数', min_value=1, step=1, key="ryouri_kinds")
    submit_button = st.form_submit_button('料理の登録')

    if submit_button:
        # 料理数に応じてフォームの入力欄を作成
        st.session_state["ryouri_info_list"] = []
        for i in range(int(kinds)):
            name_key = f"name_{i}"
            kosuu_key = f"kosuu_{i}"

            name = st.text_input(f'料理名 {i+1}', key=name_key)
            kosuu = st.number_input(f'個数 {i+1}', min_value=1, step=1, key=kosuu_key)

            if name and kosuu:
                st.session_state["ryouri_info_list"].append({
                    "name": name,
                    "quantity": kosuu
                })
        
        if st.session_state["ryouri_info_list"]:
            # 入力されたデータをデータベースに保存
            create_ryouri_table()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 入力された料理情報をデータベースに保存
            for entry in st.session_state["ryouri_info_list"]:
                cursor.execute("""
                    INSERT INTO ryouri (name, quantity)
                    VALUES (?, ?)
                """, (entry["name"], entry["quantity"]))
            
            conn.commit()
            conn.close()

            st.success("データがデータベースに保存されました！")

# データ表示ボタンを追加
if st.button('登録された料理データを表示'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 料理データをSQLクエリで取得
    cursor.execute("SELECT * FROM ryouri")
    ryouri_data = cursor.fetchall()
    if ryouri_data:
        st.write("登録された料理データ:")
        # データを表示
        ryouri_df = pd.DataFrame(ryouri_data, columns=["ID", "料理名", "個数"])
        st.write(ryouri_df)
    else:
        st.write("登録された料理データはありません。")

    conn.close()
