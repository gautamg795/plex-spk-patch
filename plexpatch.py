#! /usr/bin/env python3

import tarfile
import argparse
import io
import shutil
import patch

PATCH = patch.fromstring(
"""
--- scripts/postinst	2020-06-07 19:36:36.000000000 -0700
+++ scripts/postinst	2020-06-07 19:39:48.000000000 -0700
@@ -68,63 +68,6 @@
 # Log file output where it's located
 echo "Plex share located at $PLEX_LIBRARY_PATH"
 
-
-# Set rights on Plex share
-synoshare --setuser Plex RW = plex,admin
-
-# Add friendly warnings not to place media files in the Plex share in multiple languages
-# English, German, French, Spanish, Japanese, Chinese (simplified)
-touch "$PLEX_LIBRARY_PATH/Please do not place any media files here."
-touch "$PLEX_LIBRARY_PATH/Bitte legen Sie hier keine Mediendateien ab."
-touch "$PLEX_LIBRARY_PATH/Veuillez ne placer aucun fichier multimédia ici."
-touch "$PLEX_LIBRARY_PATH/Por favor, no coloque ningún archivo multimedia aquí."
-touch "$PLEX_LIBRARY_PATH/ここにメディアファイルを置かないでください。"
-touch "$PLEX_LIBRARY_PATH/请不要在此处放置任何媒体文件。"
-
-# Set the ACLs to standard
-synoacltool -del $PLEX_LIBRARY_PATH
-synoacltool -add $PLEX_LIBRARY_PATH group:administrators:allow:rwxpdDaARWc--:fd--
-synoacltool -add $PLEX_LIBRARY_PATH user:admin:allow:rwxpdDaARWc:fd--
-synoacltool -add $PLEX_LIBRARY_PATH user:plex:allow:rwxpdDaARWcCo:fd--
-
-# Verify the Plex share is visible from File Station for those with access permission
-synoshare --setbrowse Plex 1
-
-# Create temp transcoding and "Plex Media Server" directories if required
-if [ ! -d $PLEX_LIBRARY_PATH/tmp_transcoding ]; then
-  mkdir   $PLEX_LIBRARY_PATH/tmp_transcoding
-fi
-
-if [ ! -d  "$PLEX_LIBRARY_PATH/Library/Application Support/Plex Media Server" ]; then
-  mkdir -p "$PLEX_LIBRARY_PATH/Library/Application Support/Plex Media Server"
-fi
-
-# Are Ownership corrections needed?  ( We will do this normally when first creating the share. )
-FixOwner=0;
-
-# If plex:users is not the current owner of Library,  make it so
-[ -d $PLEX_LIBRARY_PATH/Library ]         && [ "$(stat -c %U $PLEX_LIBRARY_PATH/Library)" != "plex"  ] && FixOwner=1
-[ -d $PLEX_LIBRARY_PATH/Library ]         && [ "$(stat -c %G $PLEX_LIBRARY_PATH/Library)" != "users" ] && FixOwner=1
-
-[ -d $PLEX_LIBRARY_PATH/tmp_transcoding ] && [ "$(stat -c %U $PLEX_LIBRARY_PATH/tmp_transcoding)" != "plex"  ] && FixOwner=1
-[ -d $PLEX_LIBRARY_PATH/tmp_transcoding ] && [ "$(stat -c %G $PLEX_LIBRARY_PATH/tmp_transcoding)" != "users" ] && FixOwner=1
-
-# Do we need set owner & group?
-if [ $FixOwner -eq 1 ]; then
-
-  # Fix tmp_transcoding, Preferences.xml and Plug-in Support first
-  chown -R plex:users $PLEX_LIBRARY_PATH/tmp_transcoding
-  chown plex:users "$PLEX_LIBRARY_PATH/Library/Application Support/Plex Media Server/Preferences.xml"
-  chown -R plex:users "$PLEX_LIBRARY_PATH/Library/Application Support/Plex Media Server/Plug-in Support"
-
-  # Now launch the blanket fix-everything
-  chown -R plex:users $PLEX_LIBRARY_PATH/Library &
-
-  # Give the chown time to execute before starting. (minimize false errors for large libraries)
-  sleep 3
-fi
-
-
 # To handle TV Butler cards and fix HW Transcoding we need to make a Video group and fix some devices.
 
 # Setup udev rule for TV Butler device for that specific vendor ID.""".encode('utf8'))


def main():
    parser = argparse.ArgumentParser(
        description="Remove the permissions-changing code and annoying 'Do not place media files here' files from a Plex update SPK. Creates a backup of the input file with the suffix `.bak`."
    )
    parser.add_argument("filename", help="SPK file to edit")
    args = parser.parse_args()

    intar = tarfile.open(args.filename, mode="r:")
    member = intar.getmember("scripts/postinst")
    data = intar.extractfile(member)
    assert data, "Couldn't find postinst script"
    newlines = PATCH.patch_stream(data, PATCH.items[0])
    outbuf = io.BytesIO()
    outbuf.writelines(list(newlines))
    intar.close()
    shutil.copyfile(args.filename, args.filename + ".bak")
    outtar = tarfile.open(args.filename, mode="a:")
    member.size = outbuf.tell() - 1
    outbuf.seek(0)
    print("Output size: %s" % member.size)
    outtar.addfile(member, outbuf)
    outtar.close()


if __name__ == "__main__":
    main()
