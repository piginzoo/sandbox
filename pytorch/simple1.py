import pdb

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 6, 5)  # 1 input image channel, 6 output channels, 5x5 square convolution kernel
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)  # an affine operation: y = Wx + b
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = F.max_pool2d(F.relu(self.conv1(x)), (2, 2))  # Max pooling over a (2, 2) window
        x = F.max_pool2d(F.relu(self.conv2(x)), 2)  # If the size is a square you can only specify a single number
        x = x.view(-1, self.num_flat_features(x))
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

    def num_flat_features(self, x):
        size = x.size()[1:]  # all dimensions except the batch dimension
        num_features = 1
        for s in size:
            num_features *= s
        return num_features


net = Net()
print("网络：")
print(net)
print("参数：")
params = list(net.parameters())
for p in params:
    print(p.shape)

print("输入：")
input = Variable(torch.randn(1, 1, 32, 32))
print(input)

print("前向")
out = net(input)  # <--- 输入x=input

print("网络梯度全部初始化为0")
net.zero_grad()  # 对所有的参数的梯度缓冲区进行归零

criterion = nn.MSELoss()
y_label = Variable(torch.range(1, 10))  # <--- 输出y=y_label
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
        input = Variable(torch.randn(1, 1, 32, 32))
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
