#! /usr/bin/env python3.7

"""
ONTAP 9.10 REST API Python Client Library Scripts
Author: Vish Hulikal
This script performs the following:
        - Create an SVM (or VServer)
        - Create an S3 user
        - Create an S3 bucket
ONTAP S3 License: GARXWLLISPYQSDAAAAAAAAAAAAAA
Minimum size of the bucket to be created: 102005473280B

usage: python3 object.py [-h] -c CLUSTER -vs VSERVER_NAME -a AGGR_NAME -s S3_NAME -b BUCKET_NAME
               -un S3_USER_NAME -n SIZE [-u API_USER] [-p API_PASS]
These arguments required: -c/--cluster, -vs/--vserver_name, -a/--aggr_name, -s/--s3_name, -b/--bucket_name
               -un/--s3_user_name, -n/--size, -u/--admin, -p/--password
Usage: python3 object.py -c cluster1 -vs VServer1 -a aggr1 -s S3_Server -b s3bucket -un S3_User -n 102005473280 -u admin -p Netapp1!
"""

import argparse
from getpass import getpass
import logging

from netapp_ontap import config, HostConnection, NetAppRestError
from netapp_ontap.resources import Aggregate, Svm, S3BucketSvm, S3User

def create_svm(vserver_name: str, aggr_name: str, S3_name: str) -> None:
    """Create an SVM on the specified aggregate and configures an S3 server.
       access_key and secret_key - are returned from the Post call."""

    svm = Svm.from_dict({
      'name': vserver_name,
      'aggregates': [{'name': aggr_name}],
      's3.name': S3_name,
      'enabled': "true",
    })

    try:
        svm.post()
        print("SVM %s created successfully" % svm.name)
    except NetAppRestError as err:
        print("Error: SVM was not created: %s" % err)
    return

def make_s3_user(vserver_name: str, user_name: str) -> None:
    """Creates a new S3 user configuration"""

    vserver = Svm.find(name=vserver_name)
    resource = S3User(vserver.uuid)
    resource.name = user_name

    try:
        resource.post()
        print("S3 User %s created successfully" % resource.name)
#        print("S3 User - Access Key %s", % resource.access_key)
#        print("S3 User - Secret Key %s", % resource.secret_key)
    except NetAppRestError as err:
        print("Error: S3 User was not created" % err)
    return

def make_bucket(vserver_name: str, aggr_name: str, bucket_name: str, bucket_size: int) -> None:
    """Make an S3 Bucket"""

    vserver = Svm.find(name=vserver_name)
    aggregate = Aggregate.find(name=aggr_name)
    resource = S3BucketSvm(vserver.uuid)
    resource.name = bucket_name
    resource.comment = "S3 Bucket"
    resource.aggregates = [
        {'name': aggr_name, 'uuid': aggregate.uuid}
    ]
    resource.constituents_per_aggregate = 4
    resource.size = bucket_size

    try:
        resource.post()
        print("S3 Bucket %s created successfully" % resource.name)
    except NetAppRestError as err:
        print("Error: S3 Bucket was not created: %s" % err)
    return

def parse_args() -> argparse.Namespace:
    """Parse the command line arguments from the user"""

    parser = argparse.ArgumentParser(
        description="This script will create an SVM, an S3 User and an S3 bucket."
    )
    parser.add_argument(
        "-c", "--cluster", required=True, help="API server IP:port details"
    )
    parser.add_argument(
        "-vs", "--vserver_name", required=True, help="SVM name"
    )
    parser.add_argument(
        "-a", "--aggr_name", required=True, help="Aggregate name"
    )
    parser.add_argument(
        "-s", "--s3_name", required=True, help="S3 Server name"
    )
    parser.add_argument(
        "-b", "--bucket_name", required=True, help="Bucket name"
    )
    parser.add_argument(
        "-un", "--user_name", required=True, help="S3 User name"
    )
    parser.add_argument(
        "-n", "--size", required=True, help="Size of the bucket in bytes"
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

    # Create a VServer, an S3 user and a Bucket
    create_svm(args.vserver_name, args.aggr_name, args.s3_name)
    make_s3_user(args.vserver_name, args.user_name)
    make_bucket(args.vserver_name, args.aggr_name, args.bucket_name, args.size)


