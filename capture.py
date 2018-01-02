import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
import numpy as np
import sys
import subprocess
import datetime
import psycopg2
import psycopg2.extras
import copy
import argparse
import normalise as norm

conn = psycopg2.connect(
    "dbname=neurotech user=neurotech password=neurotech host=127.0.0.1")
cur = conn.cursor()
psycopg2.extras.register_composite('packet', cur)

parser = argparse.ArgumentParser(description='NeuroTech testing module.')
parser.add_argument('-b', '--batch', type=int, default=100,
                    help='specify the batch size for neural processing.')
args = parser.parse_args()

# Specify that all features have real-value data
feature_columns = [tf.contrib.layers.real_valued_column("", dimension=9)]

# Build 3 layer DNN with 10, 20, 10 units respectively.
classifier = tf.contrib.learn.DNNClassifier(feature_columns=feature_columns,
                                            hidden_units=[10, 20, 10],
                                            n_classes=2,
                                            model_dir="data/traffic_model")

argus = subprocess.Popen(
    "ra -n -L -1 -S 127.0.0.1:561 -c \",\" -u -s \"dur proto:10 sport dir dport state pkts bytes sbytes\" -- ip 2> /dev/null", stdout=subprocess.PIPE, shell=True)

data_bus = [[]]
numpackets = 0
abnormal = 0
batches = 0


def process_record():
    global numpackets

    bus_dest = []
    if len(data_bus) == 0 or len(bus_dest) >= args.batch:
        data_bus.append(bus_dest)
    else:
        bus_dest = data_bus[len(data_bus) - 1]

    argus.poll()
    line = argus.stdout.readline().decode("utf-8")
    if line == '' or line == '\n':
        print('Finished')
        sys.exit(1)
    else:
        line = line[:-1]
        pkt_data = norm.normalise(line)
        pkt_data.append(datetime.datetime.utcnow())
        bus_dest.append(pkt_data)
        numpackets += 1


def insert_records(data):
    rows = []
    for d in data:
        t = (d[9], tuple(d[:9]), d[10])
        rows.append(t)
    psycopg2.extras.execute_values(
        cur, "INSERT INTO packets (timestamp, packet, label) VALUES %s", rows)
    conn.commit()


def get_input(data):
    pkt = copy.deepcopy(data)
    for p in pkt:
        p.pop(9)
    return lambda: tf.constant(pkt)


def status(end='\r'):
    sys.stdout.write("\033[K")
    print('Processed ' + str(numpackets) + ' packets (' + str(batches) + ' batches), ' +
          str(abnormal) + ' abnormal detections, Ctrl + C to stop', end=end)


try:
    while True:
        process_record()
        status()
        if len(data_bus[0]) >= args.batch:
            bus_src = data_bus.pop(0)
            in_pred = classifier.predict_classes(input_fn=get_input(bus_src))
            i = 0
            for p in in_pred:
                sys.stdout.write("\033[K")
                bus_src[i].append(int(p))
                if (p == 1):
                    abnormal += 1
                i += 1

            insert_records(bus_src)
            batches += 1
        status()
except (KeyboardInterrupt, SystemExit):
    bus_src = data_bus.pop(0)
    in_pred = classifier.predict_classes(input_fn=get_input(bus_src))
    i = 0
    for p in in_pred:
        sys.stdout.write("\033[K")
        bus_src[i].append(int(p))
        if (p == 1):
            print("Abnormal packet detected!")
            abnormal += 1
        numpackets += 1
        i += 1

    insert_records(bus_src)
    batches += 1
    status('\n')
except:
    print('')
    raise sys.exc_info()[1]
