#!/usr/bin/env python
#
# MCS 
#
from flask import Flask, request,redirect, url_for, abort, make_response,jsonify

# all libvirt related stuff here
from libvirt_mcs import *

# list of hosts to manage ,,, read from a db?
hosts = ['myxen.lab.local','myxen']

# populate hosts first
mcs_gethosts('0.1',hosts)

app  = Flask(__name__)

@app.route("/mcs/api/<string:version>/hosts")
def gethosts(version):
    return mcs_gethosts(version,hosts)

@app.route("/mcs/api/<string:version>/hosts/<string:hname>")
def gethostbyuuid(version,hname):
    return mcs_gethost(version,hname)
	
@app.route("/mcs/api/<string:version>/hosts/<string:hname>/domains")
def getdomains(version,hname):
    return mcs_getdomains(version,hname)


@app.route("/mcs/api/<string:version>/hosts/<string:hname>/domains/<string:domname>")
def getdomain(version,hname,domname):
    return mcs_getdomain(version,hname,domname)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}),404)

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)

