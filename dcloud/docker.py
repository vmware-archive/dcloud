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

import subprocess
# from dcloud.utils import cmdutil
import utils.cmdutil as cmdutil

class PsResultItem:
    containerId = None
    image = None
    created = None
    status = None
    ports = None
    name = None

class ImageResultItem:
    repository = None
    tag = None
    imageId = None
    created = None
    virtualSize = None
    
class Container:
    name = None
    ip = None
    hostname = None
    fqdn = None

def installed():
    retcode, _stdout = cmdutil.execute(["which", "docker"])
    if retcode == 0:
        return True

    return False


def _parseImageResult(lines):
    result = []
    print lines[0]
    repoIndex = lines[0].index("REPOSITORY")
    tagIndex = lines[0].index("TAG")
    imageIdIndex = lines[0].index("IMAGE ID")
    createdIndex = lines[0].index("CREATED")
    virtualSizeIndex = lines[0].index("VIRTUAL SIZE")
    for line in lines:
        if line.startswith("REPOSITORY"):
            continue
        if len(line.strip()) == 0:
            continue
        
        item = ImageResultItem()

        item.repository = line[repoIndex:tagIndex].strip()
        item.tag = line[tagIndex:imageIdIndex].strip()
        item.imageId = line[imageIdIndex:createdIndex].strip()
        item.created = line[createdIndex:virtualSizeIndex].strip()
        item.virtualSize = line[virtualSizeIndex:].strip()
        result.append(item)

    return result

def images():
    _retcode, stdout = cmdutil.execute(["docker", "images"])
    return _parseImageResult(stdout.split("\n"))


def imageExist(repo, tag="latest"):
    imageList = images()
    for image in imageList:
        if repo == image.repository and tag == image.tag:
            return True
    return False

def getLatestDockerConatinerId():
    _retcode, stdout = cmdutil.execute(["docker", "ps", "-l", "-q"])
    # return subprocess.check_output(["docker", "ps", "-l", "-q"]).strip("\n")
    return stdout.strip("\n")

# TODO deprecated use getContainer
def getContainerIpAddress(containerName):
    _retcode, stdout = cmdutil.execute(["docker", "inspect", '--format="{{.NetworkSettings.IPAddress}}"', containerName])
    return stdout.strip("\n").strip('"')
    # return subprocess.check_output(["docker", "inspect", '--format="{{.NetworkSettings.IPAddress}}"', containerName]).strip("\n").strip('"')

def getContainer(containerName):
    result = Container()
    result.name = containerName
    _retcode, stdout = cmdutil.execute(["docker", "inspect", '--format="{{.NetworkSettings.IPAddress}}"', containerName])
    result.ip = stdout.strip("\n").strip('"')
    _retcode, stdout = cmdutil.execute(["docker", "inspect", '--format="{{.Config.Hostname}}"', containerName])
    result.hostname = stdout.strip("\n").strip('"')
    _retcode, stdout = cmdutil.execute(["docker", "inspect", '--format="{{.Config.Domainname}}"', containerName])
    result.fqdn = result.hostname + "." + stdout.strip("\n").strip('"')
    return result
    # return subprocess.check_output(["docker", "inspect", '--format="{{.NetworkSettings.IPAddress}}"', containerName]).strip("\n").strip('"')

def rm(containerId, force=False):
    cmd = ["docker", "rm"]
    if force:
        cmd.append("-f")

    cmd.append(containerId)

    subprocess.call(cmd)

def ps():
    '''
root@jaoki-ubuntu:/home/jaoki/coding/phd-docker# docker ps
CONTAINER ID        IMAGE               COMMAND                CREATED             STATUS              PORTS               NAMES
f61811577af2        phd:base            bash -c cp /tmp/phd-   9 minutes ago       Up 9 minutes                            mycluster2-node3
079ed8874604        phd:base            bash -c cp /tmp/phd-   9 minutes ago       Up 9 minutes                            mycluster2-node2
845fda0ffb74        phd:installed       bash -c /tmp/phd-doc   9 minutes ago       Up 9 minutes                            mycluster2-node1
5f7434e4b690        phd:base            bash -c cp /tmp/phd-   9 minutes ago       Up 9 minutes                            mycluster1-node3
e677692a7022        phd:base            bash -c cp /tmp/phd-   9 minutes ago       Up 9 minutes                            mycluster1-node2
e2481e18d7a8        phd:installed       bash -c /tmp/phd-doc   9 minutes ago       Up 9 minutes                            mycluster1-node1
    '''
    # lines = subprocess.check_output(["docker", "ps", "-a"]).split("\n")
    _retcode, stdout = cmdutil.execute(["docker", "ps", "-a"])
    return _parsePsResult(stdout.split("\n"))

def _parsePsResult(lines):
    result = []
    containerIdIndex = lines[0].index("CONTAINER ID")
    imageIndex = lines[0].index("IMAGE")
    commandIndex = lines[0].index("COMMAND")
    createdIndex = lines[0].index("CREATED")
    statusIndex = lines[0].index("STATUS")
    portsIndex = lines[0].index("PORTS")
    namesIndex = lines[0].index("NAMES")

    for line in lines:
        if line.startswith("CONTAINER ID"):
            continue
        if len(line.strip()) == 0:
            continue
        
        process = PsResultItem()

        process.containerId = line[containerIdIndex:imageIndex].strip()
        process.image = line[imageIndex:commandIndex].strip()
        process.created = line[createdIndex:statusIndex].strip()
        process.status = line[statusIndex:portsIndex].strip()
        process.name = line[namesIndex:].strip()
        result.append(process)

    return result


