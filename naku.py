#! /usr/local/bin/python3.11

"""
Purpose: Script to create using the netapp_ontap library.
         It will create an SVM.
         It will create an NFS server.
Usage: naku.py [-h] -c CLUSTER -vs VSERVER_NAME, -a AGGR_NAME,  -d DOMAIN, -s SERVER_IP,
                    -se NFS_SERVER, [-u API_USER] [-p API_PASS]
"""

import argparse
from getpass import getpass
import logging
from typing import Optional

from netapp_ontap import config, utils, HostConnection, NetAppRestError
from netapp_ontap.resources import Svm, NfsService, ExportPolicy, ExportRule

def create_svm(vserver_name: str, aggr_name: str) -> None:
    """Create an SVM on the specified aggregate"""

    svm = Svm.from_dict({
    'name': vserver_name,
    'aggregates': [{'name': aggr_name}],
    'nfsv3': {'enabled': "true"},
    'nfsv4': {'enabled': "false"},
    'nfsv41': {'enabled': "false"}
    })

    try:
        svm.post()
        print("SVM %s created successfully" % svm.name)
    except NetAppRestError as err:
        print("Error: SVM was not created: %s" % err)
    return

def create_nfs_server(vserver_name: str, domain_name: str, nfs_server: str, server_ip: str) -> None:
    """Creates a NFS server"""

    SVM = Svm.find(name=vserver_name)

    data = {
        'name': nfs_server,
        'scope': 'svm',
        'svm': {'name': vserver_name, 'uuid': SVM.uuid},
        'protocol': {'v4_id_domain': domain_name},
        'vstorage_enabled': 'true'
    }

    nfs_service = NfsService(**data)

    try:
        nfs_service.post()
        print("NFS Server %s created successfully" % nfs_server)
    except NetAppRestError as err:
        print("Error: NFS Server was not created: %s" % err)
    return

def parse_args() -> argparse.Namespace:
    """Parse the command line arguments from the user"""

    parser = argparse.ArgumentParser(
        description="This script will create a new NFS Share for a given VServer"
    )
    parser.add_argument(
        "-c", "--cluster", required=True, help="Cluster Name"
    )
    parser.add_argument(
        "-vs", "--vserver_name", required=True, help="VServer name to create NFS Share"
    )
    parser.add_argument(
        "-a", "--aggr_name", required=True, help="Aggregate name"
    )
    parser.add_argument(
        "-d", "--domain", required=True, help="DNS DOmain Name"
    )
    parser.add_argument(
        "-s", "--server_ip", required=True, help="DNS Server IP Address"
    )
    parser.add_argument(
        "-se", "--nfs_server", required=True, help="NFS Server"
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
    #    level=logging.DEBUG,
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)5s] [%(module)s:%(lineno)s] %(message)s",
    )
    args = parse_args()
    config.CONNECTION = HostConnection(
        args.cluster, username=args.api_user, password=args.api_pass, verify=False,
    )

    create_svm(args.vserver_name, args.aggr_name)
    create_nfs_server(args.vserver_name, args.domain, args.nfs_server, args.server_ip)
