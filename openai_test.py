from openai import OpenAI
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# OpenAI 클라이언트 생성
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.responses.create(
  model="gpt-5-nano",
  input="AI를 활용한 보고서 작성의 장점을 세 문장으로 설명해줘."
)

print(response.output_text)