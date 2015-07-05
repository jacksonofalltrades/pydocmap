### Use pydoc.render_doc(<mod>) to output contents of generated help to a string
###

import sys
import os
from os.path import join, getsize
import re

def is_pkg(path_parts, files):
    return "__init__.py" in files

def add_to_tree(pkg_tree, pkg_node_path):
    curr_node = pkg_tree
    for p in pkg_node_path:
        if p not in curr_node:
            curr_node[p] = {}
        curr_node = curr_node[p]
    return curr_node

def add_mod_classes(coderoot, modules):
    for m in modules:
        full_pkg_path = "%s.%s" % (m['pkg'], m['mod'])
        mod_file_path = full_pkg_path.replace(".", "/")
        mod_file_path = os.path.join(coderoot, mod_file_path + ".py")
        # path_str = open(mod_file_path, 'r').read()
        # m['mod_contents'] = path_str
        m['classes'] = re.findall("class ([a-zA-Z0-9_]+)\(", open(mod_file_path, 'r').read())

def make_pkg_tree(coderoot):
    if os.path.exists(coderoot):
        # Add to the system path so we can import modules
        sys.path.append(coderoot)
        
        pkg_tree = {}
        
        for root, dirs, files in os.walk(coderoot):
            subdir_parts = filter(lambda x: x, root[len(coderoot):].split("/"))
            if subdir_parts:
                print "pkg: %s" % subdir_parts
                if is_pkg(subdir_parts, files):
                    new_node = add_to_tree(pkg_tree, subdir_parts)
                    new_node['__modules'] = map(lambda z: {'pkg': '.'.join(subdir_parts), 'mod': z.split('.')[0]}, filter(lambda x: x.endswith(".py"), files))
                    add_mod_classes(coderoot, new_node['__modules'])
                """
                    # print subdir_parts, " is a Python package"
                # print sum(getsize(join(root, name)) for name in files),
                #print "bytes in", len(files), "non-directory files"
                #if 'CVS' in dirs:
                #    dirs.remove('CVS')  # don't visit CVS directories
                """
        return pkg_tree
    else:
        raise Exception("Code root folder [%s] not found!" % coderoot)