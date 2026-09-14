import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(
    page_title="영화 데이터 대화형 분석 도감",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 질문으로 풀어보는 영화 데이터 대화형 도감")
st.markdown("원하는 질문을 선택하면 데이터 분석 결과와 맞춤형 그래프를 보여드립니다.")
st.markdown("---")

# 2. 데이터 불러오기 및 전처리
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str), format='%Y%m%d')
    return df

try:
    df = load_data(DATA_URL)
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 3. 질문 목록 정의
questions = [
    "Q1. 특정 영화의 개봉 후 날짜별 관객 수 변화는 어떠한가요?",
    "Q2. 기간 내 가장 흥행한 Top 5 영화들의 일별 관객 수 추이는 어떻게 비교되나요?",
    "Q3. 연중 전체 박스오피스 관객 수가 가장 집중된 피크 데이(Peak Day)는 언제인가요?",
    "Q4. 해당 기간 동안 가장 많은 관객을 동원한 Top 10 영화와 장기 흥행 여부는 어떠한가요?",
    "Q5. 월별, 요일별로 관객 수가 가장 몰리는 성수기 시간대는 언제인가요?"
]

# 4. 질문 선택 드롭다운
selected_question = st.selectbox(
    "🔍 확인하고 싶은 질문을 선택하세요:",
    questions
)

st.markdown("---")

# 5. 질문별 동적 그래프 생성

# [Q1. 개별 영화 날짜별 관객 수 추이]
if selected_question == questions[0]:
    st.subheader("📌 Q1. 특정 영화의 개봉 후 날짜별 관객 수 변화")
    
    movie_list = sorted(df['영화명'].dropna().unique())
    selected_movie = st.selectbox("분석할 영화를 선택하세요:", movie_list)
    
    if selected_movie:
        movie_df = df[df['영화명'] == selected_movie].sort_values('날짜')
        
        fig1 = px.line(
            movie_df, x='날짜', y='일관객',
            title=f"[{selected_movie}] 일별 관객 수 추이",
            labels={'날짜': '날짜', '일관객': '일일 관객 수(명)'},
            markers=True
        )
        fig1.update_traces(
            hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>"
        )
        fig1.update_layout(xaxis_title="날짜", yaxis_title="일일 관객 수(명)", hovermode="x unified")
        
        st.plotly_chart(fig1, use_container_width=True)
        st.info(f"💡 **답변:** '{selected_movie}'의 개봉 초기 관객 집중도와 주말/평일 관객 수 변동 패턴을 파악할 수 있습니다.")

# [Q2. Top 5 영화 비교]
elif selected_question == questions[1]:
    st.subheader("📌 Q2. Top 5 영화의 날짜별 일관객 비교")
    
    top5_movies = df.groupby('영화명')['일관객'].sum().nlargest(5).index.tolist()
    top5_df = df[df['영화명'].isin(top5_movies)].sort_values('날짜')
    
    fig2 = px.line(
        top5_df, x='날짜', y='일관객', color='영화명',
        title=f"총 관객 수 Top 5 영화 일별 관객 수 비교",
        labels={'날짜': '날짜', '일관객': '일일 관객 수(명)', '영화명': '영화 제목'}
    )
    fig2.update_traces(
        hovertemplate="<b>영화명:</b> %{fullData.name}<br><b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>"
    )
    fig2.update_layout(xaxis_title="날짜", yaxis_title="일일 관객 수(명)", hovermode="x unified")
    
    st.plotly_chart(fig2, use_container_width=True)
    st.info(f"💡 **답변:** 최고 흥행작 5편({', '.join(top5_movies)})의 개봉 시기별 최고 피크 수치와 대작 간의 시기별 경쟁 양상을 직접 비교할 수 있습니다.")

