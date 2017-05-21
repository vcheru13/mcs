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
        print 'Parsing info of host: ', args.info
    else:
        print 'Print all host list'
else:
    if not args.hname:
        print 'hostname required' + usage
        sys.exit(1)
    if not args.dname:
        print 'domain required' + usage
        sys.exit(1)
    if not args.cmd:
        print 'printing domain: ' + args.dname + ' info on host: ' + args.hname
    else: 
        if args.cmd == 'create' and not args.opts:
            print 'create command requires --opts' + usage
            sys.exit(1)
        else:
            print 'Running command: ' + args.cmd + ' for domain: ' + args.dname + ' on host: ' + args.hname 
            if args.opts:
                print 'Opts: '  + args.opts
