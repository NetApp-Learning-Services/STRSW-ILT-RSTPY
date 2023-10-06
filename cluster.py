#! /usr/local/bin/python3.11
from netapp_ontap import config
from netapp_ontap import HostConnection
from netapp_ontap.resources import Cluster
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
conn = HostConnection("192.168.0.101", username = "admin", password = "Netapp1!", verify = False)
config.CONNECTION = conn
clus = Cluster()
clus.get()
print (clus.version)
