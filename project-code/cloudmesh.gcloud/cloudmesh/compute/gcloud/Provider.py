import sys
from datetime import datetime
from pathlib import Path
from pprint import pprint
import subprocess
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider as LibcloudProvider
from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import HEADING
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.util import path_expand
from cloudmesh.management.configuration.name import Name


class Provider(ComputeNodeABC):

    ProviderMapper = {
        "google": LibcloudProvider.GCE
    }

    def __init__(self, name=None, configuration="~/.cloudmesh/cloudmesh4.yaml"):
        """
        Initializes the provider. The default parameters are read from the configutation
        file that is defined in yaml format.
        :param name: The name of the provider as defined in the yaml file
        :param configuration: The location of the yaml configuration filw
        """
        HEADING(c=".")
        conf = Config(configuration)["cloudmesh"]
        #self.user = conf["profile"]
        self.user = Config()["cloudmesh"]["profile"]["user"]
        self.spec = conf["cloud"][name]
        self.cloud = name
        cred = self.spec["credentials"]
        self.cloudtype = self.spec["cm"]["kind"]
        super().__init__(name, conf)
        self.name_generator = Name(
            experiment="exp",
            group="grp",
            user = "user",
            kind="vm",
            counter=1)

        self.name = str(self.name_generator)
        self.name_generator.incr()

        self.name = str(self.name_generator)
        self.key_path = path_expand(Config()["cloudmesh"]["profile"]["publickey"])
        f = open(self.key_path, 'r')
        self.key_val = f.read()
        self.testnode = None

       

        if self.cloudtype in Provider.ProviderMapper:

            self.driver = get_driver(
                Provider.ProviderMapper[self.cloudtype])

            if self.cloudtype == 'google':
                self.cloudman = self.driver(
                        cred["client_email"],
                        cred["path_to_json_file"],
                        project = cred["project"]
                        )    
        else:
            print("Specified provider not available")
            self.cloudman = None
        self.default_image = None
        self.default_size = None
        self.public_key_path = conf["profile"]["publickey"]

    def dict(self, elements, kind=None):
        """
        Libcloud returns an object or list of objects With the dict method
        this object is converted to a dict. Typically this method is used internally.
        :param elements: the elements
        :param kind: Kind is image, flavor, or node
        :return:
        """
        if elements is None:
            return None
        elif type(elements) == list:
            _elements = elements
        else:
            _elements = [elements]
        d = []
        for element in _elements:
            entry = element.__dict__
            entry["kind"] = kind
            entry["driver"] = self.cloudtype
            entry["cloud"] = self.cloud

            if kind == 'node':
                entry["updated"] = str(datetime.utcnow())

                if "created_at" in entry:
                    entry["created"] = str(entry["created_at"])
                    del entry["created_at"]
                else:
                    entry["created"] = entry["modified"]
            elif kind == 'flavor':
                entry["created"] = entry["updated"] = str(datetime.utcnow())
            elif kind == 'image':
                if self.cloudtype == 'openstack':
                    entry['created'] = entry['extra']['created']
                    entry['updated'] = entry['extra']['updated']
                else:
                    pass

            if "_uuid" in entry:
                del entry["_uuid"]

            d.append(entry)
        return d

    def find(self, elements, name=None):
        """
        finds an element in elements with the specified name
        :param elements: The elements
        :param name: The name to be found
        :return:
        """
        for element in elements:
            if element["name"] == name:
                return element
        return None

    def images(self, raw=False):
        """
        Lists the images on the cloud
        :param raw: If raw is set to True the lib cloud object is returened
                    otherwise a dict is returened.
        :return: dict or libcloud object
        """
        if self.cloudman:
            entries = self.cloudman.list_images()
            if raw:
                return entries
            else:
                return self.dict(entries, kind="image")

        return None

    def image(self, name=None):
        """
        Gets the image with a given nmae
        :param name: The name of the image
        :return: the dict of the image
        """
        return self.find(self.images(), name=name)

    def flavors(self, raw=False):
        """
        Lists the flavors on the cloud
        :param raw: If raw is set to True the lib cloud object is returened
                    otherwise a dict is returened.
        :return: dict or libcloud object
        """
        if self.cloudman:
            entries = self.cloudman.list_sizes()
            if raw:
                return entries
            else:
                return self.dict(entries, kind="flavor")
        return None

    def flavor(self, name=None):
        """
        Gest the flavor with a given name
        :param name: The aname of the flavor
        :return: The dict of the flavor
        """
        return self.find(self.flavors(), name=name)

    def start(self, name=None):
        """
        start a node. NOT YET IMPLEMENTED.
    
        :param name: the unique node name
        :return:  The dict representing the node
        """
        HEADING(c=".")
        names=name
        nodes = self.list(raw=True)
        for node in nodes:
            if node.name in names:
                self.cloudman.ex_start_node(node)

        return None

    def stop(self, name=None):
        """
        stops the node with the given name. NOT YET IMPLEMENTED.
    
        :param name:
        :return: The dict representing the node including updated status
        """
        HEADING(c=".")
        names=name
        nodes = self.list(raw=True)
        for node in nodes:
            if node.name == names:
                self.cloudman.ex_stop_node(node)

        return None

    def info(self, name=None):
        """
        Gets the information of a node with a given name
    
        :param name: The name of teh virtual machine
        :return: The dict representing the node including updated status
        """
        return self.find(self.list(), name=name)


    def list(self, raw=False):
        """
        Lists the vms on the cloud
        :param raw: If raw is set to True the lib cloud object is returened
                    otherwise a dict is returened.
        :return: dict or libcloud object
        """
        entries = self.cloudman.list_nodes()

        if raw:
            return entries
        else:
            return self.dict(entries,kind="vm")

    def destroy(self, name=None):
        """
        Destroys the node
        :param names: the name of the node
        :return: the dict of the node
        """

        #names = Parameter.expand(names)
        names=name
        nodes = self.list(raw=True)
        for node in nodes:
            if node.name in names:
                self.cloudman.destroy_node(node)
        # bug status shoudl change to destroyed
        return None


    def create(self, name=None, image=None, size=None, location=None,  timeout=360, **kwargs):
        """
        creates a named node
    
        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the image
                        does not boot. The default is set to 3 minutes.
        :param kwargs: additional arguments HEADING(c=".")ed along at time of boot
        :return:
        """
        #self.image = self.spec["default"]["image"]
        #self.flavor = self.spec["default"]["size"]
        location = self.spec["credentials"]["datacenter"]

        images = self.images(raw=True)
        image_use = None
        flavors = self.flavors(raw=True)
        flavor_use = None
        
        for _image in images:
            if _image.name == image:
                image_use = _image
                break
        for _flavor in flavors:
            if _flavor.name == size:
                flavor_use = _flavor
                break

        metadata = {"items": [{"value": self.user+":"+self.key_val, "key": "ssh-keys"}]}
        node = self.cloudman.create_node(name=name, image=image_use,
                size=flavor_use, location=location,ex_metadata=metadata, **kwargs)
     
        return self.dict(node)

    def ssh(self, name=None, command=None):
        nodes = self.list(raw=True)
        for node in nodes:
            if node.name == name:
                self.testnode = node
                break
        pubip = self.testnode.public_ips[0]
        ssh = subprocess.Popen(
            ["ssh", "%s" % (pubip), "%s" % (command)],
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

    def resume(self, name=None):
        """
        resume the named node. NOT YET IMPLEMENTED.
    
        :param name: the name of the node
        :return: the dict of the node
        """
        HEADING(c=".")
        return None

    def suspend(self, name=None):
        """
        suspends the node with the given name. NOT YET IMPLEMENTED.

        :param name: the name of the node
        :return: The dict representing the node
        """
        HEADING(c=".")
        return None

    def rename(self, name=None, destination=None):
        """
        rename a node. NOT YET IMPLEMENTED.

        :param destination:
        :param name: the current name
        :return: the dict with the new name
        """
        # if destination is None, increase the name counter and use the new name
        HEADING(c=".")
        return None
