# Capture module
#
# This module connects to a running argus instance to process
# current network traffic on the network. Currently slow
# because of chokepoints related to DNN processing time.

import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
import numpy as np
import sys
import subprocess
import time
import normalise as norm

# Specify that all features have real-value data
feature_columns = [tf.contrib.layers.real_valued_column("", dimension=9)]

# Build 3 layer DNN with 10, 20, 10 units respectively.
classifier = tf.contrib.learn.DNNClassifier(feature_columns=feature_columns,
                                            hidden_units=[10, 20, 10],
                                            n_classes=2,
                                            model_dir="data/traffic_model")

argus = subprocess.Popen("ra -n -L -1 -S 127.0.0.1:561 -c \",\" -u -s \"dur proto:10 sport dir dport state pkts bytes sbytes\" 2> /dev/null",stdout=subprocess.PIPE,shell=True)

def get_input():
    argus.poll()
    line = argus.stdout.readline().decode("utf-8")
    if line == '' or line == '\n':
        print('Finished')
        sys.exit(1)
    else:
        line = line[:-1]
        #fields = line.split(',')
        #pkt_data = [[float(fields[0]), protos[fields[1]], (0 if fields[2] == '' else int(fields[2])), reps[fields[3]], (0 if fields[4] == '' else int(fields[4])), states[fields[5]], int(fields[6]), int(fields[7]), int(fields[8])]]
        pkt_data = norm.normalise(line)
        #print(pkt_data)
        x = tf.constant(pkt_data)
        return x

numpackets = 0
abnormal = 0
try:
    while True:
        in_pred = classifier.predict_classes(input_fn=get_input)
        for p in in_pred:
            sys.stdout.write("\033[K")
            if (p == 1):
                print("Abnormal packet detected!")
                abnormal += 1
            numpackets += 1
            print('Processed ' + str(numpackets) + ' packets, ' + str(abnormal) + ' abnormal, Ctrl+C to stop', end='\r')
except (KeyboardInterrupt, SystemExit):
    sys.stdout.write("\033[K")
    print('Processed ' + str(numpackets) + ' packets, ' + str(abnormal) + ' abnormal, Ctrl+C to stop', end='\r')
