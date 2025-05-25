import logging
import os

def setup_logger(name, log_file, level=logging.INFO):
    """Set up logger with file handler"""
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    # if not os.path.exists('logs'):
    #     os.makedirs('logs')
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create file handler
    file_handler = logging.FileHandler(f'logs/{log_file}')
    file_handler.setLevel(level)
    
    # Create console handler
    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    # console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    # logger.addHandler(console_handler)
    
    return logger

# Create loggers for admin
logger = setup_logger('admin', 'admin.log')