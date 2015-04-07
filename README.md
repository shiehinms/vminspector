# vminspector
Retrieve EXT2/3/4 files from vhd which is stored in Azure Storage.

Installation
============
Download the repo using git

    git clone https://github.com/shiehinms/vminspector.git

Dependencies
============

Python module: Construct==2.5.2, azure.    

    (sudo) pip install Construct==2.5.2 azure

Usage
=====
Now, you can run the script by following command:

    python inspector.py

and follow the help message(The usage part.).    
Please make sure that you have the access to the vhd you want to retrieve.

Issue
=====
Only support accessing the blob by using account key for the time being.    
And Vminspector should be able to retrieve vhd by using shared access signature in the near future.

