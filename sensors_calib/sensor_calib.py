# V:
# Sensor 0 (leftmost), pi/2
y0 = [560.0, 499.0, 445.0, 414.0, 383.0, 339.0, 315.0, 291.0, 278.0, 259.0]
max0 = 30
# Sensor 1, pi/4
y1 = [548.0, 486.0, 440.0, 400.0, 365.0, 336.0, 313.0, 293.0, 274.0, 257.0]
max1 = 23
# Sensor 2 (front), 0
y2 = [545.0, 477.0, 438.0, 390.0, 355.0, 326.0, 303.0, 283.0, 261.0, 247.0]
max2 = 30
# Sensor 3, -pi/4
y3 = [548.0, 499.0, 452.0, 429.0, 382.0, 337.0, 314.0, 290.0, 276.0, 257.0]
max3 = 18
#Note: sensor 3 was moved to analog port 10, since the other one was giving us bad results
# Sensor 4 (rightmost), -pi/2
y4 = [539.0, 475.0, 421.0, 378.0, 343.0, 318.0, 291.0, 279.0, 254.0, 242.0]
max4 = 20

# 1/d:
x = [1.0/(4.0-0.625), 1.0/(4.5-0.625), 1.0/(5.0-0.625), 1.0/(5.5-0.625), 1.0/(6.0-0.625), 1.0/(6.5-0.625), 1.0/(7.0-0.625), 1.0/(7.5-0.625), 1.0/(8.0-0.625), 1.0/(8.5-0.625)]

# from math import *
# import Gnuplot, Gnuplot.funcutils

# p0 = Gnuplot.Gnuplot()
# p0.title("Voltage (0-1024) vs 1/d (1.0/8.5 - 1.0/4.5)")
# p0("set xtics\n");
# p0("set ytics\n");
# p0("set style data linespoints\n");
# p0("set grid\n");

# p1 = Gnuplot.Gnuplot()
# p1.title("Voltage (0-1024) vs 1/d (1.0/8.5 - 1.0/4.5)")
# p1("set xtics\n");
# p1("set ytics\n");
# p1("set style data linespoints\n");
# p1("set grid\n");

# p2 = Gnuplot.Gnuplot()
# p2.title("Voltage (0-1024) vs 1/d (1.0/8.5 - 1.0/4.5)")
# p2("set xtics\n");
# p2("set ytics\n");
# p2("set style data linespoints\n");
# p2("set grid\n");

# p3 = Gnuplot.Gnuplot()
# p3.title("Voltage (0-1024) vs 1/d (1.0/8.5 - 1.0/4.5)")
# p3("set xtics\n");
# p3("set ytics\n");
# p3("set style data linespoints\n");
# p3("set grid\n");

# p4 = Gnuplot.Gnuplot()
# p4.title("Voltage (0-1024) vs 1/d (1.0/8.5 - 1.0/4.5)")
# p4("set xtics\n");
# p4("set ytics\n");
# p4("set style data linespoints\n");
# p4("set grid\n");


# p0.plot(Gnuplot.Data(x,y0))
# p1.plot(Gnuplot.Data(x,y1))
# p2.plot(Gnuplot.Data(x,y2))
# p3.plot(Gnuplot.Data(x,y3))
# p4.plot(Gnuplot.Data(x,y4))

# p0.hardcopy("sensor_0.ps", color=1)
# p1.hardcopy("sensor_1.ps", color=1)
# p2.hardcopy("sensor_2.ps", color=1)
# p3.hardcopy("sensor_3.ps", color=1)
# p4.hardcopy("sensor_4.ps", color=1)

from numpy import arange,array,ones,linalg
from pylab import plot,show

xi = array(x)
A = array([x, ones(10)])
# linearly generated sequence
m0,b0 = linalg.lstsq(A.T,y0)[0]
m1,b1 = linalg.lstsq(A.T,y1)[0]
m2,b2 = linalg.lstsq(A.T,y2)[0]
m3,b3 = linalg.lstsq(A.T,y3)[0]
m4,b4 = linalg.lstsq(A.T,y4)[0]

print '(', m0, ',', b0, '),'
print '(', m1, ',', b1, '),'
print '(', m2, ',', b2, '),'
print '(', m3, ',', b3, '),'
print '(', m4, ',', b4, '),'

# plotting the line
line0 = m0*xi+b0
line1 = m1*xi+b1
line2 = m2*xi+b2
line3 = m3*xi+b3
line4 = m4*xi+b4

plot(xi,line0,'r-',xi,y0,'o')
plot(xi,line1,'r-',xi,y1,'o')
plot(xi,line2,'r-',xi,y2,'o')
plot(xi,line3,'r-',xi,y3,'o')
plot(xi,line4,'r-',xi,y4,'o')

show()

raw_input()
