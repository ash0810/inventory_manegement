# pages/料理作成.py
import streamlit as st
import sqlite3
import pandas as pd

st.title('作るメニューと個数を入力するページ')
st.caption('消費する材料の個数を計算してデータベースを編集する')

# データベースファイルのパス（発注管理.db を共通利用）
db_path = "C:/zaiko/inventory_manegement/test_app/発注管理.db"

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

# セッション変数の初期化
if "ryouri_kinds" not in st.session_state:
    st.session_state["ryouri_kinds"] = 1
if "ryouri_inputs" not in st.session_state:
    st.session_state["ryouri_inputs"] = {}

# ── 料理数入力用フォーム ──
with st.form(key='ryouri_kinds_form'):
    kinds = st.number_input('料理数', min_value=1, step=1, value=st.session_state["ryouri_kinds"], key="ryouri_kinds_input")
    submit_kinds = st.form_submit_button('料理数を登録')
    if submit_kinds:
        st.session_state["ryouri_kinds"] = int(kinds)
        st.experimental_rerun()  # 再描画して動的入力欄を更新

# ── 動的入力欄の表示 ──
for i in range(st.session_state["ryouri_kinds"]):
    name_key = f"ryouri_name_{i}"
    qty_key = f"ryouri_quantity_{i}"
    # 初期値の設定（初回のみ）
    if name_key not in st.session_state["ryouri_inputs"]:
        st.session_state["ryouri_inputs"][name_key] = ""
    if qty_key not in st.session_state["ryouri_inputs"]:
        st.session_state["ryouri_inputs"][qty_key] = 1
    st.session_state["ryouri_inputs"][name_key] = st.text_input(f'料理名 {i+1}', 
                                                                 value=st.session_state["ryouri_inputs"][name_key], 
                                                                 key=name_key)
    st.session_state["ryouri_inputs"][qty_key] = st.number_input(f'個数 {i+1}', 
                                                                  min_value=1, step=1, 
                                                                  value=st.session_state["ryouri_inputs"][qty_key], 
                                                                  key=qty_key)

# ── 料理情報の登録ボタン ──
if st.button('料理の登録'):
    ryouri_info_list = []
    for i in range(st.session_state["ryouri_kinds"]):
        name = st.session_state.get(f"ryouri_name_{i}")
        qty = st.session_state.get(f"ryouri_quantity_{i}")
        if name and qty:
            ryouri_info_list.append({"name": name, "quantity": qty})
    if ryouri_info_list:
        create_ryouri_table()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for entry in ryouri_info_list:
            cursor.execute("""
                INSERT INTO ryouri (name, quantity)
                VALUES (?, ?)
            """, (entry["name"], entry["quantity"]))
        conn.commit()
        conn.close()
        st.success("データがデータベースに保存されました！")
        st.session_state["ryouri_inputs"] = {}  # 入力欄をリセット
    else:
        st.error("料理情報が入力されていません。")

# ── 登録済み料理データ表示ボタン ──
if st.button('登録された料理データを表示'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ryouri")
    ryouri_data = cursor.fetchall()
    if ryouri_data:
        st.write("登録された料理データ:")
        ryouri_df = pd.DataFrame(ryouri_data, columns=["ID", "料理名", "個数"])
        st.write(ryouri_df)
    else:
        st.write("登録された料理データはありません。")
    conn.close()
