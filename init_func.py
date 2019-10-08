import random
import hashlib
from node import Node
import sys

ids=[] #list all keys  for the nodes of ring
tr={} #dictionary with the hash key and  the corresponded ip,port of the node
allIps=[] #list with ips in order to avoid duplicates
def generate_ip():
    unique=0
    while unique==0:
     ip_gen=str(random.randint(0,255))+'.'+str(random.randint(0,255))+'.'+str(random.randint(0,255))+'.'+str(random.randint(0,255))
     #Make sure that the ip was not generated again.
     if ip_gen not in allIps:
      allIps.append(ip_gen)
      return ip_gen
    
def generate_port():
    return str(random.randint(0,99999))


def generate_id(ip,port):
    ''' hash finction:sha1 used for the nodes of the chord ring. The hashing value is the IP and port of each node'''
    hash_object = hashlib.sha1(ip+':'+port)
    hex_dig = hash_object.hexdigest()
    dec_dig=int(hex_dig, 16)   
    bin_dig=format(dec_dig,'b')
    dec_dig=int(bin_dig,2)
    return dec_dig

def fingers(dht,m,i,max_value):
    ''' init the finger table of each node'''
    import main
    #Local index is used to increment from the current element up to the m next.
    local_ind=1
    #cnt and entered are used when the next element is the first element and the search for the fingers should be moving to the start of the ring
    cnt=i
    entered=False
    for s in range(0,m):
        #Inner boolean variable for exiting the loop.
        done=False
        while done==False:
            #If the next value is over the max value,then we should continue finger table completion from the start
            key=tr[ids[i]]
            if dht[key].id_+(2**s)>max_value and entered==False:
                entered=True
                cnt=0
                local_ind=0
            #The modulo max value is used for finding the true value over the max that should compare for the next node
            key2=tr[ids[(cnt+local_ind)%len(ids)]]
            #max_value+1 needed in case max value successor is 0 . If not +1 ,then the result would always skip the zero and proceed to the next node.
            if ((dht[key].id_+(2**s))% (max_value+1)) <= ids[(cnt+local_ind)%len(ids)]:
                dht[key].fin_tr[ids[(cnt+local_ind)%len(ids)]]=dht[key2].ip+':'+dht[key2].port
                dht[key].fin.append(ids[(cnt+local_ind)%len(ids)])
                done=True
            else:
                #increment local index to the next item
                local_ind+=1 
                 
def init_hashing_ring(size,m):
    ''' init the chord ring nodes and return a dictionary that contains all nodes off the chornd ring'''
    ring_size=2**m
    dht={}
    nodes={}
    import main    
    for i in range(size):
        port=str(i)
        ip=generate_ip()
        id=generate_id(ip,port)
        tr[id]=str(ip)+':'+str(port)
        dht[str(ip)+':'+str(port)]=Node(ip,port,id,m)
        ids.append(id)
	ids.sort()
    return dht


def update_contacts_list(dht,m):
    ''' set succesor, predeccessor and finger table for each node of the ring'''
    #Needed to include the case that the finger table should insert values that are in the beginning of the ring
    #e.g. maximum value 57, 42+16=58(over the max value,thus the modulo will give the desired value), 58%57 = 1.
    import main
    max_value=ids[-1]
    for i in range(len(ids)):
        #successor is the next element in the sorted list of node ids, clockwise
        key=tr[ids[i]]
        key2=tr[ids[(i+1)%len(ids)]]
        dht[key].succ=[ids[(i+1)%len(ids)],key2]
        #predecessor is the previous element in the sorted list of node ids 
        key2=tr[ids[i-1]]
        dht[key].pred=[ids[i-1],key2]
        fingers(dht,m,i,max_value)
    	key=tr[ids[i]]
      
