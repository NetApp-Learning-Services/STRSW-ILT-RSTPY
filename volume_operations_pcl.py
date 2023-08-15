#! /usr/bin/env python3

"""
ONTAP REST API Python Sample Scripts

This script was developed by NetApp to help demonstrate NetApp technologies. This
script is not officially supported as a standard NetApp product.

Purpose: THE FOLLOWING SCRIPT SHOWS VOLUME OPERATIONS USING REST API PCL

Usage: volume_operations_restapi_pcl.py -a <Cluster Address> -u <User Name> -p <Password Name>
"""

import argparse
import requests
from getpass import getpass
import logging

import json,sys,ssl
from netapp_ontap import config,HostConnection, NetAppRestError
from netapp_ontap.resources import Svm, Volume, Node, Aggregate

config.RAISE_API_ERRORS = True

requests.packages.urllib3.disable_warnings()

def get_size(vol_size):
    tmp = int(vol_size) * 1024 * 1024
    return tmp

def show_aggregate(api,apiuser,apipass):
    config.CONNECTION = HostConnection(api,apiuser,apipass,verify=False)
    print ("\n List of Aggregates:- \n")
    for aggregatelist in Aggregate.get_collection(fields="uuid"):
        print (aggregatelist.name)
    return
	
def show_svm(api,apiuser,apipass):	
    config.CONNECTION = HostConnection(api,apiuser,apipass,verify=False)
    print()
    print ("Getting SVM Details")
    print ("===================")
    for svm in Svm.get_collection(fields="uuid"):
        print ("SVM name:-%s ; SVM uuid:-%s " % (svm.name,svm.uuid))
		
		
def show_volume(api,apiuser,apipass):	
    config.CONNECTION = HostConnection(api,apiuser,apipass,verify=False)
    print("The List of SVMs")
    show_svm(api,apiuser,apipass)
    print()
    svm_name = input("Enter the SVM from which the Volumes need to be listed:-")
    print()
    print ("Getting Volume Details")
    print ("===================")
    for volume in Volume.get_collection(**{"svm.name": svm_name},fields="uuid"):
        print("Volume Name = %s;  Volume UUID = %s" % (volume.name,volume.uuid))
    return

def create_volume(api,apiuser,apipass):
    config.CONNECTION = HostConnection(api,apiuser,apipass,verify=False)
    print()	
    show_svm(api,apiuser,apipass)
    print()	
    svmname = input("Enter the name of the SVM on which the volume needs to be created:- ")
    dataObj = {}
    tmp1={"name": svmname}
    dataObj['svm']=tmp1
    print()	
    show_aggregate(api,apiuser,apipass)
    print()	
    aggrname = input("Enter the name of the Aggregate on which the volume needs to be created:- ")
    tmp2=[{"name": aggrname}]
    dataObj['aggregates']=tmp2
    print()	
    volname = input("Enter the name of the Volume:- ")
    dataObj['name']=volname
    print()	
    vol_size = input("Enter the size of the Volume in MBs:- ")
    tmp3=get_size(vol_size)
    dataObj['size']=tmp3
    print()	
    	   
    volume = Volume.from_dict(dataObj)
    
    try:
        if(volume.post(poll=True)):
            print ("SVM  %s created Successfully" % volume.name)
    except NetAppRestError as e:
        print ("HTTP Error Code is " % e.http_err_response.http_response.text)
        print("Exception caught :" + str(e)) 		
    
    return


	
