import socket
import time
import threading
import zlib

msgFromClient = ''
UDPSendSocket = 0
serverip = "127.0.0.1"
clientip = "127.0.0.1"

def sendtoserver(payload):
        '''
        send client's payload to server
        '''
        global UDPSendSocket;
        serverAddressPort   = (serverip, 4444)
        # Create a UDP socket at client side
        if UDPSendSocket == 0:
            UDPSendSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        
        # Send to server using created UDP socket
        UDPSendSocket.sendto(payload, serverAddressPort)
        
def checksum_calculator(data):
    '''
    calculate the checksum
    '''
    checksum = zlib.crc32(data)
    return checksum

def sendfunc():
    '''
    Receive the input from user and send the inputed data to server
    '''
    global msgFromClient
    while True: 
        print(" *** PYTHON CLIENT *** ")
        msgFromClient       = input("Whats the name? :")
        print(msgFromClient)

        msgSelect = input("Select contents to do \n 1: Add friend/family \n 2: Input reciving client's name\n")
        msgValue = int(msgSelect)
        if msgValue == 1:
            msgFriendName = input("Enter friend's name:")
            msgFromClient = "addFreiend," + msgFromClient + "," + msgFriendName
        else:
            msgReceivingName = input("Enter receiving client's name: ")
            msgPresentContent = input("Enter present name: ")
            msgFromClient = "addPresent," + msgFromClient + "," + msgReceivingName + "," + msgPresentContent

        # send inputed data to server
        bytesToSend = str.encode(msgFromClient)
        sendtoserver(bytesToSend)
        
        
def recvfunc():
    '''
    Received the data from server.
    If first field is status, it means the result that processed the user data on server.
    If first field is not status, it means that present has arrived. In this case, after checked checksum, process.
    '''
    UDPRecvSocket = 0
    global msgFromClient
    while True:
        if msgFromClient == '':
                time.sleep(0.05)
                continue
        if UDPRecvSocket == 0:
            UDPRecvSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            UDPRecvSocket.bind((clientip, 4443))
            
        if UDPRecvSocket != 0:
            msgFromServer = UDPRecvSocket.recvfrom(1024)
            msg = "[recv]Message from Server :{}\n".format(msgFromServer[0].decode())
            print(msg)

            data = msgFromServer[0].decode()
            data1 = data.split(',')
            nlen = len(data1)
            data2 = data1[0]
            # get all fields from server except checksum field
            for i in range(1, nlen-1):
                data2 = data2 + ',' + data1[i]

            # check checksum
            if str(checksum_calculator(data2.encode())) != data1[nlen - 1]:
                print("[recv]checksum error")
                continue

            # decide the data kind from server
            if data1[0] == 'status':
                print('[recv]continue dueto status buffer',data1[1])
                continue

            # Upon successful delivery of present, a receiving client can request...
            if data1[2] == '1.0':
                bytesToSend = str.encode('allFinish,' + msgFromClient + ',' + data1[0])
                sendtoserver(bytesToSend)
                print(bytesToSend)
                continue
            
            # Thank You acknowledgement message sent
            bytesToSend = str.encode('addThank,' + msgFromClient + ',' + data1[0])
            print('[recv] senttoserver payload: ', bytesToSend)
            sendtoserver(bytesToSend)
            
        time.sleep(1)
        print('recv finished'+data+'\n')
        
def mythread():
        '''
        Create send and recv processing part
        '''
        #cthread = threading.Thread(target = sendfunc)
        #cthread.daemon = True
        #cthread.start()
        rthread = threading.Thread(target = recvfunc)
        rthread.daemon = True
        rthread.start()
        sendfunc()
def main():
    mythread()
if __name__ == '__main__':
    main()
