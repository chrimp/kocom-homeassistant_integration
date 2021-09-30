#!/usr/bin/python

#from Crypto.Cipher import AES
#from Crypto.Hash import SHA3_256
#from Crypto import Random
#import base64
#import binascii
from six.moves import urllib
import urllib
import requests
import sys
import pickle
import os.path
import os
import socket
import re
import time
import getpass
import threading
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


bs = 32
pad = lambda s: s + (bs - len(s.encode('utf-8')) % bs) * chr (bs - len(s.encode('utf-8')) % bs)
unpad = lambda s: s[:-ord(s[len(s)-1:])]
k = "457c81046ff09903028cfe2e6f09d68dbb38c5b640727bdb23e510ec189a780b"

class AESset:
    def __init__( self, key ):
        self.key = key
    
    def encrypt( self, raw ):
        raw = pad(raw)
        iv = Random.new().read(AES.block_size)
        crypt = AES.new(self.key, AES.MODE_CBC, iv)
        try:
            return base64.b64encode(iv + crypt.encrypt(raw.encode('utf-8')))
        finally:
            del raw, iv, crypt, self.key
        
    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        crypt = AES.new(self.key, AES.MODE_CBC, iv)
        try:
            return unpad(crypt.decrypt(enc[16:]).decode('utf-8'))
        finally:
            del enc, iv, crypt, self.key

def make_key(pw):
    before_hash = pw.encode()
    sha3er = SHA3_256.new()
    sha3er.update(before_hash)
    get_hash = sha3er.digest()
    get_hash_test = sha3er.hexdigest()
    print(get_hash_test)
    global key
    key = get_hash[:32]
    ec_pw = AESset(bytes(key)).encrypt(pw)
    with open(dir, 'wb') as f:
        pickle.dump(ec_pw, f)
    del key
    del get_hash
    del get_hash_test
    del sha3er
    return ec_pw
    
def decrypt_test():
    readable_hash = input("enter key")
    retain_key = binascii.unhexlify(readable_hash)
    with open(dir, 'rb') as f:
        pw_dbc = pickle.load(f)
    pw_adc = AESset(bytes(retain_key)).decrypt(pw_dbc)
    print(pw_adc)


def firstlaunch(errorcheck):
    while errorcheck == 1:
        IP = input("Enter IP Address: ")
        try:
            socket.inet_aton(IP)
            break
        except socket.error:
            print("Not a valid IP Address")
    ID = input("Enter ID: ")
    #PW = input("Enter PW: ")
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
        #ec_pw = make_key(PW)
        with open(dir, 'wb') as f:
            pickle.dump(IP, f)
        with open(dir1, 'wb') as f:
            pickle.dump(session.cookies, f)
    else:
        print("Looks like not a Kocom IP")
        firstlaunch(1)

def loadvariables(key):
    global ID, IP
    
    with open(dir, 'rb') as f:
        IP, ID, PW_bdc = pickle.load(f)
    try:
        key_bytes = binascii.unhexlify(key)
    except:
        try:
            return(args_1, args_2, args_3)
        finally:
            raise IndexError
    PW = AESset(bytes(key_bytes)).decrypt(PW_bdc)
    try:
        return PW
    finally:
        del key, key_bytes

def loadsession():
    global IP
    with open(dir, 'rb') as f:
        IP = pickle.load(f)
    global s
    s = requests.session()
    with open(dir1, 'rb') as f:
        s.cookies.update(pickle.load(f))

def stop():
    pass
    
threading.Timer(1, stop).start()

def login():
    #PW = loadvariables(key)
    loadsession()
    #data = {'m': 'in','xid': ID,'xpwd': PW}
    #url = "http://"+IP+"/sm/login.php"
    #s.post(url, data=data)
    #del PW

def control(category, room, act):
    login()
    url = 'http://'+IP+'/sm/control.php?dn='+category+'&room='+room+'&act='+act
    getcode = s.get(url)
    rawcode = getcode.text
    num = rawcode.count("")
    a = getstatus('0', 'R2', '10')

    if num == 351 or num == 1080:
        print("Failed to connect")
        print("Trying again...")
        #nxtcontrol(category, room, act)

    elif "Network Error" in rawcode:
        print("Server Error")
        print("Trying again...")
        #nxtcontrol(category, room, act)
    
    elif a == 0: print(timer.stop())

    #del key
        
