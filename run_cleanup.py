import api.batch
import utils
import logging

# 로거 설정
logger = utils.get_logger()

def main():
    logger.info("Starting cleanup job...")
    
    # utilsDb() 호출로 Firebase 등 초기화
    # 스트림릿 secrets를 사용하므로 로컬/클라우드 환경에서 .streamlit/secrets.toml이 있어야 함
    try:
        db = utils.utilsDb()
        if not db:
            logger.error("DB initialization failed.")
            return
        
        # 배치 로직 실행 (로그는 logger.info 사용)
        api.batch.cleanup_zombie_reservations(log_func=logger.info)
        
    except Exception as e:
        logger.error(f"Error during cleanup job: {e}")

if __name__ == "__main__":
    main()
