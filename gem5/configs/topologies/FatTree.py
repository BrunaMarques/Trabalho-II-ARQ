# -*- coding: utf-8 -*-
# Copyright (c) 2010 Advanced Micro Devices, Inc.
#               2016 Georgia Institute of Technology
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Brad Beckmann
#          Tushar Krishna

from __future__ import print_function
from __future__ import absolute_import

from m5.params import *
from m5.objects import *

from common import FileSystemConfig

from .BaseTopology import SimpleTopology
from math import log

# Creates a generic Mesh assuming an equal number of cache
# and directory controllers.
# XY routing is enforced (using link weights)
# to guarantee deadlock freedom.

class FatTree(SimpleTopology):
    description='FatTree'

    def __init__(self, controllers):
        self.nodes = controllers

    # Makes a generic Butterfly
    # assuming an equal number of cache and directory cntrls

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        num_cpus = options.num_cpus
        nodes = self.nodes

        num_routers = 2*num_cpus-1
        num_levels = int(log(num_cpus, 2))+1
        print("num_levels: "+ str(num_levels))
        print("num_routers: "+ str(num_routers))# default values for link latency and router latency.
        # Can be over-ridden on a per link/router basis
        link_latency = options.link_latency # used by simple and garnet
        router_latency = options.router_latency # only used by garnet


        # There must be an evenly divisible number of cntrls to routers
        # Also, obviously the number or rows must be <= the number of routers
        cntrls_per_router, remainder = divmod(len(nodes), num_cpus)
        

        # Create the routers in the mesh
        routers = [Router(router_id=i, latency = router_latency) for i in range(num_routers)]  
        network.routers = routers

        # link counter to set unique link ids
        link_count = 0
        # Add all but the remainder nodes to the list of nodes to be uniformly
        # distributed across the network.
        network_nodes = []
        remainder_nodes = []
        for node_index in range(len(nodes)):
            if node_index < (len(nodes) - remainder):
                network_nodes.append(nodes[node_index])
            else:
                remainder_nodes.append(nodes[node_index])
        # Connect each node to the appropriate router
        ext_links = []
        router_id = 0
        print(str(len(network_nodes)))
        print(str(len(routers)))
        cont = 0
        for i in range(len(network_nodes)//3):
            for j in range (3):
                print(network_nodes[int(i+j*num_cpus)])
                ext_links.append(ExtLink(link_id=link_count, ext_node=network_nodes[int(i + j*num_cpus)],
                                   	int_node=routers[int(router_id)],
                                     	latency = link_latency))
                link_count += 1
                if j==2:
                    print (str(router_id))
                    router_id += 2

        network.ext_links = ext_links        
        
        # Create the mesh links.
        int_links = []
        div_mod = num_cpus
        for level in range(num_levels):
            cont = 0
            router_id = int(2**level)
            if (level < num_levels - 1):
                for router in range(int(2**(num_levels-level - 1))):
                    if (level != 0): #Se o id do router está na metade esquerda do nivel 
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
                     #Se o id do router está na metade direita do nivel 
                
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
            else: #Se o id do router está no último nível
               	
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
    # Register nodes with filesystem
    def registerTopology(self, options):
        for i in xrange(options.num_cpus):
            FileSystemConfig.register_node([i],
                    MemorySize(options.mem_size) / options.num_cpus, i)
