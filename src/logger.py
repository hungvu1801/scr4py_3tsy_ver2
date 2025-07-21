import logging
import logging.handlers
import os
import pathlib

def setup_logger(name="MyLogger", log_dir="logs"):
    """
    Setup logger with proper configuration for production environment
    """
    project_root = pathlib.Path(__file__).parent.parent.resolve()

    if os.path.isabs(log_dir):
        abs_log_dir = pathlib.Path(log_dir)
    else:
        abs_log_dir = project_root / log_dir
    # Create logs directory if it doesn't exist
    abs_log_dir.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if logger.hasHandlers():
        return logger
    # Create handlers
    # Rotating file handler for general logs
    general_log_file = abs_log_dir / "main_log.log"
    general_handler = (
        logging
        .handlers
        .TimedRotatingFileHandler(
            general_log_file,
            when='midnight',         # Rotate at midnight
            interval=1,              # Every 1 day
            backupCount=5,           # Keep last 5 log files
            encoding='utf-8',
            utc=False                # Set to True if you want UTC time
        ))
    
    general_handler.setLevel(logging.INFO)

    # Rotating file handler for error logs
    error_log_file = os.path.join(log_dir, f"log_errors.log")
    error_handler = (
        logging
        .handlers
        .TimedRotatingFileHandler(
            error_log_file,
            when='midnight',         # Rotate at midnight
            interval=1,              # Every 1 day
            backupCount=5,           # Keep last 5 log files
            encoding='utf-8',
            utc=False   
        ))
    error_handler.setLevel(logging.ERROR)

    # Create formatters and add it to handlers
    log_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(threadName)s] - %(funcName)s - %(name)s - %(message)s'
    )
    general_handler.setFormatter(log_format)
    error_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(general_handler)
    logger.addHandler(error_handler)

    return logger 