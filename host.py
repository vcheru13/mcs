#!/usr/bin/python
from dom import Domain,createVolXML

# Xenhost class 
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
        
        
    def detailedinfo(self):
        'Return detailed host info'
        details = { 
                   'name': self.name,
                   'freeMemMB': self.freeMem,
                   'maxCpusPerGuest': self.maxGuestCpus,
                   'domains': self.domains,
                   'storagePools': self.storage_pools
                   }
        return details
    
    def info(self):
        'Return host info'
        details = { 
                   'name': self.name,
                   'freeMemMB': self.freeMem,
                   'maxCpusPerGuest': self.maxGuestCpus
                   }
        return details
    
    
    def listdomains(self):
            return self.domains.keys()
        
    def updatedomain(self,dname):
        dom = Domain(self.conn.lookupByName(dname))
        dominfo = dom.info()
        self.domains[dom.name] = dominfo
        return dominfo 
    
    def definedomain(self,domjson):
        dname = domjson['name']
        pool = domjson['pool']
        dommem = int(domjson['memoryMB'])
        
        if dname in self.domains.keys():
            return 'error: domain ' + dname + ' already defined'
                    
        if pool not in self.storage_pools.keys():
            return 'error: pool ' + pool + ' not present on host ' + self.name
                    
        if dommem > self.getFreeMem():
            return 'error: requested memory not available on host ' + self.name
    
        srcvol = domjson['sourcevolume']
        if srcvol not in self.storage_pools[pool]:
            return 'error: source volume ' + volname + ' not present in pool ' + pool
                
        volname = dname.lower() + '-vol0'
        if volname in self.storage_pools[pool]:
            return 'error: volume ' + volname + ' already present in pool ' + pool
        
        # all good, so create volume on pool and define Domain
        volsize = domjson['osdiskGB']
        newvolxml = createVolXML(volname,volsize)         
        
        # get pool/source volume objects
        poolobj =  self.conn.storagePoolLookupByName(pool)
        srcvolobj = poolobj.storageVolLookupByName(srcvol)
        
        #clone vol - slow process atm
        # TODO: check volsize => has to be > srcvol size
        newvol = poolobj.createXMLFrom(newvolxml,srcvolobj)
        
        newdom = Domain(domjson)
        self.conn.defineXML(newdom.xmlEt)
        return self.updatedomain(dname)
    
    def startdomain(self,dname):
        return self.getdomainobj(dname).create()
    
    def stopdomain(self,dname):
        return self.getdomainobj(dname).destroy()
       
    def getdomaininfo(self,dname):
        self.updatedomain(dname)
        return self.domains[dname]
    
    def getdomainobj(self,dname):
        return self.conn.lookupByName(dname)
        
    def getFreeMem(self):
        # getFreeMemory() returns bytes, convert them to MB
        return  self.conn.getFreeMemory()/1024/1024
    
            
    
        
        
        
        


