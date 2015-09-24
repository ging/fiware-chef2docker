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

chef2docker [chef_cookbook_name]

Usage Notes
-----------

Doesn't solve chef dependencies, therefore all dependant chef recipes must be included in the cookbook

License
-------

Apache License Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0>
