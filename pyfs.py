#!/usr/bin/env python
import sys
from datetime import datetime
import pprint

# python filesystem: pyfs
# list of files
# file = dict(path, name, attributes, contents)
# path is list of directories (strings)
# name is stirng
# attributes is string, as in MC VFS
# contents is a byte array
# directories are represented by a file with empty name



# * Command: list archivename
# * Command: copyout archivename storedfilename extractto
# * Command: copyin archivename storedfilename sourcefile
# * Command: rm archivename storedfilename
# * Command: mkdir archivename dirname
# * Command: rmdir archivename dirname
# * Command: run

def get_file_line(file_data):
    permission = file_data["permission"]
    nlinks = 1
    owner = file_data["owner"]
    group = file_data["group"]
    size = str(len(file_data["contents"]))
    filename = file_data["filename"]
    path = '/'.join(file_data["path"])
    file_string = path + "/" + filename
    datetime = file_data["datetime"]
    return "{} {:3} {:8} {:8} {:8} {}  {}".format(
        permission, nlinks, owner, group, size, datetime, file_string)

def get_datetime():
    now = datetime.now()
    #   format: MM-DD-YYYY hh:mm:ss
    return now.strftime("%m-%d-%Y %H:%M:%S")


def contains_dir(file_dicts, path):
    for file_dict in file_dicts:
        if file_dict["path"] == path and file_dict["contents"] == "":
            return True
    return False

def read_from_file(archivename):
    f_in = open(archivename, "r")
    ff = f_in.read()
    f_in.close()
    return eval(ff)

def write_to_file(archivename, file_list):
    out_str = pprint.pformat(file_list, sort_dicts=False)
    f_out = open(archivename, "w")
    f_out.write(out_str)
    f_out.close()

# files: -rw-rw-r--
# dirs:  drwxrwxr-x
def do_list(archivename):
    file_list = read_from_file(archivename)

    # list files
    for file_data in file_list:
        print(get_file_line(file_data))

# copyout archivename storedfilename extractto
def do_copyout(archivename, filename, extractto):
    # read data
    file_list = read_from_file(archivename)

    # configure the path
    path = filename.split('/')
    filename = path[-1]
    del path[-1]

    contents = None
    for (i,file_dict) in enumerate(file_list):
        if file_dict["path"] == path and file_dict["filename"] == filename:
            contents = file_dict["contents"]

    if not contents is None:
        f_out = open(extractto, "wb")
        f_out.write(contents)
        f_out.close()

# copyin archivename storedfilename sourcefile
def do_copyin(archivename, storedfilename, sourcefile):
    # read data
    file_list = read_from_file(archivename)

    f_in = open(sourcefile, "rb")
    contents = bytearray(f_in.read())
    f_in.close()

    datetime = get_datetime()

    # configure the path
    path = storedfilename.split('/')
    fn = path[-1]
    del path[-1]

    if fn == "": # path is directory, nothing to do here
        return

    # create file_dict
    file_dict_new = {"path" : path, "filename" : fn, "permission": "-rw-rw-r--", 
                 "owner" : "owner", "group" : "group",
                 "datetime": datetime, "contents": contents}

    existing_file_index = None
    for (i,file_dict) in enumerate(file_list):
        if file_dict["path"] == path and file_dict["filename"] == fn:
             existing_file_index = i
             
    if not existing_file_index is None:
        del file_list[i]
    file_list.append(file_dict_new)

    # write files
    write_to_file(archivename, file_list)
    

# rm archivename storedfilename
def do_rm(archivename, filename):
    # read data
    file_list = read_from_file(archivename)

    # configure the path
    path = filename.split('/')
    filename = path[-1]
    del path[-1]

    index_to_remove = None
    for (i,file_dict) in enumerate(file_list):
        if file_dict["path"] == path and file_dict["filename"] == filename:
            index_to_remove = i

    if not index_to_remove is None:
        del file_list[index_to_remove]

        # write data
        write_to_file(archivename, file_list)

# mkdir archivename dirname
def do_mkdir(archivename, dirname):
    # read data
    file_list = read_from_file(archivename)

    # insert directory with whole path
    path = dirname.split('/')
    datetime = get_datetime()
    p = []
    for dir_path in path:
        p.append(dir_path)
        if not contains_dir(file_list, p):
            new_path = p.copy()
            new_dir = {"path" : new_path, "filename" : "", "permission": "drwxrwxr-x", 
                       "owner" : "owner", "group" : "group",
                       "datetime": datetime, "contents": ""}
            file_list.append(new_dir)

    # write data
    write_to_file(archivename, file_list)
    
# rmdir archivename dirname
def do_rmdir(archivename, dirname):
    # read data
    file_list = read_from_file(archivename)

    # remove the directory
    dd = dirname[0:-1] if dirname[-1] == '/' else dirname # remove trailing '/'
    path = dd.split('/')
    index_to_remove = None
    is_empty = True
    for (i,file_dict) in enumerate(file_list):
        p = file_dict["path"]
        if p == path and file_dict["contents"] == "":
            index_to_remove = i
        elif p[0:len(path)] == path:
            is_empty = False

    if not index_to_remove is None and is_empty:
        del file_list[index_to_remove]

        # write data
        write_to_file(archivename, file_list)


def do_cat(archivename, filename):
    # read data
    file_list = read_from_file(archivename)

    # configure the path
    path = filename.split('/')
    filename = path[-1]
    del path[-1]

    contents = None
    for (i,file_dict) in enumerate(file_list):
        if file_dict["path"] == path and file_dict["filename"] == filename:
            contents = file_dict["contents"]

    if not contents is None:
        print(contents.decode('utf-8'))


command = sys.argv[1]
archivename = sys.argv[2]


match command:
    case "list":
        do_list(archivename)
    case "copyout":
        do_copyout(archivename, sys.argv[3], sys.argv[4])
    case "copyin":
        do_copyin(archivename, sys.argv[3], sys.argv[4])
    case "rm":
        do_rm(archivename, sys.argv[3])
    case "mkdir":
        do_mkdir(archivename, sys.argv[3])
    case "rmdir":
        do_rmdir(archivename, sys.argv[3])
    case "cat":
        do_cat(archivename, sys.argv[3])
    case _:
        print("unknown command {}".format(command))
