#!/usr/bin/python

import libvirt
from lxml import etree
import json
import sys
from random import randint as ri

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
    

### Main 
pkipath = config.PKIPATH    # PKI Certificates path 
xen_hosts = {}              # Initialize hash to store all info on Xen hosts and domains

# collect/update Xen hosts information on import
mcs_gethosts('0.0')

# Main function
if __name__ == '__main__':
    print xen_hosts

