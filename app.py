import streamlit as st
import pandas as pd

# -------------------------------------------------
# 設定
# -------------------------------------------------
CSV_FILE = "history_qa1.csv"  # 読み込むCSVファイル名
APP_TITLE = "歴史一問一答 完全攻略"

# -------------------------------------------------
# データ読み込み関数
# -------------------------------------------------
@st.cache_data
def load_data():
    try:
        # CSVを読み込む（ヘッダーあり）
        # 列構成: ID, 単元名, 問題, 解答, (その他の列は無視)
        df = pd.read_csv(CSV_FILE, encoding='utf-8', usecols=['ID', '単元名', '問題', '解答'])
        # 列名を統一（単元名 → 単元）
        df = df.rename(columns={'単元名': '単元'})
        return df
    except FileNotFoundError:
        st.error(f"エラー: {CSV_FILE} が見つかりません。同じフォルダに置いてください。")
        return pd.DataFrame()
    except KeyError as e:
        st.error(f"CSVファイルの列名が正しくありません。必要な列: ID, 単元名, 問題, 解答")
        st.error(f"エラー詳細: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"CSV読み込みエラー: {e}")
        return pd.DataFrame()

# -------------------------------------------------
# メイン処理
# -------------------------------------------------
def main():
    st.title(APP_TITLE)
    
    # データのロード
    df = load_data()
    if df.empty:
        return

    # 全単元のリストを作成
    units = df["単元"].unique().tolist()

    # -------------------------------------------------
    # QRコード連携（ディープリンク）ロジック
    # -------------------------------------------------
    # URLパラメータを取得 (?subject=science&unit=明治時代 とか)
    # Streamlit 1.28.0以降の新しいAPIを使用
    try:
        query_params = st.query_params
        target_unit = query_params.get("unit", None)
        # subjectパラメータも取得（将来の拡張用）
        subject = query_params.get("subject", None)
    except AttributeError:
        # 古いバージョンの場合は、st.experimental_get_query_paramsを使用
        try:
            query_params = st.experimental_get_query_params()
            target_unit = query_params.get("unit", [None])[0]
            subject = query_params.get("subject", [None])[0]
        except:
            target_unit = None
            subject = None

    # デフォルトの選択単元を決める
    default_index = 0
    if target_unit and target_unit in units:
        default_index = units.index(target_unit)
        st.success(f"📍 {target_unit} のページに移動しました！")
    
    # サイドバーで単元選択（QRから来た場合はその単元が初期値になる）
    selected_unit = st.sidebar.selectbox("単元を選んでください", units, index=default_index)

    # -------------------------------------------------
    # 問題表示エリア
    # -------------------------------------------------
    st.header(f"📂 {selected_unit}")
    
    # 選ばれた単元の問題だけを抽出
    current_questions = df[df["単元"] == selected_unit]

    # 一問ずつ表示
    for index, row in current_questions.iterrows():
        with st.expander(f"Q. {row['問題']}"):
            st.write(f"**A. {row['解答']}**")

# -------------------------------------------------
# アプリ実行
# -------------------------------------------------
if __name__ == "__main__":
    main()