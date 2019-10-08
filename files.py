import hashlib
import init_func
from scipy.stats import powerlaw

def read_file(name,n_f):
    with open(name) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    temp=content[0:n_f]
    return temp 
    
    
        
def distribute_files(file_list,dht,m,n_f,node_number):
    ''' distribute the files at the nodes of the ring based on theirs key (id) after hasing their names
    popularity= the value that calculated from powerlaw.rvs, take the first 5 digits. As popularity at that point
    is a float number, it willl be multiplied by 100.
    At the end we roundup the value. Popularity=round(power_law*(100))'''
    files={}
    r=powerlaw.rvs(0.75, size=n_f)
    popularity=[float(str(x)[:5]) for x in r]
    for ind,i in enumerate(file_list):
        pop=popularity[ind]*(100)
        pop=round(pop)
        files[generate_hash_name(i)]=[i,int(pop)]     
    return files 
                
            
        
def generate_hash_name(name):
    ''' hash finction:sha1 has been also used also for the nodes of the chord ring. The hasing value here is the name of the file'''
    hash_object = hashlib.sha1(name)
    hex_dig = hash_object.hexdigest()
    dec_dig=int(hex_dig, 16)   
    bin_dig=format(dec_dig,'b')
    dec_dig=int(bin_dig,2)
    return dec_dig
    
    
     
