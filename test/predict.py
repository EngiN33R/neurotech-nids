import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
import numpy as np
import socket
import struct

feature_columns = [tf.contrib.layers.real_valued_column("", dimension=9)]

classifier = tf.contrib.learn.DNNClassifier(feature_columns=feature_columns,
                                            hidden_units=[10, 20, 10],
                                            n_classes=2,
                                            model_dir="../data/traffic_model")

print("Creating and binding socket...")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 1111))

def get_input():
    recv = sock.recv(1024)
    print("Received datagram, length " + str(len(recv)))
    arr = [[struct.unpack("=dHHHHHHHH", recv)]]
    print(arr)
    x = tf.constant(arr)

    return x

while True:
    in_pred = classifier.predict_classes(input_fn=get_input)
    for p in in_pred:
        print(p)
