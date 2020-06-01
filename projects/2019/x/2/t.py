import sys

id = 999999
filename = "Ceres.jpg"

d = 0
n = sys.maxsize - 1
while n > 0:
    d += 1
    n //= 10
f = "0" + str(d)
p = "{:" + f + "}"
x = f"{p}".format(id)
filename = x + "-" + filename
print(filename)
