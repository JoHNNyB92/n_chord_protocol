class share_memory:
 shr = {}
 #In order to improve the speed of the execution,we store the information for each round based 
 #on the node responsible to send and check for messages. With that, instead of iterating through all the nodes
 #, we specifically call the only send/check that should be called.
 s_ip=-1 #sender ip
 s_port=-1 #sender port
 c_ip=-1 #checker ip
 c_port=-1 #checker port
 
 @staticmethod
 def send(dht):
  '''Call specifically the node that should send new message.'''
  if share_memory.s_port!=-1 and share_memory.s_ip!=-1:
   ret=dht[share_memory.s_ip+':'+share_memory.s_port].send_msg()
   share_memory.s_port=-1
   share_memory.s_ip=-1
   return ret

 @staticmethod
 def check(dht):
  '''Call specifically the node that should check for new messages.'''
  if share_memory.c_port!=-1 and share_memory.c_ip!=-1:
   ret=dht[share_memory.c_ip+':'+share_memory.c_port].check_msg()
   share_memory.c_port=-1
   share_memory.c_ip=-1
   return ret 
 
 @staticmethod
 def send_msg(msg, to):
  '''Write a message for a node at the appropriate area that has been set for this node.'''
  share_memory.shr[to] = msg
  
 @staticmethod
 def read_msg(to):
  '''Return the context that is saved on share_memory for a node.'''
  if to in share_memory.shr.keys():
   temp = share_memory.shr[to]
   del share_memory.shr[to]
   return temp
  else:
   return ''



			