def nxtcontrol(category, room, act):
    s.cookies.clear()
    #time.sleep(1)
    stop()
    login()
    #del key
    url = 'http://'+IP+'/sm/control.php?dn='+category+'&room='+room+'&act='+act
    getcode = s.get(url)
    rawcode = getcode.text
    num = rawcode.count("")

    if num == 351 or num == 1080:
        print("Login Failed!")

    elif "Network Error" in rawcode:
        print("Server Error!")

def getstatus(category, room, element):
    login()
    url = 'http://'+IP+'/sm/control.php?dn='+category+'&room='+room
    getcode = s.get(url)
    rawcode = getcode.text
    num = rawcode.count("")

    if element in rawcode:
        print("0")
        return 0
        #del key

    elif num == 351 or num == 1080:
        print("Failed to connect")
        print("Trying again...")
        nxtgetstatus(category, room, element)

    elif "Network Error" in rawcode:
        print("Server Error")
        print("Trying again...")
        nxtgetstatus(category, room, element)

def nxtgetstatus(category, room, element):
    s.cookies.clear()
    #time.sleep(1)
    stop()
    login()
    #del key
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
    login()
    url = 'http://'+IP+'/sm/control.php?dn=2&room='+room
    getcode = s.get(url)
    rawcode = getcode.text
    templist = re.findall('[0-9].png', rawcode)
    newtemplist = [i.replace('.png', '') for i in templist]
    if option == 'cur':
        try:
            #del key
            print(newtemplist[0]+newtemplist[1])
        except IndexError:
            #print(rawcode)
            #print(templist)
            #print(newtemplist)
            #raise IndexError
            nxtgettemps(room, option)
    if option == 'set':
        try:
            #del key
            print(newtemplist[2]+newtemplist[3])
        except IndexError:
            #print(rawcode)
            #print(templist)
            #print(newtemplist)
            #raise IndexError
            nxtgettemps(room, option)

