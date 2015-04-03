# vminspector
Retrieve files from vhd which is stored in Azure Storage.

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
Now, you can run the script by:

    python inspector.py

and follow the help message(The usage part.).    
Please make sure that you have the access to the vhd you want to retrieve.

Issue
=====
Only support accessing the blob by using account key for the time being.    
And it should be able to achieve it by using shared access signature in the near future.

