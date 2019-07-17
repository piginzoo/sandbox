from keras.layers import LSTM,Input, GRU, Dense, Concatenate, TimeDistributed, Bidirectional
from keras.models import Model,Sequential
import tensorflow as tf
import cv2,numpy as np


# Naive LSTM to learn one-char to one-char mapping
import numpy
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.utils import np_utils
# fix random seed for reproducibility
numpy.random.seed(7)
# define the raw dataset
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# create mapping of characters to integers (0-25) and the reverse
char_to_int = dict((c, i) for i, c in enumerate(alphabet))
int_to_char = dict((i, c) for i, c in enumerate(alphabet))
# prepare the dataset of input to output pairs encoded as integers
seq_length = 5
dataX = []
dataY = []
for i in range(0, len(alphabet) - seq_length, 1):
    seq_in = alphabet[i:i + seq_length]
    seq_out = alphabet[i + seq_length]
    dataX.append([char_to_int[char] for char in seq_in])
    dataY.append(char_to_int[seq_out])
    print (seq_in, '->', seq_out)

# reshape X to be [samples, time steps, features]
print(dataX)
X = numpy.reshape(dataX, (len(dataX), seq_length, 1))
# normalize
X = X / float(len(alphabet))
print(X.shape)
print((X.shape[1],X.shape[2]))

# one hot encode the output variable
y = np_utils.to_categorical(dataY)
y = numpy.reshape(y,(len(y),1,26))
print(list(X.shape)[1:3])
inputs = Input(shape=list(X.shape)[1:3], name='inputs')

# create and fit the model
bi_gru = Bidirectional(GRU(6,#写死一个隐含神经元数量
                                    return_sequences=False,
                                    return_state=True,
                                    name='encoder_gru'),
                            name='bidirectional_encoder')
outputs , _ , _ = bi_gru(inputs)

print(tf.shape(outputs))

dense = Dense(26, activation='softmax', name='softmax_layer')
dense_time = TimeDistributed(dense, name='time_distributed_layer')
print(tf.shape(outputs))

decoder_pred = dense_time(outputs)
model = Model(inputs=inputs, outputs=decoder_pred)
model.compile(loss='categorical_crossentropy', optimizer='adam')
# , metrics=['accuracy'])
model.fit(X, y, epochs=1, batch_size=2, verbose=2)
