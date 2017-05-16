#!/usr/bin/python
#
# Contain Xenhost class

class Xenhost():
    '''
    class to hold information for a Xen host and it's domains, storage and networks
    '''
    def __init__(self,hconn):
        self.name = hconn.getHostname()
        self.freeMem = hconn.getFreeMemory()
        self.maxGuestCpus = hconn.getMaxVcpus('xen')
        self.domains = {}
        self.storage_pools = {}
        self.networks = {}
        
        
        


