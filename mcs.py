#!/usr/bin/python
# mcs host
# mcs host --info <hname>
# mcs domain --host <hanme>
# mcs domain --host <hanme> --domu <dname>
# mcs domain --cmd start --host <hanme> --dom <dname>
# mcs domain --cmd stop  --host <hanme> --dom <dname>
# mcs domain --cmd create --host <hanme> --dom <dname> --opts={key1=value1,key2=value2...}
# mcs domain --cmd destroy --host <hanme> --dom <dname>

import argparse
import sys
import requests
import json

mcs_server_url = 'http://127.0.0.1:10080/mcs/api/v0.1'

def getmcs(mcsurl):
    r = requests.get(mcsurl)
    if r.status_code == 200:
        if isinstance(r.json(),dict):
            for k in r.json():
                print json.dumps(r.json().get(k),sort_keys=True,indent=4)
        else:
            for k in r.json():
                print k
    else:
        print 'ERROR: unable to GET ', mcsurl

def putmcs(mcsurl,payload):
    r = requests.put(mcsurl,json=payload)
    if r.status_code == 200:
        print json.dumps(r.json(),sort_keys=True,indent=4)
    else:
        print 'ERROR: unable to PUT ', mcsurl

def postmcs(mcsurl,payload):
    r = requests.post(mcsurl,json=payload)
    if r.status_code == 200:
        print json.dumps(r.json(),sort_keys=True,indent=4)
    else:
        print 'ERROR: unable to POST ', mcsurl

def gethost(hname):
    print 'Parsing info of host: ', hname
    getmcs(mcs_server_url + '/hosts/' + hname )

def getallhosts():
    print 'All hosts info'
    getmcs(mcs_server_url + '/hosts')

def getdomains(hname):
    print 'All domains on: ', hname
    getmcs(mcs_server_url + '/hosts/' + hname + '/domains')
    sys.exit()

def getdominfo(hname,dname):
    print 'Domain info ', dname, ' on: ', hname
    getmcs(mcs_server_url + '/hosts/' + hname + '/domains/' + dname)

def domstart(hname,dname):
    print 'Starting domain ', dname, ' on: ', hname
    payload = { "cmd": "start", "args": None }
    putmcs(mcs_server_url + '/hosts/' + hname + '/domains/' + dname,payload)
                             
def domstop(hname,dname):
    print 'Stoping domain ', dname, ' on: ', hname
    payload = { "cmd": "stop", "args": None }
    putmcs(mcs_server_url + '/hosts/' + hname + '/domains/' + dname,payload)

def domcreate(hname,dname,opts):
    print 'Creating domain ', dname, ' on: ', hname
    print type(opts), opts
                         
def domdestroy(hname,dname):
    print 'Destroying domain ', dname, ' on: ', hname

usage='''

 mcs host
 mcs host --info <hname>
 mcs domain --host <hanme>
 mcs domain --host <hanme> --domu <dname>
 mcs domain --cmd start --host <hanme> --domu <dname>
 mcs domain --cmd stop  --host <hanme> --domu <dname>
 mcs domain --cmd create --host <hanme> --opts={key1=value1,key2=value2...}
 mcs domain --cmd destroy --host <hanme> --domu <dname>

 ''' 

parser = argparse.ArgumentParser(usage=usage,add_help=False)
parser.add_argument('comm',choices=['host','domain'],help=' host|domain')
parser.add_argument('--info',dest='info',help='host info')
parser.add_argument('--host',dest='hname',help='hostname')
parser.add_argument('--domu',dest='dname',help='domain')
parser.add_argument('--cmd',dest='cmd',choices=['start','stop','create','destroy'],help='cmd to run on domain')
parser.add_argument('--opts',dest='opts',help='options for domain creation')
args = parser.parse_args()

if args.comm == 'host':
    if args.info:
        gethost(args.info)
    else:
        getallhosts()
else:
    if not args.hname:
        print 'hostname required' + usage
        sys.exit(1)

    if not args.dname and not args.cmd:
        # get all domains on host
        getdomains(args.hname)

    if args.dname and not args.cmd:
        # get domain info on host
        getdominfo(args.hname,args.dname)
    else: 
        if args.cmd == 'create' and not args.opts:
            print 'create command requires --opts' + usage
            sys.exit(1)
        else:
            #print 'Running command: ' + args.cmd + ' for domain: ' + args.dname + ' on host: ' + args.hname 
            #if args.opts:
            #    print 'Opts: '  + args.opts
            domcmd_funcs = { 'start': domstart, 'stop': domstop, 'create': domcreate, 'destroy': domdestroy }
            if args.opts:
                domcmd_funcs[args.cmd](args.hname,args.dname,args.opts)
            else:
                domcmd_funcs[args.cmd](args.hname,args.dname)
