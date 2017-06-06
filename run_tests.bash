#!/usr/bin/env bash
export PYTHONPATH=$PYTHONPATH:.
echo $PYTHONPATH
python3 test/test_ncsharedstate.py
python3 test/test_ncsharedstate_pypacker.py
python3 test/test_ncpacketdispatcher.py
python3 test/test_codingutils.py
#python test/test_ncacksreceipt.py
python3 test/test_nctransmitter.py
python3 test/test_ncencoder.py
#python test/test_COPEpktclasses.py
python3 test/test_netwutils.py
#python test/test_ncdecoder.py
#python test/test_ncenqueuer.py
python3 test/test_ncencapsulator.py
# python test/test_controlpktscheduler.py
# python test/test_all.py
python3 test/test_ncnetwlist.py

# python -m unittest discover ./test
#python test/run_all_tests.py