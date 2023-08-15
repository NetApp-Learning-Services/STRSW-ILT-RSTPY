
################################################################################
# REST API Scripts
#          This script was developed by NetApp to help demonstrate NetApp
#          technologies.  This script is not officially supported as a
#          standard NetApp product.
#
# Purpose: Script to create a snapshot of a volume.
#
#
# Usage:   %> create_snapshot_rewrite.py <args>
#
# Author:  Smith Gregg (smith@netapp.com)
#
# NETAPP CONFIDENTIAL
# -------------------
# Copyright 2020 NetApp, Inc. All Rights Reserved.
#
# NOTICE: All information contained herein is, and remains the property
# of NetApp, Inc.  The intellectual and technical concepts contained
# herein are proprietary to NetApp, Inc. and its suppliers, if applicable,
# and may be covered by U.S. and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law. Dissemination of this
# information or reproduction of this material is strictly forbidden unless
# permission is obtained from NetApp, Inc.
#
################################################################################

import argparse
import requests
import netapp_ontap
from netapp_ontap import config,HostConnection
from netapp_ontap import config
from netapp_ontap.resources import Volume
from netapp_ontap.resources.snapshot import Snapshot


requests.packages.urllib3.disable_warnings()

def get_uuid(vol_name):	
    for volume in Volume.get_collection():
        volume.get()
        if volume.name == vol_name:
          return volume.uuid

def print_result(snapshot):
    if(snapshot.post(poll=True)):
        print ("Snapshot  %s created Successfully" % snapshot.name)
    else:
        print ("Error: Snapshot was not created")
    return
	
def create_snapshot(vol_name,snapshot_name):
    vol_uuid = get_uuid(vol_name)
	
    snapshot = Snapshot.from_dict({
      'name': snapshot_name,
      'volume.uuid': vol_uuid
    })

    print_result(snapshot)
    return
	
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Passing variables to the program')
    parser.add_argument('-api','--api', help='API server IP:port details',dest='api',required=True)
    parser.add_argument('-apiuser','--apiuser', help='Add APIServer Username',dest='apiuser',required=True)
    parser.add_argument('-apipass','--apipass', help='Add APIServer Password',dest='apipass',required=True)
    parser.add_argument('-v','--vol_name', help='Volume to create or clone from',dest='vol_name',required=True)
    parser.add_argument('-s','--snapshot_name', help='Snapshot to create or clone from',dest='snapshot_name')
    globals().update(vars(parser.parse_args()))
    config.CONNECTION = HostConnection(api,apiuser,apipass,verify=False)
    create_snapshot(vol_name,snapshot_name)


