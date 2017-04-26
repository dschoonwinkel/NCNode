import test_codingutils
import test_ncacksreceipt
import test_ncencoder
import test_ncpacketdispatcher
import test_ncsharedstate
import test_nctransmitter
import test_netwutils
import unittest
import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('nc_node.run_all_tests')

def main():
    suites = list()
    all_tests = unittest.TestLoader().discover('./', pattern='test_*.py')
    unittest.TextTestRunner().run(all_tests)

    logger.debug("Tests run")

if __name__ == '__main__':
    main()