def patch_volume(api,apiuser,apipass):
    config.CONNECTION = HostConnection(api,apiuser,apipass,verify=False)
    
    print ("=============================================")
    print()	
    show_volume(api,apiuser,apipass)
    print()	
    vol_name = input("Enter the name  of the volume that needs to be modified:- ") 
    
    vol = Volume.find(name=vol_name)
    
    dataObj = {}
    print()	
    nambool = input("Would you like to change the volume name (y/n):- ")
    if nambool == 'y':
       nam = input("Enter the new name of the Volume: ")
       vol.name=nam
    
    print()	
    sizebool = input("Would you like to change the volume size (y/n) :- ")
    if sizebool == 'y':
       vol_size = input("Enter the new size of the Volume: ")
       vol_size_format=get_size(vol_size)
       vol.size=vol_size_format
	   
    print()	
    statebool = input("Would you like to change the volume state (y/n) :- ")
    if statebool == 'y':
       vol_state = input("Enter the new state of the Volume [offline/online]: ")
       vol.state = vol_state
       
    try:
        if(vol.patch(poll=True)):
            print ("The Volume  has been updated/patched Successfully")
    except NetAppRestError as e:
        print ("HTTP Error Code is " % e.http_err_response.http_response.text)
        print("Exception caught :" + str(e)) 	

    return

def delete_volume(api,apiuser,apipass):
    config.CONNECTION = HostConnection(api,apiuser,apipass,verify=False)

    print ("=============================================")
    print()	
    show_volume(api,apiuser,apipass)
    print()	
    volname = input("Enter the name of the volume that needs to be Deleted:- ")
    vol = Volume.find(name=volname)
	
    try:
        if(vol.delete(poll=True)):
            print ("Volume  has been deleted Successfully.")
    except NetAppRestError as e:
        print ("HTTP Error Code is " % e.http_err_response.http_response.text)
        print("Exception caught :" + str(e)) 	
    return
	
def snapshot_volume(api,apiuser,apipass):
    print()
    print("The List of SVMs")
    show_svm(api,apiuser,apipass)
    print()
    svm_name = input("Enter the SVM on which the Volume Snapshot need to be created:-")
    print()
    show_volume(api,apiuser,apipass)
    print()
    vol_uuid = input("Enter the Volume UUID on which the Snapshots need to be created:-")

    print()
    snapshot_name = input("Enter the name of the snapshot to be created:-")
	
    snapshot = Snapshot.from_dict({
    'name': snapshot_name,
    'volume.uuid': vol_uuid
    })

    try:
        if(snapshot.post(poll=True)):
            print ("Snapshot  %s created Successfully" % snapshot.name)
    except NetAppRestError as e:
        print ("HTTP Error Code is " % e.http_err_response.http_response.text)
        print("Exception caught :" + str(e)) 
    return
	
	
def clone_volume(api,apiuser,apipass):
    config.CONNECTION = HostConnection(api,apiuser,apipass,verify=False)
    
    print ("=============================================")
    print()	
    show_volume(api,apiuser,apipass)
    print()
    svm_name = input("Enter the NAME of the SVM the parent volume belongs to:-  ")
    svm_uuid =  input("Enter the UUID of the SVM the parent volume belongs to [UUID]:- ")	
    vol_name = input("Enter the NAME of the volume that needs to be Cloned:- ")
    vol_uuid =  input("Enter the UUID of the volume that needs to be Cloned [UUID]:- ")
    print()
    dataObj = {}
    clone_name = input("Enter the name of the clone:- ")
    
    tmp={'uuid': svm_uuid}
    dataObj['svm']=tmp
    
    dataObj['name']= clone_name
	
    clone_volume_json={"is_flexclone": bool("true"),"parent_svm": {"name": svm_name,"uuid": svm_uuid},"parent_volume": {  "name": vol_name,"uuid": vol_uuid}}
    
    dataObj['clone']=clone_volume_json
    
    clonesnapshot = input("Would you like to Clone from Snapshot (y/n): ")
    if clonesnapshot == 'y':
       snapshot_name = input("Enter the name of the snapshot that needs to be Cloned:- ")
       snapshot_uuid=get_key_snapshot(snapshot_name,vol_uuid)
       clone_snapshot_json={"is_flexclone": bool(true),"parent_snapshot": {"name": snapshot_name,"uuid": snapshot_uuid},"parent_svm": {"name": svmname,"uuid": svm_uuid},"parent_volume": {  "name": vol_name,"uuid": vol_uuid}}
       dataObj['clone']=clone_snapshot_json
	
    volume = Volume.from_dict(dataObj)
    
    try:
        if(volume.post(poll=True)):
            print ("SVM  %s created Successfully" % volume.name)
    except NetAppRestError as e:
        print ("HTTP Error Code is " % e.http_err_response.http_response.text)
        print("Exception caught :" + str(e)) 	
    
    return
	
