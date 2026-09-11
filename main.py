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
    # 날짜 열을 문자열로 변환 후 datetime 타입으로 변환 (YYYYMMDD 형식)
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str), format='%Y%m%d')
    return df

try:
    df = load_data(DATA_URL)
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 3. 구역 1: 개별 영화의 날짜별 일관객 변화 (선 그래프)
st.header("📌 구역 1. 개별 영화의 날짜별 일관객 변화")

# 전체 영화 목록 추출 (영화명 기준)
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
    
    fig1.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>"
    )
    
    fig1.update_layout(
        xaxis_title="날짜",
        yaxis_title="일일 관객 수(명)",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # 그래프 해석 문구 자리
    st.info(f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}'의 일별 관객 수 추이를 통해 개봉 직후 흥행 및 주말/평일 관객 수 변동 패턴을 파악할 수 있습니다.")

st.markdown("---")

# 4. 구역 2: 누적 관객 상위 Top 5 영화의 날짜별 일관객 비교
st.header("📌 구역 2. 관객 수 Top 5 영화의 날짜별 일관객 비교")

# 해당 기간 일관객 합계 상위 5개 영화 선정
top5_movies = (
    df.groupby('영화명')['일관객']
    .sum()
    .nlargest(5)
    .index.tolist()
)

# Top 5 영화 데이터 필터링
top5_df = df[df['영화명'].isin(top5_movies)].sort_values('날짜')

# Plotly 선 그래프 생성 (영화별 색상 구분)
fig2 = px.line(
    top5_df,
    x='날짜',
    y='일관객',
    color='영화명',
    title=f"기간 내 총 관객 수 Top 5 영화 ({', '.join(top5_movies)}) 일별 관객 수 비교",
    labels={'날짜': '날짜', '일관객': '일일 관객 수(명)', '영화명': '영화 제목'},
    markers=False
)

fig2.update_traces(
    hovertemplate="<b>영화명:</b> %{fullData.name}<br><b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>"
)

fig2.update_layout(
    xaxis_title="날짜",
    yaxis_title="일일 관객 수(명)",
    legend_title="영화 목록 (클릭하여 켜기/끄기)",
    hovermode="x unified"
)

st.plotly_chart(fig2, use_container_width=True)

# 그래프 해석 문구 자리
st.info(f"💡 **이 그래프로 알 수 있는 것:** 해당 기간 최고 흥행작 5편({', '.join(top5_movies)})의 흥행 시기와 최고 정점(피크) 수치를 서로 비교하여 시기별 대작 영화의 경쟁 양상 및 관객 집중 패턴을 파악할 수 있습니다.")

st.markdown("---")

# 5. 구역 3: 날짜별 Top 10 영화 일관객 합계 추이 (영역 그래프)
st.header("📌 구역 3. 날짜별 Top 10 박스오피스 총 관객 수 추이")

# 날짜별 10위권 일관객 합계 계산
daily_total = df.groupby('날짜')['일관객'].sum().reset_index()
daily_total.rename(columns={'일관객': '총일관객'}, inplace=True)

# 일관객 합계 상위 3일 추출
top3_days = daily_total.nlargest(3, '총일관객').sort_values('날짜')

# Plotly 영역 그래프 생성
fig3 = px.area(
    daily_total,
    x='날짜',
    y='총일관객',
    title="날짜별 Box Office 10위권 관객 수 합계 변화",
    labels={'날짜': '날짜', '총일관객': '10위권 총 관객 수(명)'}
)

fig3.update_traces(
    hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>총 관객 수:</b> %{y:,}명<extra></extra>"
)

# 상위 3일 포인트 표시 및 주석(어노테이션) 추가
for idx, row in top3_days.iterrows():
    date_str = row['날짜'].strftime('%Y-%m-%d')
    total_val = row['총일관객']
    
    fig3.add_annotation(
        x=row['날짜'],
        y=total_val,
        text=f"<b>TOP {top3_days.index.get_loc(idx)+1}</b><br>{date_str}<br>({total_val:,}명)",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#E74C3C",
        ax=0,
        ay=-45,
        bgcolor="#FADBD8",
        bordercolor="#E74C3C",
        borderwidth=1,
        borderpad=4
    )

fig3.update_layout(
    xaxis_title="날짜",
    yaxis_title="10위권 총 관객 수(명)",
    hovermode="x unified"
)

st.plotly_chart(fig3, use_container_width=True)

# 상위 3일 날짜 텍스트 구성
top3_str_list = [f"{row['날짜'].strftime('%Y년 %m월 %d일')}({row['총일관객']:,}명)" for _, row in top3_days.iterrows()]

st.info(f"💡 **이 그래프로 알 수 있는 것:** 연중 박스오피스 전체 시장의 활성도를 나타내며, 일관객 합계가 가장 컸던 주요 3일[{', '.join(top3_str_list)}]을 통해 연휴, 명절, 극장가 최대 대목 시즌의 관객 집중 정도를 파악할 수 있습니다.")

st.markdown("---")

# 6. 향후 추가될 구역 플레이스홀더 (확장용)
st.header("📌 구역 4. [추후 추가 예정]")
st.write("새로운 시간 기반 데이터 시각화 그래프가 여기에 추가될 예정입니다.")
st.info("💡 **이 그래프로 알 수 있는 것:** (그래프 추가 후 설명이 작성됩니다.)")
