#
# jfs9 9/10/21 basic python code for python 2 output
#    v3 experiment with raw_input
#
prompt_text = "Enter a number: "
user_in = raw_input(prompt_text)
user_num = int( user_in )

for i in range(1,10):
    print ( str(i) + " times " + str(user_num) + " is " + str(i*user_num) )

even = (user_num % 2) == 0
print(" ")
if even:
    print (str(user_num) + " is even")
else:
    print (str(user_num) + " is odd")
