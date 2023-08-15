#! /usr/bin/env python3.7
from netapp_ontap import config
from netapp_ontap import HostConnection
from netapp_ontap.resources import Node
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
conn = HostConnection("192.168.0.111", username = "admin", password = "Netapp1!", verify = False)
config.CONNECTION = conn  
node = Node()
node.get()
print (node)
