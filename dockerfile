FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1 

WORKDIR /app

# 시스템 의존성 설치 (pillow만 고려)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt ./

# pip 업그레이드는 항상 좋은 습관입니다.
RUN pip install --upgrade pip setuptools wheel

# pyarrow가 이제 휠로 설치될 것입니다.
RUN pip install -r requirements.txt

# 빌드용 패키지 정리
RUN apt-get purge -y --auto-remove build-essential python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ... (non-root 사용자 생성 및 나머지 부분은 동일) ...
RUN useradd -ms /bin/bash appuser
COPY --chown=appuser:appuser . .
USER appuser

EXPOSE 8080
CMD ["streamlit", "run", "mainPage.py", "--server.port=8080", "--server.enableCORS=false"]