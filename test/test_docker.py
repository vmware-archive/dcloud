# coding: utf-8

# Copyright (C) 2013-2014 Pivotal Software, Inc.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the under the Apache License,
# Version 2.0 (the "License”); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import dcloud.docker as docker

class TestDocker(object):

    def test_parsePsResult(self):
        lines = []
        lines.append("CONTAINER ID        IMAGE               COMMAND                CREATED             STATUS              PORTS               NAMES")
        lines.append("f61811577af2        phd:base            bash -c cp /tmp/phd-   9 minutes ago       Up 9 minutes                            mycluster2-node3")
        lines.append("079ed8874604        phd:base            bash -c cp /tmp/phd-   9 minutes ago       Up 9 minutes                            mycluster2-node2")
        lines.append("845fda0ffb74        phd:installed       bash -c /tmp/phd-doc   9 minutes ago       Up 9 minutes                            mycluster2-node1")
        lines.append("5f7434e4b690        phd:base            bash -c cp /tmp/phd-   9 minutes ago       Up 9 minutes                            mycluster1-node3")
        lines.append("e677692a7022        phd:base            bash -c cp /tmp/phd-   9 minutes ago       Up 9 minutes                            mycluster1-node2")
        lines.append("e2481e18d7a8        phd:installed       bash -c /tmp/phd-doc   9 minutes ago       Up 9 minutes                            mycluster1-node1")
        lines.append("")
        result = docker._parsePsResult(lines)
        assert type(result) is list
        assert len(result) == 6
        assert result[0].containerId == "f61811577af2"
        assert result[0].image == "phd:base"
        assert result[0].name == "mycluster2-node3"
        assert result[2].image == "phd:installed"
        assert result[5].name == "mycluster1-node1"

        # IMAGE can be stretched
        lines = []
        lines.append("CONTAINER ID        IMAGE                    COMMAND                CREATED             STATUS              PORTS               NAMES")
        lines.append("a620be5b6456        dcloud/ssh-base:latest   bash -c 'service ssh   2 days ago          Up 53 minutes                           dcloud_managed--example_cluster1--.--node3")
        lines.append("f0ff75e2901c        dcloud/ssh-base:latest   bash -c 'service ssh   2 days ago          Up 53 minutes                           dcloud_managed--example_cluster1--.--node2")
        lines.append("ea3817d1f94c        dcloud/ssh-base:latest   bash -c 'service ssh   2 days ago          Up 53 minutes                           dcloud_managed--example_cluster1--.--node1")
        lines.append("fdfcf7093a4a        dcloud/dns-base:latest   bash -c 'service ssh   2 days ago          Up 53 minutes                           dcloud_managed--example_cluster1--.--dclouddns")
        lines.append("")
        result = docker._parsePsResult(lines)
        assert type(result) is list
        assert len(result) == 4
        assert result[0].containerId == "a620be5b6456"
        assert result[0].image == "dcloud/ssh-base:latest"
        assert result[0].name == "dcloud_managed--example_cluster1--.--node3"
        
        
    def test_parseImageResult(self):
        lines = []
        lines.append("REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE")
        lines.append("phd                 node1               8a756bdf28a1        20 hours ago        4.843 GB")
        lines.append("phd                 node2               038cc981bd17        20 hours ago        1.375 GB")
        lines.append("phd                 node3               b075304686bc        20 hours ago        1.375 GB")
        lines.append("phd                 installed           46554a76f21b        2 days ago          4.733 GB")
        lines.append("phd                 downloaded          8e2c2488aaf0        2 days ago          3.011 GB")
        lines.append("phd                 base                942d6d279916        2 days ago          757.1 MB")
        lines.append("shipyard/lb         latest              f9630ba9f8be        7 days ago          474.4 MB")
        lines.append("shipyard/deploy     latest              41c4a39f38b8        12 days ago         268.5 MB")
        lines.append("shipyard/shipyard   latest              de1e3c2965de        12 days ago         538.6 MB")
        lines.append("shipyard/db         latest              a8187138ceed        12 days ago         301.2 MB")
        lines.append("shipyard/router     latest              71e73a8db7c4        4 months ago        609.9 MB")
        lines.append("shipyard/redis      latest              b48b681ac984        4 months ago        300.6 MB")
        lines.append("centos              6.4                 539c0211cd76        12 months ago       300.6 MB")
        lines.append("centos              latest              539c0211cd76        12 months ago       300.6 MB")
        lines.append("")

        result = docker._parseImageResult(lines)
        assert type(result) is list
        assert len(result) == 14
        assert result[0].repository == "phd"
        assert result[0].tag == "node1"
        assert result[0].imageId == "8a756bdf28a1"
        assert result[0].created == "20 hours ago"
        assert result[0].virtualSize == "4.843 GB"

        assert result[13].repository == "centos"
        assert result[13].tag == "latest"
        assert result[13].imageId == "539c0211cd76"
        assert result[13].created == "12 months ago"
        assert result[13].virtualSize == "300.6 MB"

        # if one of REPOSITORY is longer it could be stretched. Make sure _parseImageResult calculates dynamically
        lines = []
        lines.append("REPOSITORY                   TAG                 IMAGE ID            CREATED             VIRTUAL SIZE")
        lines.append("example_cluster1/node1       latest              42ee8837ca63        18 minutes ago      424.2 MB")
        lines.append("example_cluster1/dclouddns   latest              dad59ded9c9c        18 minutes ago      436.6 MB")
        lines.append("example_cluster1/node3       latest              9c00be5d5fe6        18 minutes ago      424.2 MB")
        lines.append("example_cluster1/node2       latest              d339d47e6086        18 minutes ago      424.2 MB")
        lines.append("dcloud/dns-base              latest              efb25cea9714        3 hours ago         436.6 MB")
        lines.append("dcloud/ssh-base              latest              aee60b7025b4        3 hours ago         424.2 MB")
        lines.append("centos                       6.4                 539c0211cd76        13 months ago       300.6 MB")
        lines.append("")

        result = docker._parseImageResult(lines)
        assert type(result) is list
        assert len(result) == 7
        assert result[0].repository == "example_cluster1/node1"
        assert result[0].tag == "latest"
