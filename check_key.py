from dotenv import load_dotenv
import os

# .env 파일을 읽어 환경변수로 등록한다.
load_dotenv()

# 환경변수에서 API Key를 가져온다.
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
  print("API Key가 정상적으로 로드되었습니다.")
  print(api_key[:10] + "*" * 20)
else:
  print("OPENAI_API_KEY가 설정되지 않았습니다.")