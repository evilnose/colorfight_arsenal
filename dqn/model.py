import tensorflow as tf
from tensorflow.layers import conv2d, dense
from tensorflow.contrib.layers import flatten

from dqn.data import INPUT_HEIGHT, INPUT_WIDTH, INPUT_CHANNELS, N_PLAYERS

CONV_FILTERS = [32, 64, 64]
CONV_KERNEL_SIZES = [(4, 4), (4, 4), (3, 3)]  # TODO add a bigger kernel sizes at front (e.g. 10*10, 20*20)
CONV_STRIDES = [2, 2, 1]
CONV_PADDINGS = ['SAME'] * 3
CONV_ACTIVATIONS = [tf.nn.relu] * 3
HIDDEN_SIZE = 1024
HIDDEN_ACTIVATION = tf.nn.relu
N_OUTPUTS = 903  # pass? + attack? + build base? + cells
K_INIT = tf.variance_scaling_initializer()


def build_overall_graph():
    x_state = tf.placeholder(tf.float32, shape=[None, INPUT_HEIGHT, INPUT_WIDTH, INPUT_CHANNELS])
    q_values = []
    trainable_params = []
    for i in range(N_PLAYERS):
        scope_name = 'q_networks/{}'.format(i)
        q_values.append(q_network(x_state, scope=scope_name))
        trainable_params.append(tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=scope_name))
    # TODO make copy operation here


def q_network(state, scope):
    x = state
    with tf.variable_scope(scope):
        for filters, kernel_size, strides, padding, activation in zip(
                CONV_FILTERS, CONV_KERNEL_SIZES, CONV_STRIDES, CONV_PADDINGS, CONV_ACTIVATIONS):
            x = conv2d(x, filters=filters, kernel_size=kernel_size, strides=strides,
                       padding=padding, activation=activation)
        conv_flat = flatten(x)
        hidden = dense(conv_flat, HIDDEN_SIZE, activation=HIDDEN_ACTIVATION, kernel_initializer=K_INIT)
        outputs = dense(hidden, N_OUTPUTS, kernel_initializer=K_INIT)

    return outputs


def loss_fn():
    # TODO
    pass


