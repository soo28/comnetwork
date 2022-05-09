import socket
import threading
import time
import udp_server
from datetime import datetime


class udpserver_multiclient(udp_server.UDPServer):
    ''' A simple UDP Server for handling multiple clients '''

    def __init__(self, host, port):
        super().__init__(host, port)
        self.socket_lock = threading.Lock()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.printwt(f'single Server binded to {self.host}:{self.port}')
        #for test
        #self.addIp('roger', '127.0.0.1')
        #self.addIp('hades', '127.0.0.2')
        #self.addIp('alasin', '127.0.0.1')
        #self.addFriend('roger', 'hades')
        #self.addFriend('robber', 'alasin')
        #self.addFriend('alasin', 'robber')
        #self.addPresent('alasin', 'robber', 'xbox')
        
    def handle_request(self, data, client_address):
        ''' Handle the received packet from the client
        '''
        # handle request
        name = data.decode('utf-8')
        datalist = name.split(',')
        
        ip = client_address[0]
        self.addIp(datalist[0], ip)
        if datalist[0] == 'addFreiend':     # when user added his friend
            resp = self.addFriend(datalist[1], datalist[2])
        elif datalist[0] == 'addPresent':   # when user added present
            resp = self.addPresent(datalist[1], datalist[2], datalist[3])
        elif datalist[0] ==  'addThank':    # when receiving user received the present
            resp = self.changeComplete(datalist[1], datalist[2], 1)
            self.printwt(resp)
            return
        elif datalist[0] == 'allFinish':    # when sending user checked that receiving user is exactly received the present
            print(datalist)
            resp = self.changeComplete(datalist[2], datalist[1], 2)
        
        # send response to the client
        self.printwt(f'[ multi RESPONSE to {client_address} ]')
        #with self.socket_lock:
        #    self.sock.sendto(resp.encode('utf-8'), client_address)
        payload = 'status,' + resp
        self.sendtoclient(ip, payload)
        print('\n multi ', resp, '\n')

    def ThreadReceveMessage(self):
        '''After receive the messages, come here '''
        while True:
            data, client_address = self.sock.recvfrom(1024)
            if len(data) > 0:
                self.handle_request(data, client_address)

    def sendfunc(self):
        '''for present, it needs'''
        while True:
            self.process_sending()
            time.sleep(1)
    def wait_for_sending(self):
        '''it needs for present'''
        try:
            self.sendfunc()
            #s_thread = threading.Thread(target = self.sendfunc)
            #s_thread.daemon = True
            #s_thread.start()

        except OSError as err:
            self.printwt(err)

    def wait_for_client(self):
        ''' Wait for clients and handle their requests '''
        try:

            c_thread = threading.Thread(target = self.ThreadReceveMessage)
            c_thread.daemon = True
            c_thread.start()


        except KeyboardInterrupt:
            self.shutdown_server()
    
def main():
    ''' Create a UDP Server and handle multiple clients simultaneously '''

    udp_server_multi_client = udpserver_multiclient('127.0.0.1', 4444)
    udp_server_multi_client.configure_server()
    udp_server_multi_client.wait_for_client()
    udp_server_multi_client.wait_for_sending()    
    
if __name__ == '__main__':
    main()
