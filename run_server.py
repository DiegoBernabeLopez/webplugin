from ete3_webserver import NodeActions, start_server
from ete3 import TreeStyle, TextFace, add_face_to_node, ImgFace, BarChartFace


# Custom demo ETE Tree styles and web actions


def show_action_change_style(node):
    return True

def show_action_clear_highlight(node):
    return True

def show_action_diff(node):
    return True

##
# Run actions

def run_action_root(tree, node, diff):
    tree.set_outgroup(node)
    return

def run_action_diff(tree, node, diff):

    # Clean background
    tree.img_style['bgcolor'] = 'white'
    tree.img_style['size'] = 0
    tree.img_style['hz_line_width'] = 0
    
    for treenode in tree.traverse():
        treenode.img_style['bgcolor'] = 'white'
        treenode.img_style['size'] = 0
        treenode.img_style['hz_line_width'] = 0
        
    #highlight selection and their differences
    if node.diffdict['distance'] < 1:        
        node.img_style['bgcolor'] = 'lightblue'
        node.img_style['size'] = 8
        node.img_style['hz_line_width'] = 4

        for leaf in node.traverse():
            attrib = getattr(leaf, 'name')
            if attrib in diff:
                leaf.img_style['bgcolor'] = 'pink'
                leaf.img_style['size'] = 8
                leaf.img_style['hz_line_width'] = 4
            else:
                leaf.img_style['bgcolor'] = 'lightblue'
                leaf.img_style['size'] = 8
                leaf.img_style['hz_line_width'] = 4            
    return

def run_clear_highlight(tree, node, diff):
    tree.img_style['bgcolor'] = 'white'
    tree.img_style['size'] = 0
    tree.img_style['hz_line_width'] = 0
    
    for treenode in tree.traverse():
        treenode.img_style['bgcolor'] = 'white'
        treenode.img_style['size'] = 0
        treenode.img_style['hz_line_width'] = 0
        
    return

def toggle_highlight_node(node, prev_highlighted):
    
    if prev_highlighted:
        node.img_style['bgcolor'] = 'white'
        node.img_style['size'] = 0
        node.img_style['hz_line_width'] = 0
    else:
        node.img_style['bgcolor'] = 'pink'
        node.img_style['size'] = 8
        node.img_style['hz_line_width'] = 4

    node.highlighted = not prev_highlighted
    
    return

def run_action_highlight(tree, node, diff):

    if not "highlighted" in node.features:
        node.add_feature("highlighted", False)
        
    prev_highlighted = node.highlighted
    
    toggle_highlight_node(node, prev_highlighted)
    
    for child in node.traverse():
        if not "highlighted" in child.features:
            child.add_feature("highlighted", False)
        toggle_highlight_node(child, prev_highlighted)
        
    return

def run_action_change_style(tree, node, diff):
    if tree.tree_style == ts:
        tree.tree_style = ts2
    else:
        tree.tree_style = ts
    return
        
def run_action_delete_node(tree, node, diff):
    parent = node.up
    remove_node = node.detach()
    
    if len(parent.get_children()) == 0:
        run_action_delete_node(tree, parent)
        
    return

def custom_layout(node):
    if node.is_leaf():
        aligned_name_face = TextFace(node.name, fgcolor='olive', fsize=14)
        add_face_to_node(aligned_name_face, node, column=2, position='aligned')
        name_face = TextFace(node.name, fgcolor='#333333', fsize=11)
        add_face_to_node(name_face, node, column=2, position='branch-right')
        node.img_style['size'] = 0
    else:
        node.img_style['size'] = 4
        node.img_style['shape'] = 'square'
        if node.name:
            name_face = TextFace(node.name, fgcolor='grey', fsize=10)
            name_face.margin_bottom = 2
            add_face_to_node(name_face, node, column=0, position='branch-top')
        if node.support:
            support_face = TextFace(node.support, fgcolor='indianred', fsize=10)
            add_face_to_node(support_face, node, column=0, position='branch-bottom')



# Server configuration

ts = TreeStyle()
ts.layout_fn = custom_layout
ts.show_leaf_name = False

ts2 = TreeStyle()

actions = NodeActions()


actions.add_action('Change style', show_action_change_style, run_action_change_style)
actions.add_action('Show differences', show_action_diff, run_action_diff)
actions.add_action('Clear highlight', show_action_clear_highlight, run_clear_highlight)


## Start server
start_server(node_actions=actions, tree_style=ts, host="localhost", port=8989)
