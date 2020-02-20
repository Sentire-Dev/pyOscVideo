import logging as log

module_logger = log.getLogger(__name__)
module_logger.setLevel(log.DEBUG)
file_handler = log.FileHandler('test_logging.log')
file_handler.setLevel(log.DEBUG)
console_handler = log.StreamHandler()
console_handler.setLevel(log.DEBUG)
formatter = log.Formatter('%(name)-20s: %(levelname)-8s %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(log.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
module_logger.addHandler(console_handler)
module_logger.addHandler(file_handler)

class TestClassA:
    def __init__(self):
        self._logger = log.getLogger(__name__+'.TestClassA')
        self._console_handler = log.StreamHandler()
        formatter = log.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        self._console_handler.setFormatter(formatter)
        self._logger.addHandler(self._console_handler)
    
    def do_something(self):
        self._logger.debug("Some Debug Message")
        self._logger.warning("Some Warning")
        self._logger.info("Some Info")

class TestClassB:
    def __init__(self):
        self._logger = log.getLogger(__name__+'.TestClassB')
        self._console_handler = log.StreamHandler()
        formatter = log.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        self._console_handler.setFormatter(formatter)
        self._logger.addHandler(self._console_handler)
    
    def do_something(self):
        self._logger.debug("Some Debug Message")
        self._logger.warning("Some Warning")
        self._logger.info("Some Info")


# Create instance of class a
module_logger.info('Creating Instance of ClassA')
class_a = TestClassA()
class_b = TestClassB()
# calling do_something won't log until level set
class_a.do_something() 
class_b.do_something() 

# set its logging options 
# NOTE: this can only be done from outside the class
module_logger.info('Changing ClassA logging level to INFO')
class_a_logger = log.getLogger(__name__+'.TestClassA')
class_a_logger.propagate = False
class_b_logger = log.getLogger(__name__+'.TestClassB')
class_b_logger.propagate = False
class_a._console_handler.setLevel(log.DEBUG)
class_b._console_handler.setLevel(log.INFO)
# after setting the level it works
class_a.do_something() 
class_b.do_something() 



        


