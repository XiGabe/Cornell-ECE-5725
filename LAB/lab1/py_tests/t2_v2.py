#
# jfs9 2/10/2024 basic python code for python 3 output
#
prompt_text = "Enter a number: "
user_in = input(prompt_text)
user_num = int( user_in )

for i in range(1,10):
    print ( str(i) + " times " + str(user_num) + " is " + str(i*user_num) )

even = (user_num % 2) == 0
print(" ")
if even:
    print (str(user_num) + " is even")
else:
    print (str(user_num) + " is odd")
