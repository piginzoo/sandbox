import tensorflow as tf
from keras import backend as K
from keras import utils 


# a = tf.constant([1, 2, 3,4, 5, 6],shape=(2,3))
# b = tf.constant([7, 8, 9,10,11,12],shape=(2,3))
# c = tf.constant([0,1,2])
# one_hots = utils.to_categorical(c,3)

# t = tf.expand_dims(tf.constant([1,2,3,4]),1)
value = tf.expand_dims(tf.constant([1,3,2,4,0]),1)
index = tf.expand_dims(tf.constant([0,1,2,3,4]),1)
concated = tf.concat([index,value],1)
one_hots = tf.sparse_to_dense(concated, output_shape=(5,10), sparse_values=1.0, default_value=0.0)
sess = tf.Session()
print(sess.run(one_hots))
