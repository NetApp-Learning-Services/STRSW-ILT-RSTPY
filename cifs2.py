#! /usr/bin/env python3

"""
Purpose: Script use the netapp_ontap library.
         It will create a volume and CIFS Share.
         It will also get the NetBIOS information for the cluster.
Author: Vish Hulikal
Usage: cifs2.py [-h] -c CLUSTER -a AGGR_NAME -vs VSERVER_NAME, -v VOLUME_NAME, -d DOMAIN,
                   -s CIFS_SEVER_IP -se CIFS_SERVER -sh CIFS_SHARE, -pa PATH, [-u API_USER] [-p API_PASS]
"""

import argparse
from getpass import getpass
import logging
from typing import Optional

from netapp_ontap import config, utils, HostConnection, NetAppRestError
from netapp_ontap.resources import Svm, Volume, CifsService, CifsShare
#from netapp_ontap.resources import Netbios

def create_volume(volume_name: str, vserver_name: str, aggr_name: str, net_path: str, volume_size: int) -> None:
    """Creates a new volume in a SVM"""

    data = {
        'name': volume_name,
        'svm': {'name': vserver_name},
        'aggregates': [{'name': aggr_name }],
        'size': volume_size,
        'nas': {'security_style': 'ntfs', 'path': net_path},
        'space_guarantee': 'volume'
    }

    volume = Volume(**data)

    try:
        volume.post()
        print("Volume %s created successfully" % volume.name)
    except NetAppRestError as err:
        print("Error: Volume was not created: %s" % err)
    return

def create_cifs_server(vserver_name: str, domain_name: str, cifs_server: str, server_ip: str) -> None:
    """Creates a CIFS server"""

    SVM = Svm.find(name=vserver_name)

    data = {
        'name': cifs_server,
        'scope': 'svm',
        'svm': {'name': vserver_name, 'uuid': SVM.uuid},
        'ad_domain': {'fqdn': domain_name, 'organizational_unit': 'CN=Computers', 'user': 'Administrator', 'password': 'Netapp1!'},
        'netbios': {'wins_servers': [server_ip]},
        'enabled': 'True'
    }

    cifs_service = CifsService(**data)

    try:
        cifs_service.post()
        print("CIFS Server %s created successfully" % cifs_service.name)
    except NetAppRestError as err:
        print("Error: CIFS Server was not created: %s" % err)
    return

def create_cifs_share(vserver_name: str, net_share: str, net_path: str) -> None:
    """Creates a CIFS share for a CIFS Server"""

    data = {
        'name': net_share,
        'path': net_path,
        'svm': {'name': vserver_name}
    }

    cifs_share = CifsShare(**data)

    try:
        cifs_share.post()
        print("CIFS Share %s created successfully" % cifs_share.name)
    except NetAppRestError as err:
        print("Error: CIFS Share was not created: %s" % err)
    return

###
def get_netbios_info(vserver_name: str) -> None:
    """Get NetBIOS information of the cluster"""

    given_svm = SVM.find(name=vserver_name)
    print(list(Netbios.get_collection(return_timeout=15, fields="*", **{"svm.uuid": given_svm.uuid})))
    return
###

def parse_args() -> argparse.Namespace:
    """Parse the command line arguments from the user"""

    parser = argparse.ArgumentParser(
        description="This script will create a new CIFS Share for a given VServer"
    )
    parser.add_argument(
        "-c", "--cluster", required=True, help="Cluster Name"
    )
    parser.add_argument(
        "-a", "--aggr_name", required=True, help="aggregate name"
    )
    parser.add_argument(
        "-vs", "--vserver_name", required=True, help="VServer name to create CIFS Share"
    )
    parser.add_argument(
        "-v", "--volume_name", required=True, help="Volume name to create CIFS Share"
    )
    parser.add_argument(
        "-s", "--server_ip", required=True, help="CIFS Server IP Address"
    )
    parser.add_argument(
        "-se", "--cifs_server", required=True, help="CIFS Server"
    )
   parser.add_argument(
        "-d", "--domain", required=True, help="Domain"
    )
    parser.add_argument(
        "-sh", "--cifs_share", required=True, help="CIFS Share"
    )
    parser.add_argument(
        "-pa", "--cifs_path", required=True, help="CIFS Share Path"
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

    #utils.LOG_ALL_API_CALLS = 1

    args = parse_args()
    config.CONNECTION = HostConnection(
        args.cluster, username=args.api_user, password=args.api_pass, verify=False,
    )

    create_volume(args.volume_name, args.vserver_name, args.aggr_name, args.cifs_path, 300000000)
    create_cifs_server(args.vserver_name, args.domain, args.cifs_server, args.server_ip)
    create_cifs_share(args.vserver_name, args.cifs_share, args.cifs_path)
#    get_netbios_info(args.vserver_name)



