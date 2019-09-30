'''
broadcasting
张量维度扩张的手段，在某一个维度上重复n多次，但是没有真正的复制一个数据
两个维度不同的tensor运算
1、如果维度不一致，先复制维度使之相等，如：A是[4, 2, 3]. B是[2, 3]。先将B复制成[1,2,3]
2、维度一直了，看看每个维度的shape一样不，如果不一样，只有shape是1的可以复制成相等。如：把B复制成[4,2,3]
这个复制并不是复制一个真正的数据，是一个虚拟的


几个例子
1、A:[4,32,14,14]  B[1,32,1,1]
B可以复制成A

2、A:[4,32,14,14]  B[14,14]
B->[1,1,14,14]->[4,32,14,14],B可以复制成A

3、A:[4,32,14,14]  B[2,32,14,14]
B不能复制成A。因为A的第一维是4，B的第一维是2，都不是1

'''

import tensorflow as tf

a = tf.random.normal([4, 32, 32, 3])
b = tf.random.normal([3])

print(a.shape)
print(b.shape)

c = a + b # [4,32,32,3] + [3] = [4,32,32,3] 是因为b自动利用broadcasting变成了[4,32,32,3]
print(c.shape)

# 利用broadcast_to 将其扩张为想要的维度。
b1 = tf.broadcast_to(b, [4,32,32,3])
print(b1.shape)








