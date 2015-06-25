### Use pydoc.render_doc(<mod>) to output contents of generated help to a string
###

import os
from os.path import join, getsize

def is_pkg(path_parts, files):
    return "__init__.py" in files

def is_parent_pkg(pkg_tree, path_parts):
    if len(path_parts) <= 1:
        return True
    else:
        for p in path_parts[0:-1]:
            if p not in pkg_tree:
                return False
        return True

def get_parent_node(pkg_tree, path_parts):
    curr_node = pkg_tree
    if path_parts[0] not in pkg_tree:
        return pkg_tree

    for p in path_parts[0:-1]:
        if p in pkg_tree:
            curr_node = pkg_tree[p]
        else:
            return None
    return curr_node

def get_mod_classes(modules):
    pass

def make_pkg_tree(coderoot):
    if os.path.exists(coderoot):
        pkg_tree = {}
        
        for root, dirs, files in os.walk(coderoot):
            subdir_parts = filter(lambda x: x, root[len(coderoot):].split("/"))
            if subdir_parts:
                #print "FILES: %s" % files
                if is_pkg(subdir_parts, files) and is_parent_pkg(pkg_tree, subdir_parts):
                    parent = get_parent_node(pkg_tree, subdir_parts)
                    parent[subdir_parts[-1]] = {
                        "__modules": filter(lambda x: x.endswith(".py"), files)
                    }
                    # print subdir_parts, " is a Python package"
                # print sum(getsize(join(root, name)) for name in files),
                #print "bytes in", len(files), "non-directory files"
                #if 'CVS' in dirs:
                #    dirs.remove('CVS')  # don't visit CVS directories
        return pkg_tree
    else:
        raise Exception("Code root folder [%s] not found!" % coderoot)