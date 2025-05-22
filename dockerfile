FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 의존성 설치 (필요한 경우)
# 예: RUN apt-get update && apt-get install -y libpq-dev gcc

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드를 이미지로 복사합니다.
# Dockerfile과 streamlitMakePage_SDG.py (또는 메인 실행 파일) 및 관련 파일들이 같은 디렉토리에 있다고 가정합니다.
# 만약 소스 코드가 src 폴더 등에 있다면 `COPY src/ .` 와 같이 경로를 수정하세요.
COPY . .

EXPOSE 8501

# 컨테이너 실행 시 Streamlit 애플리케이션을 실행합니다.
CMD ["streamlit", "run", "mainPage.py"]