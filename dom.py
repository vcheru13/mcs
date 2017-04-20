# domain related stuff
from lxml import etree

class domain():
    """
    Holds domain info, needs XMLDesc() output as param
    """
    def __getdom_name(self,dElt):
        return dElt.xpath('/domain/name')[0].text

    def __getdom_type(self,dElt):
        return dElt.xpath('/domain')[0].attrib['type']

    def __getdom_ostype(self,dElt):
        return dElt.xpath('/domain/os/type')[0].text

    def __getdom_uuid(self,dElt):
        return dElt.xpath('/domain/uuid')[0].text

    def __getdom_mem(self,dElt):
        memUnit = dElt.xpath('/domain/memory')[0].attrib['unit']
        mem = dElt.xpath('/domain/memory')[0].text
        return mem + memUnit

    def __getdom_vcpu(self,dElt):
        return dElt.xpath('/domain/vcpu')[0].text

    def __getdom_disks(self,dEdit):
        return True

    def __init__(self,domxmlspec):
        dElt = etree.fromstring(domxmlspec)
        self.name =     self.__getdom_name(dElt)
        self.type =     self.__getdom_type(dElt)
        self.ostype =   self.__getdom_ostype(dElt)
        self.uuid =     self.__getdom_uuid(dElt)
        self.memory =   self.__getdom_mem(dElt)
        self.vcpu =     self.__getdom_vcpu(dElt)
        self.disks  =   self.__getdom_disks(dElt)

    def __repr__(self):
        "Return domain info as string"
        details = {
                'name': self.name,
                'type': self.type,
                'ostype': self.ostype,
                'uuid': self.uuid,
                'memory': self.memory,
                'vcpu': self.vcpu,
                'disks': self.disks
                }
        return str(details)

    def info(self):
        "Return domain info as hash"
        details = {
                'name': self.name,
                'type': self.type,
                'ostype': self.ostype,
                'uuid': self.uuid,
                'memory': self.memory,
                'vcpu': self.vcpu,
                'disks': self.disks
                }
        return details
