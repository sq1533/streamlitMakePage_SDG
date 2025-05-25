FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1 

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# pip install 명령어 실패 시 자세한 로그를 위해 -vvv 옵션을 일시적으로 추가할 수 있습니다.
COPY requirements.txt ./
RUN pip install -r requirements.txt

# 보안 강화를 위해 non-root 사용자 생성
RUN useradd -ms /bin/bash appuser

# 애플리케이션 코드를 이미지로 복사합니다.
# Dockerfile과 streamlitMakePage_SDG.py (또는 메인 실행 파일) 및 관련 파일들이 같은 디렉토리에 있다고 가정합니다.
COPY --chown=appuser:appuser . .

# non-root 사용자로 전환
USER appuser

EXPOSE 8502

# 컨테이너 실행 시 Streamlit 애플리케이션을 실행합니다.
CMD ["streamlit", "run", "mainPage.py"]