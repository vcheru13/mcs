#!/usr/bin/python

import libvirt
from lxml import etree
import json
import sys
from pprint import pformat as pf
from dom import *
from random import randint as ri

# All mac DB - for Xen guests
macdb = '.mcs_mac_db'

# Hash to store xen guest macs
allmacs = {} 

def readmacdb():
    with open(macdb) as mb:
        for l in mb:
            if l:
                allmacs[l.strip()] = ''

# read macs from db 
readmacdb()

# Hash to store Xen host connections
host_conn_hash = {}

#store all xen host/domain info
# { h: { 'sysinfo': 'sysinfo like uuid', 'domains': 'list of domains/objects' } 
#  } 
xen_hosts = {}

def mcs_gethosts(version,hosts):
    "Get info for all Xen hosts in hosts"
    for h in hosts:
        if h in host_conn_hash:
            conn = host_conn_hash[h]
        else:
            # connect using SSH for now (make sure to setup keys) - should change to TLS via certs
            name = 'xen+ssh://' + h + '/'
            conn = libvirt.open(name=name)
            if conn is None:
                print('Failed to connect to Xen host:' + name )
                sys.exit(1)
            else:
                # update connection cache
                host_conn_hash[h] = conn
        parse_sysinfo(h,conn.getSysinfo())
    return jsonp(xen_hosts)


def mcs_gethost(version,hname):
    "Return host info"
    if hname in xen_hosts:
        return jsonp({hname: xen_hosts[hname]})
    else:
        return jsonp({ hname: 'Not found' })


def mcs_getdomains(version,hname):
    "Return all domains on host hname"
    if hname not in xen_hosts:
        return jsonp({ hname: 'Not found' })
    else:
        domains = populate_domains(hname)
        return jsonp({ hname: domains })

def mcs_getdomain(version,hname,domname):
    "Return domain info on host hname"
    if hname not in xen_hosts:
        return jsonp({ hname: 'Not found' })
    else:
        if domname not in xen_hosts[hname]['dominfo']:
            return jsonp({ domname: 'Not found on ' + hname })
        else:
            return jsonp({ hname: xen_hosts[hname]['dominfo'][domname] })

def populate_domains(hname):
    "Populate domains in xen_hosts[hname] and return domain names"
    conn = host_conn_hash[hname]
    doms = conn.listAllDomains()
    xen_hosts[hname]['domains'] = doms
    # initialize 'dominfo'
    xen_hosts[hname]['dominfo'] = {}
    for dom in doms:
        domobj = domain(dom.XMLDesc())
        xen_hosts[hname]['dominfo'][domobj.name] = domobj.info()
    return xen_hosts[hname]['dominfo'].keys()
       

def mcs_createdomain(version,hname,domname,domjson):
    "Create a domain, if not already present"
    if __is_dom_inuse(hname,domjson['name']):
        return False
    newdomxml = createdomxml(domjson)
    conn = host_conn_hash[hname]
    conn.defineXML(newdomxml)
    return newdomxml


def jsonp(s):
    "Pretty print json"
    return str(json.dumps(s,sort_keys=True,separators=(',',': '),indent=4))
    #return '<pre>' + str(json.dumps(s,sort_keys=True,separators=(',',': '),indent=4)) + '</pre>'

def parse_sysinfo(h,sys_info):
    "Parse sysinfo and store result in xen_hosts"
    doc = etree.fromstring(sys_info)
    si = doc.find('system')
    uuid = [ e.text for e in si.getchildren() if e.items() == [('name','uuid')] ] [0]
    s_info = { 'sysinfo': { 'uuid': uuid } }
    xen_hosts[h] = s_info

def createdomxml(config):
    "Return domain config in XML format for libvirt"
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
    nicMac = etree.SubElement(nicElt,'mac',attrib={'address': getnextmac() })
    # tty
    ttyElt = etree.SubElement(devElt,'console',attrib={'type': 'pty'})
    ttyTarget = etree.SubElement(ttyElt,'target',attrib={'type': 'xen','port': '0'})
    # metadata for the domain
    metaElt = etree.SubElement(domroot,'metadata')
    imageElt = etree.SubElement(metaElt,'osimage')
    imageElt.text = config['osimage']
    return etree.tostring(domroot,pretty_print=True)

def __createdisk(diskGB):
    return True

def __is_dom_inuse(hname,domname):
    "check if domname is in use on the host"
    if domname in xen_hosts[hname]['dominfo']:
        return True
    else:
        return False


def getnextmac():
    "Generate random macs in range 00:16:3e:xx:xx:xx - used by Xen"
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

# Main
if __name__ == '__main__':
    print mcs_gethosts('v1.0',['myxen'])

