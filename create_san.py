#! /usr/local/bin/python3.11

"""
Purpose: Script to create sn SVM by using the netapp_ontap library.
         It will create a SVM, a volume, two data interfaces and enable iscsi.
Author: Vish Hulikal
Usage: python3.11 create_san.py [-h] -c CLUSTER -a AGGR_NAME, -n NODE_NAME, -vs VSERVER_NAME, -v VOLUME_NAME -ip DATA_LIF,
                 -lif INTERFACE_NAME,   -nm NET_MASK, [-u API_USER] [-p API_PASS]
"""

import argparse
from getpass import getpass
import logging
from typing import Optional

from netapp_ontap import config, utils, HostConnection, NetAppRestError
from netapp_ontap.resources import Svm, Volume, IpInterface, IscsiService

def create_svm(vserver_name: str, aggr_name: str) -> None:
    """Create an SVM on the specified aggregate"""

    svm = Svm.from_dict({
    'name': vserver_name,
    'aggregates': [{'name': aggr_name}],
    'iscsi': {'enabled': "true"}
    })

    try:
        svm.post()
        print("SVM %s created successfully" % svm.name)
    except NetAppRestError as err:
        print("Error: SVM was not created: %s" % err)
    return

def make_iscsi_service(vserver_name: str) -> None:
    """Enable iSCSI service for an SVM"""

    data = {
        'svm': {'name': vserver_name},
    }

    iScsiService = IscsiService(**data)

    try:
        iScsiService.post()
        print("iSCSI Service %s created successfully" % vserver_name)
    except NetAppRestError as err:
        print("Error: iScsi Service was not created: %s" % err)
    return

def make_volume(volume_name: str, vserver_name: str, aggr_name: str, volume_size: int) -> None:
    """Creates a new volume in a SVM"""

    data = {
        'name': volume_name,
        'svm': {'name': vserver_name},
        'aggregates': [{'name': aggr_name }],
        'size': volume_size,
        'space_guarantee': 'volume'
    }

    volume = Volume(**data)

    try:
        volume.post()
        print("Volume %s created successfully" % volume.name)
    except NetAppRestError as err:
        print("Error: Volume was not created: %s" % err)
    return

def create_data_interface(vserver_name: str, interface_name: str, node_name: str, ip_address: str, ip_netmask: str) -> None:
    """Creates an SVM-scoped IP Interface"""

    data = {
        'name': interface_name,
        'ip': {'address': ip_address, 'netmask': ip_netmask},
        'enabled': True,
        'scope': 'svm',
        'svm': {'name': vserver_name},
        'port': {'name': 'e0d', 'node': node_name},
        'location': {
           'auto_revert': True,
           'broadcast_domain': {'name': 'Default'},
        }
    }

    ip_interface = IpInterface(**data)

    try:
        ip_interface.post()
        print("Ip Interface %s created successfully" % ip_interface.ip.address)
    except NetAppRestError as err:
        print("Error: IP Interface was not created: %s" % err)
    return

def parse_args() -> argparse.Namespace:
    """Parse the command line arguments from the user"""

    parser = argparse.ArgumentParser(
        description="This script will create a SAN configuration"
    )
    parser.add_argument(
        "-c", "--cluster", required=True, help="Cluster Name"
    )
    parser.add_argument(
        "-n", "--node_name", required=True, help="API server Node Name"
    )
    parser.add_argument(
        "-a", "--aggr_name", required=True, help="Aggregate name"
    )
    parser.add_argument(
        "-vs", "--vserver_name", required=True, help="VServer name"
    )
    parser.add_argument(
        "-v", "--volume_name", required=True, help="Volume name"
    )
    parser.add_argument(
        "-ip", "--ip_address", required=True, help="Data Interface IP Address"
    )
    parser.add_argument(
        "-nm", "--ip_netmask", required=True, help="DNS Server IP Address"
    )
    parser.add_argument(
        "-lif", "--interface_name", required=True, help="Interface name"
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

    create_svm(args.vserver_name, args.aggr_name)
    make_volume(args.volume_name, args.vserver_name, args.aggr_name, 300000000)
    create_data_interface(args.vserver_name, args.interface_name, args.node_name, args.ip_address, args.ip_netmask)
