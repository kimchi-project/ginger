# -*- coding: utf-8 -*-
#
# Project Ginger
#
# Copyright IBM, Corp. 2015
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

import json
import mock
import os
import tempfile
import time
import unittest
import urllib2
from functools import partial

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from wok.plugins.ginger.models import GingerModel

from tests.utils import get_free_port, patch_auth, request
from tests.utils import run_server, wait_task, get_fake_user

from wok.utils import add_task


objstore_dict = {}

class ArchivesMockModel(object):

    def create(self, params):
        global objstore_dict

        print '---------- mock_create ---------'

        archive_id = str(uuid.uuid4())
        stamp = int(time.mktime(time.localtime()))
        include = params.get('include', [])
        exclude = params.get('exclude', [])
        temp_file_name = next(tempfile._get_candidate_names())

        ar_params = {'identity': archive_id,
                     'include': include,
                     'exclude': exclude,
                     'description': params.get('description', ''),
                     'checksum': {},
                     'timestamp': stamp,
                     'file': temp_file_name}

        objstore_dict[archive_id] = ar_params

        return archive_id

    def get_list(self):
        return objstore_dict.keys()


class ArchiveMockModel(object):

    def lookup(self, archive_id):
        return objstore_dict[archive_id]

    def delete(self, archive_id):
        global objstore_dict

        del objstore_dict[archive_id]


test_server = None
model = None
host = None
port = None
ssl_port = None
cherrypy_port = None


#@mock.patch('wok.plugins.ginger.models.backup.ArchivesModel',
#            autospec=True)
#@mock.patch('wok.plugins.ginger.models.backup.ArchiveModel',
#            autospec=True)
def setUpModule():
    global test_server, model, host, port, ssl_port, cherrypy_port

    patch_auth()

    host = 'localhost'
    port = get_free_port('http')
    ssl_port = get_free_port('https')
    cherrypy_port = get_free_port('cherrypy_port')
    test_server = run_server(host, port, ssl_port,
                             test_mode=True, cherrypy_port=cherrypy_port)
    time.sleep(5)

def tearDownModule():
    test_server.stop()


class ConfigurationBackupUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        chromedriver = "/home/danielhb/Downloads/chromedriver"
        os.environ["webdriver.chrome.driver"] = chromedriver
        cls.driver = webdriver.Chrome(chromedriver)
        #driver = webdriver.Firefox()
        cls.driver.get('http://'+host+':'+str(port))

        fake_user = get_fake_user()
        user_field = cls.driver.find_element_by_name("username")
        user_field.send_keys(fake_user.keys()[0])

        passwd_field = cls.driver.find_element_by_name("password")
        passwd_field.send_keys(fake_user.values()[0])

        cls.driver.find_element_by_id("btn-login").click()

        cls.conf_bkp_frame_link = '#backup-ppc-content-area'

        host_admin_html = 'plugins/ginger/host-admin.html'
        host_admin_tab_xpath = \
            '//*[@id="tabPanel"]/ul/li[1]/a[@href="%s"]' % host_admin_html

        WebDriverWait(cls.driver, 10).until(
            EC.presence_of_element_located(
               (By.XPATH, host_admin_tab_xpath)
           )
        )

    def get_open_conf_bkp_link(self):
        conf_bkp_frame_link = '#backup-ppc-content-area'
        frame_xpath = '//*[@id="accordion"]/h3/a[@href="%s"]' % conf_bkp_frame_link
        config_backup_link= self.driver.find_element(
            By.XPATH,
            frame_xpath
        )
        return config_backup_link

    def get_actions_button(self):
        button_xpath = '//*[@id="backup-pcc-action-area"]/span/div/button'
        actions_button = self.driver.find_element(
            By.XPATH,
            button_xpath
        )
        return actions_button

    def get_new_default_bkp_button(self):
        return self.driver.find_element(
            By.ID, "newDefaultBakBtn"
        )

    def get_new_custom_bkp_button(self):
        return self.driver.find_element(
            By.ID, "newCustomBakBtn"
        )

    def get_batch_delete_button(self):
        return self.driver.find_element(
            By.ID, "batDelBtn"
        )

    def test_components_show_hide(self):
        config_bkp_frame_link = self.get_open_conf_bkp_link()
        self.assertIsNotNone(config_bkp_frame_link)
        config_bkp_frame_link.click()
        time.sleep(0.5)

        actions_button = self.get_actions_button()
        self.assertIsNotNone(actions_button)
        actions_button.click()
        time.sleep(0.5)

        self.assertIsNotNone(self.get_new_default_bkp_button())
        self.assertIsNotNone(self.get_new_custom_bkp_button())
        self.assertIsNotNone(self.get_batch_delete_button())

        actions_button.click()
        time.sleep(0.5)
        config_bkp_frame_link.click()
        time.sleep(0.5)

    @mock.patch('wok.plugins.ginger.models.backup.ArchivesModel') 
    def test_create_default_backup(self, mock_get_list):
        mock_get_list = ArchivesMockModel()

        config_bkp_frame_link = self.get_open_conf_bkp_link()
        self.assertIsNotNone(config_bkp_frame_link)
        config_bkp_frame_link.click()
        time.sleep(0.5)

        actions_button = self.get_actions_button()
        self.assertIsNotNone(actions_button)
        actions_button.click()
        time.sleep(0.5)

        default_bkp_button = self.get_new_default_bkp_button()
        default_bkp_button.click()

        time.sleep(30)
