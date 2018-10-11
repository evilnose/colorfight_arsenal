import tensorflow as tf
import os

CHECKPOINT_PATH = './dqn_saved.ckpt'


def train(game):
    init = tf.global_variables_initializer()
    saver = tf.train.Saver()
    with tf.Session() as sess:
        if os.path.isfile(CHECKPOINT_PATH):
            saver.restore(sess, CHECKPOINT_PATH)
        else:
            init.run()

