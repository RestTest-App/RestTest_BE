import logging

logger = logging.getLogger("resttest")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")

handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)