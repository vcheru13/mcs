# domain related stuff
from lxml import etree

class Domain():
    '''
    Holds domain info
    '''
    def __getdom_ostype(self):
        return self.xmlEt.xpath('/domain/os/type')[0].text

    def __getdom_vcpu(self):
        return self.xmlEt.xpath('/domain/vcpu')[0].text

    def __getdom_disks(self):
        if self.name == 'Domain-0':
            return False
        disk_dev = self.xmlEt.xpath('/domain/devices/disk/source')[0].attrib['dev']
        disk = self.xmlEt.xpath('/domain/devices/disk/target')[0].attrib['dev']
        return disk + ':' + disk_dev

    def __getdom_mac(self):
        if self.name == 'Domain-0':
            return False
        return self.xmlEt.xpath('/domain/devices/interface/mac')[0].attrib['address']

    def updatestate(self,dominfo):
        states = { 0: 'shutdown', 1: 'running' }
        self.state = states[dominfo.isActive()]

    def __init__(self,dominfo):
        '''
        Create domain object based on 'dominfo' : 
            - if it's libvirt.virDomain instance, get domain info from there and populate
            - if it's a JSON object, create a new domain 
        '''
        if isinstance(dominfo,libvirt.virDomain):
            'Gather domain info from object'
            self.name = dominfo.name()
            self.type = dominfo.OSType()
            self.memory = dominfo.maxMemory()
            self.uuid = dominfo.UUIDString()
            self.xmlEt = etree.fromstring(dominfo.XMLDesc())
            self.ostype =   self.__getdom_ostype()
            self.vcpu =     self.__getdom_vcpu()
            self.disks  =   self.__getdom_disks()
            self.mac  =     self.__getdom_mac()
            self.updatestate(dominfo)
        elif  isinstance(dominfo,dict):
            'Create domXML based on json dict'
            pass
                   

    def __repr__(self):
        'Return domain info as string'
        details = {
                'name': self.name,
                'state': self.state,
                'type': self.type,
                'ostype': self.ostype,
                'uuid': self.uuid,
                'memory': self.memory,
                'vcpu': self.vcpu,
                'mac': self.mac,
                'disks': self.disks
                }
        return str(details)

    def info(self):
        'Return domain info as hash'
        details = {
                'name': self.name,
                'state': self.state,
                'type': self.type,
                'ostype': self.ostype,
                'uuid': self.uuid,
                'memory': self.memory,
                'vcpu': self.vcpu,
                'mac': self.mac,
                'disks': self.disks
                }
        return details
