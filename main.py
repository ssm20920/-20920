import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown("1년치(365일) 일별 박스오피스 데이터를 바탕으로 시간의 흐름에 따른 영화 관객 수와 추세를 탐색합니다.")
st.markdown("---")

# 2. 데이터 불러오기 및 전처리
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    # 날짜 열(YYYYMMDD 8자리 숫자/문자)을 datetime 타입으로 변환
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str), format='%Y%m%d')
    return df

try:
    df = load_data(DATA_URL)
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 3. 구역 1: 개별 영화의 날짜별 일관객 변화 (선 그래프)
st.header("📌 구역 1. 개별 영화의 날짜별 일관객 변화")

# 전체 영화 목록 추출
movie_list = sorted(df['영화명'].dropna().unique())

selected_movie = st.selectbox("분석할 영화를 선택하세요:", movie_list)

if selected_movie:
    movie_df = df[df['영화명'] == selected_movie].sort_values('날짜')
    
    # Plotly 선 그래프 생성
    fig1 = px.line(
        movie_df,
        x='날짜',
        y='일관객',
        title=f"[{selected_movie}] 일별 관객 수 추이",
        labels={'날짜': '날짜', '일관객': '일일 관객 수(명)'},
        markers=True
    )
    
    # 마우스 오버 시 날짜 및 관객 수 표시 설정
    fig1.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>"
    )
    
    fig1.update_layout(
        xaxis_title="날짜",
        yaxis_title="일일 관객 수(명)",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # 그래프 설명 문구 자리
    st.info(f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}'의 일별 관객 수 추이를 통해 개봉 직후 흥행 추이 및 주말/평일 관객 수 변동 패턴을 한눈에 확인할 수 있습니다.")

st.markdown("---")

# 4. 향후 그래프 추가용 예시 구역 (확장 구역)
st.header("📌 구역 2. [추후 그래프 추가 예정]")
st.write("새로운 시간 기반 분석 그래프가 이곳에 추가될 예정입니다.")
st.info("💡 **이 그래프로 알 수 있는 것:** (그래프 추가 시 문구가 작성됩니다.)")
