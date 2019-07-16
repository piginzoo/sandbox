import tensorflow as tf
import cv2,numpy as np

with tf.Graph().as_default():
    a = tf.constant([[1,2],[3,4]],name='a') 
    b = tf.tile(a,[3,3])
    sess = tf.Session()
    print(sess.run(b))