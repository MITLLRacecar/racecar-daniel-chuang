import numpy as np
from pylab import *

y = [10, 20, 30, 40, 80, 120, 160, 200]
x = [37260, 28458, 27349, 17848, 4984.0, 2276, 1299, 822]

degrees = np.polyfit(x, y, 6)

def areaToDistance(area: float) -> int:
    return np.polyval(degrees, area)

plot(x, y)
x_range = np.array(range(800, 37260))
plot(x_range, areaToDistance(x_range))
show()


# Presentation Notes:
# Key Points: areaToDistance: 53, remap_range: 61, Porp_control: 163
# The final "dip" is really sharp because you start losing vision of the cone!