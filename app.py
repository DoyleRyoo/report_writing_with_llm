import os

import streamlit as st
from dotenv import load_dotenv

from llm_service import request_to_llm
from models import VulnerabilityReport

from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------
# 1. 환경변수 확인
# ---------------------------------------------------------
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

def report_to_markdown(report: VulnerabilityReport) -> str:
  markdown = f"""
# 취약점 보고서

## 1. 기본 정보

| 항목 | 내용 |
|---|---|
| 취약점명 | {report.title} |
| 위험도 | {report.severity} |
| 취약점 유형 | {report.vulnerability_type} |
| 대상 시스템 | {report.target} |

---

## 2. 취약점 설명
{report.description}

---

## 3. 영향받는 파라미터
{report.affected_parameter}

---

## 4. 재현 예시
{report.proof_of_concept}

---

## 5. 예상 영향
{report.impact}

---

## 6. 조치 방안
"""

  for item in report.remediation:
    markdown += f"- {item}\n"
	
  return markdown

def save_markdown(markdown: str) -> str:
  output_dir = Path("./output")
  output_dir.mkdir(parents=True, exist_ok=True)

  report_date = datetime.now().strftime("%Y%m%d_%H%M%S")
  filename = output_dir / f"vulnerability_report_{report_date}.md"

  with open(filename, "w", encoding="utf-8") as file:
    file.write(markdown)

  return str(filename)

# ---------------------------------------------------------
# 2. Streamlit 기본 화면 설정
# ---------------------------------------------------------
st.set_page_config(
  page_title="AI 보고서 생성기",
  layout="wide"
)

st.title("AI를 활용한 보고서 작성 웹앱")
st.write("원시 점검 내용을 입력하면 AI가 구조화된 보고서로 정리합니다.")

st.divider()


# ---------------------------------------------------------
# 3. 사이드바 구성
# ---------------------------------------------------------
with st.sidebar:
  st.header("실습 안내")
  st.write("1. 원시 점검 내용을 입력합니다.")
  st.write("2. 보고서 생성 버튼을 누릅니다.")
  st.write("3. AI가 구조화된 보고서를 생성합니다.")
  st.write("4. 결과를 화면에서 확인합니다.")

  st.divider()
  st.write("API Key 상태")

  if api_key:
    st.success("API Key 로드 완료")
  else:
    st.error("API Key가 설정되지 않았습니다.")


# ---------------------------------------------------------
# 4. 테스트용 원시 데이터
# ---------------------------------------------------------
sample_text = """대상: 사내 게시판 시스템
발견 내용:
- 게시글 검색 기능에서 SQL Injection 의심
- 파라미터: keyword
- payload: ' OR '1'='1
- 검색 결과에 비정상적으로 많은 데이터 노출
- 로그인하지 않은 사용자도 접근 가능
"""


# ---------------------------------------------------------
# 5. 사용자 입력 영역
# ---------------------------------------------------------
raw_data = st.text_area(
  "보고서로 변환할 원시 점검 내용을 입력하세요.",
  value=sample_text,
  height=260
)


# ---------------------------------------------------------
# 6. AI 보고서 생성
# ---------------------------------------------------------
if st.button("AI 보고서 생성", type="primary"):
  if not raw_data.strip():
    st.warning("원시 점검 내용을 입력하세요.")
  else:
    with st.spinner("AI가 보고서를 생성하는 중입니다..."):
      try:
        report = request_to_llm(raw_data)
        markdown = report_to_markdown(report)
        saved_path = save_markdown(markdown)

        st.success("보고서 생성이 완료되었습니다.")
        st.info(f"Markdown 파일 저장 위치: {saved_path}")

        col1, col2 = st.columns(2)

        with col1:
          st.subheader("구조화된 보고서 데이터")
          st.json(report.model_dump())

        with col2:
          st.subheader("Markdown 보고서 미리보기")
          st.markdown(markdown)

      except Exception as e:
        st.error("보고서 생성 중 오류가 발생했습니다.")
        st.exception(e)