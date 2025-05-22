FROM python:3.9-slim

# Python 로그가 버퍼링 없이 즉시 출력되도록 설정
# pip 캐싱 비활성화 (Docker build에서 더 효율적)
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1 

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 라이브러리 설치
# 여기에 필요한 다른 시스템 라이브러리를 추가하세요.
# 예시: libgl1-mesa-glx, libsm6, libxext6, libxrender1, libpq-dev, zlib1g-dev, libjpeg-dev 등
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    # --- 추가될 수 있는 일반적인 시스템 라이브러리 (필요에 따라 주석 해제 또는 추가) ---
    # libgl1-mesa-glx \
    # libsm6 \
    # libxext6 \
    # libxrender1 \
    # git \
    # libpq-dev \
    # zlib1g-dev \
    # libjpeg-dev \
    # libpng-dev \
    # libtiff-dev \
    # libatlas-base-dev \ # For numpy/scipy with BLAS/LAPACK
    # gfortran \          # For numpy/scipy with Fortran extensions
    # --- 여기까지 ---
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 Python 패키지 설치
# pip install 명령어 실패 시 자세한 로그를 위해 -vvv 옵션을 일시적으로 추가할 수 있습니다.
# RUN pip install -vvv -r requirements.txt
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