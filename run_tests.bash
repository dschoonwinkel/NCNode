#!/usr/bin/env bash
export PYTHONPATH=$PYTHONPATH:.
echo $PYTHONPATH
#python test/test_ncsharedstate.py
#python test/test_ncpacketdispatcher.py
#python test/test_codingutils.py
#python test/test_ncacksreceipt.py
#python test/test_nctransmitter.py
#python test/test_ncencoder.py
#python test/test_COPEpktclasses.py
#python test/test_netwutils.py
#python test/test_ncdecoder.py
#python test/test_ncenqueuer.py

# python test/test_all.py

# python -m unittest discover ./test
python test/run_all_tests.py