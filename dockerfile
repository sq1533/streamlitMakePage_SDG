FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1 

WORKDIR /app

# 시스템 의존성 설치 및 정리
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
# (pip install 명령어 실패 시 자세한 로그를 위해 RUN 명령어에 -vvv 옵션을 일시적으로 추가할 수 있습니다.)
COPY requirements.txt ./
RUN pip install -r requirements.txt

# 보안 강화를 위해 non-root 사용자 생성
RUN useradd -ms /bin/bash appuser

# 애플리케이션 코드를 이미지로 복사
COPY --chown=appuser:appuser . .

# non-root 사용자로 전환하여 보안 강화
USER appuser

ENV PORT=8080
EXPOSE 8080

# 컨테이너 실행 시 Streamlit 애플리케이션을 실행합니다.
CMD ["streamlit", "run", "mainPage.py"]