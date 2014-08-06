#!/usr/bin/python
# coding: utf-8

# Copyright (C) 2013-2014 Pivotal Software, Inc.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the under the Apache License,
# Version 2.0 (the "License”); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os, subprocess, sys, json, copy, getpass
import docker
from utils import ssh
from utils import cmdutil

NAMESPACE = "dcloud"
VERSION = "0.2"

COMMAND_CREATE = "create"
COMMAND_LIST = "list"
COMMAND_HOSTSFILE = "hostsfile"
COMMAND_DESTROY = "destroy"
COMMAND_SNAPSHOT = "snapshot"
COMMAND_DELETESNAPSHOT = "deletesnapshot"
COMMAND_ARCHIVE = "archive"

REPO_DNS_BASE = "{0}/dns-base:{1}".format(NAMESPACE, VERSION)

class RunResult:
    dns = ""
    hosts = ""

_WORK_DIR = "/tmp/dcloud_work"

def usage():
    print "Usage:"
    print "  " + COMMAND_CREATE + ":    Create dcloud cluster. dcloud "
    print "  " + COMMAND_LIST + ":      List dcloud clusters"
    print "  " + COMMAND_HOSTSFILE + ": Outputs hosts file format to a specified file. Users can redirect it to /etc/hosts"
    print "  " + COMMAND_DESTROY + ":   Destroy a dcloud cluster"
    print "  " + COMMAND_SNAPSHOT + ":  Snapshot a dcloud cluster. This is to 'docker commit' to all Docker containers in a specified cluster"
    print "  " + COMMAND_DELETESNAPSHOT + ":  Delete a cluster snapshot."
    # print "  " + COMMAND_ARCHIVE + ":   Make a tar ball of cluster nodes"

def usageCreate():
    print "usage:  dcloud create [-id <cluster_id>] <dcluster_config file>"
    print "  -id option overrides the clusterId specified in the config file"
    print "  e.g. dcloud create example/cluster_from_images.json"

def _parseHostname(exp):
    '''
    node1.mydomain.com --> ["node1.mydomain.com"]
    node[1..3].mydomain.com --> ["node1.mydomain.com", "node2.mydomain.com", "node3.mydomain.com"]
    '''
    if "[" not in exp and "]" not in exp:
        return [exp]
    
    expStart = int(exp.index("["))
    dotdotStart = exp.index("..")
    expEnd = int(exp.index("]"))
    startNumber = int(exp[expStart+1:dotdotStart])
    endNumber = int(exp[dotdotStart+2:expEnd])
    result = []
    for i in range(startNumber, endNumber + 1):
        result.append(exp[:expStart] + str(i) + exp[expEnd+1:])
    return result
    
def _flattenHostname(conf):    
    copiedNodes = copy.deepcopy(conf["nodes"])
    conf["nodes"] = []
    for node in copiedNodes:
        hostnames = _parseHostname(node["hostname"])
        for hostname in hostnames:
            newnode = copy.deepcopy(node)
            newnode["hostname"] = hostname
            conf["nodes"].append(newnode)
            
    return conf

def _flattenDockerfile(conf):
    for node in conf["nodes"]:
        if "Dockerfile" in node:
            tempImageName = conf["id"] + "/" + node["hostname"].replace("[", "_").replace("]", "_")
            cmdutil.execute(["docker", "build", "-t", tempImageName, node["Dockerfile"]])
            node["imageName"] = tempImageName
    return conf


