#!/usr/bin/env python
import os
import sys
import shutil
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

    # Make sure we can find the files we need
    libdir = os.path.join(docroot_abspath)
    if not os.path.exists(libdir):
        print "LIBDIR=%s" % libdir
        print "Please make sure pydoclib folder is in your docroot [%s]" % (docroot)
        exit(1)
        
    # Check for package.json
    datapath = os.path.join(coderoot, "package.json")
    if not os.path.exists(datapath) or forceRegen:
        from pydoclib.treegen import make_pkg_tree
        make_pkg_tree(coderoot)
        
    shutil.copy(datapath, os.path.join(docroot_abspath, "data", "package.json"))

    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    
    httpd = SocketServer.TCPServer(("", port), Handler)
    
    print "serving at port", port
    httpd.serve_forever()
    
if __name__ == "__main__":
    run(sys.argv[1])