# [Q3. 박스오피스 총관객 수 피크 데이]
elif selected_question == questions[2]:
    st.subheader("📌 Q3. 전체 박스오피스 총관객 수 추이 및 피크 데이")
    
    daily_total = df.groupby('날짜')['일관객'].sum().reset_index()
    daily_total.rename(columns={'일관객': '총일관객'}, inplace=True)
    top3_days = daily_total.nlargest(3, '총일관객').sort_values('날짜')
    
    fig3 = px.area(
        daily_total, x='날짜', y='총일관객',
        title="날짜별 Box Office 10위권 관객 수 합계 변화",
        labels={'날짜': '날짜', '총일관객': '10위권 총 관객 수(명)'}
    )
    fig3.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>총 관객 수:</b> %{y:,}명<extra></extra>"
    )
    
    for idx, row in top3_days.iterrows():
        date_str = row['날짜'].strftime('%Y-%m-%d')
        total_val = row['총일관객']
        fig3.add_annotation(
            x=row['날짜'], y=total_val,
            text=f"<b>TOP {top3_days.index.get_loc(idx)+1}</b><br>{date_str}<br>({total_val:,}명)",
            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2,
            arrowcolor="#E74C3C", ax=0, ay=-45,
            bgcolor="#FADBD8", bordercolor="#E74C3C", borderwidth=1, borderpad=4
        )
        
    fig3.update_layout(xaxis_title="날짜", yaxis_title="10위권 총 관객 수(명)", hovermode="x unified")
    
    st.plotly_chart(fig3, use_container_width=True)
    top3_str_list = [f"{row['날짜'].strftime('%Y년 %m월 %d일')}({row['총일관객']:,}명)" for _, row in top3_days.iterrows()]
    st.info(f"💡 **답변:** 가장 많은 관객이 극장을 찾은 상위 3일은 [{', '.join(top3_str_list)}]이며, 연휴 및 명절 대목의 극장가 활성도를 보여줍니다.")

# [Q4. 기간 내 Top 10 영화]
elif selected_question == questions[3]:
    st.subheader("📌 Q4. 기간 내 관객 수 Top 10 영화 및 유지 기간")
    
    top10_summary = (
        df.groupby('영화명')
        .agg(총관객수=('일관객', 'sum'), 차트인일수=('날짜', 'nunique'))
        .reset_index()
        .nlargest(10, '총관객수')
        .sort_values('총관객수', ascending=True)
    )
    
    fig4 = px.bar(
        top10_summary, x='총관객수', y='영화명', orientation='h',
        title="기간 내 일관객 합계 상위 10개 영화",
        labels={'총관객수': '총 관객 수(명)', '영화명': '영화 제목'},
        text_auto=',d', color='총관객수', color_continuous_scale='Viridis'
    )
    fig4.update_traces(
        hovertemplate="<b>영화명:</b> %{y}<br><b>총 관객 수:</b> %{x:,}명<br><b>10위권 진입 일수:</b> %{customdata[0]}일<extra></extra>",
        customdata=top10_summary[['차트인일수']].values
    )
    fig4.update_layout(xaxis_title="총 관객 수(명)", yaxis_title="영화 제목", coloraxis_showscale=False)
    
    st.plotly_chart(fig4, use_container_width=True)
    st.info("💡 **답변:** 최상위 10개 흥행작의 규모와 10위권 진입 일수를 한눈에 파악하여 장기 흥행 여부를 판단할 수 있습니다.")

# [Q5. 월×요일별 히트맵]
elif selected_question == questions[4]:
    st.subheader("📌 Q5. 월×요일별 관객 수 분포 (성수기 분석)")
    
    df_heatmap = df.copy()
    df_heatmap['월'] = df_heatmap['날짜'].dt.month.map(lambda x: f"{x}월")
    day_map = {'Monday': '월요일', 'Tuesday': '화요일', 'Wednesday': '수요일', 'Thursday': '목요일', 'Friday': '금요일', 'Saturday': '토요일', 'Sunday': '일요일'}
    df_heatmap['요일'] = df_heatmap['날짜'].dt.day_name().map(day_map)
    
    days_order = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    months_order = [f"{m}월" for m in range(1, 13)]
    
    pivot_df = df_heatmap.groupby(['월', '요일'])['일관객'].sum().reset_index()
    
    fig5 = px.density_heatmap(
        pivot_df, x='요일', y='월', z='일관객',
        category_orders={'요일': days_order, '월': months_order},
        title="월 및 요일별 일관객 합계 분포",
        labels={'요일': '요일', '월': '월', '일관객': '총 관객 수(명)'},
        color_continuous_scale='Blues', text_auto=',d'
    )
    fig5.update_traces(
        hovertemplate="<b>월:</b> %{y}<br><b>요일:</b> %{x}<br><b>관객 수 합계:</b> %{z:,}명<extra></extra>"
    )
    fig5.update_layout(xaxis_title="요일 (월요일 ➔ 일요일)", yaxis_title="월", coloraxis_colorbar=dict(title="관객 수(명)"))
    
    st.plotly_chart(fig5, use_container_width=True)
    st.info("💡 **답변:** 요일별(평일 vs 주말) 유입 특성과 월별 계절성 시즌이 결합된 최고 성수기 타임슬롯을 진한 색상으로 확인할 수 있습니다.")
