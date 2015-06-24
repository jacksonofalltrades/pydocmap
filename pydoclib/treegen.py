import os

def make_pkg_tree(coderoot):
    if os.path.exists(coderoot):
        for root, dirs, files in os.walk(coderoot):
            print root, "consumes",
            print sum(getsize(join(root, name)) for name in files),
            print "bytes in", len(files), "non-directory files"
            if 'CVS' in dirs:
                dirs.remove('CVS')  # don't visit CVS directories
    else:
        raise Exception("Code root folder [%s] not found!" % coderoot)