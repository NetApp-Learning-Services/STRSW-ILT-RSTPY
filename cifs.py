#! /usr/bin/env python3

"""
Purpose: Script to create sn SVM by using the netapp_ontap library.
         It will create a Data Interface, Network Default, Gateway.
         It will also create a DNS Domain, CIFS Server and CIFS Share.
Author: Vish Hulikal
Usage: cifs.py [-h] -c CLUSTER -a AGGR_NAME, -n NODE_NAME, -vs VSERVER_NAME, -v VOLUME_NAME -ip DATA_LIF, -g GATEWAY, -d DOMAIN, -s SERVER_IP,
                    -nm NET_MASK -se CIFS_SERVER, -sh CIFS_SHARE, -pa PATH, [-u API_USER] [-p API_PASS]
python3.7 cifs.py: -c cluster -a aggr_name, -n/--node_name, -vs/--vserver_name, -v/--volume_name, -ip/--ip_address, -g/--gateway_ip, -d/--domain,
                -s/--server_ip, -nm/--net_mask -se/--cifs_server, -sh/--cifs_share, -pa/--cifs_path
"""

import argparse
from getpass import getpass
import logging
from typing import Optional

from netapp_ontap import config, utils, HostConnection, NetAppRestError
from netapp_ontap.resources import Svm, Volume, IpInterface, NetworkRoute , Dns, CifsService, CifsShare

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

def make_volume(volume_name: str, vserver_name: str, aggr_name: str, net_path: str, volume_size: int) -> None:
    """Creates a new volume in a SVM"""

    data = {
        'name': volume_name,
        'svm': {'name': vserver_name},
        'aggregates': [{'name': aggr_name }],
        'size': volume_size,
        'nas': {'security_style': 'ntfs', 'path': net_path},
        #'junction_path': net_path,
        #'security_style': 'ntfs',
        'space_guarantee': 'volume' 
    }

    volume = Volume(**data)

    try:
        volume.post()
        print("Volume %s created successfully" % volume.name)
    except NetAppRestError as err:
        print("Error: Volume was not created: %s" % err)
    return

def create_mgmt_interface(vserver_name: str, interface_name: str, node_name: str, ip_address: str, ip_netmask: str) -> None:
    """Creates an SVM-scoped IP Interface"""

    data = {
        'name': interface_name,
        'ip': {'address': ip_address, 'netmask': ip_netmask},
        'enabled': True,
        'scope': 'svm',
        'svm': {'name': vserver_name},
        'port': {'name': 'e0c', 'node': node_name},
        'location': {
           'auto_revert': True,
           'broadcast_domain': {'name': 'Default'},
        }
    }

    ip_interface = IpInterface(**data)

    try:
        ip_interface.post()
        print("Management Ip Interface %s created successfully" % ip_interface.ip.address)
    except NetAppRestError as err:
        print("Error: Management IP Interface was not created: %s" % err)
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

def create_route(vserver_name: str, net_gateway_ip: str) -> None:
    """Creates a network route"""
    """The default destination will be set to "0.0.0.0/0" for IPv4 gateway addresses""" 

    data = {
        'gateway': net_gateway_ip,
        'svm': {'name': vserver_name}
    }

    route = NetworkRoute(**data)

    try:
        route.post()
        print("Route %s created successfully" % route.gateway)
    except NetAppRestError as err:
        print("Error: Route was not created: %s" % err)
    return

def create_dns(vserver_name: str, domain: str, dns_server_ip: str) -> None:
    """Creates a DNS server"""

    data = {
        'domains': [domain],
        'servers': [dns_server_ip],
        'svm': {'name': vserver_name}
    }

    dns = Dns(**data)

    try:
        dns.post()
        print("DNS %s created successfully" % dns.domains)
    except NetAppRestError as err:
        print("Error: DNS was not created: %s" % err)
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

def parse_args() -> argparse.Namespace:
    """Parse the command line arguments from the user"""

    parser = argparse.ArgumentParser(
        description="This script will create a new CIFS Share for a given VServer"
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
        "-vs", "--vserver_name", required=True, help="VServer name to create CIFS Share"
    )
    parser.add_argument(
        "-v", "--volume_name", required=True, help="Volume name to create CIFS Share"
    )
    parser.add_argument(
        "-ip", "--ip_address", required=True, help="Data Interface IP Address"
    )
    parser.add_argument(
        "-g", "--gateway_ip", required=True, help="Default Gateway IP Address"
    )
    parser.add_argument(
        "-d", "--domain", required=True, help="DNS DOmain Name"
    )
    parser.add_argument(
        "-s", "--server_ip", required=True, help="DNS Server IP Address"
    )
    parser.add_argument(
        "-nm", "--ip_netmask", required=True, help="DNS Server IP Address"
    )
    parser.add_argument(
        "-se", "--cifs_server", required=True, help="CIFS Server"
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

    create_svm(args.vserver_name, args.aggr_name)
    make_volume(args.volume_name, args.vserver_name, args.aggr_name, args.cifs_path, 300000000)
    #create_mgmt_interface(args.vserver_name, args.vserver_name, args.node_name, args.ip_address, args.ip_netmask)
    create_data_interface(args.vserver_name, args.volume_name, args.node_name, args.ip_address, args.ip_netmask)
    create_route(args.vserver_name, args.gateway_ip)
    create_dns(args.vserver_name, args.cluster, args.server_ip)
    create_cifs_server(args.vserver_name, args.domain, args.cifs_server, args.server_ip)
    create_cifs_share(args.vserver_name, args.cifs_share, args.cifs_path)

