import logging
import sys
from pathlib import Path
from loguru import logger

def setup_logger():
    """
    Configures the logger with console and file sinks.
    Standard logging is intercepted to be handled by loguru.
    """
    # Define log directory and file
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "app.log"

    # Remove default loguru handler
    logger.remove()

    # Add Console sink with rich formatting
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # Add File sink (Asynchronous via enqueue=True)
    logger.add(
        str(log_file),
        rotation="10 MB",
        retention="10 days",
        level="DEBUG",
        enqueue=True,  # This makes logging non-blocking
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        backtrace=True,
        diagnose=True,
    )

    # Intercept standard python logging
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            logging_file = getattr(logging, "__file__", None)
            while frame and logging_file and frame.f_code.co_filename == logging_file:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    # Replace standard logging handlers with our InterceptHandler
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Silence excessive logs from some libraries if needed
    for logger_name in ("uvicorn", "uvicorn.access", "httpx"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    logger.info("Logger initialized successfully with async file sinking.")