def patch_collection_volume(api,apiuser,apipass):
    """Turn the given volumes off then on again"""
    print ("=============================================")
    print()	
    show_volume(api,apiuser,apipass)
    print()
    noofnames= int(input("Enter number of Volumes to be Updated [eg: int value:1,2,3] : "))
    volume_names = list(map(str,input("\nEnter the Volume names to be updated [eg: aaa bbb ccc] : ").strip().split()))[:noofnames]
    volume_names_final = '|'.join([str(v) for v in volume_names])
    vol_state = input("Enter the new state of the Volume [offline/online]: ")
    page_size = min(len(volume_names_final) - 1, 1)
    
    try:
        Volume.patch_collection({"state": vol_state}, name=volume_names_final, max_records=page_size)
        print(list(Volume.get_collection(fields='state', name=volume_names_final)))
    except NetAppRestError as e:
        print ("HTTP Error Code is " % e.http_err_response.http_response.text)
        print("Exception caught :" + str(e)) 
    return	
        	
def delete_collection_volume(api,apiuser,apipass):
    print ("=============================================")
    print()	
    show_volume(api,apiuser,apipass)
    print()
    noofnames= int(input("Enter number of Volumes to be Deleted [eg: int value:1,2,3] : "))
    volume_names = list(map(str,input("\nEnter the Volume names to be Deleted [eg: aaa bbb ccc] : ").strip().split()))[:noofnames]
    volume_names_final = '|'.join([str(v) for v in volume_names])
    vol_state = input("Enter the new state of the Volume [offline/online]: ")
    page_size = min(len(volume_names_final) - 1, 1)

		
    try:
        Volume.delete_collection(name=volume_names_final)
        print(list(Volume.get_collection()))
    except NetAppRestError as e:
        print ("HTTP Error Code is " % e.http_err_response.http_response.text)
        print("Exception caught :" + str(e))
    return
	
def volume_ops(api,apiuser,apipass):
    print()
    print("THE FOLLOWING SCRIPT SHOWS VOLUME OPERATIONS USING REST API:- ")
    print("============================================================")
    print()
    volumebool = input("What Volume Operation would you like to do? [show/create/update/delete/clone/snapshot/batch_patching/batch_deleting] ")
    if volumebool  == 'show':
       show_volume(api,apiuser,apipass)
    if volumebool  == 'create':
       create_volume(api,apiuser,apipass)   
    if volumebool  == 'update':
       patch_volume(api,apiuser,apipass)
    if volumebool  == 'delete':
       delete_volume(api,apiuser,apipass)
    if volumebool  == 'clone':
       clone_volume(api,apiuser,apipass)
    if volumebool  == 'snapshot':
       snapshot_volume(api,apiuser,apipass)
    if volumebool  == 'batch_patching':
       patch_collection_volume(api,apiuser,apipass)
    if volumebool  == 'batch_deleting':
       delete_collection_volume(api,apiuser,apipass)

    return
	
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Passing variables to the program')
    parser.add_argument('-api','--api', help='API server IP:port details',dest='api',required=True)
    parser.add_argument('-apiuser','--apiuser', help='Add APIServer Username',dest='apiuser',required=True)
    parser.add_argument('-apipass','--apipass', help='Add APIServer Password',dest='apipass',required=True)
    globals().update(vars(parser.parse_args()))
    volume_ops(api,apiuser,apipass)


