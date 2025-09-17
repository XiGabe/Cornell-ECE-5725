# jfs9 9/5/2022 prints 1 to 10 with 1 sec delay

import time

#prompt_text = "Enter a number: "
#user_in = input(prompt_text)
#user_num = int( user_in )

user_num = 1

for i in range(1,10):
    print (i, "times" , user_num, " is ", i*user_num)
    time.sleep(1)

even = (user_num % 2) == 0
print(" ")
if even:
    print (user_num, " is even")
else:
    print (user_num, " is odd")
