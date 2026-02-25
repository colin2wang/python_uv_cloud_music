import logging
import os
from datetime import datetime

def setup_logger(name: str = __name__, log_level: str = "INFO") -> logging.Logger:
    """
    配置并返回一个日志记录器
    
    Args:
        name: 日志记录器名称
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        配置好的 Logger 对象
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 设置日志级别
    log_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # 添加处理器到记录器
    logger.addHandler(console_handler)
    
    # 创建文件处理器（可选）
    try:
        # 创建 logs 目录
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # 生成日志文件名 - 使用完整时间戳确保每次运行都是新文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f"cloud_music_{timestamp}.log"
        log_filepath = os.path.join(log_dir, log_filename)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        
        # 添加文件处理器
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"无法创建文件日志处理器: {e}")
    
    return logger

# 创建默认的日志记录器
logger = setup_logger(__name__)

if __name__ == "__main__":
    # 测试日志功能
    test_logger = setup_logger("test")
    test_logger.debug("这是调试信息")
    test_logger.info("这是普通信息")
    test_logger.warning("这是警告信息")
    test_logger.error("这是错误信息")
    test_logger.critical("这是严重错误信息")