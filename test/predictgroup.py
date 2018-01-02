import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
import numpy as np
import struct

feature_columns = [tf.contrib.layers.real_valued_column("", dimension=9)]

classifier = tf.contrib.learn.DNNClassifier(feature_columns=feature_columns,
                                            hidden_units=[10, 20, 10],
                                            n_classes=2,
                                            model_dir="../data/traffic_model")


def get_input():
    arr = [
        [9.004991,2,3277,1,25,1,3,186,186],
        [0.144585,2,2087,1,80,159,9,3272,1729],
        [9.012734,2,4108,1,25,1,3,186,186],
        [9.013404,2,2010,1,4506,1,3,186,186],
        [8.943968,2,4432,1,25,1,3,186,186],
        [9.013024,2,3361,1,25,1,3,186,186],
        [9.029091,2,2978,1,25,1,3,186,186],
        [36.854553,2,4597,1,80,3,33,5896,1123],
        [9.01333,2,3048,1,25,1,3,186,186],
        [9.013199,2,3563,1,25,1,3,186,186]
    ]
    x = tf.constant(arr)
    return x

in_pred = classifier.predict_classes(input_fn=get_input)
for p in in_pred:
    print(p)
