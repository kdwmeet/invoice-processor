import streamlit as st
import json
from app.graph import app_graph

st.set_page_config(page_title="인보이스 파싱 파이프라인", layout="wide")

st.title("지능형 B2B 인보이스 및 발주서 파이프라인")
st.markdown("정제되지 않은 인보이스 텍스트를 입력하면, Pydantic으로 강제된 엄격한 스키마 규격에 맞춰 데이터를 추출합니다.")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("원본 데이터 입력")
    raw_input = st.text_area(
        "OCR로 인식되었거나 이메일 본문에서 복사한 인보이스 텍스트를 입력하십시오.",
        height=350,
        placeholder="Invoice from: Tech Corp...\nDate: Oct 12, 2026..."
    )
    submit_btn = st.button("구조화된 데이터 추출 시작", type="primary", use_container_width=True)

with col2:
    st.subheader("ERP 연동용 규격화 데이터 (JSON)")
    result_container = st.container(border=True)

    if submit_btn:
        if raw_input.strip():
            initial_state = {
                "raw_text": raw_input,
                "parsed_data": {},
                "error": ""
            }

            with st.spinner("Pydantic 스키마 기반 데이터 추출 및 검증 중..."):
                final_state = app_graph.invoke(initial_state)
            
            with result_container:
                if final_state.get("error"):
                    st.error(final_state.get("error"))
                else:
                    st.success("데이터 추출 및 스키마 검증 완료")
                    # 추출된 딕셔너리를 보기 좋게 JSON 포맷으로 출력
                    st.json(final_state.get("parsed_data"))

        else:
            st.warning("원본 텍스트를 입력해주십시오.")