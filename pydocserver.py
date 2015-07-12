#!/usr/bin/env python
import os
import glob
import json
import sys
import shutil
import argparse
def run(coderoot, docroot=None, port=8000, forceRegen=False):
    import SimpleHTTPServer
    import SocketServer

    if not coderoot:
        print "You must specify a code root folder."
        exit(1)
    
    if not docroot or not os.path.exists(docroot):
        docroot = "."
        
    docroot_abspath = os.path.abspath(os.path.join(docroot, "pydoclib/chart"))
    os.chdir(docroot_abspath)

    data_dir = os.path.join(docroot_abspath, "data")

    # Make sure we can find the files we need
    libdir = os.path.join(docroot_abspath)
    if not os.path.exists(libdir):
        print "LIBDIR=%s" % libdir
        print "Please make sure pydoclib folder is in your docroot [%s]" % (docroot)
        exit(1)
        
    # Check for package.json
    pkgname = os.path.basename(coderoot)
    datapath = os.path.join(coderoot, "package.json")
    if not os.path.exists(os.path.join(data_dir, pkgname)) or forceRegen:
        from pydoclib.treegen import make_pkg_tree
        make_pkg_tree(coderoot)
    
    dest_path = os.path.join(data_dir, pkgname)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
        
    # Make package-list.json
    pkglist = {}
    dirs = glob.glob(os.path.join(data_dir, "*"))
    for d in dirs:
        if os.path.isdir(d):
            path = os.path.basename(d)
            pkglist[path.capitalize()] = path
    
    with open(os.path.join(data_dir, "package-list.json"), 'w') as f:
        json.dump(pkglist, f)
    
    shutil.copy(datapath, os.path.join(dest_path, "package.json"))

    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    
    httpd = SocketServer.TCPServer(("", port), Handler)
    
    print "serving at port", port
    httpd.serve_forever()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run python doc treemap server')
    parser.add_argument('coderoot',
                       help='Source root dir for a code tree')
    parser.add_argument('--force-regen', action='store_true',
                        default=False,
                        help='Regenerate package')
    args = parser.parse_args()
    run(args.coderoot, forceRegen=args.force_regen)
