# AI 보고서 생성기

원시 보안 점검 내용을 입력하면 OpenAI API를 사용해 구조화된 취약점 보고서를 생성하는 Streamlit 웹앱입니다. 생성된 결과는 화면에서 JSON과 Markdown 형식으로 확인할 수 있으며, Markdown 파일은 `output/` 디렉터리에 자동 저장됩니다.

## 주요 기능

- 원시 점검 메모를 취약점 보고서 형식으로 변환
- 위험도, 취약점 유형, 대상 시스템, 설명, 영향, 조치 방안 등을 구조화
- Pydantic 모델을 사용해 LLM 응답 형식 검증
- 생성된 보고서를 Markdown 파일로 저장
- Streamlit 기반 웹 UI 제공
- 사이드바에서 API Key 로드 상태 확인

## 프로젝트 구조

```text
.
├── app.py              # Streamlit 웹앱 진입점
├── llm_service.py      # OpenAI API 호출 및 구조화 응답 처리
├── models.py           # 취약점 보고서 Pydantic 모델 정의
├── check_key.py        # OPENAI_API_KEY 로드 확인용 스크립트
├── openai_test.py      # OpenAI API 호출 테스트용 스크립트
├── output/             # 생성된 Markdown 보고서 저장 위치
└── README.md
```

## 실행 환경

- Python 3.10 이상 권장
- OpenAI API Key

## 설치

가상환경을 생성하고 필요한 패키지를 설치합니다.

```bash
python -m venv .venv
source .venv/bin/activate
pip install streamlit python-dotenv openai pydantic
```

Windows PowerShell을 사용하는 경우 가상환경 활성화 명령은 다음과 같습니다.

```powershell
.\.venv\Scripts\Activate.ps1
```

## 환경변수 설정

프로젝트 루트에 `.env` 파일을 만들고 OpenAI API Key를 설정합니다.

```env
OPENAI_API_KEY=your_openai_api_key_here
```

API Key가 정상적으로 로드되는지 확인하려면 다음 명령을 실행합니다.

```bash
python check_key.py
```

## 실행 방법

Streamlit 앱을 실행합니다.

```bash
streamlit run app.py
```

브라우저에서 Streamlit이 안내하는 로컬 주소로 접속한 뒤, 원시 점검 내용을 입력하고 `AI 보고서 생성` 버튼을 누릅니다.

## 사용 흐름

1. 사용자가 원시 보안 점검 내용을 입력합니다.
2. `request_to_llm()` 함수가 입력 내용을 OpenAI API에 전달합니다.
3. LLM 응답은 `VulnerabilityReport` Pydantic 모델 형태로 파싱됩니다.
4. `report_to_markdown()` 함수가 구조화된 데이터를 Markdown 보고서로 변환합니다.
5. `save_markdown()` 함수가 보고서를 `output/` 디렉터리에 저장합니다.
6. Streamlit 화면에 JSON 데이터와 Markdown 미리보기가 함께 표시됩니다.

## 보고서 데이터 모델

`models.py`의 `VulnerabilityReport` 모델은 다음 필드를 사용합니다.

| 필드 | 설명 |
|---|---|
| `title` | 취약점명 |
| `severity` | 위험도 |
| `vulnerability_type` | 취약점 유형 |
| `target` | 대상 시스템 |
| `description` | 취약점 설명 |
| `affected_parameter` | 영향받는 파라미터 |
| `proof_of_concept` | 재현 예시 |
| `impact` | 예상 영향 |
| `remediation` | 조치 방안 목록 |

## 출력 파일

보고서 생성에 성공하면 다음 형식의 Markdown 파일이 생성됩니다.

```text
output/vulnerability_report_YYYYMMDD_HHMMSS.md
```

예시:

```text
output/vulnerability_report_20260608_144447.md
```

## 참고 사항

- `.env` 파일에는 실제 API Key가 들어가므로 Git에 커밋하지 않아야 합니다.
- OpenAI API 호출에는 사용량에 따른 비용이 발생할 수 있습니다.
- LLM 응답이 모델 형식에 맞지 않거나 API Key가 없으면 앱 화면에 예외 정보가 표시됩니다.
