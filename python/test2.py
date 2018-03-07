import numpy as np
a = np.array([1,2,3])
b= np.array([4,5,6])
c= np.array([1,2,3,4,5,6,7,8,9])
np.stack(a,b,axis=0)
np.stack(a,b,axis=1)
np.reshape(c,(-1,3))