import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(
    page_title="영화 데이터 대화형 Q&A 도감",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 무엇이든 물어보세요!")
st.markdown("데이터 관련 질문을 입력하거나 아래 예시 질문 버튼을 클릭하면 맞춤형 그래프를 생성합니다.")
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

# 3. 예시 질문 버튼 세트
st.write("**💡 추천 질문 예시:**")
col1, col2, col3, col4, col5 = st.columns(5)

example_q = ""
if col1.button("개별 영화 추이"):
    example_q = "특정 영화의 일별 관객 수 추이가 궁금해"
if col2.button("Top 5 비교"):
    example_q = "Top 5 영화 관객 수 비교해줘"
if col3.button("피크 데이"):
    example_q = "총 관객 수가 가장 많았던 날은 언제야?"
if col4.button("Top 10 종합"):
    example_q = "가장 관객이 많았던 상위 10개 영화 알려줘"
if col5.button("월×요일 히트맵"):
    example_q = "월별 요일별 관객 수 히트맵 보여줘"

# 4. 질문 입력창
user_question = st.text_input(
    "💬 질문을 입력하세요:",
    value=example_q if example_q else "",
    placeholder="예: 월별 요일별 관객 수 분포 히트맵 보여줘"
)

st.markdown("---")

# 5. 질문 분석 및 동적 그래프 출력
if user_question:
    q = user_question.strip().lower()
    
    # [답변 1: 개별 영화 추이]
    if any(k in q for k in ["개별", "특정", "추이", "선 그래프", "영화별"]):
        st.subheader("📌 [답변] 개별 영화의 날짜별 관객 수 변화")
        
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
            fig1.update_traces(hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>")
            fig1.update_layout(xaxis_title="날짜", yaxis_title="일일 관객 수(명)", hovermode="x unified")
            
            st.plotly_chart(fig1, use_container_width=True)

    # [답변 2: Top 5 영화 비교]
    elif any(k in q for k in ["top 5", "top5", "비교", "상위 5", "5개"]):
        st.subheader("📌 [답변] 관객 수 Top 5 영화의 날짜별 일관객 비교")
        
        top5_movies = df.groupby('영화명')['일관객'].sum().nlargest(5).index.tolist()
        top5_df = df[df['영화명'].isin(top5_movies)].sort_values('날짜')
        
        fig2 = px.line(
            top5_df, x='날짜', y='일관객', color='영화명',
            title="총 관객 수 Top 5 영화 일별 관객 수 비교",
            labels={'날짜': '날짜', '일관객': '일일 관객 수(명)', '영화명': '영화 제목'}
        )
        fig2.update_traces(hovertemplate="<b>영화명:</b> %{fullData.name}<br><b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>")
        fig2.update_layout(xaxis_title="날짜", yaxis_title="일일 관객 수(명)", hovermode="x unified")
        
        st.plotly_chart(fig2, use_container_width=True)

    # [답변 3: 피크 데이 / 영역 그래프]
    elif any(k in q for k in ["피크", "가장 많았던 날", "합계", "영역", "총관객", "언제"]):
        st.subheader("📌 [답변] 날짜별 박스오피스 총관객 수 추이 및 주요 피크 데이")
        
        daily_total = df.groupby('날짜')['일관객'].sum().reset_index()
        daily_total.rename(columns={'일관객': '총일관객'}, inplace=True)
        top3_days = daily_total.nlargest(3, '총일관객').sort_values('날짜')
        
        fig3 = px.area(
            daily_total, x='날짜', y='총일관객',
            title="날짜별 Box Office 10위권 관객 수 합계 변화",
            labels={'날짜': '날짜', '총일관객': '10위권 총 관객 수(명)'}
        )
        fig3.update_traces(hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>총 관객 수:</b> %{y:,}명<extra></extra>")
        
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

    # [답변 4: Top 10 가로 막대]
    elif any(k in q for k in ["top 10", "top10", "10개", "막대", "누적"]):
        st.subheader("📌 [답변] 기간 내 관객 수 Top 10 영화")
        
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

    # [답변 5: 월×요일 히트맵]
    elif any(k in q for k in ["월", "요일", "히트맵", "성수기", "주말"]):
        st.subheader("📌 [답변] 월×요일별 일관객 합계 히트맵")
        
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
        fig5.update_traces(hovertemplate="<b>월:</b> %{y}<br><b>요일:</b> %{x}<br><b>관객 수 합계:</b> %{z:,}명<extra></extra>")
        fig5.update_layout(xaxis_title="요일 (월요일 ➔ 일요일)", yaxis_title="월", coloraxis_colorbar=dict(title="관객 수(명)"))
        
        st.plotly_chart(fig5, use_container_width=True)

    else:
        st.warning("⚠️ 질문을 이해하지 못했습니다. 상단의 추천 질문 버튼을 클릭하거나 'Top 5', '월별 요일', '개별 영화', '피크' 등의 키워드를 포함해 질문해주세요.")
else:
    st.info("👆 상단의 텍스트 입력창에 질문을 입력하거나 추천 질문 버튼을 눌러주세요.")
