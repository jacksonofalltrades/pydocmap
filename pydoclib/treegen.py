### Use pydoc.render_doc(<mod>) to output contents of generated help to a string
###

import sys
import os
import glob
from os.path import join, getsize
import re
import json

def is_pkg(path_parts, files):
    return "__init__.py" in files

def count_class_refs(class_name, all_files):
    """
    Patterns:
    =\s+<class_name>\s*\(
    <class_name>\.
    """
    refs = 0
    pats = [
        '=\s+%s\s*\(' % class_name,
        '\s+%s\.' % class_name
    ]
    # print "Searching for refs to class [%s]..." % class_name
    for fpath in all_files:
        with open(fpath, "r") as f:
            for line in f:
                for p in pats:
                    matches = re.findall(p, line)
                    refs += len(matches)
    # print "\tFound %s!" % refs
    
    if refs > 0:
        return refs
    else:
        return 1


def add_to_tree(pkg_tree, pkg_node_path):
    curr_node = pkg_tree
    for p in pkg_node_path:
        if p not in curr_node:
            curr_node[p] = {}
        curr_node = curr_node[p]
    return curr_node

def add_mod_classes(coderoot, modules):
    coderoot_base = os.path.basename(coderoot)
    for m in modules:
        if coderoot_base == m['pkg']:
            full_pkg_path = m['mod']
        else:
            full_pkg_path = "%s.%s" % (m['pkg'], m['mod'])
        mod_file_path = full_pkg_path.replace(".", "/")
        mod_file_path = os.path.join(coderoot, mod_file_path + ".py")
        # path_str = open(mod_file_path, 'r').read()
        # m['mod_contents'] = path_str
        m['classes'] = re.findall("class ([a-zA-Z0-9_]+)\(", open(mod_file_path, 'r').read())

def build_tree_map(all_files, pkg_tree):
    treemap_data = []
    """
    {
        "name": "sample package",
        "tree": {
            "name": "flare",
            "children": [
            ]
        }
    }
    """
    
    if type(pkg_tree) == dict:
        for key, val in pkg_tree.items():
            if key == '__modules':
                for mod, classlist in map(lambda x: (x['mod'], x['classes']), filter(lambda y: y['classes'], val)):
                    node = {
                        'name': mod,
                        'children': build_tree_map(all_files, classlist)
                    }
                    treemap_data.append(node)
            else:
                node = {
                    'name': key,
                    'children': build_tree_map(all_files, val)
                }
                treemap_data.append(node)
    elif len(pkg_tree) and type(pkg_tree) == list:
        for c in pkg_tree:
            node = {
                'name': c,
                'value': count_class_refs(c, all_files)
            }
            treemap_data.append(node)

    return treemap_data


def make_pkg_tree(coderoot):
    if os.path.exists(coderoot):
        # Add to the system path so we can import modules
        sys.path.append(coderoot)
        
        treename = os.path.basename(coderoot)
        
        pkg_tree = {}
        
        all_files = []
        
        for root, dirs, files in os.walk(coderoot):
            all_files.extend(map(lambda x: os.path.join(root, x), files))
            subdir_parts = filter(lambda x: x, root[len(coderoot):].split("/"))
            if subdir_parts:
                # print "pkg: %s" % subdir_parts
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

        root_files = map(lambda x: os.path.basename(x), glob.glob(os.path.join(coderoot, "*.py")))
        pkg_tree['__modules'] = map(lambda z: {'pkg': treename, 'mod': z.split('.')[0]}, root_files)
        # print pkg_tree['__modules']
        add_mod_classes(coderoot, pkg_tree['__modules'])
        
        # Convert to format needed for d3 tree map
        treemap_data = {
            'name': treename,
            'children': build_tree_map(all_files, pkg_tree)
        }
        
        meta = {
            'tree': treemap_data,
            'name': treename
        }
        
        with open(os.path.join(coderoot, "package.json"), 'w') as f:
            json.dump(meta, f, indent=4, sort_keys=True)

    else:
        raise Exception("Code root folder [%s] not found!" % coderoot)