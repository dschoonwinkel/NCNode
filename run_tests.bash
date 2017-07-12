#!/usr/bin/env bash
export PYTHONPATH=$PYTHONPATH:.
echo $PYTHONPATH
# python3 test/test_ncsharedstate.py
# python3 test/test_ncsharedstate_pypacker.py
# python3 test/test_ncpacketdispatcher.py
# python3 test/test_codingutils.py
# python3 test/test_ncacksreceipt.py
# python3 test/test_nctransmitter.py
# python3 test/test_ncencoder.py
# python3 test/test_COPEpktclasses.py
# python3 test/test_netwutils.py
# python3 test/test_ncdecoder.py
# python3 test/test_ncenqueuer.py
# python3 test/test_ncencapsulator.py
python3 test/test_ncnetwlist.py
# python3 test/test_controlpktscheduler.py
# python3 test/test_all.py


# python3 -m unittest discover ./test
# python3 test/run_all_tests.py