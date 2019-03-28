#################################################################
# nosetest -v --nopature
# nosetests -v --nocapture tests/test_compute_google.py
#################################################################

from pprint import pprint
import time
import subprocess
import sys
from cloudmesh.common.util import HEADING
from cloudmesh.compute.gcloud.Provider import Provider as GCloudProvider
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.Printer import Printer
from cloudmesh.common.FlatDict import FlatDict, flatten
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.management.configuration.name import Name
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common.util import banner
from Crypto.PublicKey import RSA
from pathlib import Path
from cloudmesh.common.util import path_expand


class TestName:

    def setup(self):
        banner("setup", c="-")
        self.user = Config()["cloudmesh"]["profile"]["user"]
        self.key_path = path_expand(Config()["cloudmesh"]["profile"]["publickey"])
        f = open(self.key_path, 'r')
        self.key_val = f.read()
  
        self.clouduser = 'cc'
        self.name_generator = Name(
            experiment="exp",
            group="grp",
            user = "user",
            kind="vm",
            counter=1)
        
        self.name = str(self.name_generator)
        self.name_generator.incr()

        self.new_name = str(self.name_generator)

        self.p = GCloudProvider(name="google")

        self.secgroupname = "CM4TestSecGroup"
        self.secgrouprule = {"ip_protocol": "tcp",
                             "from_port": 8080,
                             "to_port": 8088,
                             "ip_range": "129.79.0.0/16"}
        self.testnode = None

    def test_01_list_keys(self):
        HEADING()
        print("List Key Method is not supported by google")
        '''
        self.keys = self.p.keys()
        pprint(self.keys)

        print(Printer.flatwrite(self.keys,
                                sort_keys=("name"),
                                order=["name", "fingerprint"],
                                header=["Name", "Fingerprint"])
              )
        '''

    def test_02_key_upload(self):
        HEADING()
        print("Upload Key method is not supported by google")
        '''
        key = SSHkey()
        print(key.__dict__)

        self.p.key_upload(key)

        self.test_01_list_keys()
        '''
    def test_03_list_images(self):
        HEADING()
        images = self.p.images()
        # pprint(images)

        print(Printer.flatwrite(images,
                                sort_keys=("name"),
                                order=["name", "id", "driver"],
                                header=["Name", "Id", "Driver"])
              )

    def test_04_list_flavors(self):
        HEADING()
        flavors = self.p.flavors()
        # pprint (flavors)

        print(Printer.flatwrite(flavors,
                                sort_keys=("name", "disk"),
                                order=["name", "id", "ram", "disk"],
                                header=["Name", "Id", "RAM", "Disk"])
              )

    def test_04_list_vm(self):
        HEADING()
        vms = self.p.list()
        print(vms)
        print(type(vms))
        print(Printer.flatwrite(vms,
                                sort_keys=("name"),
                                order=["name",
                                       "state",
                                       "extra.task_state",
                                       "extra.vm_state",
                                       "extra.userId",
                                       "extra.key_name",
                                       "private_ips",
                                       "public_ips"],
                                header=["Name",
                                        "State",
                                        "Task state",
                                        "VM state",
                                        "User Id",
                                        "SSHKey",
                                        "Private ips",
                                        "Public ips"])
              )
    def test_05_list_secgroups(self):
        HEADING()
        print("List security group method is not supported by google")
        '''
        secgroups = self.p.list_secgroups()
        for secgroup in secgroups:
            print(secgroup["name"])
            rules = self.p.list_secgroup_rules(secgroup["name"])
            print(Printer.write(rules,
                                sort_keys=(
                                "ip_protocol", "from_port", "to_port",
                                "ip_range"),
                                order=["ip_protocol", "from_port", "to_port",
                                       "ip_range"],
                                header=["ip_protocol", "from_port", "to_port",
                                        "ip_range"])
                  )
        '''

    def test_06_secgroups_add(self):
        print("List add security groups method is not supported by google")
        '''
        self.p.add_secgroup(self.secgroupname)
        self.test_05_list_secgroups()
        '''

    def test_07_secgroup_rules_add(self):
        print("List Add security group rules method is not supported by google")
        '''
        rules = [self.secgrouprule]
        self.p.add_rules_to_secgroup(self.secgroupname, rules)
        self.test_05_list_secgroups()
        '''

    def test_08_secgroup_rules_remove(self):
        print("Remove security group rules method is not supported by google")
        '''
        rules = [self.secgrouprule]
        self.p.remove_rules_from_secgroup(self.secgroupname, rules)
        self.test_05_list_secgroups()
        '''

    def test_09_secgroups_remove(self):
        print("Remove security groups method is not supported by google")
        '''
        self.p.remove_secgroup(self.secgroupname)
        self.test_05_list_secgroups()
        '''
    def test_10_create(self):
        HEADING()
        image = "ubuntu-minimal-1810-cosmic-v20190320"
        size = "n1-standard-4"
        location = "us-central1-a"
        metadata = {"items": [{"value": self.user+":"+self.key_val, "key": "ssh-keys"}]}
        self.p.create(name=self.name,
                      image=image,
                      size=size,
                      location=location,
                      ex_metadata=metadata
                      #,
                      # username as the keypair name based on
                      # the key implementation logic
                      #ex_keyname=self.user,
                      #ex_security_groups=['default']
                      )
        time.sleep(5)
        nodes = self.p.list()
        node = self.p.find(nodes, name=self.name)
        pprint(node)

        nodes = self.p.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break

        assert node is not None

    def test_11_publicIP_attach(self):
        HEADING()
        print("Attach Public IP method is not supported by google")
        '''
        pubip = self.p.get_publicIP()
        pprint(pubip)
        nodes = self.p.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break
        if self.testnode:
            print("attaching public IP...")
            self.p.attach_publicIP(self.testnode, pubip)
            time.sleep(5)
        self.test_04_list_vm()
        '''

    def test_12_publicIP_detach(self):
        print("Detach Public IP method is not supported by google")
        '''
        print("detaching and removing public IP...")
        time.sleep(5)
        nodes = self.p.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break
        ipaddr = self.testnode.public_ips[0]
        pubip = self.p.cloudman.ex_get_floating_ip(ipaddr)
        self.p.detach_publicIP(self.testnode, pubip)
        time.sleep(5)
        self.test_04_list_vm()
        '''

    def test_13_info(self):
        HEADING()
        self.p.info(name=self.name)

    def test_14_destroy(self):
        HEADING()
        self.p.destroy(names=self.name)
        nodes = self.p.list()
        node = self.p.find(nodes, name=self.name)

        pprint(node)

        assert node is None

    def test_15_list_vm(self):
        self.test_04_list_vm()

    def test_16_vm_login(self):
        self.test_04_list_vm()
        self.test_10_create()
        # use the self.testnode for this test
        time.sleep(30)
        #self.test_11_publicIP_attach()
        time.sleep(5)
        nodes = self.p.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break
        # pprint (self.testnode)
        # pprint (self.testnode.public_ips)
        pubip = self.testnode.public_ips[0]

        COMMAND = "cat /etc/*release*"

        ssh = subprocess.Popen(
            ["ssh", "%s@%s" % (self.clouduser, pubip), COMMAND],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        if result == []:
            error = ssh.stderr.readlines()
            print("ERROR: %s" % error)
        else:
            print("RESULT:")
            for line in result:
                line = line.decode("utf-8")
                print(line.strip("\n"))

        self.test_14_destroy()
        self.test_04_list_vm()