def nxtgettemps(room, option):
    s.cookies.clear()
    #time.sleep(1)
    stop()
    login()
    #del key
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
    timer.reset()
    timer.start()
    try:
        args_1 = sys.argv[1]
        args_2 = sys.argv[2]
        args_3 = sys.argv[3]
    except IndexError:
        pass
   
    if args_1 == 'L' and args_2 == 'on' and args_3 == '1': control('0', 'L1', '11')
    if args_1 == 'L' and args_2 == 'off' and args_3 == '1': control('0', 'L1', '10')

    if args_1 == 'L' and args_2 == 'on' and args_3 == '2': control('0', 'L1', '21')
    if args_1 == 'L' and args_2 == 'off' and args_3 == '2': control('0', 'L1', '20')

    if args_1 == 'L' and args_2 == 'on' and args_3 == '3': control('0', 'L1', '31')
    if args_1 == 'L' and args_2 == 'off' and args_3 == '3': control('0', 'L1', '30')

    if args_1 == 'R1' and args_2 == 'on' and args_3 == '1': control('0', 'R1', '11')
    if args_1 == 'R1' and args_2 == 'off' and args_3 == '1': control('0', 'R1', '10')

    if args_1 == 'R1' and args_2 == 'on' and args_3 == '2': control('0', 'R1', '21')
    if args_1 == 'R1' and args_2 == 'off' and args_3 == '2': control('0', 'R1', '20')

    if args_1 == 'R2' and args_2 == 'on': control('0', 'R2', '11')

    if args_1 == 'R2' and args_2 == 'off': control('0', 'R2', '10')
    
    if args_1 == 'R3' and args_2 == 'on': control('0', 'R3', '11')
    if args_1 == 'R3' and args_2 == 'off': control('0', 'R3', '10')

    if args_1 == 'R4' and args_2 == 'on' and args_3 == '1': control('0', 'R4', '11')
    if args_1 == 'R4' and args_2 == 'off' and args_3 == '1': control('0', 'R4', '10')

    if args_1 == 'R4' and args_2 == 'on' and args_3 == '2': control('0', 'R4', '21')
    if args_1 == 'R4' and args_2 == 'off' and args_3 == '2': control('0', 'R4', '20')

    if args_1 == 'R4' and args_2 == 'on' and args_3 == '3': control('0', 'R4', '31')
    if args_1 == 'R4' and args_2 == 'off' and args_3 == '3': control('0', 'R4', '30')

    if args_1 == 'R6' and args_2 == 'on': control('0', 'R6', '11')
    if args_1 == 'R6' and args_2 == 'off': control('0', 'R6', '10')

    if args_1 == 'gas' and args_2 == 'off': control('1', 'R1', '10')

    if args_1 == 'LH' and args_2 == 'on': control('2', 'L1', 'p1')
    if args_1 == 'LH' and args_2 == 'off': control('2', 'L1', 'p0')

    if args_1 == 'R1H' and args_2 == 'on': control('2', 'R1', 'p1')
    if args_1 == 'R1H' and args_2 == 'off': control('2', 'R1', 'p0')

    if args_1 == 'R2H' and args_2 == 'on': control('2', 'R2', 'p1')
    if args_1 == 'R2H' and args_2 == 'off': control('2', 'R2', 'p0')

    if args_1 == 'R3H' and args_2 == 'on': control('2', 'R3', 'p1')
    if args_1 == 'R3H' and args_2 == 'off': control('2', 'R3', 'p0')
    if args_1 == 'R3H' and args_2 == 'settemp': control('2', 'R3', 's'+args_3)

    if args_1 == 'fan' and args_2 == 'on': control('5', 'L1', 'p1')
    if args_1 == 'fan' and args_2 == 'off': control('5', 'L1', 'p0')
    if args_1 == 'fan' and args_2 == 'setspd': control('5', 'L1', 's'+args_3)

    if args_1 == 'status' and args_2 == 'L' and args_3 == '1': getstatus('0', 'L1', '10')
    if args_1 == 'status' and args_2 == 'L' and args_3 == '2': getstatus('0', 'L1', '20')
    if args_1 == 'status' and args_2 == 'L' and args_3 == '3': getstatus('0', 'L1', '30')

    if args_1 == 'status' and args_2 == 'R1' and args_3 == '1': getstatus('0', 'R1', '10')
    if args_1 == 'status' and args_2 == 'R1' and args_3 == '2': getstatus('0', 'R1', '20')

    if args_1 == 'status' and args_2 == 'R2': getstatus('0', 'R2', '10')

    if args_1 == 'status' and args_2 == 'R3': getstatus('0', 'R3', '10')

    if args_1 == 'status' and args_2 == 'R4' and args_3 == '1': getstatus('0', 'R4', '10')
    if args_1 == 'status' and args_2 == 'R4' and args_3 == '2': getstatus('0', 'R4', '20')
    if args_1 == 'status' and args_2 == 'R4' and args_3 == '3': getstatus('0', 'R4', '30')

    if args_1 == 'status' and args_2 == 'R6': getstatus('0', 'R6', '10')

    if args_1 == 'status' and args_2 == 'LH': getstatus('2', 'L1', 'p0')

    if args_1 == 'status' and args_2 == 'R1H': getstatus('2', 'R1', 'p0')

    if args_1 == 'status' and args_2 == 'R2H': getstatus('2', 'R2', 'p0')

    if args_1 == 'status' and args_2 == 'R3H': getstatus('2', 'R3', 'p0')

    if args_1 == 'status' and args_2 == 'fan': getstatus('5', 'L1', 'sel.png')
 
    if args_1 == 'firstlaunch': firstlaunch(1)

    if args_1 == 'testec': make_key("qwerty1234")

    if args_1 == 'testdc': decrypt_test()

    if args_1 == 'teststop': stop()

    if args_1 == 'gettemp' and args_2 == 'L1' and args_3 == 'cur': gettemps('L1', 'cur')
    if args_1 == 'gettemp' and args_2 == 'L1' and args_3 == 'set': gettemps('L1', 'set')

    if args_1 == 'gettemp' and args_2 == 'R1' and args_3 == 'cur': gettemps('R1', 'cur')
    if args_1 == 'gettemp' and args_2 == 'R1' and args_3 == 'set': gettemps('R1', 'set')

    if args_1 == 'gettemp' and args_2 == 'R2' and args_3 == 'cur': gettemps('R2', 'cur')
    if args_1 == 'gettemp' and args_2 == 'R2' and args_3 == 'set': gettemps('R2', 'set')

    if args_1 == 'gettemp' and args_2 == 'R3' and args_3 == 'cur': gettemps('R3', 'cur')
    if args_1 == 'gettemp' and args_2 == 'R3' and args_3 == 'set': gettemps('R3', 'set')