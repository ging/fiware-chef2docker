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
from __future__ import unicode_literals
import os
from docker.errors import DockerException, NotFound
from docker import Client as DC
import sys
import logging
from io import BytesIO

LOG = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


class DockerClient(object):
    """
    Wrapper for Docker client
    """

    def __init__(self, url=None):
        """Connect to docker server"""
        if not url:
            url = "unix:///var/run/docker.sock"
        self.container = None
        self.image_name = None
        self.cookbook_name = None
        try:
            self.dc = DC(base_url=url)
        except DockerException as e:
            LOG.error("Docker client error: %s" % e)
            raise e

    def generate_image(self, dockerfile, chef_name):
        """generate docker image"""
        status = True
        self.cookbook_name = chef_name
        # # inject config files dir to syspath
        # LOG.debug("Injecting %s dir to syspath..." % root_dir)
        # sys.path.insert(0, root_dir)
        # os.chdir(root_dir)

        # configure chef-solo
        with open("solo.json.sample", "r") as f:
            cont = f.read()
        with open("solo.json", "w") as f:
            f.write(cont.replace("<<COOKBOOKNAME>>", self.cookbook_name))

        # inject cookbook to dockerfile
        LOG.debug("injecting cookbook to dockerfile...")
        with open(dockerfile, "r") as f:
            cont = f.read()
        with open("Dockerfile", "w") as df:
            df.write(cont.replace("<<COOKBOOKNAME>>", self.cookbook_name))

        # generate image
        self.image_name = "docker-%s" % self.cookbook_name
        LOG.debug("generating image %s" % self.image_name)
        resp = self.dc.build(
            path=root_dir,
            rm=True,
            tag=self.image_name,
            decode=True,
        )
        for l in resp:
            if "error" in l.keys():
                status = False
                LOG.error(l['errorDetail']['message'])
            if "stream" in l.keys():
                LOG.debug(l['stream'].replace("\n",""))
        return status