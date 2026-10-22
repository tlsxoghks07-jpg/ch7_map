import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math

# 1. 앱 제목 설정
st.title("🚇 부산 지하철 역별 이용객 수 지도 분석")

# 2. 파일 업로드 기능 (CSV 파일)
uploaded_file = st.file_uploader("busan_subway.csv 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    # CSV 데이터 불러오기
    df = pd.read_csv(uploaded_file)

    # 3. [표] 이용객 상위 5개 역을 표로 표시
    st.subheader("🏆 이용객 수 상위 5개 역")
    top5_df = df.sort_values(by='이용객수', ascending=False).head(5)
    st.dataframe(top5_df)

    st.markdown("---")

    # 4. [호선 필터] multiselect로 원하는 호선 선택 기능
    st.subheader("🗺️ 역별 이용객 수 지도")
    all_lines = df['호선'].unique()  # 데이터에 있는 모든 호선 목록 추출
    selected_lines = st.multiselect("조회할 호선을 선택하세요", all_lines, default=all_lines)

    # 선택한 호선만 데이터 필터링
    filtered_df = df[df['호선'].isin(selected_lines)]

    # 지도 중심 설정 (필터링된 데이터의 평균 위도/경도)
    if not filtered_df.empty:
        center_lat = filtered_df['위도'].mean()
        center_lon = filtered_df['경도'].mean()
    else:
        center_lat, center_lon = 35.1796, 129.0756  # 데이터가 없을 경우 기본 부산 시청 위치

    # folium 지도 객체 생성
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11)

    # 5. [색상] 호선별 지정 색상 딕셔너리 (1호선: 주황, 2호선: 초록, 3호선: 갈색, 4호선: 파랑)
    color_map = {
        '1호선': 'orange',
        '2호선': 'green',
        '3호선': 'brown',
        '4호선': 'blue'
    }

    # 6. 필터링된 데이터의 각 행을 돌며 지도에 마커 표시
    for index, row in filtered_df.iterrows():
        # 호선별 색상 가져오기 (등록되지 않은 호선일 경우 기본 회색)
        line_name = row['호선']
        marker_color = color_map.get(line_name, 'gray')

        # 원의 면적이 이용객수에 비례하도록 반지름을 제곱근(sqrt)으로 계산
        radius_value = math.sqrt(row['이용객수']) * 0.05

        # CircleMarker 추가
        folium.CircleMarker(
            location=[row['위도'], row['경도']],  # 위도, 경도 위치
            radius=radius_value,  # 계산된 반지름 크기
            color=marker_color,  # 지정된 호선 테두리 색상
            fill=True,  # 원 내부 채우기
            fill_color=marker_color,  # 지정된 호선 채우기 색상
            fill_opacity=0.6,  # 투명도 설정
            tooltip=f"[{row['호선']}] {row['역명']}",  # 마우스를 올렸을 때: [호선] 역명
            popup=f"{row['호선']} {row['역명']}역 이용객수: {row['이용객수']:,}명"  # 클릭했을 때: 상세 정보
        ).add_to(m)

    # Streamlit 화면에 folium 지도 표시
    st_folium(m, width=700, height=500)

else:
    st.info("시작하려면 CSV 파일을 업로드해주세요.")