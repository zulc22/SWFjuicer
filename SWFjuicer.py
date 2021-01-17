#!/usr/bin/env python3

# OPTIONS (will be set by command later)
NOREADME = False
EXTRACT = True

import sys, os, re, struct, os.path 

if not NOREADME:
    if os.path.isfile('README.txt'):
        with open('README.txt', 'r') as fp:
            print(fp.read())
    else:
        print("""
SWFjuicer 0.2.0

README.txt not found
""")

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

# FWS=uncompressed, CWS=zlib'd (6+), ZWS=LZMA'd (13+)
HEAD_DESC = {
    b'FWS': "uncompressed SWF header",
    b'CWS': "compressed SWF header, zlib",
    b'ZWS': "compressed SWF header, LZMA"
}

def processFile(f:str):
    
    print("Reading",f,"into RAM...\n")
    
    fp = open(f,"rb") # File pointer
    fc = fp.read() # File contents
    fp.close()

    print("Searching for headers...")

    unverified = []
    SWFs = []
    
    for h in HEAD_DESC.keys():
        unverified.extend( allOccurences(fc, h) )

    for o in unverified:
        header = fc[o:o+3]
        print(f"\nFound '{header.decode()}' ({HEAD_DESC[header]}) @",hex(o))

        swfVersion = fc[o+3]
        print("SWF format version (c+0x03) is", swfVersion)
        if (swfVersion >= 0x10):
            print("Active@ says a SWF with a version over 0x10 "+
                  "can't exist, making the file invalid.")
            continue
        
        # FWS=uncompressed, CWS=zlib'd (6+), ZWS=LZMA'd (13+)
        if (header == f'CWS' and swfVersion < 6):
            print("zlib compressed SWF files were not supported until SWF version 6,"+
                 " making this file invalid.")
            continue
        if (header == f'ZWS' and swfVersion < 13):
            print("LZMA compressed SWF files were not supported until SWF version 13,"+
                 " making this file invalid.")
            continue

        swfSize = struct.unpack('<I', fc[o+4:o+8])[0]
        print("SWF size (<I+0x04..0x08) is", swfSize)
        if (swfSize > len(fc)-o):
            print("SWF goes beyond end of file, meaning this SWF "+
                  "cannot possibly be valid or extractable.")
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

    bfn = os.path.basename(f)
    if EXTRACT:
        print(f"Extracting SWFs to current directory... ({os.getcwd()})\n")
        for o in SWFs:
            n = f"{bfn}_{hex(o[0])}.swf"
            print(f" {n}")
            with open(n, 'wb') as fp:
                fp.write(fc[ o[0] : o[0]+o[1] ])
        print()

for file in files:
    processFile(file)
