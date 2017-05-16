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
        if conn is None:
            print('Failed to connect to host:' + name )
            sys.exit(1)
        else:
            xen_hosts[h] = Xenhost(conn)
            
    return jsonp(xen_hosts.keys())

def mcs_gethost(version,hname):
    'Return host info'
    if hname in xen_hosts.keys():
        return jsonp({hname: xen_hosts[hname].info()})
    else:
        return jsonp({ 'error': hname + ' not found' })

def mcs_getdomains(version,hname):
    'Return all domains on host hname'
    if hname not in xen_hosts.keys():
        return jsonp({ 'error': hname + ' not found' })
    else:
        return jsonp({ hname: xen_hosts[hname].listdomains() })

def mcs_getdomain(version,hname,domname):
    'Return domain info on host hname'
    if hname not in xen_hosts.keys():
        return jsonp({ 'error': hname + ' not found' })
    else:
        if domname not in xen_hosts[hname].listdomains() :
            return jsonp({ 'error': domname + ' not found on ' + hname })
        else:
            return jsonp({ domname: xen_hosts[hname].getdomaininfo(domname) })
       
def mcs_createdomain(version,hname,domjson):
    'Create a domain, if not already present'
    if hname not in xen_hosts.keys():
        return jsonp({ 'error': hname + ' not found' })
    else:
        return jsonp({ hname: xen_hosts[hname].definedomain(domjson) })
        
def mcs_updatedomain(version,hname,domname,command):
    'Update domain with given cmd, args'
    if __is_dom_inuse(hname,domname):
        return jsonp({ 'Command': command })
    else:
        return jsonp({ 'error': domname + ' not found on '  + hname })

def jsonp(s):
    'Pretty print json'
    return str(json.dumps(s,sort_keys=True,separators=(',',': '),indent=4))
    #return '<pre>' + str(json.dumps(s,sort_keys=True,separators=(',',': '),indent=4)) + '</pre>'

### Main 
pkipath = config.PKIPATH    # PKI Certificates path 
xen_hosts = {}              # Initialize hash to store all info on Xen hosts and domains

# collect/update Xen hosts information on import
mcs_gethosts('0.0')

# Main function
if __name__ == '__main__':
    print xen_hosts

