#!/usr/bin/env python3

print("""
SWFjuicer 0.1.0

This project uses Semantic Versioning 2.0.0. (https://semver.org)

Copyright © 2020 Scott Blacklock <zulc22.db@gmail.com>
This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

Searches any file for valid SWF files barried inside.
Can not check for headers contained within compression.
Created for reverse-engineering of the Leapster 1 and 2, but can be
useful for many flash projects.
""")

import sys, os, re, struct

files = sys.argv[1:]

def allOccurences(c:bytes, sub:bytes):
    start = 0
    occurence = 0
    occurences = []

    while True:
        occurence = c.find(sub, start)
        if occurence != -1:
            start = occurence+1
            occurences.append(occurence)
        else: # occurence == -1 (meaning we already saw the last)
            break
    
    return occurences

def processFile(f:str):
    
    print("Reading",f,"into RAM...\n")
    
    fp = open(f,"rb") # File pointer
    fc = fp.read() # File contents
    fp.close()

    print("Searching for headers...")

    unverified = allOccurences(fc, b'FWS') # FWS=uncompressed, CWS=zlib'd (6+), ZWS=LZMA'd (13+)
    SWFs = []

    for o in unverified:
        print("\nFound 'FWS' (implication of SWF header) @",hex(o))
        swfVersion = fc[o+3]
        print("SWF format version (c+0x03) is", swfVersion)
        if (swfVersion >= 0x10):
            print("Active@ says a SWF with a version over 0x10 "+
                  "can't exist, meaning header must not belong to a SWF.")
            continue
        swfSize = struct.unpack('<I', fc[o+4:o+8])[0]
        print("SWF size (<I+0x04..0x08) is", swfSize)
        if (swfSize > len(fc)-o):
            print("SWF goes beyond end of file, meaning this SWF "+
                  "cannot possibly be extracted from this file.")
            continue
        if (swfSize <= 8):
            print("SWFs cannot POSSIBLY be less or equal to 8 bytes long.")
            continue
        print("From a cursory glance, SWF seems valid.")
        SWFs.append([o, swfSize])
    
    print("\nSWF OFFSETS:")
    for o in SWFs:
        print(hex(o[0]),"..",hex(o[0]+o[1]))
    if len(SWFs) == 0:
        print("None valid found.")
    print()
    


for file in files:
    processFile(file)

os.system("pause")