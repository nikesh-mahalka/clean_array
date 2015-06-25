#    Copyright 2014 Objectif Libre
#    Copyright 2015 DotHill Systems
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

from hashlib import md5
import math
import time
import urllib2
import os

from lxml import etree


class DotHillClient(object):
    def __init__(self, host, login, password, protocol):
        self._login = login
        self._password = password
        self._base_url = "%s://%s/api" % (protocol, host)
        self._session_key = None

    def _get_auth_token(self, xml):
        """Parse an XML authentication reply to extract the session key."""
        self._session_key = None
        tree = etree.XML(xml)
        if tree.findtext(".//PROPERTY[@name='response-type']") == "success":
            self._session_key = tree.findtext(".//PROPERTY[@name='response']")

    def login(self):
        """Authenticates the service on the device."""
        hash_ = md5("%s_%s" % (self._login, self._password))
        digest = hash_.hexdigest()

        url = self._base_url + "/login/" + digest
        xml = urllib2.urlopen(url).read()
        self._get_auth_token(xml)

    def _build_request_url(self, path, *args, **kargs):
        url = self._base_url + path
        if kargs:
            url += '/' + '/'.join(["%s/%s" % (k.replace('_', '-'), v)
                                   for (k, v) in kargs.items()])
        if args:
            url += '/' + '/'.join(args)

        return url

    def _request(self, path, *args, **kargs):
        """Performs an HTTP request on the device.

        Raises a DotHillRequestError if the device returned but the status is
        not 0. The device error message will be used in the exception message.

        If the status is OK, returns the XML data for further processing.
        """

        url = self._build_request_url(path, *args, **kargs)
        headers = {'dataType': 'api', 'sessionKey': self._session_key}
        req = urllib2.Request(url, headers=headers)
        xml = urllib2.urlopen(req).read()

    def logout(self):
        url = self._base_url + '/exit'
        try:
            urllib2.urlopen(url)
            return True
        except Exception:
            return False 

    def delete_pool(self):
        pool_name = os.environ['POOL_NAME']
        path = "/delete/vdisks/prompt/yes/%s" % pool_name
        tree = self._request(path)

    def create_pool(self):
        pool_name = os.environ['POOL_NAME']
        disk_slots = os.environ['DISK_SLOTS']
        controller = os.environ['CONTROLLER']
        raid_level = os.environ['RAID_LEVEL']
        path = ("/create/vdisk/level/%(raid_level)s/disks/%(disk_slots)s/assign"
                "ed-to/%(controller)s/mode/online/%(pool_name)s" %
                {'raid_level': raid_level,
                 'disk_slots': disk_slots,
                 'controller': controller,
                 'pool_name': pool_name, })
        print "path is %s" % path
        tree = self._request(path)

if __name__ == "__main__":
    req_client = DotHillClient('172.16.2.100', 'manage', '!manage', 'http')
    req_client.login()
    req_client.delete_pool()
    req_client.create_pool()
    req_client.logout()
