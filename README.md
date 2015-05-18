# vminspector
Retrieve EXT2/3/4 files from vhd which is stored in Azure Storage.

Functionality
==========
You can use vminspector to retrieve your file from Azure Storage need not to turn off you Virtual Machine.    

You can access your vhd file by using:    

- Account Key
- shared access signature (i.e. SAS)

You can combine your container key and container name to form a URL. More detail will be covered in the following section.

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
After installation of the tool and dependencies, you can run the script by following command:

    python inspector.py

and follow the help message(The usage part.).    
Please make sure that you have the access to the vhd you want to retrieve.

Options:
-----------
    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -u URL, --url=URL     Url of the vhd *
    -k ACCOUNT_KEY, --key=ACCOUNT_KEY
                        Account Key
    -f FILENAME, --file=FILENAME
                        File name
    -p PATH, --path=PATH  Searching path *
    -e EXTENSION, --extension=EXTENSION
                        Extension
    -t TYPE, --type=TYPE  EXT2/3/4; 2,3,4
    --ls                  List the dir

-

-u    

Ever vhd stored in Azure Storage have a URL address, which can be used to locate the vhd file. You can get the url of a particular vhd file from Portal.

-

-k    

The account key of your container. Notice that, -k and -e are mutually exclusive.

-

-f    

the file which you want to retrieve. Notice that, the absolute path of the file should not be passed.

-

-p    

The directory which contain the file you want to retrieve.

-

-e    

The extension of files you want to retrieve. Notice that, -k and -e are mutually exclusive.

-

-t    

Predeclared the file system of your virtual machine if you actually know it. This option is used to speed up the parsing process.

-

--ls    

If you want to inspect a specific directory before you take any action about it, you can list them.


Issue
=====
- For the time being, this tool can only be used to retrieve file remotely, but can not be used to revise the vhd file. However, revisability is a more practical functionality we want, and it's on the schedule.
- It would take approximately 15s to retrieve a single file.