import tensorflow as tf
x = [[3.]]
m = tf.matmul(x, x)
print(m.numpy())
a = tf.constant([[1,9],[3,6]])
print(a)
b = tf.add(a, 2)
print(b)
print(a*b)

@tf.function
def simple_nn_layer(x, y):
    return tf.nn.relu(tf.matmul(x, y))


x = tf.random.uniform((3, 3))
y = tf.random.uniform((3, 3))

z=simple_nn_layer(x, y)
print("z=",z)