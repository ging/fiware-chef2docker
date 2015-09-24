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

    def generate_initial_image(self, dockerfile, chefdir):
        """generate docker image"""
        status = True
        root_dir, self.cookbook_name = os.path.split(chefdir)
        # inject config files dir to syspath
        LOG.debug("injecting dir %s to syspath..." % root_dir)
        wp = os.path.abspath(root_dir)
        sys.path.insert(0, wp)
        os.chdir(wp)
        # inject cookbook to dockerfile
        LOG.debug("injecting cookbook to dockerfile...")
        with open(dockerfile, "r") as f:
            cont = f.read()
        with open("Dockerfile", "w") as f:
            f.write(cont.replace("<<COOKBOOKNAME>>", self.cookbook_name))
        self.image_name = "docker-%s" % self.cookbook_name
        # generate image
        LOG.debug("generating image %s" % self.image_name)
        with open("Dockerfile") as df:
            resp = self.dc.build(
                fileobj=df,
                rm=True,
                tag=self.image_name
            )
        for l in resp:
            if "error" in l.lower():
                status = False
            LOG.debug(l)
        return status

    def dump_docker_image(self):
        """generate file from docker image"""
        LOG.debug("Dumping Docker Image %s" % self.image_name)
        with open("%s.tar" % self.image_name, 'wb') as image_tar:
            image_tar.write(self.dc.get_image("%s:latest" % self.image_name).data)

    def deploy_cookbook(self):
        """
        Try to process a recipe and return results
        :param recipe: recipe to deploy
        :param image: image to deploy to
        :return: dictionary with results
        """
        LOG.debug("Sending recipe to docker server")
        b_success = True
        msg = {}
        self.run_container()
        # inject custom solo.json/solo.rb file
        json_cont = CONF.clients_chef.cmd_config % self.cookbook_name
        cmd_inject = CONF.clients_chef.cmd_inject.format(json_cont)
        self.execute_command(cmd_inject)

        msg['deploy'] = self.run_deploy()
        b_success &= msg['deploy']['success']

        # check execution output
        if b_success:
            msg['result'] = {
                'success': True,
                'result': "Recipe %s successfully deployed\n" % self.cookbook_name
            }
        else:
            msg['result'] = {
                'success': False,
                'result': "Error deploying recipe {}\n".format(self.cookbook_name)
            }
            LOG.error(msg)
        self.remove_container()
        return msg

    def run_deploy(self):
        """ Run recipe deployment
        :param recipe: recipe to deploy
        :return msg: dictionary with results and state
        """
        try:
            # launch execution
            cmd_launch = CONF.clients_chef.cmd_launch
            resp_launch = self.execute_command(cmd_launch)
            msg = {
                'success': True,
                'response': resp_launch
            }
            LOG.debug("Launch result: %s" % resp_launch)
            if resp_launch is None or "FATAL" in resp_launch:
                msg['success'] = False
        except Exception as e:
            self.remove_container(self.container)
            LOG.error("Recipe deployment exception %s" % e)
        return msg

    def generate_final_image(self):
        self.stop_container()
        self.commit_container()
        res = self.dump_docker_image()
        return res

    def stop_container(self):
        res = self.dc.stop(self.container)
        return res

    def commit_container(self):
        pass

    def run_container(self):
        """Run and start a container based on the given image
        :param image: image to run
        :return:
        """
        contname = "{}-deploy".format(self.image_name).replace("/", "_")
        try:
            try:
                self.dc.remove_container(contname, force=True)
                LOG.info('Removing old %s container' % contname)
            except NotFound:
                pass
            self.container = self.dc.create_container(
                self.image_name,
                tty=True,
                name=contname
            ).get('Id')
            self.dc.start(container=self.container)
        except AttributeError as e:
            LOG.error("Error creating container: %s" % e)

    def remove_container(self, kill=True):
        """destroy container on exit
        :param kill: inhibits removal for testing purposes
        """
        self.dc.stop(self.container)
        if kill:
            self.dc.remove_container(self.container)

    def execute_command(self, command):
        """ Execute a command in the given container
        :param command:  bash command to run
        :return:  execution result
        """
        bash_txt = "/bin/bash -c \"{}\"".format(command.replace('"', '\\"'))
        exec_txt = self.dc.exec_create(
            container=self.container,
            cmd=bash_txt
        )
        return self.dc.exec_start(exec_txt)
