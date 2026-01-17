import os
import shutil
import logging
import sys

# 로거 설정을 위한 기본 로깅 (utils 로딩 전)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('cleanup_job')

def bootstrap_secrets():
    """
    Cloud Run Job에서 마운트된 비밀번호 파일(/secrets/secrets.toml)을
    Streamlit이 인식할 수 있는 .streamlit/secrets.toml 경로로 복사합니다.
    """
    # 1. 배포 시 설정한 마운트 경로
    mount_path = "/secrets/secrets.toml"
    
    # 2. 목표 경로 (.streamlit 폴더 생성)
    target_dir = ".streamlit"
    target_path = os.path.join(target_dir, "secrets.toml")
    
    if os.path.exists(mount_path):
        logger.info(f"Found secrets at {mount_path}. Copying to {target_path}...")
        try:
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy(mount_path, target_path)
            logger.info("Secrets setup complete.")
        except Exception as e:
            logger.error(f"Failed to copy secrets: {e}")
    else:
        logger.warning(f"No secrets found at {mount_path}. Assuming local environment or IAM auth.")

def main():
    # 1. 시크릿 설정 우선 실행
    bootstrap_secrets()

    # 2. 이제 utils 및 api 모듈 임포트 (st.secrets가 파일을 읽을 수 있도록)
    try:
        import utils
        import api.batch
        
        # utils 로거로 교체
        app_logger = utils.get_logger()
        app_logger.info("Starting cleanup job...")
        
        db = utils.utilsDb()
        if not db:
            app_logger.error("DB initialization failed.")
            return
        
        # 배치 로직 실행
        api.batch.cleanup_zombie_reservations(log_func=app_logger.info)
        
    except Exception as e:
        logger.error(f"Error during cleanup execution: {e}")


if __name__ == "__main__":
    main()
