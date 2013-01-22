# V:
# Sensor 0 (leftmost), pi/2
y0 = [470.0, 398.0, 355.0, 332.5, 286.0, 247.0, 232.0, 218.0, 195.0, 183.0]
max = 12
# Sensor 1, pi/4
y1 = [470.0, 402.0, 353.0, 321.0, 283.0, 259.0, 227.0, 211.0, 199.0, 171.0]
max = 12
# Sensor 2 (front), 0
y2 = [454.0, 401.0, 350.0, 322.0, 271.0, 251.0, 228.0, 212.0, 202.0, 171.0]
max = 30
# Sensor 3, -pi/4
y3 = [269.0, 235.0, 206.0, 187.0, 171.5, 157.0, 142.0, 132.0, 124.0, 115.0]
# Sensor 4 (rightmost), -pi/2
y4 = [277.0, 242.0, 212.0, 188.0, 170.0, 156.0, 141.0, 129.0, 120.0, 112.0]

# 1/d:
x = [1.0/(4.0-0.645), 1.0/(4.5-0.645), 1.0/(5.0-0.645), 1.0/(5.5-0.645), 1.0/(6.0-0.645), 1.0/(6.5-0.645), 1.0/(7.0-0.645), 1.0/(7.5-0.645), 1.0/(8.0-0.645), 1.0/(8.5-0.645)]

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

#plot(xi,line0,'r-',xi,y0,'o')
#plot(xi,line1,'r-',xi,y1,'o')
#plot(xi,line2,'r-',xi,y2,'o')
plot(xi,line3,'r-',xi,y3,'o')
plot(xi,line4,'r-',xi,y4,'o')

xMaster = array(x+x+x)
A = array([x+x+x, ones(30)])
m,b = linalg.lstsq(A.T,y0+y1+y2)[0]
print "Master:", m, b

line5 = m*xMaster+b
plot(xMaster,line5,'r-',xMaster,y0+y1+y2,'o')


show()

raw_input()
