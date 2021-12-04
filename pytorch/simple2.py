import pdb

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(32*32, 512)  # an affine operation: y = Wx + b
        self.bn1 = nn.BatchNorm1d(512),
        self.fc2 = nn.Linear(512, 2)
        self.bn2 = nn.BatchNorm1d(2)

    def forward(self, x):
        x = self.fc1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.fc2(x)
        x = self.bn2(x)
        return x


net = Net()
print("网络：")
print(net)
print("参数：")
params = list(net.parameters())
for p in params:
    print(p.shape)

print("输入：")
input = Variable(torch.randn(1, 32*32))
print(input)

print("前向")
out = net(input)  # <--- 输入x=input

print("网络梯度全部初始化为0")
net.zero_grad()  # 对所有的参数的梯度缓冲区进行归零

criterion = nn.MSELoss()
y_label = Variable(torch.range(1, 2))  # <--- 输出y=y_label
loss = criterion(out, y_label)

print('conv1.bias.grad before backward')
print(net.conv1.bias.grad)
loss.backward()
print('conv1.bias.grad after backward')
print(net.conv1.bias.grad)

# create your optimizer
optimizer = optim.SGD(net.parameters(), lr=0.01)
optimizer.zero_grad()  # zero the gradient buffers

print('训练开始.....')
for epoch in range(2):  # loop over the dataset multiple times

    running_loss = 0.0
    for i in range(3):
        input = Variable(torch.randn(1, 32 * 32))
        output = net(input)
        loss = criterion(output, y_label)
        loss.backward()
        optimizer.step()  # Does the update，更新

        # print statistics
        # pdb.set_trace()
        running_loss += loss.data.item()
        print('[%d, %5d] loss值: %.3f' % (epoch + 1, i + 1, running_loss / 2000))
        running_loss = 0.0
print('训练结束.....')

print("尝试预测：")
outputs = net(Variable(torch.randn(1, 1, 32, 32)))
_, predicted = torch.max(outputs.data, 1)
print('预测结果: %r' % predicted)