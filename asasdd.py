from threading import Thread
from time import sleep


def a():
    print(1)
    sleep(5)
    print(2)

tasks = []

for i in range(20):
    tasks.append(Thread(target=a))

for i in tasks:
    i.start()

#for i in tasks:
#    i.join()

sleep(2)
print(12)
