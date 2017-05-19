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


### Instance meta-data handling
# latest only
@app.route("/openstack")
def version():
        return "latest"

# return metadata for client
@app.route("/openstack/latest/meta_data.json")
def metadata():
    '''
    Returns instance metadata. Example format
       {
        "uuid": "mcs-00001",
        "hostname": "cvtest1.lab.local",
        "name": "cvtest1",
        "public_keys": {
            "mykey": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDNOjFSxcbcjcZXM6WQK2E58lLM2TOSfONngQ6su94MhfR+hdWLaF484cQDn0WvojulqqomAch/dch89gRIWcOh9EuvU0rc4e8tECMAnUOfJEA1nSb4HaHVTrQ6YjUXf3D9gFZiZbuAVULApt06fTlYiqUxR5w4UU6C8UOg5z3H8Yhrsa6xOVF4dBp1UL705Gau00z4u7PdHp25ywMuvHFnczP5hcYQ8XLR+xB68RuI7qM/gvl/4Ml+mshWJ079Smkg8xpDZHcY9JZVckXcJx1PUy/trQFrOIFEG3WnMfPp8DoSOLN9uHQM8N88UROwk0VZcgj/b6X7sn+chsO2HN95"
            }
        }
    '''
    return make_response(jsonify(mcs_getinstancemeta(request.remote_addr)))

# /openstack/latest/user_data 
@app.route("/openstack/latest/user_data")
def userdata():
    return make_response(mcs_getinstanceuser())

# /openstack/latest/vendor_data.json
@app.route("/openstack/latest/vendor_data.json")
def vendordata():
    'Null for now'
    return make_response(jsonify({}))

# /openstack/latest/network_data.json
@app.route("/openstack/latest/network_data.json")
def networkdata():
    'Null for now'
    return make_response(jsonify({}))

# 404 handler
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}),404)

# 405 handler
@app.errorhandler(405)
def not_allowed(error):
    return make_response(jsonify({'error': 'Method not allowed'}),405)

# Main
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=10080,debug=True)
