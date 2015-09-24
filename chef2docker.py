# -*- coding: utf-8 -*-
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

"""Helper tool to generate a valid deployment image in docker format"""

from __future__ import unicode_literals
import argparse
import logging
from docker_client import DockerClient

LOG = logging.getLogger()


def main():
    """
    Generates a Docker Image of ChefSDK based on a local dockerfile.
    Installs a local recipe in the image.
    :return:
    """
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Generates Docker images based on Chef cookbooks')
    parser.add_argument('chef_name', help='The chef cookbook to deploy')
    parser.add_argument('-f', '--fast', dest='fast', action='store_true', help='Fast save (RAM intensive), slow commandline save by default')
    parser.add_argument('-H', dest='host', help='docker url (defaults to local socket')
    parser.add_argument('-v', '--verbose', dest='debug', action='store_true', help='Show verbose messages')
    args = parser.parse_args()

    # logging management
    lev = logging.ERROR
    if args.debug:
        lev = logging.DEBUG
    logging.basicConfig(level=lev)
    # generate the docker image
    print "Connecting to Docker Client...",
    dc = DockerClient(args.host)
    print "OK"
    print "Generating Image...",
    sta = dc.generate_image("ChefImage.docker", args.chef_name)
    print "OK" if sta else "FAILED"
    print "Saving Image file docker-%s.tar to disk ..." % args.chef_name,
    if args.fast:
        dc.save_image()
    else:
        dc.save_image_cmd()
    print "OK"


if __name__ == '__main__':
    main()
