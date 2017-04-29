#!/usr/bin/python
# { memoryMB: 1024, name: ubun2, osdiskGB: 16, osimage: ubuntu-1604, vcpu: 2 }

from pprint import pformat as pf
from lxml import etree
import json

def createdomxml(config):
    "Return domain config in XML format for libvirt"
    if __isnameinuse(config['name']):
        return False
    if not __createdisk(config['osdiskGB']):
        return False
    # Build domain XML now
    domroot = etree.Element('domain',attrib={'type': 'xen'})    # root element, always xen type for now
    nmElt = etree.SubElement(domroot,'name')
    nmElt.text = config['name']
    memElt = etree.SubElement(domroot,'memory',attrib={'unit': 'KiB'})
    memElt.text = str(int(config['memoryMB']) * 1024)
    cpuElt = etree.SubElement(domroot,'vcpu',attrib={'placement': 'static'})
    cpuElt.text = str(config['vcpu'])
    osElt = etree.SubElement(domroot,'os')
    osTypeElt = etree.SubElement(osElt,'type',attrib={'arch': 'x86_64','machine': 'xenpv'})
    osTypeElt.text = 'linux'
    osCmdElt = etree.SubElement(osElt,'cmdline')
    osCmdElt.text = 'modules=loop,squashfs console=hvc0'
    # devices
    devElt = etree.SubElement(domroot,'devices')
    #disk
    diskElt = etree.SubElement(devElt,'disk',attrib={'type': 'block'})
    diskSrc = etree.SubElement(diskElt,'source',attrib={'dev': '/dev/xenvg/lv_' + config['name'].lower()})
    diskTarget = etree.SubElement(diskElt,'target',attrib={'dev': 'xvda','bus': 'xen'})
    # nic
    nicElt = etree.SubElement(devElt,'interface',attrib={'type': 'bridge'})
    nicSrc = etree.SubElement(nicElt,'source',attrib={'bridge': 'xenbr0'})
    nicMac = etree.SubElement(nicElt,'mac',attrib={'address': getmac() })
    # tty
    ttyElt = etree.SubElement(devElt,'console',attrib={'type': 'pty'})
    ttyTarget = etree.SubElement(ttyElt,'target',attrib={'type': 'xen','port': '0'})
    # metadata for the domain
    metaElt = etree.SubElement(domroot,'metadata')
    imageElt = etree.SubElement(metaElt,'osimage')
    imageElt.text = config['osimage']

    return etree.tostring(domroot,pretty_print=True)


def getmac():
    #00:16:3e:xx:xx:xx.
    return '00:16:3e:00:00:01'

def __createdisk(diskGB):
    return True

def __isnameinuse(domnanme):
    "check domnames on the host"
    return False


x = {u'memoryMB': 1024, u'vcpu': 2, u'osdiskGB': 16, u'name': u'ubun2', u'osimage': u'ubuntu-1604'}
print createdomxml(x)