def create(clusterConfigFilePath, overrideClusterId):
    '''
    return:
    {
       "dns": "172.17.0.2",
       "hosts": "172.17.0.2 master\n172.17.0.3 slave1\n172.17.04 slave2"
    }
    '''
    
    dnsServerAddress = None
    hosts = ""
    
    with open(clusterConfigFilePath, "r") as conffile:
        conf = conffile.read()
    
    try:
        clusterConfig = json.loads(conf)
    except ValueError as e:
        print "Given cluster config json file " + clusterConfigFilePath + " is invalid "
        print e.message
        return 1
        
    # docker build if Dockerfile is specified
    clusterConfig = _flattenDockerfile(clusterConfig)

    clusterConfig = _flattenHostname(clusterConfig)
    
    if overrideClusterId != None:
        clusterConfig["id"] = overrideClusterId

    # Append DNS
    dnsNode = {
        "hostname" : "dclouddns",
        "imageName" : REPO_DNS_BASE,
        "cmd" : "service sshd start && tail -f /var/log/yum.log"
    }
    clusterConfig["nodes"].insert(0, dnsNode)

    for i in range(len(clusterConfig["nodes"])):
        # The first iteration is for DNS
        node = clusterConfig["nodes"][i]

        container_name = _generateContainerName(clusterConfig["id"], node["hostname"])

        cmd = ["docker", "run"
		    , "-d" # daemon
      		, "--privileged"]

        # DNS
        cmd.append("--dns")
        if i == 0:
            cmd.append("127.0.0.1") # localhost 
        else:
            cmd.append(dnsServerAddress)

        if "dns" in clusterConfig:
            for dnsIp in clusterConfig["dns"]:
                cmd.append("--dns")
                cmd.append(dnsIp)

        if "domain" in clusterConfig:
            cmd.append("--dns-search")
            cmd.append(clusterConfig["domain"])

        cmd.append("--name")
        cmd.append(container_name)

        fqdn = node["hostname"] + "." + clusterConfig["domain"]
        cmd.append("-h")
        cmd.append(fqdn)

        if "volumes" in node:
            for volumn in node["volumes"]:
                cmd.append("-v")
                cmd.append(volumn)

        cmd.append(node["imageName"])
        cmd.append("bash")
        cmd.append("-c")
        cmd.append(node["cmd"])
        print "executing: " + ' '.join(cmd)
        subprocess.call(cmd)

        ip = docker.getContainerIpAddress(container_name)
        if i == 0:
            dnsServerAddress = ip
        hosts += ip + " " + fqdn + " " + node["hostname"] + "\n"

    print "dnsServerAddress: " + dnsServerAddress
    if(not ssh.connection_check(dnsServerAddress, "root", "changeme")):
        print "**** ERROR ****"
        print "ssh connection to root@" + dnsServerAddress + " could not be established"
        return 1

    ssh.exec_command2(dnsServerAddress, "root", "changeme", "echo '" + hosts + "' > /etc/dcloud/dnsmasq/hosts")
    ssh.exec_command2(dnsServerAddress, "root", "changeme", "service dnsmasq restart")

    print "hosts:"
    print hosts
    result = RunResult()
    result.dns = dnsServerAddress
    result.hosts = hosts
    return 0

def destroy(dClusterId):
    psResult = docker.ps()
    for item in psResult:
        dclusterName, _nodeName = _parseContainerName(item.name)
        if dclusterName == dClusterId:
            subprocess.call(["docker", "kill", item.containerId])
            docker.rm(item.containerId, True)

def listClusterInfo(dClusterId=None):
    psResult = docker.ps()
    if dClusterId is None:
        clusterIds = []
        for container in psResult:
            clusterName, _ = _parseContainerName(container.name)
            if clusterName is not None and clusterName not in clusterIds:
                clusterIds.append(clusterName)
        print "cluster Ids"
        print "\n".join(clusterIds)
        return

    for container in psResult:
        clusterName, _ = _parseContainerName(container.name)
        if clusterName == dClusterId:
            ip = docker.getContainerIpAddress(container.name)
            print ip
            
def hostsfile(dclusterId, outputfile):
    hosts = ""
    psResult = docker.ps()
    for container in psResult:
        clusterName, _ = _parseContainerName(container.name)
        if clusterName == dclusterId:
            container = docker.getContainer(container.name)
            hosts += container.ip + " " + container.fqdn + " " + container.hostname + "\n"
    with open(outputfile, "w") as text_file:
        text_file.write(hosts)

    print 0

DCLOUD_MANAGED_CONTAINER_PREFIX = "dcloud_managed--"
DCLOUD_MANAGED_CONTAINER_DIVIDER = "--.--"

def _parseContainerName(containerName):
    '''
    "dcloud_managed--example_cluster--.--node2" --> "example_cluster" and "node2"
    "conatiner1" --->  None and None
    '''
    if(DCLOUD_MANAGED_CONTAINER_PREFIX in containerName and DCLOUD_MANAGED_CONTAINER_DIVIDER in containerName):
        return containerName[len(DCLOUD_MANAGED_CONTAINER_PREFIX):containerName.index(DCLOUD_MANAGED_CONTAINER_DIVIDER)], containerName[containerName.index(DCLOUD_MANAGED_CONTAINER_DIVIDER)+len(DCLOUD_MANAGED_CONTAINER_DIVIDER):]
    else:
        return None, None

def _generateContainerName(clusterName, hostname):
    return DCLOUD_MANAGED_CONTAINER_PREFIX + clusterName + DCLOUD_MANAGED_CONTAINER_DIVIDER + hostname
            
def snapshot(dClusterId, tag=None):
    psResult = docker.ps()
    for container in psResult:
        clusterId, nodeName = _parseContainerName(container.name)
        if clusterId == dClusterId:
            if tag is None:
                subprocess.call(["docker", "commit", container.name, clusterId + "/" + nodeName])
            else:
                subprocess.call(["docker", "commit", container.name, clusterId + "/" + nodeName + ":" + tag])

