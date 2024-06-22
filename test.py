from math import log, sqrt
m = 64
n = 64
num = "0x410ef4e5ae04e8000000"

int_num = int(num, 16)
print(hex(int_num))
bin_128_num = bin(int_num)[2::].rjust(128, "0")

print(bin_128_num)

int_part = int(bin_128_num[0:64], 2)
decimal_part = int(bin_128_num[64::], 2)/2**64

res = int_part+decimal_part
print(log(184776, 1.0001))
print(1.0001**0x2d1c8)
print(log(res, 1.0001))
print(log(res**2,1.0001))
print(1)
print(res**2)
int_part = int(res)
float_part = res%1
bin_int_part = bin(int_part)[2::].rjust(m, "0")
bin_float_part = bin(int(float_part*2**n))[2::].rjust(n, "0")
res_bin = bin_int_part + bin_float_part
ress = int(res_bin, 2)
print(hex(ress))

p = 1.2340382117643097e-05
1305.11 
184776

tick = 184776
value = 105759285.85988262
p = 1305.11/(1+0.0001)**184776 
int_part = int(value)
float_part = value%1
bin_int_part = bin(int_part)[2::].rjust(m, "0")
bin_float_part = bin(int(float_part*2**n))[2::].rjust(n, "0")
res_bin = bin_int_part + bin_float_part
res = int(res_bin, 2)
0x42ea77a02e0200000000
print(hex(res))
base = 0
#price/base = 1.0001**tick
#log(price/base, 1.0001)
