from __future__ import print_function

from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.variables import Variables
from cloudmesh.common.console import Console
from pprint import pprint, pformat
from cloudmesh.common.parameter import Parameter
from cloudmesh.management.configuration.config import Active
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common.Printer import Printer
from cloudmesh.common.FlatDict import FlatDict, flatten
from cloudmesh.common.util import banner
from cloudmesh.terminal.Terminal import VERBOSE
class VmCommand(PluginCommand):

    @command
    def do_vm(self, args, arguments):
        """
        ::

            Usage:
                vm start [--cloud=CLOUD]
                         [--name=NAME]
                vm stop [--cloud=CLOUD]
                        [--name=NAME]
                vm delete [--cloud=CLOUD]
                          [--name=NAME]
                vm list [--cloud=CLOUDS]
                vm boot [--name=NAME]
                        [--cloud=CLOUD]
                        [--image=IMAGE]
                        [--flavor=FLAVOR]
                vm ssh  [--cloud=CLOUD]
                        [--name=NAME]
                        [--command=COMMAND]
                vm info [--cloud=CLOUD]
                        [--format=FORMAT]
                vm resize [NAMES] [--size=SIZE]
                vm images [--cloud=CLOUD]
                vm flavors [--cloud=CLOUD]

            Arguments:
                NAMES          server name. By default it is set to the name of last vm from database.
                NAME           server name.

            Options:
                --ip=IP           give the public ip of the server
                --cloud=CLOUD     give a cloud to work on, if not given, selected
                                  or default cloud will be used
                --flavor=FLAVOR   give the name or id of the flavor
                --image=IMAGE     give the name or id of the image
                --command=COMMAND specify the commands to be executed


            Description:
                commands used to boot, start or delete servers of a cloud

                vm boot [options...]
                    Boots servers on a cloud, user may specify flavor, image
                    .etc, otherwise default values will be used, see how to set
                    default values of a cloud: cloud help

                vm start [options...]
                    Starts a suspended or stopped vm instance.

                vm stop [options...]
                    Stops a vm instance .

                vm delete [options...]

                    Delete servers of a cloud, user may delete a server by its
                    name or id, delete servers of a group or servers of a cloud,
                    give prefix and/or range to find servers by their names.
                    Or user may specify more options to narrow the search

                vm ssh [options...]
                    login to a server or execute commands on it

                vm list [options...]
                    same as command "list vm", please refer to it

                vm status [options...]
                    Retrieves status of the VM requested

                vm refresh [--cloud=CLOUDS]
                    this command refreshes the data for virtual machines,
                    images and flavors for the specified clouds.

            Tip:
                give the VM name, but in a hostlist style, which is very
                convenient when you need a range of VMs e.g. sample[1-3]
                => ['sample1', 'sample2', 'sample3']
                sample[1-3,18] => ['sample1', 'sample2', 'sample3', 'sample18']

            Quoting commands:
                cm vm login gvonlasz-004 --command=\"uname -a\"

        """

        def map_parameters(arguments, *args):
            for arg in args:
                flag = "--" + arg
                if flag in arguments:
                    arguments[arg] = arguments[flag]
                else:
                    arguments[arg] = None

        def get_cloud_and_names(label, arguments):
            names = []
            clouds = []
            if arguments["--cloud"]:
                clouds = get_clouds(arguments, variables)
            else:
                clouds = get_clouds(arguments, variables)

            names = get_names(arguments, variables)

            return clouds, names

        def get_cloud_and_names_commands(label, arguments):
            names = []
            clouds = []
            commands = []
            if arguments["--cloud"]:
                clouds = get_clouds(arguments, variables)
            else:
                clouds = get_clouds(arguments, variables)
            names = get_names(arguments, variables)
            commands = get_commands(arguments, variables)
            return clouds, names, commands

        def get_clouds(arguments, variables):
        
            clouds = arguments["cloud"] or arguments["--cloud"]          
            if "active" == clouds:
                active = Active()
                clouds = active.clouds()
            else:
                clouds = clouds

            if (clouds is None) or (clouds == ""):
                Console.error("you need to specify a cloud")
                return None
            return clouds

        def get_names(arguments, variables):
            names = arguments["NAME"] or arguments["NAMES"] or arguments["--name"] or variables["vm"]
            if names is None:
                Console.error("you need to specify a vm")
                return None
            else:
                return names
        def get_image(arguments, variables):
            image = arguments["image"] or arguments["--image"]
            if image is None:
                Console.error("you need to specify an image")
                return None
            else:
                return image

        def get_command(arguments, variables):
            command = arguments["command"] or arguments["--command"]
            if command is None:
                Console.error("you need to specify a command")
                return None
            else:
                return command

        def get_flavor(arguments, variables):
            flavor = arguments["flavor"] or arguments["--flavor"]
            if flavor is None:
                Console.error("you need to specify a flavor")
                return None
            else:
                return flavor

        def get_commands(label, arguments):
            names = []
            if "images" == label:
                clouds = get_clouds(arguments, variables)
                return clouds
            if "flavors" == label:
                clouds = get_clouds(arguments, variables)
                return clouds
            if "boot" == label:
                clouds = get_clouds(arguments, variables)
                names = get_names(arguments, variables)
                image = get_image(arguments, variables)
                flavor = get_flavor(arguments, variables)
                return clouds, names, image, flavor
            if "stop" == label:
                clouds = get_clouds(arguments, variables)
                names = get_names(arguments, variables)
                return clouds, names
            if "start" == label:
                clouds = get_clouds(arguments, variables)
                names = get_names(arguments, variables)
                return clouds, names
            if "list" == label:
                clouds = get_clouds(arguments, variables)
                return clouds
            if "ssh" == label:
                clouds = get_clouds(arguments, variables)
                names = get_names(arguments, variables)
                command = get_command(arguments, variables)
                return clouds, names, command
            if "delete" == label:
                clouds = get_clouds(arguments, variables)
                names = get_names(arguments, variables)
                return clouds, names

        map_parameters(arguments,
                       'cloud',
                       'command',
                       'flavor',
                       'format',
                       'image',
                       'ip',
                       'name',
                       'NAME')

        VERBOSE.print(arguments, verbose=9)

        variables = Variables()

        
        if arguments.images:
            clouds = get_commands("images", arguments)
            if clouds is None:
                return ""
            else:
                p = Provider(clouds)
                images = p.p.images()
                print(Printer.flatwrite(images,
                                sort_keys=("name"),
                                order=["name", "id", "driver"],
                                header=["Name", "Id", "Driver"])
                )
        elif arguments.flavors:
            clouds = get_commands("flavors", arguments)
            if clouds is None:
                return ""
            else:
                p = Provider(clouds)
                flavors = p.p.flavors()
                print(Printer.flatwrite(flavors,
                                sort_keys=("name", "disk"),
                                order=["name", "id", "ram", "disk"],
                                header=["Name", "Id", "RAM", "Disk"])
                )

        elif arguments.boot:

            print("Creating a new vm")
            clouds, names, image, flavor = get_commands("boot", arguments)
            if clouds is None or names is None or image is None or flavor is None:
                return ""
            else:
                p = Provider(clouds)
                node = p.p.create(name=names, size=flavor, image=image)
                print(Printer.flatwrite(node,
                                sort_keys=("name"),
                                order=["name", "state", "public_ips", "private_ips", "size", "image"],
                                header=["Name", "State", "Public IP", "Private IP", "Size", "Image"])
                )  
    
        elif arguments.start:
            print("Starting the requested vm")
            clouds, names = get_commands("start", arguments)
            if clouds is None or names is None:
                return ""
            else:
                p = Provider(clouds)
                node = p.p.start(name=names)

        elif arguments.stop:
            print("Stopping the requested vm")
            clouds, names = get_commands("stop", arguments)
            if clouds is None or names is None:
                return ""
            else:
                p = Provider(clouds)
                node = p.p.stop(name=names)


        elif arguments.delete:
            print("Delete the specified VM")
            clouds, names = get_commands("delete", arguments)
            if clouds is None or names is None:
                return ""
            else:
                p = Provider(clouds)
                p.p.destroy(name=names)

            return ""

        elif arguments.list:
            print("list the vms in the cloud")

            clouds = get_commands("list", arguments)
            if clouds is None:
                return ""
            else:
                p = Provider(clouds)
                vms = p.p.list()
                print(Printer.flatwrite(vms,
                                sort_keys=("name"),
                                order=["name", "state", "public_ips", "private_ips", "size", "image"],
                                header=["Name", "State", "Public IP", "Private IP", "Size", "Image"])
                )


        elif arguments.resize:
            """
            vm resize [NAMES] [--size=SIZE]
            """
            pass

        elif arguments.ssh:

            print("ssh  into the vm and execute command")

            clouds, names, command = get_commands("ssh", arguments)
            if clouds is None or names is None or command is None:
                return ""
            else:
                p = Provider(clouds)
                p.p.ssh(name=names, command=command)
