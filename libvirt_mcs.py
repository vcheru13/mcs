#!/usr/bin/python

import libvirt
from lxml import etree
import json
import sys
from pprint import pformat as pf
from dom import *


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

# Main
if __name__ == '__main__':
    print mcs_gethosts('v1.0',['myxen'])
