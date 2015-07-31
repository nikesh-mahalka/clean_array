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
        "

        """
        url = self._build_request_url(path, *args, **kargs)
        headers = {'dataType': 'api', 'sessionKey': self._session_key}
        req = urllib2.Request(url, headers=headers)
        xml = urllib2.urlopen(req).read()
        tree = etree.XML(xml)
        return tree

    def logout(self):
        url = self._base_url + '/exit'
        try:
            urllib2.urlopen(url)
            return True
        except Exception:
            return False 
    def delete_volumes(self):
        pool_name = os.environ['POOL_NAME']
        path = "/show/volumes/type/all/vdisk/%s" % pool_name
        tree = self._request(path)
        tree = [prop.text for prop in tree.xpath(".//PROPERTY[@name='serial-number']")]
        path = "/show/snap-pools/pool/%s" % pool_name
        snap_tree = self._request(path)
        snap_tree = [prop.text for prop in snap_tree.xpath(".//PROPERTY[@name='serial-number']")]
		tree = tree + snap_tree
        list_loop = True
        while list_loop:
            if len(tree) >50:
                t1 = tree[:50]
                tree = tree[50:]
            else:
	        t1 = tree
                list_loop = False
            path = "/delete/volumes/%s"  % ",".join(t1)
            tree_3 = self._request(path)
        
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
        tree = self._request(path)

if __name__ == "__main__":
	ip = os.environ['ARRAY_IP']
    req_client = DotHillClient(ip, 'manage', '!manage', 'http')
    req_client.login()
    req_client.delete_volumes()
    #req_client.delete_pool()
    #req_client.create_pool()
    req_client.logout()
