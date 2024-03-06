import logging
import seqlog
import json
import os
import psutil
from logging.handlers import RotatingFileHandler
# from dotenv import load_dotenv

# load_dotenv()


def get_logger():
    return logging.getLogger('app_logger')


def get_system_vitals():
    cpu_percent = psutil.cpu_percent()
    ram_percent = psutil.virtual_memory().percent
    available_ram = psutil.virtual_memory().available * 100 / \
        psutil.virtual_memory().total

    return (cpu_percent, ram_percent, available_ram)


def get_cpu_percent():
    return get_system_vitals()[0]


def get_ram_percent():
    return get_system_vitals()[1]


def get_available_ram():
    return get_system_vitals()[2]


def init_logger():
    SEQ_URL = os.getenv('SEQ_URL')
    LOG_LEVEL = int(os.getenv('LOG_LEVEL'))

    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)s %(threadName)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler = RotatingFileHandler(filename='logs/amns_error_log.log',
                                  maxBytes=1024 * 1024 * 20,
                                  backupCount=10)
    handler.setFormatter(formatter)

    seqLogHandler = seqlog.log_to_seq(
        server_url=SEQ_URL,
        level=LOG_LEVEL,
        batch_size=10,
        auto_flush_timeout=10,
        support_stack_info=True,
        json_encoder_class=json.encoder.JSONEncoder
    )

    seqLogHandler.setFormatter(formatter)
    seqlog.set_global_log_properties(
        CpuPercent=get_cpu_percent,
        RamPercent=get_ram_percent,
        AvailableRam=get_available_ram
    )

    logger = get_logger()

    logger.addHandler(handler)
    logger.addHandler(seqLogHandler)
    logger.setLevel(LOG_LEVEL)
