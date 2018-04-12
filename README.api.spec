
mcs - my cloud services

RESTful API specs:

Hosts:
    GET /mcs/api/v0.1/hosts              # to get all managed hosts
    GET /mcs/api/v0.1/hosts/<host-name>  # to get details of a particular host
    POST /mcs/api/v0.1/hosts             # add host ?
    
Domains:

Get domain details:
    GET /mcs/api/v0.1/hosts/<host-name>/domains             # to get all domains on a host
    GET /mcs/api/v0.1/hosts/<host-name>/domains/<domname>   # to get domain info on host

Create domain on host:
    POST /mcs/api/v0.1/hosts/<host-name>/domains             # create a new domain on host
curl -i -H "Content-Type: application/json" http://192.168.56.101:5000/mcs/api/v1.1/hosts/myxen/domains -X POST -d @newdomain.post
    {
    "name": "ubun8",
    "memoryMB": 512,
    "osdiskGB": 16,
    "osimage": "ubuntu-1604",
    "vcpu": 1
    }

Update a domain on host: 
    PUT /mcs/api/v0.1/hosts/<host-name>/domains/domname             # update domain on host
curl -i -H "Content-Type: application/json" http://192.168.56.101:5000/mcs/api/v1.1/hosts/myxen/domains/ubun8 -X POST -d @newdomain.post
    {
    "cmd":  "start/stop/add_disk/rm_disk",
    "args": ""
    }

Delete a domain on host:
    DELETE /mcs/api/v0.1/hosts/<host-name>/domains/domname             # delete a domain on host
curl -i -H "Content-Type: application/json" http://192.168.56.101:5000/mcs/api/v1.1/hosts/myxen/domains/ubun8 -X DELETE -d @newdomain.post

## squash this - 1
