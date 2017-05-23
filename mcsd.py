#!/usr/bin/env python
#
# MCS 
#
from flask import Flask, request,redirect, url_for, abort, make_response,jsonify
from libvirt_mcs import *

app  = Flask(__name__)

# Get list of Xen hosts
@app.route("/mcs/api/<string:version>/hosts")
def gethosts(version):
    return mcs_gethosts(version)

# Get info of a specific Xen host
@app.route("/mcs/api/<string:version>/hosts/<string:hname>")
def gethostbyuuid(version,hname):
    return mcs_gethost(version,hname)

# Get list of domains on a specific Xen host
@app.route("/mcs/api/<string:version>/hosts/<string:hname>/domains",methods=['GET'])
def getdomains(version,hname):
    return mcs_getdomains(version,hname)

# Create a domain on a specific Xen host
@app.route("/mcs/api/<string:version>/hosts/<string:hname>/domains",methods=['POST'])
def createdomain(version,hname):
    if not request.json:
        abort(400)
    new_domain = mcs_createdomain(version,hname,request.json)
    return new_domain

# Get info of domain on a specific Xen host
@app.route("/mcs/api/<string:version>/hosts/<string:hname>/domains/<string:domname>",methods=['GET'])
def getdomain(version,hname,domname):
    return mcs_getdomain(version,hname,domname)

# Update domain on a specific Xen host
@app.route("/mcs/api/<string:version>/hosts/<string:hname>/domains/<string:domname>",methods=['PUT'])
def updatedomain(version,hname,domname):
    if not request.json:
        abort(400)
    return mcs_updatedomain(version,hname,domname,request.json)

# 404 handler
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}),404)

# 405 handler
@app.errorhandler(405)
def not_allowed(error):
    return make_response(jsonify({'error': 'Method not allowed'}),405)

if __name__ == "__main__":
    app.run(host='127.0.0.1',port=10080,debug=True)

