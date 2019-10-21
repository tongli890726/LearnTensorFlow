'''
一般会将数据集分成三份，
1、train set 训练数据集。用于训练，更新参数
2、val set   验证数据集。用户自我验证，从验证结果可以挑选合适的模型
3、test set  测试数据集。最后出了产品，客户用户测试的，一般开发过程拿不到

而现在的数据集都是两部分，train和test.所以我们将train分成两部分，train和val

'''

import tensorflow as tf
from tensorflow.keras import datasets, layers, optimizers, Sequential, metrics


def preprocess(x, y):
    """
    x is a simple image, not a batch
    """
    x = tf.cast(x, dtype=tf.float32) / 255.
    x = tf.reshape(x, [28 * 28])
    y = tf.cast(y, dtype=tf.int32)
    y = tf.one_hot(y, depth=10)
    return x, y


batchsz = 128
# 获取数据集。
(x, y), (x_test, y_test) = datasets.mnist.load_data()
print('datasets:', x.shape, y.shape, x.min(), x.max())

# 生成60k个数。随机打乱，保证下面取前50k的随机性。这60k个数，相当于索引
idx = tf.range(60000)
idx = tf.random.shuffle(idx)

# 将x和y 的前50k的数据当做trainset。
# gather.一个一维的索引数组，将张量中对应索引的向量提取出来.即通过索引取出数据集中的张量
x_train, y_train = tf.gather(x, idx[:50000]), tf.gather(y, idx[:50000])
# 将x和y 的后10k的数据当做valset
x_val, y_val = tf.gather(x, idx[-10000:]), tf.gather(y, idx[-10000:])
print(x_train.shape, y_train.shape, x_val.shape, y_val.shape)
# 将trainset valset testset做预处理
db_train = tf.data.Dataset.from_tensor_slices((x_train, y_train))
db_train = db_train.map(preprocess).shuffle(50000).batch(batchsz)

db_val = tf.data.Dataset.from_tensor_slices((x_val, y_val))
db_val = db_val.map(preprocess).shuffle(10000).batch(batchsz)

db_test = tf.data.Dataset.from_tensor_slices((x_test, y_test))
db_test = db_test.map(preprocess).batch(batchsz)

sample = next(iter(db_train))
print(sample[0].shape, sample[1].shape)

network = Sequential([layers.Dense(256, activation='relu'),
                      layers.Dense(128, activation='relu'),
                      layers.Dense(64, activation='relu'),
                      layers.Dense(32, activation='relu'),
                      layers.Dense(10)])
network.build(input_shape=(None, 28 * 28))
network.summary()

network.compile(optimizer=optimizers.Adam(lr=0.01),
                loss=tf.losses.CategoricalCrossentropy(from_logits=True),
                metrics=['accuracy']
                )

network.fit(db_train, epochs=6, validation_data=db_val, validation_freq=2)

print('Test performance:')

# 利用testSet做测试
network.evaluate(db_test)

# 利用训练的结果，得出最终的预测
sample = next(iter(db_test))
x = sample[0]
y = sample[1]  # one-hot
pred = network.predict(x)  # [b, 10]
# convert back to number
y = tf.argmax(y, axis=1)
pred = tf.argmax(pred, axis=1)

print(pred)
print(y)


