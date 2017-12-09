# Testing module
#
# This module tests the DNN against a test dataset to determine
# its accuracy.

import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='NeuroTech testing module.')
parser.add_argument('-d', '--dataset', type=str, default="data/merged.testing.contrib.csv", help='specify the data set to train on (default data/merged.training.contrib.csv).')
args = parser.parse_args()

TRAFFIC_TESTING = os.path.join(os.path.dirname(__file__), args.dataset)

test_set = tf.contrib.learn.datasets.base.load_csv_with_header(
    filename=TRAFFIC_TESTING,
    target_dtype=np.int,
    features_dtype=np.float32,
    target_column=9)

# Specify that all features have real-value data
feature_columns = [tf.contrib.layers.real_valued_column("", dimension=9)]

# Build 3 layer DNN with 10, 20, 10 units respectively.
classifier = tf.contrib.learn.DNNClassifier(feature_columns=feature_columns,
                                            hidden_units=[10, 20, 10],
                                            n_classes=2,
                                            model_dir="data/traffic_model")
# Define the test inputs
def get_test_inputs():
    x = tf.constant(test_set.data)
    y = tf.constant(test_set.target)

    return x, y

# Evaluate accuracy.
test_eval = classifier.evaluate(input_fn=get_test_inputs,
                                     steps=1)

print("\nTest Accuracy: {0:f}\n".format(test_eval["accuracy"]))
print(test_eval)
