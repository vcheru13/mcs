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

mcs_server_url = 'http://127.0.0.1:10080/'


def gethost(hname):
    print 'Parsing info of host: ', hname

def getallhosts():
    print 'All hosts info'

def getdomains(hname):
    print 'All domains on: ', hname

def getdominfo(hname,dname):
    print 'Domain info ', dname, ' on: ', hname

def domstart(hname,dname):
    print 'Starting domain ', dname, ' on: ', hname
                             
def domstop(hname,dname):
    print 'Stoping domain ', dname, ' on: ', hname

def domcreate(hname,dname,opts):
    print 'Creating domain ', dname, ' on: ', hname
                         
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
    if not args.dname:
        print 'domain required' + usage
        sys.exit(1)
    if not args.cmd:
        getdominfo(args.hname,args.dname)
    else: 
        if args.cmd == 'create' and not args.opts:
            print 'create command requires --opts' + usage
            sys.exit(1)
        else:
            #print 'Running command: ' + args.cmd + ' for domain: ' + args.dname + ' on host: ' + args.hname 
            #if args.opts:
            #    print 'Opts: '  + args.opts
            domcmd_funcs = { 'start': domstart(args.hname,args.dname),
                             'stop': domstop(args.hname,args.dname),
                             'create': domcreate(args.hname,args.dname,args.opts),
                             'destroy': domdestroy(args.hname,args.dname) }
            domcmd_funcs[args.cmd]
