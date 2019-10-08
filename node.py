import share_memory as shr_mem
import files

class Node:
 file_reqs=dict() #file reqs per file
 msg_routed=0
 succ=-1
 pred=-1
 fin=list() #holds the noded id
 fin_tr=dict() #holds the IP and port of nodes that are contained at the finger table
 ip=''
 port=-1
 id_=-1
 m=-1 #number of bits of the identifiers
 found=False 
 #a list that has the form [file_id,init_node]. 
 #Init node contains the information ip:port. Need it to achieve the communication 
 #between the node that has the file and the node that initiated the file query. In case the node happens  
 #to have the file, it adds a third element in the list, the communication info for the first node to communicate with the file owner.
 msg=list() 
 recipient='' #node id from the node that will receive the message
 q_answer=-1 #ip:port of the init node, this node has the requested file
	
	
 def __init__(self,ip_,port_,id__,m_):
  self.ip=ip_
  self.port=port_
  self.id_=id__
  self.fin=list()
  self.msg=list()
  self.fin_tr=dict()
  self.m=m_
  self.file_reqs=dict()
  self.recipient=-1
  self.q_answer=-1
  self.msg_routed=0

 def look_up(self,file_):
  ''' look up at the nodes of the ring for a file'''
  import main
  file_id=files.generate_hash_name(file_)
  #Check whether the file is between the node and his predecessor.We also include the case where predecessor is the last node 
  #and current node is the first one.If it is, return -1 so the query initiates from another node because this one already has that file.
  if (self.id_> self.pred[0] and self.pred[0]<file_id<=self.id_) or (self.id_<self.pred[0] and (self.pred[0]<file_id or self.id_>=file_id)):
   return -1
   #Else,find the next node that should search for the file.
  succ=self.find_successor(file_id,self.id_,str(self.ip)+':'+str(self.port))
  return 0

 def check_msg(self):
  ''' check the msg has been set for this node. The msg defines if the Query found or you have to continue with the successor node'''
  msg=shr_mem.share_memory.read_msg(str(self.ip)+':'+str(self.port))
  if msg=='':
   return
  elif msg[1]==str(self.ip)+':'+str(self.port):
   #If node's id and port are equal to the second item of the message,the response reached the original node.
   #Return the node that had the file with that id.
   return (msg[2],self.id_)
  else:
   #Increase counter for the desired file.Otherwise, create it.
   if msg[0] in self.file_reqs.keys():
    self.file_reqs[msg[0]]+=1
   else:
    self.file_reqs[msg[0]]=1
   #Continue searching for file by finding the successor of the node.
   self.find_successor(msg[0],self.id_,msg[1])

 def send_msg(self):
  ''' Define the type of msg that is goint to be sent.
  1st case: this message is the answer to the original query. 
  2nd case: this message will be forwarded to the next node.'''
  if self.q_answer!=-1:
   shr_mem.share_memory.c_ip=self.q_answer.split(':')[0]
   shr_mem.share_memory.c_port=self.q_answer.split(':')[1]
   shr_mem.share_memory.send_msg(self.msg,self.q_answer)
   self.q_answer=-1
   self.msg=[]
   self.msg_routed+=1
  elif self.recipient!=-1:
   recipient_addr=self.fin_tr[self.recipient]
   shr_mem.share_memory.c_ip=recipient_addr.split(':')[0]
   shr_mem.share_memory.c_port=recipient_addr.split(':')[1]
   shr_mem.share_memory.send_msg(self.msg,recipient_addr)
   self.recipient=-1
   self.msg_routed+=1
   self.msg=[]
  	
   		
 def find_successor(self,file_id,current_node_id,init_node):
  ''' find the successor node'''
  import main
  successor=self.succ[0]
  #Check whether the file is between the node and his predecessor.We also include the case where predecessor is the last node 
  #and current node is the first one.With that check,this node will inform the initial node that he has the file requested.
  if (self.id_> self.pred[0] and self.pred[0]<file_id<=self.id_) or (self.id_<self.pred[0] and (self.pred[0]<file_id or self.id_>=file_id)):
   self.q_answer=init_node
   self.msg=[file_id,init_node,self.id_]
  #Check whether the file is between the node and his successor.We also include the case where successor is the first node 
  #and current node is the last one.
  elif ((current_node_id<successor and current_node_id<file_id<=successor) or (current_node_id>successor and (current_node_id<file_id or file_id<=successor))):
   self.msg=[file_id,init_node]
   self.recipient=successor 
  #Otherwise,find the next node that will continue the search for the query
  else:
   n2=self.closest_preceding_node(file_id,current_node_id)
   self.msg=[file_id,init_node]
   self.recipient=n2 
  shr_mem.share_memory.s_ip=self.ip
  shr_mem.share_memory.s_port=self.port
     
 def closest_preceding_node(self,file_id,current_node_id):
  '''find the closest preceding node'''
  '''The following lines is the variation of the algorithm we thought. In case the file id is smaller than current node id we find the 
     max node from the finger table.By that, we speed up the process of searching because the search will be driven to finish the cycle
     and start searching from nodes with id close to zero.(e.g. current node id is 8 and search for file 5 . Go to max neighbor of 8 and
     send the message to him.If the same condition applies to him also,the he will forward it to his max node id from the finger table
     and so on. We will reach a node with id less than 5 but bigger from 0 so the search will continue from there much faster than leaving
     the original algorithm execute as it will proceed to the successor node until it reaches a node greater than zero.
     
  
  if file_id<current_node_id:
   max=-1
   for neighbor in self.fin:
    if neighbor<max:
     return max
    else:
     max=neighbor'''
     
  #check the finger table from the end
  for i in range(self.m-1,0,-1):
   if current_node_id<self.fin[i] and file_id>self.fin[i]:
    return self.fin[i]
  return self.succ[0]
  
        

