import sys
from collections import defaultdict
from ete3 import Tree, TextFace, BarChartFace, add_face_to_node, TreeStyle

CAST = {'float': float,
        'node': int,
        'str': str,
        'list': list,
        'int': int,
        'url': str}

def load(treefile):
    defines = {}
    id2node = defaultdict(Tree)
    for line in open(treefile):
        if line.startswith('##'):
            continue
        fields = map(str.strip, line.split('\t'))
        if fields[0] == '#define':
            dcode, dname, dcast, dtype = fields[1:]
            defines[dcode] = [dname, dcast, dtype]
        else:
            nodeid, dcode, value = fields
            nodeid = int(nodeid)
            dname, dcast, _ = defines[dcode]
            value = CAST[dcast](value)
            if dcode == 'PAR':
                if value != -1:
                    id2node[value].add_child(id2node[nodeid])
            else:
                setattr(id2node[nodeid], dname, value)
            # For consistency in ETE
            if dcode == 'BLE':
                id2node[value].dist = value
            if dcode == 'BSS':
                id2node[value].support = value

    for nid, n in id2node.items():
        n._id = nid
    return id2node[0], defines

def export(tree, defines):
    for dcode, (dname, dcast, dtype) in defines.items():
        print '\t'.join(['#define', dname, dcast, dtype])

    for n in tree.traverse():
        for dcode, (dname, dcast, dtype) in defines.items():
            if hasattr(n, dname):
                print '\t'.join(map(str, [n._id, dcode, getattr(n, dname)]))

def render(tree):
    ts = TreeStyle()
    ts.show_leaf_name = False
    ts.layout_fn = layout
    tree.render('example.png', tree_style=ts)


def layout(node):
    node.img_style['size'] = 0
    if hasattr(node, 'bootstrap'):
        add_face_to_node(TextFace(" %s " %node.support, fsize=5), node, column=0, position='branch-bottom')

    if hasattr(node, 'posterior'):
        add_face_to_node(TextFace(node.support, fsize=5, fgcolor='red'), node, column=1, position='branch-bottom')
    if hasattr(node, 'name'):
        if node.is_leaf():
            add_face_to_node(TextFace(node.name, fsize=12, fgcolor='steelblue'), node, column=0, position='branch-right')
        else:
            add_face_to_node(TextFace(node.name, fsize=8, fgcolor='steelblue'), node, column=0, position='branch-top')

if __name__ == "__main__":
    tree, defs = load(sys.argv[1])
    print tree
    defs.pop('IMS')
    defs.pop('IMA')
    defs.pop('IML')
    export(tree, defs)
    render(tree)
