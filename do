python3.11 rest.py   -c cluster1 -v Vol1 -vs VServer1 -a aggr1 -n cluster1-01 -d 5 -s 30000000 -u admin -p Netapp1!

python3.11 volume.py -c cluster1 -v Vol2 -vs VServer1 -a aggr1 -ma aggr2 -rs 40000000 -s 30000000 -u admin -p Netapp1!

python3.11 snap.py -c cluster1 -v Vol1 -vs VServer1 -s Snap1 -sp SnapPolicy1 -sc NewWeek -u admin -p Netapp1!
-------------------------------------------------------
python3.11 qtree.py -c cluster1 -v Vol1 -vs VServer1 -q QTree1 -qos QoS_Policy1 -sh 1000000 -fh 1000 -un admin -u admin -p Netapp1!
-------------------------------------------------------------------
python3.11 cifs.py -c cluster1 -n cluster1-01 -a aggr1_cluster1_01_data -vs nas_svm_02 -v nas_svm_02_cifs_02 -ip 192.168.0.210 -nm 255.255.255.0 -g 192.168.0.1 -d demo.netapp.com -s 192.168.0.253 -se nas_svm_02 -sh share_02 -pa /nas_svm_02_cifs_02 -u admin -p Netapp1!
---------------------------------------------------------------------
python3.11 nfs.py -c cluster1 -n cluster1-01 -a aggr1_cluster1_01_data -vs nas_svm_03 -v nas_svm_03_nfs_03 -ip 192.168.0.215 -nm 255.255.255.0 -g 192.168.0.1 -d demo.netapp.com -s 192.168.0.253 -se nas_svm_03 -sh /nas_svm_03_nfs_03 -u admin -p Netapp1!
---------------------------------------------------------
python3.11 protocol2.py  -c cluster1 -vs nas_svm -v nas_svm_vol_01 -u admin -p Netapp1!
--------------------------------------------------------------------------------------
python3.11 create_san.py -c cluster1 -n cluster1-01 -a aggr1_cluster1_01_data -vs san_svm -v san_vol -ip 192.168.0.241 -nm 255.255.255.0 -lif san_svm_iscsi_1 -u admin -p Netapp1!
-----------------------
python3.11 create_igroup.py -c cluster1 -vs san_svm -l /vol/san_vol/lun1 -lif san_svm_iscsi_2 -ig igroup1 -n cluster1-02 -ip 192.168.0.242 -nm 255.255.255.0 -u admin -p Netapp1!
----------------------
python3.11 cifs2.py -c cluster1 -a aggr1_cluster1_01_data -vs nas_svm_03 -v nas_svm_03_cifs_03 -sh share_03 -pa /nas_svm_03_cifs_03 -d demo.netapp.com -s 192.168.0.253 -se nas_svm_03  -u admin -p Netapp1!
-----------------------------
python3.11 object.py -c cluster1 -vs VServer1 -a aggr1_cluster1_01_data -s S3_Server -b s3bucket -un S3_User -n 102005473280 -u admin -p Netapp1!
--------------

