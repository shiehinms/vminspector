# vminspector
extract data from vhd

Installation
============
Download the repo using git

    git clone https://github.com/shiehinms/vminspector.git

Dependencies
============

    (sudo) pip install Construct azure

Usage
=====
Now, you can run the script by:

    python inspector.py

and follow the help message(The usage part.).

Please make sure that you have the access to the vhd you want to retrieve.

Issue
=====

Only support accessing the blob by account key for the time being.
It should be able to achieve it by shared access signature in the near future.

