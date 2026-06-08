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
# .env 파일에 저장된 환경변수를 현재 파이썬 프로세스로 불러옵니다.
# OPENAI_API_KEY는 llm_service.py에서 OpenAI API를 호출할 때 필요합니다.
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

def report_to_markdown(report: VulnerabilityReport) -> str:
  # LLM 응답은 VulnerabilityReport 모델 형태로 들어옵니다.
  # 화면 미리보기와 파일 저장에 모두 사용할 수 있도록 Markdown 문자열로 변환합니다.
  # f-string을 사용해 모델의 각 필드를 보고서 템플릿의 알맞은 위치에 삽입합니다.
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

  # remediation은 여러 개의 조치 항목을 담은 리스트이므로
  # Markdown 목록 문법("- 항목")에 맞춰 한 줄씩 추가합니다.
  for item in report.remediation:
    markdown += f"- {item}\n"
	
  return markdown

def save_markdown(markdown: str) -> str:
  # 생성된 보고서는 output 디렉터리에 저장합니다.
  # 디렉터리가 아직 없다면 mkdir(..., exist_ok=True)로 자동 생성합니다.
  output_dir = Path("./output")
  output_dir.mkdir(parents=True, exist_ok=True)

  # 같은 이름의 파일이 덮어써지지 않도록 현재 시각을 파일명에 포함합니다.
  report_date = datetime.now().strftime("%Y%m%d_%H%M%S")
  filename = output_dir / f"vulnerability_report_{report_date}.md"

  # 한글이 깨지지 않도록 UTF-8 인코딩으로 Markdown 파일을 저장합니다.
  with open(filename, "w", encoding="utf-8") as file:
    file.write(markdown)

  # Streamlit 화면에 저장 경로를 표시할 수 있도록 문자열 경로를 반환합니다.
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
# 사이드바에는 사용 순서와 API Key 설정 여부를 보여줍니다.
# API Key가 없으면 버튼을 눌렀을 때 LLM 호출 단계에서 실패할 수 있습니다.
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
# 앱을 처음 실행했을 때 바로 테스트할 수 있도록 기본 입력값을 제공합니다.
# 사용자는 이 내용을 지우고 실제 점검 메모나 취약점 발견 내용을 붙여 넣을 수 있습니다.
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
# text_area의 반환값은 사용자가 입력한 원문 문자열입니다.
# 이후 버튼을 누르면 이 문자열이 LLM 프롬프트 입력으로 전달됩니다.
raw_data = st.text_area(
  "보고서로 변환할 원시 점검 내용을 입력하세요.",
  value=sample_text,
  height=260
)


# ---------------------------------------------------------
# 6. AI 보고서 생성
# ---------------------------------------------------------
# Streamlit은 사용자가 버튼을 누를 때마다 스크립트를 위에서부터 다시 실행합니다.
# 따라서 실제 보고서 생성 로직은 st.button(...)이 True인 순간에만 수행합니다.
if st.button("AI 보고서 생성", type="primary"):
  # 공백만 입력된 경우에는 API를 호출하지 않고 사용자에게 입력을 요청합니다.
  if not raw_data.strip():
    st.warning("원시 점검 내용을 입력하세요.")
  else:
    # LLM 호출은 시간이 걸릴 수 있으므로 spinner로 진행 상태를 표시합니다.
    with st.spinner("AI가 보고서를 생성하는 중입니다..."):
      try:
        # 1) 원시 점검 내용을 LLM에 전달해 구조화된 VulnerabilityReport 객체를 받습니다.
        report = request_to_llm(raw_data)

        # 2) 구조화된 객체를 Markdown 보고서 텍스트로 변환합니다.
        markdown = report_to_markdown(report)

        # 3) 생성된 Markdown을 output 디렉터리에 파일로 저장합니다.
        saved_path = save_markdown(markdown)

        st.success("보고서 생성이 완료되었습니다.")
        st.info(f"Markdown 파일 저장 위치: {saved_path}")

        # 결과 확인을 쉽게 하기 위해 왼쪽에는 원본 구조화 데이터(JSON),
        # 오른쪽에는 사람이 읽기 좋은 Markdown 미리보기를 배치합니다.
        col1, col2 = st.columns(2)

        with col1:
          st.subheader("구조화된 보고서 데이터")
          st.json(report.model_dump())

        with col2:
          st.subheader("Markdown 보고서 미리보기")
          st.markdown(markdown)

      except Exception as e:
        # API Key 누락, 네트워크 오류, 모델 응답 검증 실패 등 모든 예외를 화면에 표시합니다.
        # st.exception은 상세 traceback까지 보여주므로 실습 중 원인 파악에 유용합니다.
        st.error("보고서 생성 중 오류가 발생했습니다.")
        st.exception(e)
