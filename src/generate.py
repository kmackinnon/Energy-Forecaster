#! /usr/bin/python2.7

MINUS_DAY = -23
PLUS_16 = 16

# the hours from the last day and the next 16
data = []

for i in range(MINUS_DAY, PLUS_16):
	if i<0:
		data.append(str(i))
	elif i==0:
		data.append('Current time')
	else:
		data.append("+" + str(i))

st = "'" + "', '".join(data) + "'"

f = open('x_axis.txt', 'wb')
f.write(st)
f.close()
