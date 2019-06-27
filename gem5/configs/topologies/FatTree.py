from __future__ import print_function
from __future__ import absolute_import

from m5.params import *
from m5.objects import *

from common import FileSystemConfig

from .BaseTopology import SimpleTopology
from math import log


class FatTree(SimpleTopology):
    description='FatTree'

    def __init__(self, controllers):
        self.nodes = controllers


    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        num_cpus = options.num_cpus
        nodes = self.nodes

        num_routers = 2*num_cpus-1
        num_levels = int(log(num_cpus, 2))+1
   
        link_latency = options.link_latency 
        router_latency = options.router_latency 


        cntrls_per_router, remainder = divmod(len(nodes), num_cpus)
        

        routers = [Router(router_id=i, latency = router_latency) for i in range(num_routers)]  
        network.routers = routers

        link_count = 0

        network_nodes = []
        remainder_nodes = []
        for node_index in range(len(nodes)):
            if node_index < (len(nodes) - remainder):
                network_nodes.append(nodes[node_index])
            else:
                remainder_nodes.append(nodes[node_index])

        ext_links = []
        router_id = 0

        cont = 0
        for i in range(len(network_nodes)//3):
            for j in range (3):
                ext_links.append(ExtLink(link_id=link_count, ext_node=network_nodes[int(i + j*num_cpus)],
                                   	int_node=routers[int(router_id)],
                                     	latency = link_latency))
                link_count += 1
                if j==2:
                    router_id += 2

        network.ext_links = ext_links        
        
        int_links = []
        div_mod = num_cpus
        for level in range(num_levels):
            cont = 0
            router_id = int(2**level)
            if (level < num_levels - 1):
                for router in range(int(2**(num_levels-level - 1))):
                    if (level != 0):
                        int_links.append(IntLink(link_id=link_count,
                    	                src_node=routers[router_id - 1],
                      	                dst_node=routers[router_id + int(2**(level-1)) - 1],
                                    	#src_outport="East",
                                      	#dst_inport="North",
                                        latency = link_latency))
                        link_count+=1
                        int_links.append(IntLink(link_id=link_count,
                            	        src_node=routers[router_id - 1],
                            	        dst_node=routers[router_id - int(2**(level-1)) - 1],
                            	        #src_outport="West",
                            	        #dst_inport="North",
                            	        latency = link_latency))
                        link_count+=1
                
		    if cont == 0:                     
                        int_links.append(IntLink(link_id=link_count,
                                	src_node=routers[router_id - 1],
                                	dst_node=routers[router_id + int(2**(level) )- 1],
                                	#src_outport="North",
                                	#dst_inport="West",
                                	latency = link_latency))
                        link_count += 1
                        cont = 1
                    else:            
                        int_links.append(IntLink(link_id=link_count,
                        	        src_node=routers[router_id - 1],
                                	dst_node=routers[router_id - int(2**(level))- 1],
                                	#src_outport="North",
                                	#dst_inport="East",
                                	latency = link_latency))                            
                 	link_count += 1
                        cont =0
                    router_id += int(2**(level+1))
                div_mod /= 2
            else:
               	
                int_links.append(IntLink(link_id=link_count,
                        	src_node=routers[router_id - 1],
                        	dst_node=routers[router_id + int(2**(level-1)) - 1],
                        	#src_outport="East",
                        	#dst_inport="North",
                        	latency = link_latency))
                link_count+=1
                int_links.append(IntLink(link_id=link_count,
                        	src_node=routers[router_id - 1],
                        	dst_node=routers[router_id - int(2**(level-1)) - 1],
                        	#src_outport="West",
                        	#dst_inport="North",
                        	latency = link_latency)) 
                link_count+=1
        network.int_links = int_links

    def registerTopology(self, options):
        for i in xrange(options.num_cpus):
            FileSystemConfig.register_node([i],
                    MemorySize(options.mem_size) / options.num_cpus, i)
