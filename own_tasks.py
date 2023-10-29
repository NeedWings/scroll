from BaseClasses import *

def own_tasks(self):
    tasks = SETTINGS["own_tasks"].copy()
    self.delay = 0
    shuffle(tasks)
    for task in tasks:
        if type(task) == type([1,2,3]):
            for task2 in task:
                #print(task2)
                self.task_number = task2
                self.start()
        else:
            #print(task)
            self.task_number = task
            self.start()
    if random.choice(SETTINGS["SwapAtTheEnd"]):
        self.swap_to_one_token(random.choice(SETTINGS["toSaveFunds"]))

