import requests
import os
import time
import platform
import sys

PARAMS = CMD = USERNAME = PASSWORD = API = ""
HOST = "localhost"
PORT = "1105"


def show_func():
    print("\n" + "USERNAME : " + USERNAME + "\n" + "API : " + API + "\n")
    print("What do you want to do : ")
    print("1 => send ticket")
    print("2 => get ticket")
    print("3 => change status for user")
    print("4 => change status for admin")
    print("5 => response to tickets(admin)")
    print("6 => logout(login with another account)")
    print ("7 => exit")



def __postcr__():
    return "http://" + HOST + ":" + PORT + "/" + CMD + "?"

while True:
    print ("        Welcome")
    print ("what do you want to do? ")
    print ("1 => signup")
    print ("2 => login")
    print ("3 => exit")

    flag = sys.stdin.readline()

    if flag[:1] == '3':
        sys.exit()

    if flag[:-1] == '1':

        while True:
            print("To create new account enter the Authentication (back?? just click 1 otherwise click enter )")
            backflag = sys.stdin.readline()
            if backflag[:1] == '1':
                break
            else:
                print("Enter Username : ")
                USERNAME = sys.stdin.readline()[:-1]
                print("Enter Password : ")
                PASSWORD = sys.stdin.readline()[:-1]
                print("Enter Firstname : ")
                FIRSTNAME = sys.stdin.readline()[:-1]
                print("Enter Lastname : ")
                LASTNAME = sys.stdin.readline()[:-1]

                while True:
                    print("if you are user press enter (admin press number 1)")
                    temp = sys.stdin.readline()[:-1]
                    if temp == '1':
                        ROLE = 'admin'
                        break
                    else:
                        ROLE = 'user'
                        break


                CMD = "signup"
                PARAMS = {'username': USERNAME, 'password': PASSWORD, 'role': ROLE, 'firstname': FIRSTNAME,
                          'lastname': LASTNAME}
                r = requests.post(__postcr__(), PARAMS)
                if str(r.json()['code']) == "200":
                    print("Your Account Is Created")
                    print("Your Username :" + USERNAME)
                    print("Your API : " + str(r.json()['api']))
                    print("Your Role : " + ROLE)
                    print('Press enter to continue')
                    x = sys.stdin.readline()[:-1]
                    break

                else:
                    print(str(r.json()['message']) + "\n" + "Try Again")
                    print('Press enter to continue')
                    x = sys.stdin.readline()[:-1]


    if flag[:-1] == '2':
        while True:
            print ("Username : ")
            USERNAME = sys.stdin.readline()[:-1]
            print ("Password : ")
            PASSWORD = sys.stdin.readline()[:-1]
            CMD = "retrieve"
            PARAMS = {'username': USERNAME, 'password': PASSWORD}
            r = requests.post(__postcr__(), PARAMS)
            if str(r.json()['code']) == 'found':
                print("Logged in successfully :)")
                API = str(r.json()['api'])
                break
            else:
                print("Username Or Password is Incorrect\nTry Again ^____^")

        while True:
            show_func()
            func_type = sys.stdin.readline()
            if func_type[:-1] == '1':
                print("subject : ")
                subject = sys.stdin.readline()[:-1]
                print("body : ")
                body = sys.stdin.readline()[:-1]
                CMD = "sendTicket"
                PARAMS = {'Token': API, 'subject': subject, 'body': body}
                data = requests.post(__postcr__(), PARAMS)

                if str(data.json()['code']) == "200":
                    print("message ID : " + str(data.json()['id']))
                    print(str(data.json()['message']))

                print('Press enter to continue')
                x = sys.stdin.readline()[:-1]

            if func_type[:-1] == '6':
                break

            if func_type[:-1] == '7':
                sys.exit()

            if func_type[:-1] == '2':
                CMD = "getTicket"
                PARAMS = {"Token": API}
                r = requests.post(__postcr__(), PARAMS)

                if str(r.json()['code']) == "200":
                    print(str(r.json()['tickets']))
                    index = int(r.json()['index'])
                    for i in range(0, index):
                        block = 'block ' + str(i)
                        print("Message id : " + str(r.json()[block]['id']))
                        print("Subject : " + str(r.json()[block]['subject']))
                        print("Message : " + str(r.json()[block]['body']))
                        print("Status : " + str(r.json()[block]['status']))
                        print("Response : " + str(r.json()[block]['response']) + "\n")

                else:
                    print(str(r.json()['tickets']))

            if func_type[:-1] == '3':
                CMD = "closeticket"
                print("enter your ticket ID : ")

                id = sys.stdin.readline()[:-1]
                PARAMS = {"Token": API, 'id': id}
                r = requests.post(__postcr__(), PARAMS)
                if str(r.json()['code']) == "200":
                    print(str(r.json()['message']))
                else:
                    print(str(r.json()['message']))

            if func_type[:1] == '4':
                CMD = "changeStatusByAdmin"
                print("enter ticket ID : ")
                id = sys.stdin.readline()[:-1]
                while True:
                    print("change status to this options:")
                    print("1 => open")
                    print("2 => close")
                    print("3 => in progress")

                    statusflag = sys.stdin.readline()[:-1]
                    if statusflag == '1':
                        statusflag = 'open'
                        break
                    elif statusflag == '2':
                        statusflag = 'close'
                        break
                    elif statusflag == '3':
                        statusflag = 'in progress'
                        break
                    else:
                        print("enter number between 1 to 3")
                PARAMS = {"Token": API, 'id': id, 'status': statusflag}
                r = requests.post(__postcr__(), PARAMS)
                if str(r.json()['code']) == "200":
                    print(str(r.json()['message']))
                else:
                    print(str(r.json()['message']))

            if func_type[:1] == '5':
                CMD = "response"
                print("enter ticket ID : ")
                id = sys.stdin.readline()[:-1]
                print("enter your response for this ticket : ")
                body = sys.stdin.readline()[:-1]
                PARAMS = {"Token": API, 'id': id, 'body': body}
                r = requests.post(__postcr__(), PARAMS)
                if str(r.json()['code']) == "200":
                    print(str(r.json()['message']))
                else:
                    print(str(r.json()['message']))
