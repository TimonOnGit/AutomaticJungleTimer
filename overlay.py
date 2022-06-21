import os
import time
import json

from threading import Timer
import keyboard
import leagueofevents
import sys

from PyQt5 import QtGui, QtCore, uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread, QCoreApplication

class CustomEvent(QObject):
    updateValuesEvent = pyqtSignal()
    finishedEvent = pyqtSignal()
    clockUpdate = pyqtSignal()

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.sig = CustomEvent()
        self.sig.updateValuesEvent.connect(self.updateVals)
        self.sig.finishedEvent.connect(self.updateFinish)
        self.sig.clockUpdate.connect(self.updateClock)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.X11BypassWindowManagerHint |
            QtCore.Qt.FramelessWindowHint
        )
        self.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter,
                QtCore.QSize(315, 400),
                QtWidgets.qApp.desktop().availableGeometry()
        ))
        self.setStyleSheet("background:rgba(140, 140, 140, 180);")
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.labels = {
            'header': QtWidgets.QLabel, 
            'clock': QtWidgets.QLabel, 
            'gromp': QtWidgets.QLabel, 
            'buff1': QtWidgets.QLabel, 
            'wolves': QtWidgets.QLabel, 
            'raptors': QtWidgets.QLabel, 
            'buff2': QtWidgets.QLabel, 
            'krugs': QtWidgets.QLabel, 
            'finished_time': QtWidgets.QLabel
        }
        self.comp_times = []
        self.curr_camp = 0
        self.initVals()

    def initVals(self):
        '''
        Initializes all labels with their start values. Also reads in the times from comp_times to compare to.
        Because labels have images they are html formatted. Due to this one cannot use \t so instead mult_space func is used
        which creates multiple html spaces.
        '''
        with open ('comp_times.json', 'r') as f:
            self.comp_times = json.load(f)
        for i, label in enumerate(self.labels):
            self.labels[label] = QtWidgets.QLabel(self)
            if label == 'header': 
                self.labels[label].setText(f'Camp{mult_space_pl(4)}Rel{mult_space_pl(8)}Abs{mult_space_pl(8)}Ing{mult_space_pl(8)}Cmp  ')
                self.labels[label].setGeometry(QtCore.QRect(0, 0, 310, 20))
            elif label == 'clock':
                self.labels[label].setText(f'{mult_space_pl(10)}0:00{mult_space_pl(8)}0:00{mult_space_pl(8)}1:30{mult_space_pl(8)}------ ')
                self.labels[label].setGeometry(QtCore.QRect(0, 25, 310, 20))    
            elif label == 'finished_time':
                self.labels[label].setText(f'Finished{mult_space_pl(14)}------{mult_space_pl(6)}------{mult_space_pl(6)}{self.comp_times["total"]} ')
                self.labels[label].setGeometry(QtCore.QRect(0, 55*i-60, 310, 20))
            else:
                self.labels[label].setText(f"<html><img src='pics/{label}.webp'>{mult_space(3)}0:00{mult_space(7)}0:00{mult_space(7)}0:00{mult_space(7)}{self.comp_times[label]} </html>")
                self.labels[label].setGeometry(QtCore.QRect(0, 55*i-60, 310, 50))

            self.labels[label].setFont(QtGui.QFont('Arial', 13))
            
            


    def updateVals(self):
        '''
        Will get called every time a camp is finished. Updates the time for the specific camp.
        '''
        for label in self.labels:
            if label in ('header', 'clock', 'finished_time'):
                continue
            self.labels[label].setText(f"<html><img src='pics/{label}.webp'>{mult_space(3)}{rel_times[label]}{mult_space(7)}{abs_times[label]}{mult_space(7)}{game_times[label]}{mult_space(7)}{self.comp_times[label]} </html>")
            if game_times[label] != "0:00":
                if cmp_time_str(game_times[label], self.comp_times[label]):
                    self.labels[label].setStyleSheet("background:rgba(163, 75, 75, 180);")    
                else:
                    self.labels[label].setStyleSheet("background:rgba(75, 163, 75, 180);")                 

    def updateClock(self):
        '''
        Will get called every second. This updates all the clocks and adds 1 second to them.
        '''
        if game_times['total'] != '0:00':
            return
        self.labels['clock'].setText(f'{mult_space_pl(12)}{curr_rel_time.toString("m:ss")}{mult_space_pl(7)}{curr_abs_time.toString("m:ss")}{mult_space_pl(7)}{curr_game_time.toString("m:ss")}{mult_space_pl(6)}------ ')
    
    def updateFinish(self):
        '''
        will get called when the clear is finished. Updates the last label (the finished label) to represent
        the times when the clear was finished.
        '''
        game_times['total'] = curr_game_time.toString("m:ss")
        abs_times['total'] = curr_abs_time.toString("m:ss")
        self.labels['finished_time'].setText(f'Finished{mult_space_pl(14)}{abs_times["total"]}{mult_space_pl(7)}{game_times["total"]}{mult_space_pl(7)}{self.comp_times["total"]}')
        if cmp_time_str(game_times['total'], self.comp_times["total"]):
            self.labels["finished_time"].setStyleSheet("background:rgba(163, 75, 75, 180);")    
        else:
            self.labels["finished_time"].setStyleSheet("background:rgba(75, 163, 75, 180);") 
        self.jsonfy_times()
    
    def jsonfy_times(self):
        '''
        Reads old times and appends new times to them. Then creates a json out of it. In case
        no file is found / file is empty a new file is craeted.
        '''
        new_times = []
        try:
            with open('times.json', 'r') as f:
                   
                    old_times = json.load(f)
                    new_times = old_times
        except FileNotFoundError:
            pass
        new_times.append(game_times)   
        with open('times.json', 'w+') as f:
            json.dump(new_times, f)

