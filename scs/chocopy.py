#!/usr/bin/python

import requests
import sys
import pickle
import os.path
import os
import socket
import re
import getpass
from datetime import datetime

homedir = os.path.expanduser("~")
dir = homedir + "/vari.pkl"
dir1 = homedir + "/session.pkl"
dir_log = homedir + "/IndexError.log"

class StopWatch:
    def __init__(self):
        self.reset()

    def reset(self):
        self.start_datetime = None
        self.end_datetime = None
        
    def start(self):
        self.reset()
        self.start_datetime = datetime.now()
        
    def stop(self):
        self.end_datetime = datetime.now()
        return self.get_elapsed_seconds()
        
    def get_elapsed_seconds(self):
        assert isinstance(self.start_datetime, datetime), 'call start() first'
        assert isinstance(self.end_datetime, datetime),   'call end() fist'
        # Return the total number of seconds contained in the duration
        # Equivalent to td / timedelta(seconds=1)
        return (self.end_datetime - self.start_datetime).total_seconds()

timer = StopWatch()

def firstlaunch(errorcheck):
    while errorcheck == 1:
        IP = input("Enter IP Address: ")
        try:
            socket.inet_aton(IP)
            break
        except socket.error:
            print("Not a valid IP Address")
    ID = input("Enter ID: ")
    PW = getpass.getpass("Enter PW: ")
    data = {'m': 'in', 'xid': ID, 'xpwd': PW}
    url = "http://"+ IP +"/sm/login.php"
    session = requests.session()
    try:
        t = session.post(url, data=data)
    except requests.exceptions.ConnectionError:
        print("Not existing IP Address")
        firstlaunch(1)
    if t.status_code == 200 and 'Invalid' in t.text:
        print("Wrong ID or PW")
        firstlaunch(2)
    elif "img src= 'img/m lam" and "mainbtn" in t.text:
        print("Loged In")
        os.makedirs(os.path.dirname(dir), exist_ok=True)
        with open(dir, 'wb') as f:
            pickle.dump(IP, f)
        with open(dir1, 'wb') as f:
            pickle.dump(session.cookies, f)
    else:
        print("Looks like not a Kocom IP")
        firstlaunch(1)

def loadsession():
    global IP
    with open(dir, 'rb') as f:
        IP = pickle.load(f)
    global s
    s = requests.session()
    with open(dir1, 'rb') as f:
        s.cookies.update(pickle.load(f))

def control(category, room, act):
    loadsession()
    url = 'http://'+IP+'/sm/control.php?dn='+category+'&room='+room+'&act='+act
    s.get(url)

    #a = getstatus('0', 'R2', '10')
    #if a == 0: print(timer.stop())

def getstatus(category, room, element):
    loadsession()
    url = 'http://'+IP+'/sm/control.php?dn='+category+'&room='+room
    getcode = s.get(url)
    rawcode = getcode.text

    if element in rawcode:
        print("0")
        #return 0

def nxtgetstatus(category, room, element):
    s.cookies.clear()
    loadsession()
    url = 'http://'+IP+'/sm/control.php?dn='+category+'&room='+room
    getcode = requests.get(url)
    rawcode = getcode.text
    num = rawcode.count("")

    if element in rawcode:
        print(0)

    elif num == 351 or num == 1080:
        print("Login Failed!")

    elif "Network Error" in rawcode:
        print("Server Error")

def gettemps(room, option):
    loadsession()
    url = 'http://'+IP+'/sm/control.php?dn=2&room='+room
    getcode = s.get(url)
    rawcode = getcode.text
    templist = re.findall('[0-9].png', rawcode)
    newtemplist = [i.replace('.png', '') for i in templist]
    if option == 'cur':
        try:
            print(newtemplist[0]+newtemplist[1])
        except IndexError:
            nxtgettemps(room, option)
    if option == 'set':
        try:
            print(newtemplist[2]+newtemplist[3])
        except IndexError:
            nxtgettemps(room, option)

def nxtgettemps(room, option):
    s.cookies.clear()
    loadsession()
    url = 'http://'+IP+'/sm/control.php?dn=2&room='+room
    getcode = s.get(url)
    rawcode = getcode.text
    templist = re.findall('[0-9].png', rawcode)
    newtemplist = [i.replace('.png', '') for i in templist]
    if option == 'cur':
        try:
            print(newtemplist[0]+newtemplist[1])
        except IndexError:
            with open(dir_log, 'a') as f:
                f.write(rawcode,"\n",templist,"\n",newtemplist)
            raise IndexError
    elif option == 'set':
        try:
            print(newtemplist[2]+newtemplist[3])
        except IndexError:
            with open(dir_log, 'a') as f:
                f.write(rawcode,"\n",templist,"\n",newtemplist)
            raise IndexError

if __name__ == "__main__":
    #timer.reset()
    #timer.start()
    try:
        args_1 = sys.argv[1]
        args_2 = sys.argv[2]
        args_3 = sys.argv[3]
        args_4 = sys.argv[4]
    except IndexError:
        pass
   
    if args_1 == 'ctl': control(args_2, args_3, args_4)

    if args_1 == 'status': getstatus(args_2, args_3, args_4)

    if args_1 == 'R3H' and args_2 == 'settemp': control('2', 'R3', 's'+args_3)

    if args_1 == 'fan' and args_2 == 'setspd': control('5', 'L1', 's'+args_3)
 
    if args_1 == 'firstlaunch': firstlaunch(1)

    if args_1 == 'gettemp': gettemps(args_2, args_3)