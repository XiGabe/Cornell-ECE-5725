#
# jfs9 2/10/2024: modifications for exception check in python2 or python3
#
#                 input test
#
prompt_text = "Enter a text command: "
my_command = "start"
while (my_command!="quit"):
   my_command = str( input (prompt_text) )
   print ( "Entered text = " + my_command )