class RepeatTimer(Timer):
    '''
    Class to create a timer that does a function every x seconds.
    '''
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class TimerThread(QThread):
    '''
    Worker thread that does the calculation of camp killing.
    '''
    def __init__(self):
        super().__init__()
        self.last_gold = 0
        self.curr_buffer = 0
        self.killed_camps = 0
        self.could_be = {
            'gromp': True,
            'buff1': True,
            'wolves': True,
            'raptors': True,
            'buff2': True,
            'krugs': True
        }
        self.killed = {
            'gromp': False,
            'buff1': False,
            'wolves': False,
            'raptors': False,
            'buff2': False,
            'krugs': False
        }
        self.krugs_last = False
        self.krugs_dead = 0
        self.finished = False
        self.start_timer = None
        self.rel_timer = None

    def run(self):
        leagueofevents.subscribe_to_event("onGoldGain", self.find_camp)
    
    def start_timer_func(self):
        self.start_timer = time.time()
        self.rel_timer = time.time()

    def find_camp(self, gold):
        '''
        When the player earns more than 3 gold in one timeframe they had some income.
        This income will then get stored in curr_buffer until a camp is finished. Also
        the last gold earn is always saved in last_gold.
        Calls function that determine if a camp was actually killed.
        '''
        if gold < 3:
            return
        self.last_gold = gold
        self.curr_buffer += gold
        self.camp_checker()
        self.check_camp_killed()
        self.check_finished()

    def check_finished(self):
        '''
        Will signal the overlay that the clear is finished. Sets killed_camps to 0 so the function
        does not get called again.
        '''
        if self.killed_camps == 6:
            self.killed_camps = 0
            mywindow.sig.finishedEvent.emit()

    def camp_checker(self):
        '''
        Checks every unique gold value a camp can have. When the player gains gold it can only come 
        from certain camps. A buffer of 1 gold is implemented because the killing of the monster can 
        align with the passive gold.
        '''
        # This is a special case: Krugs should count as finished when only one small krug is still alive. 
        # However when this krug is killed this gold should not be in the buffer because it is an assett 
        # from krugs.
        if self.krugs_last == True:   
            self.krugs_last = False
            if self.last_gold in (13, 14):
                if time.time() - self.krugs_dead < 4:
                    self.curr_buffer = 0
                    return           
        if self.last_gold not in (90, 91):
            self.could_be['gromp'] = False
        if self.last_gold not in (100, 101):
            self.could_be['buff1'] = False
            self.could_be['buff2'] = False
        if self.last_gold not in (15, 16, 30, 31, 65, 66, 80, 81, 95, 96):
            self.could_be['wolves'] = False
        if self.last_gold not in (8, 9, 16, 17, 24, 25, 32, 33, 40, 41, 45, 46, 53, 54, 61, 62, 69, 70, 77, 78, 85, 86):
            self.could_be['raptors'] = False
        if self.last_gold not in (7, 8, 13, 14, 15, 20, 21, 22, 26, 27, 28, 32, 33, 34, 39, 40, 41, 45, 46, 47, 52, 53, 59, 60, 65, 66, 78, 79):
            self.could_be['krugs'] = False

    def check_camp_killed(self):     
        '''
        Checks if a camp is killed by checking if the gold gains fit the camp and the buffer fits it as well.
        '''   
        if self.could_be['wolves'] and not self.killed['wolves'] and self.curr_buffer >= 95 and self.curr_buffer < 100:
            self.camp_killed('wolves')
        elif self.could_be['gromp'] and not self.killed['gromp'] and self.curr_buffer >= 90 and self.curr_buffer < 95:
            self.camp_killed('gromp')
        elif self.could_be['buff1'] and not self.killed['buff1'] and self.curr_buffer >= 100 and self.curr_buffer < 103:
            self.camp_killed('buff1')
        elif self.could_be['raptors'] and not self.killed['raptors'] and self.curr_buffer >= 85 and self.curr_buffer < 90:
            self.camp_killed('raptors')
        elif self.could_be['buff2'] and not self.killed['buff2'] and self.curr_buffer >= 100 and self.curr_buffer < 103:
            self.camp_killed('buff2')
        elif self.could_be['krugs'] and not self.killed['krugs'] and self.curr_buffer >= 118:
            self.camp_killed('krugs')
            self.krugs_last = True
            self.krugs_dead = time.time()

    def camp_killed(self, camp):
        '''
        Does multiple things when a camp is killed. Sets times in abs_times, rel_times and game_times,
        and resets the relative timer. Also emits to the overlay to update the times for said camp.
        '''
        global curr_rel_time
        abs_time = int(time.time() - self.start_timer)
        abs_time_str = f'{abs_time//60}:{abs_time%60:02}'
        rel_time = int(time.time() - self.rel_timer)
        rel_time_str = f'{rel_time//60}:{rel_time%60:02}'
        game_time_str = f'{(abs_time+90)//60}:{(abs_time+90)%60:02}'

        abs_times[camp] = abs_time_str
        rel_times[camp] = rel_time_str
        game_times[camp] = game_time_str
        self.rel_timer = time.time()
        curr_rel_time = QtCore.QTime(0, 0)
        self.curr_buffer = 0
        self.killed_camps += 1
        self.killed[camp] = True
        for label in self.could_be:
            self.could_be[label] = True
        mywindow.sig.updateValuesEvent.emit()

