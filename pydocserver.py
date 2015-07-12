#!/usr/bin/env python
import os
import glob
import json
import sys
import shutil
import argparse
import SimpleHTTPServer
import SocketServer

def run(coderoots=[], docroot=None, port=8000, forceRegen=False):
    if not docroot or not os.path.exists(docroot):
        docroot = "."

    docroot_abspath = os.path.abspath(os.path.join(docroot, "pydoclib/chart"))
    data_dir = os.path.join(docroot_abspath, "data")

    dirs = filter(lambda d: os.path.isdir(d), glob.glob(os.path.join(data_dir, "*")))

    if not dirs and not pkglist:
        print "You must specify a code root folder to generate a tree map from."
        exit(1)


    os.chdir(docroot_abspath)

    # Make sure we can find the files we need
    libdir = os.path.join(docroot_abspath)
    if not os.path.exists(libdir):
        print "Please make sure pydoclib folder is in your docroot [%s]" % (docroot)
        exit(1)
    
    for coderoot in coderoots:
        # Check for package.json
        pkgname = os.path.basename(coderoot)
        datapath = os.path.join(coderoot, "package.json")
        if not os.path.exists(os.path.join(data_dir, pkgname)) or forceRegen:
            from pydoclib.treegen import make_pkg_tree
            make_pkg_tree(coderoot)
        
        dest_path = os.path.join(data_dir, pkgname)
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        shutil.copy(datapath, os.path.join(dest_path, "package.json"))
    
    # Make package-list.json
    pkglist = {}
    for d in dirs:
        if os.path.isdir(d):
            path = os.path.basename(d)
            pkglist[path.capitalize()] = path

    with open(os.path.join(data_dir, "package-list.json"), 'w') as f:
        json.dump(pkglist, f)

    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    
    httpd = SocketServer.TCPServer(("", port), Handler)
    
    print "serving at port", port
    httpd.serve_forever()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run python doc treemap server')
    parser.add_argument('coderoots', nargs='*',
                       help='Source root dir for a code tree')
    parser.add_argument("--docroot", action="store",
                        default=".", help="Specify docroot to run server from.")
    parser.add_argument('--force-regen', action='store_true',
                        default=False,
                        help='Regenerate package')
    args = parser.parse_args()
    run(args.coderoots, docroot=args.docroot, forceRegen=args.force_regen)
