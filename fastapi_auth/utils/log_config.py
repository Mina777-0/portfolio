import logging
import os 

log_path= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.log'))

def get_log(name= "debug"):
    global log_path
    logger= logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        handler= logging.FileHandler(filename= log_path, encoding='utf-8')
        formatter= logging.Formatter(fmt='%(asctime)s %(message)s', datefmt="%d/%m/%Y - %H:%M:%S")

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        logger.propagate= False

    return logger

#logger= get_log()
#logger.info('This .log first test')
        