#! /usr/bin/env python3

import tarfile
import argparse
import io
import shutil


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
    lines = data.readlines()
    start = None
    end = None
    for i, x in enumerate(lines):
        if x.startswith(b"# Set rights on Plex share"):
            assert start is None
            start = i
        if x.startswith(b"# Verify the Plex share is visible"):
            end = i - 1
            break
    assert start, "Couldn't find start block"
    assert end, "Couldn't find end block"
    print("Removing {} lines".format(end-start))
    newlines = lines[:start] + lines[end:]
    outbuf = io.BytesIO()
    outbuf.writelines(newlines)
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
