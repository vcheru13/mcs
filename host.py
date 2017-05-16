#!/usr/bin/python
#
# Contain Xenhost class

from dom import Domain

class Xenhost():
    '''
    class to hold information for a Xen host and it's domains, storage and networks
    '''
    def __init__(self,hconn):
        'Init code'
        self.conn = hconn               # save connection info
        self.name = self.conn.getHostname()
        self.freeMem = self.getFreeMem()
        self.maxGuestCpus = self.conn.getMaxVcpus('xen')
        self.domains = { Domain(x).name: Domain(x).info() for x in self.conn.listAllDomains() }
        self.storage_pools = { p.name() : [ v.name() for v in p.listAllVolumes() ] for p in self.conn.listAllStoragePools() }
        self.networks = self.conn.listNetworks()
        
        
    def info(self):
        'Return host info'
        details = { 
                   'name': self.name,
                   'freeMem': self.freeMem,
                   'maxCpusPerGuest': self.maxGuestCpus,
                   'domains': str(self.domains),
                   'storagePools': str(self.storage_pools)
                   }
        
        return details
    
    
    def listdomains(self):
            return self.domains.keys()
        
    def updatedomain(self,dname):
        dom = Domain(self.conn.lookupByName(dname))
        self.domains[dom.name] = dom.info()
    
    def definedomain(self,domjson):
        dname = domjson['name']
        pool = domjson['pool']
        dommem = int(domjson['memoryMB'] * 1024)
        
        if dname in self.domains.keys():
            print 'error: domain ' + dname + ' already defined'
            return
        
        if pool not in self.storage_pools.keys():
            print 'error: pool ' + pool + ' not present on host ' + self.name
            return
        
        if mem > self.getFreeMem():
            print 'error: requested memory not available on host ' + self.name
            return
        # all good, so define Domain
        newdom = Domain(domjson)
        self.conn.defineXML(newdom.xmlEt)
        self.updatedomain(dname)
    
    def startdomain(self):
        pass
    
    def stopdomain(self):
        pass
    
    def getdomaininfo(self,dname):
        self.updatedomain(dname)
        return self.domains[dname]
        
    def getFreeMem(self):
        return  self.conn.getFreeMemory()   
    
        
        
        
        


