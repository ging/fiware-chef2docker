FI-Ware Chef2Docker
======================

Description
-----------

A simple helper script to install software in generated docker images from chef recipes

Features Implemented
--------------------
Chef Recipe to docker image conversion

Requirements
------------
A local docker server with version >= 0.9
A chef cookbook folder placed in the script path (needed by the generated Dockerfile for injection)

Installation
------------
No installation is necessary

Commandline Usage
-----------------
```bash
usage: chef2docker.py [-h] [-f] [-H HOST] [-v] chef_name

Generates Docker images based on Chef cookbooks

positional arguments:
  chef_name      The chef cookbook to deploy

optional arguments:
  -h, --help     show this help message and exit
  -f, --fast     Fast save (RAM intensive), slow commandline save by default
  -H HOST        docker url (defaults to local socket
  -v, --verbose  Show verbose messages
```

Usage Notes
-----------

Doesn't solve chef dependencies, therefore all dependant chef recipes must be included in the cookbook

License
-------

Apache License Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0>
