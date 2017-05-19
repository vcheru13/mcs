#!/usr/bin/python

import libvirt
from lxml import etree
import json
import sys
from random import randint as ri
from subprocess import Popen,PIPE

# Custom host/domain specifics
from host import Xenhost
# import global configuration
import config

def mcs_gethosts(version):
    'Get info for all Xen hosts in hosts'
    for h in config.HOSTS:
        # Connect using TLS Authentication
        name = 'xen://' + h + '/system?pkipath=' + pkipath
        conn = libvirt.open(name=name)
        xen_hosts[h] = Xenhost(conn)
    return jsonp(xen_hosts.keys())

def mcs_gethost(version,hname):
    'Return host info'
    if isValidHost(hname):
        return jsonp({hname: xen_hosts[hname].info()})
    else:
        return jsonp({ 'error': 'host not found' })

def mcs_getdomains(version,hname):
    'Return all domains on host hname'
    if isValidHost(hname):
        return jsonp({ hname: xen_hosts[hname].listdomains() })
    else:
        return jsonp({ 'error': 'host not found' })

def mcs_getdomain(version,hname,domname):
    'Return domain info on host hname'
    if isValidHost(hname) and isValidDomain(hname, domname):
        return jsonp({ domname: xen_hosts[hname].getdomaininfo(domname) })
    else:
        return jsonp({ 'error': 'host or domain not found' })
        
       
def mcs_createdomain(version,hname,domjson):
    'Create a domain, if not already present'
    if isValidHost(hname):
        return jsonp({ hname: xen_hosts[hname].definedomain(domjson) })
    else:
        return jsonp({ 'error': 'host not found' })
        
def mcs_updatedomain(version,hname,domname,command):
    'Update domain with given cmd, args'
    if isValidHost(hname) and isValidDomain(hname, domname):
        # known commands for now 'start' , 'stop'
        if command['cmd'] == 'start':
            return jsonp({ 'status': xen_hosts[hname].startdomain(domname) })
        elif command['cmd'] == 'stop':
            return jsonp({ 'status': xen_hosts[hname].stopdomain(domname) })
        else:
            return jsonp({ 'Command': command['cmd'] + ' unknown' })
    else:
        return jsonp({ 'error': domname + ' not found on '  + hname })

def isValidHost(hname):
    if hname in xen_hosts.keys():
        return True
    else:
        return False
    
def isValidDomain(hname,domname):
    if domname in xen_hosts[hname].listdomains() :
        return True
    else:
        return False

def jsonp(s):
    'Pretty print json'
    return json.dumps(s,sort_keys=True,separators=(',',': '),indent=4)


## Metadata 
def mcs_getinstancemeta(remoteip):
    inst_mac = getmacforip(remoteip)
    if inst_mac:
        # if IP found, update in domain first and retrive it's meta-data
        for h in xen_hosts:      # 
            for dom in xen_hosts[h].listdomains():
                if xen_hosts[h].domains[dom]['mac'] == inst_mac:
                    # add ip into domain info
                    print 'Found MAC ' +  xen_hosts[h].domains[dom]['mac'] + ' for IP:' + remoteip
                    xen_hosts[h].domains[dom] = xen_hosts[h].updatedomain(dom,remoteip)
                    print xen_hosts[h].domains[dom]
                    # Return meta data
                    inst_meta = { 
                                "uuid": xen_hosts[h].domains[dom]['uuid'],
                                "name": xen_hosts[h].domains[dom]['name'],
                                "hostname": xen_hosts[h].domains[dom]['name'] + '.lab.local',
                                "public_keys": {
                                    "mykey": 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC7+iDRImD7iezhz27xI4QYEjVhY2aKfjdQL1SxcIpn0TbZwWSTKIJb/gXavETQlASby4dxVOcFQKlwNHT2ZO5sjynJ8mdEuWsLTHxtFs3CFUUy0mp+pScLfpzg9VNj72uszFdbQgWxwFYn34zyavqqGkguPVEihx1B3T45678PUvbYKPijij40+v8rzQMx31AWoZZSsHPo/H1Jf3QppfrQt2J0vsF4tb7EMOKSyL5aQK4q6WA7KSMJKWOyA5o9FQ2khHDwVUgIMXxmuWzH4izcLd2v7mvzqaUYDbrFzQXR4qdUE6PiIt/e8mlMZQU2JUC4yHePqKw1MTlcCW0WtKkAv4U4Do7f8YLXivA7TMtooCsRDCsA/ID8oJJ6isAejgqucGp+tE3quxFN7tieRMKwIwfqIvmoObOvbnkqw5T7zBIspxdmTicfWejlvl+5JmLJiWimN+UiA8XWiAQkQ9WZ0Aw9P+EXj7oHL3atWdbj9/4cDf4HYZO6RVlC/nK292GVo+DpJt2w/AZ44NjSk+HOGGLlcBWGOSsVJnt+ToJUEdIRQjDQogAEqJC9qdPuf1y+iC4wdwsCqlVUBAWwyAYIKpbiGD1hLo40LdiFl1tXHJCBZiqCzJP1kXcnsOXk+6mbaTiBZm+dHIjvXarXjghrbjp8UnHifbj+cruNpuaeaQ==' }
                                }
                    return inst_meta
        return None

# Userdata
def mcs_getinstanceuser():
    return ""

# Fix 0's in MAC address
def fixmac(mac):
        'fix mac so, all 6 octets are 2 nibbles - esp 0'
        return ':'.join(map(lambda x: '0' + x if int('0x' + x,16) <= 16 else x , mac.split(':')))

# get MAC of metadata requester
def getmacforip(remoteip):
    'Return MAC of ip based on arp cache'
    arp_out = Popen(['arp','-an'],stdout=PIPE).communicate()[0].splitlines()
    knownmacs = { l.split()[1].lstrip('(').rstrip(')'):fixmac(l.split()[3]) for l in arp_out if not 'incomplete' in l }
    if remoteip in knownmacs.keys():
        return knownmacs[remoteip]
    else:
        return None


### Main 
pkipath = config.PKIPATH    # PKI Certificates path 
xen_hosts = {}              # Initialize hash to store all info on Xen hosts and domains
knownmacs = {}              # arp cache on host where this program is running

# collect/update Xen hosts information on import
mcs_gethosts('0.0')

# Main function
if __name__ == '__main__':
    print xen_hosts

