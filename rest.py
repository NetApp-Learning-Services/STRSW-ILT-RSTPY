#! /usr/bin/env python3.7

"""
ONTAP 9.7 REST API Python Client Library Scripts
Author: Vish Hulikal
This script performs the following:
        - Create an aggregate
        - Create an SVM (or VServer)
        - Create a volume
        - List all volumes

usage: python3.7 rest.py [-h] -c CLUSTER -v VOLUME_NAME -vs VSERVER_NAME -a AGGR_NAME
               -n NODE_NAME -d DISK_COUNT -s VOLUME_SIZE [-u API_USER] [-p API_PASS]
The following arguments are required: -c/--cluster, -v/--volume_name, -vs/--vserver_name,
          -a/--aggr_name, -n/--node_name, -d/--disk_count, -s/--volume_size
"""

import argparse
from getpass import getpass
import logging

from netapp_ontap import config, HostConnection, NetAppRestError
from netapp_ontap.resources import Aggregate, Svm, Volume

def create_aggregate(aggr_name: str, node_name: str, disk_count: int) -> None:
    """Create an aggregate on the specified node"""

    aggregate = Aggregate.from_dict({
    'node': {'name':node_name},
    'name': aggr_name,
    'block_storage': {'primary': {'disk_count': disk_count}}
    })

    try:
        aggregate.post()
        print("Aggregate %s created successfully" % aggregate.name)
    except NetAppRestError as err:
        print("Error: Aggregate was not created: %s" % err)
    return

def create_svm(vserver_name: str, aggr_name: str) -> None:
    """Create an SVM on the specified aggregate"""

    svm = Svm.from_dict({
    'name': vserver_name,
    'aggregates': [{'name': aggr_name}],
    'cifs': {'enabled': "true"}
    })

    try:
        svm.post()
        print("SVM %s created successfully" % svm.name)
    except NetAppRestError as err:
        print("Error: SVM was not created: %s" % err)
    return

def make_volume(volume_name: str, vserver_name: str, aggr_name: str, volume_size: int) -> None:
    """Creates a new volume in a SVM"""

    data = {
        'name': volume_name,
        'svm': {'name':vserver_name},
        'aggregates': [{'name': aggr_name }],
        'size': volume_size
    }

    volume = Volume(**data)

    try:
        volume.post()
        print("Volume %s created successfully" % volume.name)
    except NetAppRestError as err:
        print("Error: Volume was not created: %s" % err)
    return

def list_volumes(vserver_name: str) -> None:
    """List Volumes in a SVM """

    print ("\nList of Volumes:-")
    try:
        for volume in Volume.get_collection(**{"svm.name": vserver_name}):
            volume.get()
            print (volume.name)
    except NetAppRestError as err:
        print("Error: Volume list was not created: %s" % err)
    return

def parse_args() -> argparse.Namespace:
    """Parse the command line arguments from the user"""

    parser = argparse.ArgumentParser(
        description="This script will create a new volume."
    )
    parser.add_argument(
        "-c", "--cluster", required=True, help="API server IP:port details"
    )
    parser.add_argument(
        "-v", "--volume_name", required=True, help="Volume to create or clone from"
    )
    parser.add_argument(
        "-vs", "--vserver_name", required=True, help="SVM to create the volume from"
    )
    parser.add_argument(
        "-n", "--node_name", required=True, help="Node name where to create the aggregate"
    )
    parser.add_argument(
        "-a", "--aggr_name", required=True, help="Aggregate to create the volume from"
    )
    parser.add_argument(
        "-d", "--disk_count", required=True, help="Number of disks in the aggregate"
    )
    parser.add_argument(
        "-s", "--volume_size", required=True, help="Size of the volume."
    )
    parser.add_argument("-u", "--api_user", default="admin", help="API Username")
    parser.add_argument("-p", "--api_pass", help="API Password")
    parsed_args = parser.parse_args()

    # collect the password without echo if not already provided
    if not parsed_args.api_pass:
        parsed_args.api_pass = getpass()

    return parsed_args


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)5s] [%(module)s:%(lineno)s] %(message)s",
    )
    args = parse_args()
    config.CONNECTION = HostConnection(
        args.cluster, username=args.api_user, password=args.api_pass, verify=False,
    )

    # Create an Aggregate, a VServer and a Volume
    create_aggregate(args.aggr_name, args.node_name, args.disk_count)
    create_svm(args.vserver_name, args.aggr_name)
    make_volume(args.volume_name, args.vserver_name, args.aggr_name , args.volume_size)

    # List all volumes in the VServer
    list_volumes(args.vserver_name)
