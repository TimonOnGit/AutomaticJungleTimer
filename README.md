# AutomaticJungleTimer   
This is a tool to automatically track your jungle clear in practice tool. All functions will be explained later on in this file.   

# How to install?   
You need to have python installed. If not simply download it here https://www.python.org/downloads/   
Now download this repository. After you unzipped the file to a resonable place you need to install its requirements.  To do so you simply start the `install_requirements.bat`.   
Alternative way is to open cmd in the file directory and type `pip install -r requirements.txt`. If you don't have pip installed already, install it via `python -m ensurepip --upgrade`. It is an installer for python packages.

# How to use?
Simply start the  `start_overlay.bat` file.    
Alternative way is to open cmd in your directory and type `python overlay.py`.   
After you started it a small window will open that shows you current timers. To start the timer press `5` (so when you start your clear, press `5`). To reset the timer press `6` (Note: After that you need to press `5` again to start, `6` simply resets the program). To close the programm press `7`. All this does not have to be done in the window, you can conveniently do it while in your practice tool. 

# Features
You can compare your times with preset times. To do so simply change the times in `comp_times.json` to the times you want to reach. The timer will compare those with the ingame timer and mark them red if you finished them below the time and green if you finished them on time.   

The program also stores your times in `times.json`. This is a list of the times you did in all your runs. The idea is to rename this file as soon as your session is over to have all of your champ runs saved. In the future I plan on creating a tool that visualizes these values. The values will NOT be overwritten instead new values will always be appended. So make sure to rename or delete the file as soon as you finished one champion.

# Feedback
I hope you are happy with this tool. If you have any remarks, ideas for feature or find any bugs please let me know on github or on Discord Timon#1853. 