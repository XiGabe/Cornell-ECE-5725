#
# jfs9 9/10/2024  example to illustrate python subprocess 
#

import subprocess

# Use a python subprocess to execute some 'echo' commands...

# build a shell command in the 'my_cmd' variable
my_cmd = 'echo "Hello There!" > /tmp/test_file_sub.txt'

# use subprocess call to send 'my_cmd' to the linux shell for execution
subprocess.check_output(my_cmd, shell=True)
