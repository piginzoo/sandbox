from keras.layers import LSTM,Input, GRU, Dense, Concatenate, TimeDistributed, Bidirectional
from keras.models import Model,Sequential
import tensorflow as tf
import cv2,numpy as np
import numpy
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.utils import np_utils

# 准备数据
# x = ['xxxxx','xxxxx','xxxxx']
# y = ['yyyyy','yyyyy','yyyyy']
# x => y 是一个简单的m:m预测，而不是一个m:n的seq
numpy.random.seed(7)
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
char_to_int = dict((c, i) for i, c in enumerate(alphabet))
int_to_char = dict((i, c) for i, c in enumerate(alphabet))
seq_length = 5
dataX = []
dataY = []
for i in range(0, len(alphabet) - seq_length, 1):
    seq_in =  alphabet[i:i + seq_length]
    seq_out = alphabet[i + seq_length]
    dataX.append([char_to_int[char] for char in seq_in])
    dataY.append(char_to_int[seq_out])
    print (seq_in, '->', seq_out)
X = numpy.reshape(dataX, (len(dataX), seq_length, 1))
X = X / float(len(alphabet))
y = numpy.reshape(dataY, (len(dataY), 1, 1))
y = np_utils.to_categorical(y)

# 构建模型，使用了Bidirectional+GRU，做编码器encoder
inputs = Input(shape=list(X.shape)[1:3], name='inputs')
encoder_bi_gru = Bidirectional(GRU(10,#写死一个隐含神经元数量
                                    return_sequences=True,
                                    return_state=True,
                                    name='encoder_gru'),
                            name='bidirectional_encoder')
encoder_out, encoder_fwd_state, encoder_back_state = encoder_bi_gru(inputs)


# 构建模型，使用了GRU，做解码器decoder
decoder_inputs = Input(shape=(5, 20), name='decoder_inputs')
decoder_gru = GRU(20, return_sequences=True, return_state=True, name='decoder_gru')
decoder_out, decoder_state = decoder_gru(decoder_inputs, initial_state=Concatenate(axis=-1)([encoder_fwd_state, encoder_back_state]))

# 最后输出
dense = Dense(25, activation='softmax', name='softmax_layer')
dense_time = TimeDistributed(dense, name='time_distributed_layer')
decoder_pred = dense_time(decoder_out)


model = Model(inputs=inputs, outputs=decoder_pred)
model.compile(loss='categorical_crossentropy', optimizer='adam')
model.fit(X, y, epochs=1, batch_size=2, verbose=2)
