#! /usr/bin/env python3.7

"""
ONTAP 9.7 REST API Python Client Library Scripts

This script performs the following:
        - Monitors Volume Metrics

usage: python3.7 protocol2.py [-h] -c CLUSTER -v VOLUME_NAME -vs VSERVER_NAME
                 [-u API_USER] [-p API_PASS]
The following arguments are required: -c/--cluster, -v/--volume_name, -vs/--vserver_name,
"""

import argparse
from getpass import getpass
import logging

from netapp_ontap import config, HostConnection, NetAppRestError
from netapp_ontap.resources import Volume, VolumeMetrics

def list_volumes(vserver_name: str) -> None:
    """List Volumes"""
    for volume in Volume.get_collection():
        one_hour_throughput_total = []
        for metrics in VolumeMetrics.get_collection(volume.uuid, fields="throughput.total", interval="1h"):
            one_hour_throughput_total.append(metrics.throughput.total)
        print(f"Throughput over the last hour for volume {volume.name} was {sum(one_hour_throughput_total)}")
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

    # List all volumes
    list_volumes(args.volume_name)


