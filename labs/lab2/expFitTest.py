from pylab import *
from scipy.optimize import curve_fit

x = np.array([17848, 4984.0, 2276, 1299, 822])
y = np.array([40, 80, 120, 160, 200])

def func(x, a, b, c, d):
    return a*np.exp(-c*(x-b))+d

popt, pcov = curve_fit(func, x, y, [100,400,0.001,0])
print(popt)

plot(x,y)
x=linspace(400,6000,10000)
plot(x,func(x,*popt))
show()