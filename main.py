import init_func
from share_memory import share_memory
import hashlib
import files
import random
import sys
import collections
import numpy as np
from collections import Counter

if __name__ == "__main__":
 temp_avg_msg=0
 temp_avg_msg_all=0
 temp_avg_file_reqs=0
 temp_avg_file_reqs_all=0
 temp_hops=[]
 temp_hops_avg=0
 times=-1
 #load arguments from command line
 node_number=int(sys.argv[1])
 n_files=342884
 m=160 #160 bits becuase of sha1 hash function
 file_msg=dict()
 #how many queries
 query_load=int(sys.argv[2])
 #execution home many executions in the network
 execution=int(sys.argv[3]) 
 print '=========================================CHORD RING=============================='
 print 'Arguments:nodes=',node_number,' ,m=',m,' ,query_load=', query_load,' ,execution=',execution
 print '=========================================INIT===================================='
 print 'About to initialize ring.'
 dht=init_func.init_hashing_ring(node_number,m)
 print 'Updating contacts.'
 init_func.update_contacts_list(dht,m)
 tr_sorted = list(collections.OrderedDict(sorted(init_func.tr.items())))
 print 'Ring initialized with ',len(tr_sorted), 'nodes'
 shr_mem=share_memory()
 print 'Initialize and distribute files.'
 files_lst=files.read_file('filenames.txt',n_files)
 files_dict=files.distribute_files(files_lst,dht,m,n_files,node_number)
 print '=====================================END INIT====================================='
 n_number=len(init_func.ids)
 f_number=len(files_lst)
 check=0
 results_avg_msg=[]
 results_avg_msg_all=[]
 results_avg_file_reqs=[]
 results_avg_file_reqs_all=[]
 results_avg_hops=[]
 results=[]
 simulation_run=0
 for ing in range(execution):
  for q in range(query_load):
   val=-1
   #search for a random file
   fn=random.randint(0,f_number-1)
   #check how many time this file is requested according its popularity from law distribution
   file_name_hashed=files.generate_hash_name(files_lst[fn])
   file_times_requested=files_dict[file_name_hashed]
   while file_times_requested[1]==0:
    fn=random.randint(0,f_number-1)
    #check how many time this file is requested according its popularity from law distribution
    file_name_hashed=files.generate_hash_name(files_lst[fn])
    file_times_requested=files_dict[file_name_hashed]
   print 'Execution number:',ing,'|query number:',q,'|requested:',file_times_requested[1]
   nn=node=file_=0
   for freq in range (1,int(file_times_requested[1])+1):
    val=-1
    while(val==-1):
    #Get a random node that will lookup for a file.We need to have the ip:port in order to enable the lookup
    #so the translation dictionary we have serves that purpose.Also get a random file to search for based on power law
    #distribution.While case is in case the file is already on that node so the node must be changed( e.g. a node initiates a file
    #query for a file he already has).
     nn=random.randint(0,n_number-1)
     #the ip and port  for that node
     node=init_func.tr[init_func.ids[nn]]
     #search for this file
     file_=files_lst[fn]
     #search for file_ starting from node node.Return -1 means the node originally holds that file so we should re run the procedure.
     val=dht[node].look_up(file_) 
     
    k=0
    for key in init_func.ids:
     if init_func.tr[key]==node:
      k=key
      break
    i=0
    found=False
    prev=file_
    #Search in rounds until the init node gets contacted for the requested file.
    while  found ==False:
    #If result is different to none it means that the initial node received a message that contains information about the ip and
    #the port of the node that has the file.
     result=share_memory.check(dht)
     if result!=None:
      found=True
      #print 'Query answered after ',i,' steps.Node ',result[1],' requested file ',file_,'-',files.generate_hash_name(file_),' and node ',result[0],' had that file.'
      file_msg[file_]=i
      break
     if found==False:
      result=share_memory.send(dht)
     i+=1
    hops=0
    for key in file_msg.keys():
     hops+=file_msg[key]
     file_msg[key]=0
    avg_msg=0
    num_of_nodes_with_msgs=0
    avg_file_reqs=0

    for nd in dht:
     for key in dht[nd].file_reqs.keys():
      #sum all the reqs happened at the ring
      avg_file_reqs+=dht[nd].file_reqs[key]  
     #sum the nodes that routed at least one msg
     if dht[nd].msg_routed!=0:
      num_of_nodes_with_msgs+=1
     dht[nd].file_reqs[key]=0
     #sum the messages routed at the ring
     avg_msg+=dht[nd].msg_routed
     
    dht[nd].msg_routed=0
    
    if num_of_nodes_with_msgs!=0:
     results.append([avg_msg/float(num_of_nodes_with_msgs),avg_file_reqs/float(num_of_nodes_with_msgs),hops, avg_msg/float(node_number),avg_file_reqs/float(node_number)])
    #print '================================MEASUREMENTS PER EXECUTION================================'
    temp_avg_msg=0
    temp_avg_msg_all=0
    temp_avg_file_reqs=0
    temp_avg_file_reqs_all=0
    temp_hops=[]
    temp_hops_avg=0
    times=-1
    for ind,entry in enumerate(results):
     temp_avg_msg+=entry[0]
     temp_avg_file_reqs+=entry[1]
     temp_hops.append(entry[2])
     temp_hops_avg+=entry[2]
     temp_avg_msg_all+=entry[3]
     temp_avg_file_reqs_all+=entry[4]
     
 #all executions are completed, sum up the lists
 results_avg_msg.append(temp_avg_msg)
 results_avg_msg_all.append(temp_avg_msg_all)
 results_avg_file_reqs.append(temp_avg_file_reqs)
 results_avg_file_reqs_all.append(temp_avg_file_reqs_all)
 #find the median num of hops
 results_hops=np.median(temp_hops)
 #to compare which measurement is betetr
 results_avg_hops.append(temp_hops_avg)
 hops_mode = Counter(temp_hops)
 #how many reqs executed 
 simulation_run+=len(results)
 

 print '================================MEASUREMENTS AFTER ALL EXECUTIONS================================'
 if simulation_run>0:
  final_avg_msg=sum(results_avg_msg)/float(simulation_run)   
  final_avg_msg_all=sum(results_avg_msg_all)/float(simulation_run)   
  final_avg_file_reqs=sum(results_avg_file_reqs)/float(simulation_run) 
  final_avg_file_reqs_all=sum(results_avg_file_reqs_all)/float(simulation_run) 
  final_hops_avg=sum(results_avg_hops)/float(simulation_run) 
  
  print 'After ',simulation_run, 'turns we got: AVG MSG PER NODE =',final_avg_msg,' ---AVG MSG PER ALL NODES =',final_avg_msg_all
  print ' ---AVG FILE REQS PER NODE=',final_avg_file_reqs,' ---AVG FILE REQS PER ALL NODES=',final_avg_file_reqs_all,' --- HOPS=',results_hops, '---AVG HOPS=', final_hops_avg, '---MODE HOPS', hops_mode.most_common(1)
 
  

