# Learning module
#
# This module is meant to be run in a production environment
# under normal network conditions. It produces a dataset for
# training purposes which reflects normal operation. The more
# records processed, the better the quality of the resulting
# dataset.

import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
import numpy as np
import sys
import subprocess
import time
import normalise as norm

argus = subprocess.Popen("ra -n -L -1 -S 127.0.0.1:561 -c \",\" -u -s \"dur proto:10 sport dir dport state pkts bytes sbytes\" 2> /dev/null",stdout=subprocess.PIPE,shell=True)

numlines = 0
out = ""
try:
    while True:
        argus.poll()
        line = argus.stdout.readline().decode("utf-8")
        if line == '' or line == '\n':
            print('Finished')
            sys.exit(1)
        else:
            line = line[:-1]
            pkt_data = norm.normalise(line, label=0)
            out += ",".join(str(x) for x in pkt_data[0]) + "\n"
            numlines += 1
            print('Processed ' + str(numlines) + ' records, Ctrl+C to stop', end='\r')
except (KeyboardInterrupt, SystemExit):
    sys.stdout.write("\033[K")
    print('\nProcessed ' + str(numlines) + ' records, flushing to file')
    with open('data/training.learned.csv', 'w') as fh:
        fh.writelines((str(numlines) + ",9,0,0,0,0,0,0,0,0\n", out))
