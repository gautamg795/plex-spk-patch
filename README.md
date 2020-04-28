# plex-spk-patch
Patch the .spk files for updating Plex on Synology such that they don't reset permissions on the Plex share, and so they don't create the "Don't place media in this folder" warning files in 10 languages. 

usage: `plexpatch.py [-h] filename`

Automatically backs up the input file with the suffix `.bak`.
