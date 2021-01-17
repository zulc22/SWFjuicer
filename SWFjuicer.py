#!/usr/bin/env python3

import sys, os, re, struct, os.path 

if os.path.isfile('README.txt'):
    with open('README.txt', 'r') as fp:
        print(fp.read())

if len(sys.argv) < 2:
    print("No files specified. Usage:")
    print()
    python3 = "python3"
    print(f"{python3} ./SWFjuicer.py <file1> [file2] [file3...] ")

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

    # FWS=uncompressed, CWS=zlib'd (6+), ZWS=LZMA'd (13+)

    unverified = allOccurences(fc, b'FWS') 
    SWFs = []

    for o in unverified:
        print("\nFound 'FWS' (uncompressed SWF header) @",hex(o))
        swfVersion = fc[o+3]
        print("SWF format version (c+0x03) is", swfVersion)
        if (swfVersion >= 0x10):
            print("Active@ says a SWF with a version over 0x10 "+
                  "can't exist, making the file invalid.")
            continue
        swfSize = struct.unpack('<I', fc[o+4:o+8])[0]
        print("SWF size (<I+0x04..0x08) is", swfSize)
        if (swfSize > len(fc)-o):
            print("SWF goes beyond end of file, meaning this SWF "+
                  "cannot possibly be extracted from this file.")
            continue
        if (swfSize <= 8):
            print("SWFs cannot POSSIBLY be less than or equal to 8 bytes long.")
            continue
        print("SWF seems valid.")
        SWFs.append([o, swfSize])
    
    print(f"\nCONFIRMED SWF OFFSETS IN '{f}':")
    for o in SWFs:
        print(hex(o[0]),"..",hex(o[0]+o[1]))
    if len(SWFs) == 0:
        print("None valid found.")
    print()

for file in files:
    processFile(file)
