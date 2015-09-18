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
import gc as collector
from glanceclient.v2 import client as GlanceClient
from chef2docker import LOG, CONF, cmdline_upload
from credentials import get_glance_connection


def upload_to_glance():
    """upload docker image to glance via buffer"""
    LOG.debug("Connecting Glance Client")
    gdata = get_glance_connection()
    gc = GlanceClient.Client(**gdata)
    for im in gc.images.list():
        if CONF.tag in im.name:
            LOG.debug("Deleting old Glance Image")
            gc.images.delete(im.id)
    # Memory starvation even with intermediate file
    # dump_docker_image()
    # upload_glance_image_from_file(gc)
    cmdline_upload()


def upload_glance_image_from_file(gc):
    "upload file image to glance"
    LOG.debug("Generating Glance Image")
    with open("/tmp/temp.tar", 'rb') as image_tar:
        gc.images.create(
            name=CONF.tag,
            is_public='true',
            container_format='docker',
            disk_format='raw',
            data=image_tar
        )
    collector.collect()