def deletesnapshot(dClusterId, tag=None):
    images = docker.images()
    for image in images:
        if image.repository.startswith(dClusterId) and tag is None:
            cmdutil.execute(["docker", "rmi", image.repository + ":" + image.tag])
        elif image.repository.startswith(dClusterId + "/") and tag == image.tag:
            cmdutil.execute(["docker", "rmi", image.repository + ":" + image.tag])


def getContainers(dClusterId):
    psResult = docker.ps()
    result = []
    for container in psResult:
        clusterId, nodeName = _parseContainerName(container.name)
        if clusterId == dClusterId:
            result.append(container)
            
    return result


def archive(dClusterId, repo=None):
    '''
    Export docker containers and make a tar.gz
    '''
    if repo is None:
        repo = dClusterId
        
    ARCHIVE_DIR = _WORK_DIR + "/" + dClusterId
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

    # docker export
    containers = getContainers(dClusterId)
    for container in containers:
        _, nodeName = _parseContainerName(container.name)

        print "Exporting " + container.name + "..."
        with open(ARCHIVE_DIR + "/" + repo + "-" + nodeName + ".tar", "w") as file1:
            p = subprocess.Popen(["docker", "export", container.name], stdout=file1)
            p.wait()
            file1.flush()

    # tar.gz
    archive_file = dClusterId + ".tar.gz"
    print "Making " + archive_file + "..."
    subprocess.Popen(["tar", "-zcvf", archive_file, dClusterId], cwd=_WORK_DIR).wait()
    print "Making " + archive_file + ".md5..."
    with open(archive_file + ".md5", "w") as file1:
        subprocess.Popen(["md5sum", archive_file, dClusterId], cwd=_WORK_DIR, stdout=file1).wait()
        file1.flush()


def parseCreateParams(argv):

    argLength = len(argv)
    if argLength != 1 and argLength !=3:
        raise ParseException()

    if argLength == 1:
        clusterId = None
        file1 = argv[0]
    else:
        if argv[0] != "-id":
            raise ParseException()

        clusterId = argv[1]
        file1 = argv[2]

    return file1, clusterId

def main():
    if(len(sys.argv) <= 1):
        usage()
        return 0

    if not os.path.exists(_WORK_DIR):
        os.makedirs(_WORK_DIR)
        
    if getpass.getuser() != "root":
        print "Currently only root user is supported. It is an outstanding issue. https://jira.greenplum.com/browse/HDQA-85"
        return 1
        
    if not docker.installed():
        print "docker command is not available. Follow the installation document http://docs.docker.io/installation and install docker"
        return 1

    command = sys.argv[1]
    if command == COMMAND_DESTROY:
        if len(sys.argv) != 3:
            print "usage: destroy <dClusterId>"
            return 1

        destroy(sys.argv[2])

    elif command == COMMAND_CREATE:
        try:
            conffile, overrideClusterId = parseCreateParams(sys.argv[2:])
        except ParseException:
            usageCreate()
            return 1
        return create(conffile, overrideClusterId)
        
    elif command == COMMAND_SNAPSHOT:
        if len(sys.argv) == 3:
            snapshot(sys.argv[2])
        elif len(sys.argv) == 4:
            snapshot(sys.argv[2], sys.argv[3])
        else:
            print "usage: snapshot <dClusterId> [<tag>]"
            print "This will make docker images of the specified cluster."
            print "Image name becomes"
            print "REPOSITORY               TAG"
            print "<dClusterId>/<hostname>  <tag>"
            return 1

    elif command == COMMAND_DELETESNAPSHOT:
        if len(sys.argv) == 3:
            deletesnapshot(sys.argv[2])
        elif len(sys.argv) == 4:
            deletesnapshot(sys.argv[2], sys.argv[3])
        else:
            print "usage: deletesnapshot <dClusterId> [<tag>]"
            return 1

        
    elif command == COMMAND_ARCHIVE:
        if len(sys.argv) == 3:
            archive(sys.argv[2])
        elif len(sys.argv) == 4:
            archive(sys.argv[2], sys.argv[3])

        else:
            print "usage: archive <dClusterId> [<repo>]"
            return 1

    elif command == COMMAND_LIST:
        if len(sys.argv) > 2:
            listClusterInfo(sys.argv[2])
        else:
            listClusterInfo()

    elif command == COMMAND_HOSTSFILE:
        if len(sys.argv) != 4:
            print "usage: hostsfile <dClusterId> <file>"
            return 1
        
        hostsfile(sys.argv[2], sys.argv[3])

    else:
        usage()
        return 1

if __name__ == '__main__' :
    sys.exit(main())

class ParseException(Exception):
    pass
