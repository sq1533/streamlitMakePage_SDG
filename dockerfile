FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# 시스템 의존성 설치 (최적화보다는 안정성 우선으로 변경)
# purge를 제거하여 필요한 런타임 라이브러리가 삭제되는 것을 방지합니다.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# sed를 사용하여 index.html의 <title>을 변경하고 Open Graph 메타태그를 삽입합니다.
RUN find /usr/local/lib/python3.12/site-packages/streamlit -name "index.html" -exec sed -i 's|<title>Streamlit</title>|<title>AMUREDO</title><meta property="og:title" content="AMUREDO" /><meta property="og:description" content="AMUREDO 공식 온라인 스토어" /><meta property="og:image" content="https://amuredo.shop/media/nav.webp" />|g' {} +

# 3. 사용자 권한 설정
RUN useradd -ms /bin/bash appuser
COPY --chown=appuser:appuser . .
USER appuser

EXPOSE 8080

CMD ["streamlit", "run", "mainPage.py", \
    "--server.port=8080", \
    "--server.address=0.0.0.0", \
    "--server.enableCORS=false", \
    "--server.enableXsrfProtection=false", \
    "--server.headless=true"]