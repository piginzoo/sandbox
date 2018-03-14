#-*- coding:utf-8 -*-  
from module1.module11 import test11
import module1.module12.test12
# import module1.module12.test12.Class_Test12 不行！
test11.test()
#ct12 = test12.Class_Test12() 不行！
ct12 = module1.module12.test12.Class_Test12()