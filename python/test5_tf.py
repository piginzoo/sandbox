#-*- coding:utf-8 -*- 
import tensorflow as tf
import numpy as np


def main(_):
	sess = tf.InteractiveSession()

	_num_symbol = 3
	_charset_num = 3

	y_pred = tf.placeholder(tf.int64, [None,9]) 
	y_true = tf.placeholder(tf.int64, [None,9])

	predict = tf.reshape(y_pred, [-1, _num_symbol, _charset_num])
	predict = tf.Print(predict,[predict,tf.shape(predict)],"predict")
	
	max_idx_p = tf.argmax(predict, 2)#这个做法牛逼，不用再做stack和reshape了，2，是在Charset那个维度上
	max_idx_p = tf.Print(max_idx_p,[max_idx_p,tf.shape(max_idx_p)],"max_idx_p")

	max_idx_l = tf.argmax(tf.reshape(y_true, [-1, _num_symbol, _charset_num]), 2)
	max_idx_l = tf.Print(max_idx_l,[max_idx_l,tf.shape(max_idx_l)],"max_idx_l")


	'''max_idx_l结果为：
		[
			[[1,0,0],
			 [1,0,0],
			 [0,1,0]],
			[[0,1,0],
			 [1,0,0],
			 [0,1,0]],
			[[0,1,0],
			 [1,0,0],
			 [0,1,0]]
		]
	'''

	correct_pred = tf.equal(max_idx_p, max_idx_l)
	correct_pred = tf.Print(correct_pred,[correct_pred,tf.shape(correct_pred),''],"correct_pred")
	#结果是[[0,1,1],[0,1,1]]

	# _result = [each.all() for each in correct_pred]
	_result = tf.map_fn(fn=lambda e: tf.reduce_all(e),elems=correct_pred,dtype=tf.bool)

	result = tf.reduce_mean(tf.cast(_result, tf.float32))
	result = tf.Print(result,[result,tf.shape(result),''],"result")

	tf.global_variables_initializer().run()

	__y_pred = np.array([
		[0.1,1.2,12, 1,0.1,0.5, 0.1,1.3,0.3],
		[0.1,12,1.2, 1,0.1,0.5, 0.1,1.3,0.3],
		[0.1,12,1.2, 1,0.1,0.5, 0.1,1.3,0.3],
		[0.1,12,1.2, 1,0.1,0.5, 0.1,1.3,0.3]])#010,100,010
	__y_true = np.array([
		[0,0,1,0,1,0,0,1,0],
		[0,1,0,1,0,0,0,1,0],
		[0,1,0,1,0,0,0,1,0],
		[0,1,0,1,0,0,0,1,0]])

	print_result = tf.Print(result,[result],message="结果是：")

	sess.run(print_result,feed_dict={y_pred: __y_pred,
	                           y_true: __y_true});

	x=tf.constant([2,3,4,5])
	x=tf.Print(x,[x,x.shape,'any thing i want'],message='Debug message:',summarize=100)  
	sess.run(x)

	sess.close()

if __name__ == '__main__':
  tf.app.run(main=main)
