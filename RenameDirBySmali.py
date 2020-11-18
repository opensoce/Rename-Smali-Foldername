#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import random
import sys
import json
import shutil


def handleWalkError(err):
    print ('Error When Access ', err.filename)
    print (err)


def move_files(source_dir, dest_dir):
    try:
        shutil.move(source_dir, dest_dir)
    except (IOError, OSError) as ex:
        pass

def rename_dir2(source_dir, dest_dir):  # Rename a directory
    try:
        os.renames(source_dir, dest_dir)
    except OSError as ex:
        move_files(source_dir, dest_dir)
        

def rename_dir(source_dir, dest_dir):  # Rename a directory
    try:
        shutil.copytree(source_dir, dest_dir)
    except Exception as e:
        try:
            shutil.move(source_dir, dest_dir)
        except Exception as ee:
            pass
    try:
        shutil.rmtree(source_dir)
    except Exception as e:
        pass


def processSmali(smali_root):
    smali_root = os.path.abspath(smali_root)
    length = len(smali_root)
    _letterPath = {}
    _dirPath = {}
    for root, dirsaa, files in os.walk(smali_root, onerror=handleWalkError):
        dir = root[length+1:].replace(os.sep,'/')
        dirs = dir.split('/')
        if len(dirs[0])==1 or len(dirs[-1])==1:
            if dir not in _dirPath:
                dir2 = ''
                for d in dirs:
                    if (len(d)==2 and d[-1].isnumeric()) or (len(d)==1) :
                        if d not in _letterPath:
                            _letterPath[d] = 'dir'+d
                        dir2 = dir2 + '/' + _letterPath[d]
                    else:
                        dir2 = dir2 + '/' + d
                dir2 = dir2[1:]
                _dirPath[dir] = dir2

    #sort by key length desc
    new_d = {}
    for k in sorted(_dirPath, key=len, reverse=True):
        new_d[k] = _dirPath[k]
    _dirPath = new_d.copy()
    # replace all classes
    for root, dirs, files in os.walk(smali_root, onerror=handleWalkError):
        if not files:
            continue
        for f in files:
            if f.endswith(".smali"):
                smalifile = os.path.join(root, f)
                content = open(smalifile, 'r').read()
                for dir in _dirPath:
                    content = content.replace('L' + dir + '/', 'L' + _dirPath[dir] + '/')
                    content = content.replace('L' + dir + ';', 'L' + _dirPath[dir] + ';')
                open(smalifile, 'w').write(content)

    #rename dir Recursion
    hasLetter = True
    while (hasLetter):
        hasLetter=False
        for root, dirs, files in os.walk(smali_root):
            if not dirs:
                continue
            for d in dirs:
                if d in _letterPath:
                    hasLetter = True
                    olddir = os.path.join(root, d)
                    newdir = os.path.join(root, _letterPath[d])
                    rename_dir2(olddir, newdir)
    jsObj = json.dumps(sorted(_dirPath), indent=4)
    fileObject = open('_dirMap.json', 'w')
    fileObject.write(jsObj)
    fileObject.close()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print ('Please provide root directory for smali')
        sys.exit(2)
    smali_root = sys.argv[1]
    print ('Begine to process *.smali under ', smali_root)
    processSmali(smali_root)
    print ('Done')
