from openai import OpenAI
from dotenv import load_dotenv
import os

from models import VulnerabilityReport
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def request_to_llm(raw_data: str) -> VulnerabilityReport:
  response = client.responses.parse(
    model="gpt-5.4-nano",
    input=[
      {
        "role": "system",
        "content": """
당신은 보안 점검 보고서 작성 전문가입니다.
사용자가 제공한 원시 정보를 분석하여 정형화된 취약점 보고서를 작성하세요.

규칙:
1. severity는 반드시 Critical, High, Medium, Low, Informational 중 하나만 사용합니다.
2. 전문 용어를 제외한 설명은 한국어로 작성합니다.
3. 조치 방안은 구체적인 실행 목록으로 작성합니다.
4. 확인되지 않은 사실은 단정하지 않습니다.
"""
      },
      {
        "role": "user",
        "content": raw_data
      }
    ],
    text_format=VulnerabilityReport,
  )

  return response.output_parsed