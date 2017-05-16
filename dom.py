# domain related stuff
from lxml import etree
import libvirt
import config
from random import randint as ri

macdb = config.MACDB        # MAC database for guest domains
allmacs = {}                # Hash to store Xen guest MAC's

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
            self.birth = 0
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
            '''
            Create domXML based on dict, ex format below: 
            
            {   u'memoryMB': 1024, 
                u'vcpu': 2, 
                u'osdiskGB': 16, 
                u'name': u'ubun2', 
                u'osimage': u'ubuntu-1604',
                u'pool': u'xenvg'
            }
            '''
            self.birth = 1
            self.type   = 'xen'
            self.Et     = etree.Element('domain',attrib={'type': 'xen'})
            self.name   = self.__setdom_name(dominfo)
            self.ostype = self.__setdom_ostype(dominfo)
            self.memory = self.__setdom_mem(dominfo)
            self.vcpu   = self.__setdom_vcpu(dominfo)
            self.disks  = self.__setdom_disks(dominfo)
            self.mac    = self.__setdom_mac(dominfo)
            self.__setdom_metadata(dominfo)
            self.state  = 0
            self.xmlEt  = etree.tostring(self.Et,pretty_print=True)
        else:
            print 'Error in argument' 
                   

    def __setdom_name(self,dominfo):
        nmElt = etree.SubElement(self.Et,'name')
        nmElt.text = dominfo['name']
        return dominfo['name']

    def __setdom_mem(self,dominfo):
        memElt = etree.SubElement(self.Et,'memory',attrib={'unit': 'KiB'})
        memElt.text = str(int(dominfo['memoryMB']) * 1024)
        return str(int(dominfo['memoryMB']) * 1024)
    
    def __setdom_vcpu(self,dominfo):
        cpuElt = etree.SubElement(self.Et,'vcpu',attrib={'placement': 'static'})
        cpuElt.text = str(dominfo['vcpu'])
        return str(dominfo['vcpu'])
    
    def __setdom_ostype(self,dominfo):
        osElt = etree.SubElement(self.Et,'os')
        osTypeElt = etree.SubElement(osElt,'type',attrib={'arch': 'x86_64','machine': 'xenpv'})
        osTypeElt.text = 'linux'
        osCmdElt = etree.SubElement(osElt,'cmdline')
        osCmdElt.text = 'modules=loop,squashfs console=hvc0'
        return 'linux'
        
    def __setdom_disks(self,dominfo):
        # devices
        devElt = etree.SubElement(self.Et,'devices')
        #disk
        diskElt = etree.SubElement(devElt,'disk',attrib={'type': 'block'})
        diskSrc = etree.SubElement(diskElt,'source',attrib = {                                                    
            'dev': '/dev/' + dominfo['pool'] + '/' + self.name.lower() + '-vol0' 
                } )
        diskTarget = etree.SubElement(diskElt,'target',attrib={'dev': 'xvda','bus': 'xen'})
        return 'xvda:' + '/dev/' + dominfo['pool'] + '/' + self.name.lower() + '-vol0'
        
        
    def __setdom_mac(self,dominfo):
        devElt = self.Et.find('devices')    
        # nic
        nicElt = etree.SubElement(devElt,'interface',attrib={'type': 'bridge'})
        nicSrc = etree.SubElement(nicElt,'source',attrib={'bridge': 'xenbr0'})
        mac = getnextmac()
        nicMac = etree.SubElement(nicElt,'mac',attrib={'address': mac })
        return mac
    
    def __setdom_others(self,dominfo):
        devElt = self.Et.find('devices')
        # tty
        ttyElt = etree.SubElement(devElt,'console',attrib={'type': 'pty'})
        ttyTarget = etree.SubElement(ttyElt,'target',attrib={'type': 'xen','port': '0'})
        
    def __setdom_metadata(self,dominfo):
        # metadata for the domain
        metaElt = etree.SubElement(self.Et,'metadata')
        imageElt = etree.SubElement(metaElt,'osimage')
        imageElt.text = dominfo['osimage']

    def info(self):
        'Return domain info as hash'
        if self.birth:
            uuid = 'New'
        else:
            uuid = self.uuid
            
        details = {
                'name': self.name,
                'state': self.state,
                'type': self.type,
                'ostype': self.ostype,
                'uuid': uuid,
                'memory': self.memory,
                'vcpu': self.vcpu,
                'mac': self.mac,
                'disks': self.disks
                }
        
        return details
    

def readmacdb():
    'Read MAC addresses from config.MACDB into hash'
    with open(macdb) as mb:
        for l in mb:
            if l:
                allmacs[l.strip()] = ''

def getnextmac():
    'Generate random macs in range 00:16:3e:xx:xx:xx - used by Xen'
    nextmac = '00:16:3e:00:' + hex(ri(0,256)).strip('0x') + ':' + hex(ri(0,256)).strip('0x')
    if nextmac not in allmacs:
        with open(macdb,'a') as mb: # append new mac at the end of file and in hash
            mb.write(nextmac + '\n')
            allmacs[nextmac] = ''
        mb.close()
        return nextmac
    else:
        #print 'Found duplicate, re-generating'
        return getnextmac()


