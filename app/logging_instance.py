import inspect
import logging

def customLogger(logLevel=logging.DEBUG, filename="logs/robot_results.log", logger_name="_general_"):
    # Gets the name of the class / method from where this method is called
    loggerName = logger_name
    logger = logging.getLogger(loggerName)
    # By default, log all messages
    logger.setLevel(logging.DEBUG)

    fileHandler = logging.FileHandler(filename, mode='w')
    fileHandler.setLevel(logLevel)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    return logger