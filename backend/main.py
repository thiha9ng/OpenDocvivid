import uvicorn
from src.configs.config import settings
from src.utils.logger import get_logger

# Get logger for this module
logger = get_logger(__name__)

def main():
    """Start the service"""
    logger.info("Starting ai-docvivid-service...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Host: {settings.host}")
    logger.info(f"Port: {settings.port}")
    logger.info(f"Debug mode: {'Enabled' if settings.debug else 'Disabled'}")
    logger.info(f"Log level: {settings.log_level}")
    
    uvicorn.run(
        "src.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )

if __name__ == "__main__":
    main() 