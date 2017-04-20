
mcs - my cloud services

RESTful API specs:

Hosts:
    GET /mcs/api/v0.1/hosts              # to get all managed hosts
    GET /mcs/api/v0.1/hosts/<host-uuid>  # to get details of a particular host
    POST /mcs/api/v0.1/hosts             # add host ?
    
Domains:
    GET /mcs/api/v0.1/hosts/<host-uuid>/domains  # to get all domains on a host
    GET /mcs/api/v0.1/hosts/<host-uuid>/domains/<dom-uuid>   # to get domain info on host


