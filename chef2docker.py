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
import os
from docker_client import DockerClient

LOG = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


def main():
    """
    Generates a Docker Image of ChefSDK based on a local dockerfile.
    Installs a local recipe in the image.
    :return:
    """
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Generates Docker images based on Chef cookbooks')
    parser.add_argument('chef_name', metavar='CHEF_NAME', help='The chef cookbook to deploy')
    args = parser.parse_args()

    # generate the docker image
    print "Connecting to Docker Client...",
    dc = DockerClient()
    print "OK"
    print "Generating Image...",
    sta = dc.generate_image("ChefImage.docker", args.chef_name)
    print "OK" if sta else "FAILED"

if __name__ == '__main__':
    main()
