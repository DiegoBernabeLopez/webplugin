from ete3_webserver import NodeActions, start_server
from ete3 import TreeStyle, TextFace, add_face_to_node, ImgFace, BarChartFace


# Custom ETE Tree styles and web actions


# def show_action_root(node):
#     if node.up:
#         return True
#     return False

# def show_action_highlight(node):
#     # Any node can be highlighted
#     return True

def show_action_change_style(node):
    return True

def show_action_clear_highlight(node):
    return True

# def show_action_delete_node(node):
#     return True

def show_action_diff(node):
    return True

##
# Run actions

def run_action_root(tree, node):
    tree.set_outgroup(node)
    return

def run_action_diff(tree, node):
    # Clean background
    for leaf in tree.iter_leaves():
        leaf.img_style['bgcolor'] = 'white'
        leaf.img_style['size'] = 0
        leaf.img_style['hz_line_width'] = 0

    for leaf in node.iter_leaves():
        attrib = getattr(leaf, 'name')
        if attrib in node.diffdict['diff']:
            leaf.img_style['bgcolor'] = 'pink'
            leaf.img_style['size'] = 8
            leaf.img_style['hz_line_width'] = 4
    return

def run_clear_highlight(tree, node):
    for leaf in tree.iter_leaves():
        leaf.img_style['bgcolor'] = 'white'
        leaf.img_style['size'] = 0
        leaf.img_style['hz_line_width'] = 0
        
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

def run_action_highlight(tree, node):

    if not "highlighted" in node.features:
        node.add_feature("highlighted", False)
        
    prev_highlighted = node.highlighted
    
    toggle_highlight_node(node, prev_highlighted)
    
    for child in node.traverse():
        if not "highlighted" in child.features:
            child.add_feature("highlighted", False)
        toggle_highlight_node(child, prev_highlighted)
        
    return

def run_action_change_style(tree, node):
    if tree.tree_style == ts:
        tree.tree_style = ts2
    else:
        tree.tree_style = ts
    return
        
def run_action_delete_node(tree, node):
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

        if node.name in tip2info:
            # For some reason img urls are very slow!
            #img_face = ImgFace(tip2info[node.name][0], is_url=True)
            #add_face_to_node(img_face, node, column=4, position='branch-right')
            habitat_face = TextFace(tip2info[node.name][2], fsize=11, fgcolor='white')
            habitat_face.background.color = 'steelblue'
            habitat_face.margin_left = 3
            habitat_face.margin_top = 3
            habitat_face.margin_right = 3
            habitat_face.margin_bottom = 3
            add_face_to_node(habitat_face, node, column=3, position='aligned')
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

tip_info_csv = """
Rangifer_tarandus,http://eol.org/pages/328653/overview,109.09,herbivore
Cervus_elaphus,http://eol.org/pages/328649/overview,240.87,herbivore
Bos_taurus,http://eol.org/pages/328699/overview,618.64,herbivore
Ovis_orientalis,http://eol.org/pages/311906/overview,39.1,herbivore
Suricata_suricatta,http://eol.org/pages/311580/overview,0.73,carnivore
Cistophora_cristata,http://eol.org/pages/328632/overview,278.9,omnivore
Mephitis_mephitis,http://eol.org/pages/328593/overview,2.4,omnivore"""
tip2info = {}
for line in tip_info_csv.split('\n'):
    if line:
        name, url, mass, habit = map(str.strip, line.split(','))
        tip2info[name] = [url, mass, habit]


# Server configuration

ts = TreeStyle()
ts.layout_fn = custom_layout
ts.show_leaf_name = False

ts2 = TreeStyle()

actions = NodeActions()

# actions.add_action('Root here', show_action_root, run_action_root)
# actions.add_action('Highlight', show_action_highlight, run_action_highlight)
actions.add_action('Change style', show_action_change_style, run_action_change_style)
# actions.add_action('Delete node', show_action_delete_node, run_action_delete_node)
actions.add_action('Show differences', show_action_diff, run_action_diff)
actions.add_action('Clear highlight', show_action_clear_highlight, run_clear_highlight)

start_server(node_actions=actions, tree_style=ts, host="localhost", port=8989)
