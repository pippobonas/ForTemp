import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s][%(levelname)s]: %(message)s")

def stdo(message=""):
    logging.info(message)
    
def stde(message=""):
    logging.error(message)
    
def stdw(message=""):
    logging.warning(message)