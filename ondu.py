#! /usr/bin/env python3.7
"""
	Sample Python Script
Author: Vish Hulikal
This will get detials about aggregates.
"""

from netapp_ontap import config
from netapp_ontap import HostConnection
from netapp_ontap.resources import Aggregate
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
conn = HostConnection("192.168.0.111", username = "admin", password = "Netapp1!", verify = False)
config.CONNECTION = conn  
aggr = Aggregate()
aggr.get()
print (aggr)

