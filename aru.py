#! /usr/bin/env python3

"""
Purpose: Script to create sn SVM by using the netapp_ontap library.
         It will create a Group, a lun and map the igroup to the lun.
Author: Vish Hulikal
Usage: python3.11 aru.py [-h] -c CLUSTER -vs VSERVER_NAME, -l LUN_NAME -ig IGROUP_NAME
       [-u API_USER] [-p API_PASS]
"""

import argparse
from getpass import getpass
import logging
from typing import Optional

from netapp_ontap import config, utils, HostConnection, NetAppRestError
from netapp_ontap.resources import Volume, Lun, Igroup, LunMap

def create_igroup(igroup_name: str, vserver_name: str) -> None:
    """Create an Igroup on the SVM"""

    data = {
        'name': igroup_name,
        'svm': {'name': vserver_name},
        'protocol': 'iscsi',
        'os_type': 'windows'
    }

    igroup = Igroup(**data)

    try:
        igroup.post()
        print("Igroup %s created successfully" % igroup.name)
    except NetAppRestError as err:
        print("Error: Igroup was not created: %s" % err)
    return

def create_lun(lun_name: str, vserver_name: str, lun_size: int) -> None:
    """Creates a new lun in a volume"""

    data = {
        'name': lun_name,
        'svm': {'name': vserver_name},
        'space': {'size': lun_size},
        'os_type': 'windows'
    }

    lun = Lun(**data)

    try:
        lun.post()
        print("Lun %s created successfully" % lun.name)
    except NetAppRestError as err:
        print("Error: Lun was not created: %s" % err)
    return

def create_lun_map(vserver_name: str, igroup_name: str, lun_name: str) -> None:
    """Create a map between Lun and the igroup"""

    data = {
        'svm': {'name': vserver_name},
        'igroup': {'name': igroup_name},
        'lun': {'name': lun_name}
    }

    lun_map = LunMap(**data)

    try:
        lun_map.post()
        print("Lun Map %s created successfully" % lun_map.igroup.name)
    except NetAppRestError as err:
        print("Error: Lun Map was not created: %s" % err)
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
        "-vs", "--vserver_name", required=True, help="VServer name"
    )
    parser.add_argument(
        "-l", "--lun_name", required=True, help="LUN path-name"
    )
    parser.add_argument(
        "-ig", "--igroup_name", required=True, help="Igroup name"
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

    create_igroup(args.igroup_name, args.vserver_name)
    create_lun(args.lun_name, args.vserver_name, 30000000)
    create_lun_map(args.vserver_name, args.igroup_name, args.lun_name)