def mult_space(amt):
    '''
    Returns amt many html spaces.
    '''
    sp = ''
    for i in range(amt):
        sp += '&nbsp;'
    return sp

def mult_space_pl(amt):
    '''
    Returns amt many plain text spaces.
    '''
    sp = ''
    for i in range(amt):
        sp += ' '
    return sp

def cmp_time_str(time1, time2):
    '''
    Compares two time strings. Returns true if the first time 
    str is larger (greater time).
    '''
    if time1[0] > time2[0]:
        return True
    elif time1[0] < time2[0]:
        return False    
    if time1[2] > time2[2]:
        return True
    elif time1[2] < time2[2]:
        return False
    if time1[3] > time2[3]:
        return True
    elif time1[3] < time2[3]:
        return False
    return False

def timerEvent():
    '''
    Will get called every second. Updates timers and emits signal to overlay.
    '''
    global curr_rel_time
    global curr_abs_time
    global curr_game_time
    curr_rel_time = curr_rel_time.addSecs(1)
    curr_abs_time = curr_abs_time.addSecs(1)
    curr_game_time = curr_game_time.addSecs(1)
    mywindow.sig.clockUpdate.emit()
    mywindow.updateClock()

 

if __name__ == "__main__":
    abs_times = {
        'wolves': '0:00',
        'gromp': '0:00',
        'buff1': '0:00',
        'raptors': '0:00',
        'buff2': '0:00',
        'krugs': '0:00',
        'total': '0:00'
    }

    rel_times = {
        'wolves': '0:00',
        'gromp': '0:00',
        'buff1': '0:00',
        'raptors': '0:00',
        'buff2': '0:00',
        'krugs': '0:00'
    }

    game_times = {
        'wolves': '0:00',
        'gromp': '0:00',
        'buff1': '0:00',
        'raptors': '0:00',
        'buff2': '0:00',
        'krugs': '0:00',
        'total': '0:00'
    }


    app = QApplication(sys.argv)
    thread = TimerThread()
    thread.start()

    mywindow = MainWindow()
    curr_rel_time = QtCore.QTime(0, 0, 0)
    curr_abs_time = QtCore.QTime(0, 0, 0)
    curr_game_time = QtCore.QTime(0, 1, 30)
    timer = RepeatTimer(0.994, timerEvent)

    def start_key_pressed():
        '''
        Key listener for start key. Works even when window is not focused.
        '''
        try: 
            timer.start()
            print('start!')
            thread.start_timer_func()
        except RuntimeError:
            print('Already started. If you want to restart press 6!')

    def restart_key_pressed():
        '''
        Key listener for restart key. Works even when window is not focused.
        '''
        print('restart!')    
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv) 

    def exit_key_pressed():
        '''
        Key listener for exit key. Works even when window is not focused. Needs to be 
        os._exit(0) because it gets called from a thread and sys.exit() only kills the thread.
        '''
        print('exit!')
        os._exit(0)

    keyboard.add_hotkey('5', start_key_pressed)
    keyboard.add_hotkey('6', restart_key_pressed)
    keyboard.add_hotkey('7', exit_key_pressed)

    mywindow.show()
    app.exec_() 
