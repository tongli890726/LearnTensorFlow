import tensorflow as tf
from  tensorflow import keras
from  tensorflow.keras import datasets, layers, optimizers, Sequential, metrics
import  os
import ssl


'''
这一节，主要学习metrics.
1、创建meter.
    acc_meter = metrics.Accuracy() 新建准确度meter
    loss_meter = metrics.Mean()     新建平均值(损失值)meter
    
2、更新meter
    acc_meter.update_state(y, pred)  更新准确度meter
    loss_meter.update_state(loss) 更新平均值(损失值)meter
    
    
3、读取meter
    acc_meter.result().numpy()
    loss_meter.result().numpy()
    

3、重置meter
    acc_meter.reset_states()    重置准确度meter
    loss_meter.reset_states()   重置平均值(损失值)meter
    


'''




# 全局取消ssl证书验证
ssl._create_default_https_context = ssl._create_unverified_context

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 对数据预处理函数
def preprocess(x, y):
    x = tf.cast(x, dtype=tf.float32) / 255. # 转换到0~1的范围
    y = tf.cast(y, dtype=tf.int32)
    return x, y

batchSize = 128 # 设置batch的大小


#导入数据集 x是每个点的alpha值
(x, y), (x_test, y_test) = datasets.mnist.load_data()

print(x.shape, y.shape)  # (60k, 28, 28) (60k)

# 构造数据集
db = tf.data.Dataset.from_tensor_slices((x,y))

# 对数据预处理.map将处理后的数据，映射到原来的db数据集中.
# shuffle().打乱数据集。数值越大，混乱程度越大
# batch # 将数据分成128一组的.一次喂入神经网络的数据量
db = db.map(preprocess).shuffle(60000).batch(batchSize).repeat(10)


# 对test数据集同样的预处理
db_test = tf.data.Dataset.from_tensor_slices((x_test,y_test))
db_test = db_test.map(preprocess).batch(batchSize) # 测试集不用shuffle



# 进行5层变换。构建出5层的全连接层
# sequential容器，可以将多个Dense层包含起来，可以逐次进行
network = Sequential([
    # x的shape=(b,784) w(784,256)
    # 第一层 输出维度是256，推断，kernel(即w)为[784, 256]，这样x@w才是[b, 256]
    layers.Dense(256, activation=tf.nn.relu), # [b, 784] -> [b,256]
    # 第一层 输出维度是128。kernel(即w)为[256, 128]
    layers.Dense(128, activation=tf.nn.relu),# [b, 256] -> [b,128]
    layers.Dense(64, activation=tf.nn.relu),# [b, 128] -> [b,64]
    layers.Dense(32, activation=tf.nn.relu),# [b, 64] -> [b,32]
    layers.Dense(10)# [b, 32] -> [b,10]
])
# 输入的维度，28*28=784,即和上面的第一层联系起来
network.build(input_shape=[None, 28*28])
network.summary() # 调试功能


# 声明优化器
# 他的作用是更新优化参数，即w = w - lr*grad这样更新
optimizer = optimizers.Adam(lr=0.01)

# 第一步，新建meter
acc_meter = metrics.Accuracy() # 新建一个准确度的meter
loss_meter = metrics.Mean()    # 新建一个平均值(损失值)的meter


# 遍历数据集.由于db一共是60k个数据，而batch是128,所以一共循环60k/128次
for step, (x, y) in enumerate(db):
    # x:[b, 28, 28],其中b=128,因为batch是128
    # y:[b]

    with tf.GradientTape() as tape:

        # 对x进行维度变换
        x = tf.reshape(x, [-1, 28*28]) # [b, 28, 28] -> [b, 784]


        # 将x传递给构造好的全连接层，这样x[b, 784]->[b, 10]
        out = network(x)
        y_onehot = tf.one_hot(y, depth=10)

        #利用crossEntropy(交叉熵)求loss
        loss_ce = tf.losses.categorical_crossentropy(y_onehot, out, from_logits=True)
        loss_ce = tf.reduce_mean(loss_ce)
        # 第二步。更新平均值(损失值)meter
        loss_meter.update_state(loss_ce)



    #计算梯度。 trainable_variables就是全连接层的参数，即w1 b1 w2 b2....
    grads = tape.gradient(loss_ce, network.trainable_variables)
    # 更新trainable_variables，即w1 b1 w2 b2..这些参数。更新方法就是上面声明的优化器
    optimizer.apply_gradients(zip(grads, network.trainable_variables))

    if step % 100 == 0:
        # 第三步，读取meter
        print(step, 'loss:', loss_meter.result().numpy())
        # 第四步，重置平均值(损失值)meter
        loss_meter.reset_states()



    # 测试

    if step % 500 == 0:

        total_correct = 0. # 总分数，也是正确的个数
        total = 0 #总个数
        # 重置准确度meter
        acc_meter.reset_states()

        for step, (x,y) in enumerate(db_test):

            #对x进行维度转换
            # x: [b, 28, 28] => [b, 784]
            # y: [b]
            x = tf.reshape(x ,[-1, 28*28])

            # x[b, 784]->[b, 10]
            out = network(x)
            # 概率最大所在的下标,即在10这个维度，取最大的下标。 [b,10]->[b]
            pred = tf.argmax(out, axis=1) # int64
            #转换成int32
            pred = tf.cast(pred, dtype=tf.int32)

            # 将预测的和真实值相比较
            correct = tf.equal(pred, y) # 长度是b.每个参数是true或者false
            # 将true变成1，false是0.然后相加，得到分数.
            # cast将bool转换成int32
            total_correct += tf.reduce_sum(tf.cast(correct, dtype=tf.int32)).numpy()

            total_correct += int(correct)
            # 每循环一次就是一次batch,x.shape[0]就是batch的大小
            total += x.shape[0]

            # 更新准确度meter
            acc_meter.update_state(y, pred)
            # 读取准确度meter
            print(step, 'test acc', total_correct/total, acc_meter.result().numpy())

