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

import dcloud.dcloud as dcloud
from nose.tools import ok_ as ok_

class TestDCloud(object):

    def test_parseContainerName(self):
        id1, node = dcloud._parseContainerName("dcloud_managed--example_cluster2--.--node3")
        print id1
        print node
        assert id1 == "example_cluster2"
        assert node == "node3"

        id1, node = dcloud._parseContainerName("dcloud_managed--example-cluster2--.--node3")
        assert id1 == "example-cluster2" # this includes "-" 
        assert node == "node3"

        id1, node = dcloud._parseContainerName("container1")
        assert id1 is None
        assert node is None

        id1, node = dcloud._parseContainerName("dcloud_managed--container1")
        assert id1 is None
        assert node is None

        id1, node = dcloud._parseContainerName("container1--.--host1")
        assert id1 is None
        assert node is None

    def test_generateContainerName(self):
        result = dcloud._generateContainerName("example_cluster1", "host1")
        assert result == "dcloud_managed--example_cluster1--.--host1"

    def test_parseHostname(self):
        hostnames = dcloud._parseHostname("node2.mydomain.com")
        assert len(hostnames) == 1
        assert hostnames[0] == "node2.mydomain.com"

        hostnames = dcloud._parseHostname("node[1..10].mydomain.com")
        assert len(hostnames) == 10
        assert hostnames[0] == "node1.mydomain.com"
        assert hostnames[1] == "node2.mydomain.com"
        assert hostnames[2] == "node3.mydomain.com"
        assert hostnames[9] == "node10.mydomain.com"

        hostnames = dcloud._parseHostname("node[11..12].mydomain.com")
        assert len(hostnames) == 2
        assert hostnames[0] == "node11.mydomain.com"
        assert hostnames[1] == "node12.mydomain.com"
        # TODO add more tests like node[3..1], node[1.....2], node[abc] node[1..], node[], node1..3] etc.
        
    def test_flattenHostname(self):
        config = {
            "id" : "example_cluster1",
            "domain" : "mydomain.com",
            "dns" : ["dns1", "dns2"],
            "nodes": [
                {
                    "hostname" : "node[1..3]",
                    "imageName" : "imagea",
                    "cmd" : "cmd1"
                },
                {
                    "hostname" : "nodeA",
                    "imageName" : "imageb",
                    "cmd" : "cmd2",
                    "volumes" : [
                        "v1",
                        "v2"
                    ]
                }
            ]
        }
        
        config = dcloud._flattenHostname(config)
        assert config["id"] == "example_cluster1"
        assert config["domain"] == "mydomain.com"
        assert config["dns"][0] == "dns1"
        assert config["dns"][1] == "dns2"

        assert len(config["nodes"]) == 4
        assert config["nodes"][0]["hostname"] == "node1"
        assert config["nodes"][0]["imageName"] == "imagea"
        assert "volumes" not in config["nodes"][0]
        assert config["nodes"][1]["hostname"] == "node2"
        assert config["nodes"][1]["imageName"] == "imagea"
        assert "volumes" not in config["nodes"][1]
        assert config["nodes"][2]["hostname"] == "node3"
        assert config["nodes"][2]["imageName"] == "imagea"
        assert "volumes" not in config["nodes"][2]
        assert config["nodes"][3]["hostname"] == "nodeA"
        assert config["nodes"][3]["imageName"] == "imageb"
        assert "volumes" in config["nodes"][3]
        assert config["nodes"][3]["volumes"][0] == "v1"
        assert config["nodes"][3]["volumes"][1] == "v2"

    def test_parseCreateParams(self):
        argv = ["file"] # good
        file1, clusterId = dcloud.parseCreateParams(argv)
        assert file1 == "file"
        assert clusterId == None

        argv = ["-id", "file"] # bad
        try:
            dcloud.parseCreateParams(argv)
            ok_(False, "exception should have been thrown")
        except dcloud.ParseException:
            pass

        argv = ["id", "id", "file"] # bad
        try:
            dcloud.parseCreateParams(argv)
            ok_(False, "exception should have been thrown")
        except dcloud.ParseException:
            pass

        argv = ["-id", "id", "file"] # good
        file1, clusterId = dcloud.parseCreateParams(argv)
        assert file1 == "file"
        assert clusterId == "id"

        argv = ["file", "-id", "id"] # bad
        try:
            dcloud.parseCreateParams(argv)
            ok_(False, "exception should have been thrown")
        except dcloud.ParseException:
            pass
