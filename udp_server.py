import socket
from datetime import datetime
import pandas as pd
import numpy as np
import time
import zlib

class UDPServer:
    ''' A simple UDP Server '''

    # Create friend/family variables 
    
    pdFriend = pd.DataFrame({'name':[], 'friend':[]})
    pdBuffer = pd.DataFrame({'name':[], 'receiver':[], 'content':[], 'complete':[], 'time':[]})
    pdIp = pd.DataFrame({'name':[], 'address':[]})
    
    def __init__(self, host, port):
    	self.host = host    # Host address
    	self.port = port    # Host port
    	self.sock = None    # Socket
        #for test
    	
    def printwt(self, msg):
        ''' Print message with current date and time '''

        current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[{current_date_time}]  {msg}')

    def configure_server(self):
        ''' Configure the server '''

        # create UDP socket with IPv4 addressing
        self.printwt('single Creating socket...')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.printwt('single Socket created')

        # bind server to the address
        self.printwt(f'single Binding server to {self.host}:{self.port}...')
        self.sock.bind((self.host, self.port))
        self.printwt(f'single Server binded to {self.host}:{self.port}')
        
    def sendtoclient(self, ip, payload):
        ''' send the payload to client corresponding to ip'''
        checksum = self.checksum_calculator(payload.encode())
        self.printwt(checksum)
        bytetosend = payload + ','+str(checksum)
        self.printwt(bytetosend)
        sendsock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sendsock1.settimeout(0.25)
        serverAddressPort   = (ip, 4443)
        print(serverAddressPort)
        sendsock1.sendto(bytetosend.encode('utf-8'), serverAddressPort)
        
        
    def checksum_calculator(self,data):
        '''calculate the checksum'''
        checksum = zlib.crc32(data)
        return checksum

    def addIp(self, name, address):
        '''add user name and user's ip address to ip dataframe'''
        nExist = len(self.pdIp[self.pdIp['name'] == address])
        if nExist != 0:
            return 'Already exists'
        
        adddata = pd.DataFrame({'name':[name], 'address':[address]})
        self.pdIp = pd.concat([self.pdIp, adddata], ignore_index=True)
        return 'Successfully is added in friend list'
    
    def addFriend(self, name, fname):
        '''add the user name and user's friend/family name to friend dataframe'''
        nExist = len(self.pdFriend[(self.pdFriend['name'] == name)&(self.pdFriend['friend'] == fname)])
        if nExist != 0:
            return 'Already exists'
        adddata = pd.DataFrame({'name':[name], 'friend':[fname]})
        self.pdFriend = pd.concat([self.pdFriend, adddata], ignore_index=True)
        return 'Successfully is added in friend list'
    
    def addPresent(self, name, rname, content):
        '''add the user name, receiving user name and present content to present dataframe'''
        if len(self.pdBuffer) == 10:
            return 'Add Failed to overflow'
        adddata = pd.DataFrame({'name':[name], 'receiver':[rname], 'content':[content], 'complete':[0], 'time':[0]})
        self.pdBuffer = pd.concat([self.pdBuffer, adddata], ignore_index=True)
        return 'Successfully is added to Buffer'
    
    def changeComplete(self, rname, sname, status):
        '''Change buffer's complete status
           Sending user name is sname and receiving user name is rname'''    
        index1 = self.pdBuffer[(self.pdBuffer['name'] == sname)&(self.pdBuffer['receiver'] == rname)].index
        print("----------changeComplete------------- : ", status, sname, rname, index1)
        self.pdBuffer.loc[index1, 'complete'] = status
        #print("Status changed", self.pdBuffer)
        self.printwt(self.pdBuffer)
        return 'Successfully is changed into Buffer'
    def get_gift(self, name):
    
    	''' Get phone no for a given name '''
        
    	#glist = {'Joshua': 'XBOX', 'Sooraj': 'Playstation', 'Jack': 'Chelsea Kit','Rowan': 'Skateboard'}
    	
    	#if name in glist.keys():
    	#	return f"single {name}'s xmas gift is {glist[name]}"
    	#else:
    	#	return f"single No records found for {name}"
     
    def IsValidPresent(self):
        '''
        Check that valid present exists in present buffer 
        '''
        for i in self.pdBuffer.index:
            if self.pdBuffer.loc[i, 'complete'] == 2:
                print('++++++++++++  delete ++++++++++++++')
                self.pdBuffer = self.pdBuffer.drop([i])
                continue
            elif self.pdBuffer.loc[i, 'complete'] == 1:
                elapsedtime = time.time() - self.pdBuffer.loc[i, 'time']
                if elapsedtime >= 2:
                    
                    r = self.pdBuffer.loc[i, 'name']
                    ip = self.pdIp[self.pdIp['name'] == r].iloc[0][1]
                    
                    
                    bytetosend = self.pdBuffer.loc[i, 'receiver']+ ','+self.pdBuffer.loc[i, 'content'] + ',' + str(self.pdBuffer.loc[i, 'complete'])
                    self.sendtoclient(ip, bytetosend)
                    print('>>>>>>>>>>>>>>  resend >>>>>>>>>>>>>>')
                    self.pdBuffer.loc[i, 'time'] = time.time()
                                    
                continue
            
            sname = self.pdBuffer.loc[i, 'name']
            rname = self.pdBuffer.loc[i, 'receiver']
            self.printwt(sname)

            # if receiving user is not registered on server, it's ignored
            reg = len(self.pdIp[self.pdIp['name'] == rname])
            if reg == 0:
                continue

            # check if the sending client is contained in the receiving clients family/friends list and the receiving client is contained in the sending clients family/friends list.
            df = self.pdFriend
            s = len(df[(df['name'] == sname)&(df['friend'] == rname)])
            r = len(df[(df['friend'] == sname)&(df['name'] == rname)])
            if (s >= 1) & (r >= 1):
                return i
        return -1
    
    def process_sending(self):
        '''
        If all conditions is satisfied, present is sent
        '''
        try:
            # This part is important. This is corresponded to 1). If today is not 25th, processing part never work
            # For test, please make two lines to comments
            #if datetime.now().strftime('%d') != '25':
            #    return
            
            date1 = datetime.now().strftime('%d')
            date1 = '24' # for test
            if date1 != '25':
                return

            # In present list, check if valid present exists             
            nret = self.IsValidPresent()
            if nret == -1:
                return

            # get the address of receiving user
            r = self.pdBuffer.loc[nret][1]
            ip = self.pdIp[self.pdIp['name'] == r].iloc[0][1]
            self.printwt(ip)

            # generate the radomised count
            randomcount = np.random.randint(4, size=1)
            randomcount[0] = randomcount[0] + 1
            timeSleep = randomcount[0]
            while True:
                # if sent the present
                if self.pdBuffer.loc[nret, 'complete'] == 1:
                    break

                # randomcount is reached zero, but if is not completed, generate bigger randomcount than previous value
                if str(self.pdBuffer.loc[nret, 'time']) != '0.0':
                    if (time.time() - self.pdBuffer.loc[nret, 'time']) < timeSleep:
                        continue
                    else:
                        randomcount = np.random.randint(4, size=1)
                        timeSleep = randomcount[0] + timeSleep                

                # sent the present to receiving client
                bytetosend = self.pdBuffer.loc[nret, 'name']+ ','+self.pdBuffer.loc[nret, 'content'] + ',' + str(self.pdBuffer.loc[nret, 'complete'])
                self.sendtoclient(ip, bytetosend)
                
                self.pdBuffer.loc[nret, 'time'] = time.time()
                print('------------------send------------------------')
                
        except OSError as err:
            self.printwt(err)
        

    def shutdown_server(self):
        ''' Shutdown the UDP server '''

        self.printwt('single Shutting down server...')
        self.sock.close()

'''
if __name__ == '__main__':
    main()
'''
