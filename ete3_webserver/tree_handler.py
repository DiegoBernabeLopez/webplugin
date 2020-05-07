import time
import string
import random
import logging as log
from ete3 import PhyloTree, TreeStyle, NCBITaxa, Tree
from ete3.parser.newick import NewickError
from ete3.tools.ete_diff import treediff, EUCL_DIST

def timeit(f):
    def a_wrapper_accepting_arguments(*args, **kargs):
        t1 = time.time()
        r = f(*args, **kargs)
        #print " %0.3f secs: %s" %(time.time() - t1, f.__name__)
        return r
    return a_wrapper_accepting_arguments

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))



class WebTreeHandler(object):
    def __init__(self, newick, alg, taxid, tid, actions, style, predraw_fn=None):
        try:
            self.tree = PhyloTree(newick = newick, alignment = alg, alg_format="fasta")            
        except NewickError:
            self.tree = Tree(newick, format=1)
            
        self.diffdict = dict()
        self.diffdict['nodes'] = dict()
        self.diffdict['target'] = ''
            
        if predraw_fn:
            predraw_fn(self.tree)
        self.tree.actions = actions
        self.tree.tree_style = style
        
        self.taxid = taxid

        self.treeid = tid
        self.mapid = "map_" + tid
        self.imgid = "img_" + tid
        self.boxid = 'box_' + tid
        # Initialze node internal IDs
        for index, n in enumerate(self.tree.traverse('preorder')):
            n._nid = index
            self.diffdict['nodes'][n._nid] = {'target_nodeid' : -1, 'distance' : None, 'side1' : None, 'side2' : None, 'diff' : set()}

    def diff(self, ht, attr1 = 'name', attr2 = 'name', dist_fn=EUCL_DIST, reduce_matrix=False,extended=False, jobs=1):

        result = treediff(self.tree, ht.tree, attr1 = 'name', attr2 = 'name', dist_fn=EUCL_DIST, reduce_matrix=False,extended=False, jobs=1)
        
        self.diffdict['target'] = ht
        
        for r in result:
            node = self.tree.search_nodes(_nid=int(r[-2]._nid))[0]
            target = ht.tree.search_nodes(_nid=int(r[-1]._nid))[0]
            dist = r[0]
            side1 = r[2]
            side2 = r[3]
            diff = r[4]
            
            self.diffdict['nodes'][node._nid] = {'target_nodeid' : target._nid, 'distance' : dist, 'side1' : side1, 'side2' : side2, 'diff' : diff} 
            
            
                    
    @timeit
    def redraw(self):
        base64_img, img_map = self.tree.render("%%return.PNG", tree_style=self.tree.tree_style)
        _, target_map = self.diffdict['target'].tree.render("%%return.PNG", tree_style=self.tree.tree_style)
        base64_img = base64_img.data().decode("utf-8")
        
        html_map = self.get_html_map(img_map,target_map)

        html_img = """<img id="%s" class="ete_tree_img" USEMAP="#%s" onLoad="javascript:bind_popup();" src="data:image/gif;base64,%s">""" %(self.imgid, self.mapid, base64_img)
        ete_link = '<div style="margin:0px;padding:0px;text-align:left;"><a href="http://etetoolkit.org" style="font-size:7pt;" target="_blank" >Powered by etetoolkit</a></div>'

        tree_div_id = self.boxid
        return html_map+ '<div id="%s" >'%tree_div_id + html_img + ete_link + "</div>"

    def get_html_map(self, img_map, target_map):
        
        html_map = '<MAP NAME="%s" class="ete_tree_img">' %(self.mapid)
        if img_map["nodes"]:
            for x1, y1, x2, y2, nodeid, text in img_map["nodes"]:
                
                text = "" if not text else text
                area = img_map["node_areas"].get(int(nodeid), [0,0,0,0])
                area2 = target_map["node_areas"].get(int(self.diffdict['nodes'][nodeid]['target_nodeid']), [0,0,0,0])
                html_map += """ <AREA SHAPE="rect" COORDS="%s,%s,%s,%s" 
                                onMouseOut='hide_diff();'
                                onMouseMove='highlight_node("%s", "%s", "%s", "%s", "%s", %s, %s, %s, %s, %s, %s, %s, %s);'
                                onClick='show_actions("%s", "%s");'
                                href="javascript:void('%s');">""" %\
                    (int(x1), int(y1), int(x2), int(y2), # coords
                     self.treeid, self.diffdict['target'].treeid, nodeid, self.diffdict['nodes'][nodeid]['target_nodeid'], text, area[0], area[1], area[2]-area[0], area[3]-area[1], area2[0], area2[1], area2[2]-area2[0], area2[3]-area2[1], # highlight_node
                     self.treeid, nodeid, # show_actions
                     nodeid) # javascript:void

        if img_map["faces"]:
            for x1, y1, x2, y2, nodeid, text in img_map["faces"]:
                text = "" if not text else text
                area = img_map["node_areas"].get(int(nodeid), [0,0,0,0])
                area2 = target_map["node_areas"].get(int(self.diffdict['nodes'][nodeid]['target_nodeid']), [0,0,0,0])
                html_map += """ <AREA SHAPE="rect" COORDS="%s,%s,%s,%s"
                                onMouseLeave='hide_diff();'
                                onMouseEnter='highlight_node("%s", "%s", "%s", "%s", "%s", %s, %s, %s, %s, %s, %s, %s, %s);'
                                onClick='show_actions("%s", "%s", "%s");'
                                href='javascript:void("%s");'>""" %\
                    (int(x1),int(y1),int(x2),int(y2),
                     self.treeid, self.diffdict['target'].treeid, nodeid, self.diffdict['nodes'][nodeid]['target_nodeid'], text, area[0], area[1], area[2]-area[0], area[3]-area[1], area2[0], area2[1], area2[2]-area2[0], area2[3]-area2[1],
                     self.treeid, nodeid, text,
                     text,
                     )
        html_map += '</MAP>'
        return html_map

    def get_avail_actions(self, nodeid):
        target = self.tree.search_nodes(_nid=int(nodeid))[0]
        action_list = []
        for aindex, aname, show_fn, run_fn in self.tree.actions:
            if show_fn(target):
                action_list.append([aindex, aname])
        return action_list

    def run_action(self, aindex, nodeid):
        target = self.tree.search_nodes(_nid=int(nodeid))[0]
        taxid = self.taxid
        run_fn = self.tree.actions.actions[aindex][2]
        return run_fn(self.tree, target, taxid)
    
class NodeActions(object):
    def __str__(self):
        text = []
        for aindex, aname, show_fn, run_fn in self:
            text.append("%s: %s, %s, %s" %(aindex, aname, show_fn, run_fn))
        return '\n'.join(text)

    def __iter__(self):
        for aindex, (aname, show_fn, run_fn) in self.actions.items():
            yield (aindex, aname, show_fn, run_fn)

    def __init__(self):
        self.actions = {}

    def clear_default_actions(self):
        self.actions = {}

    def add_action(self, action_name, show_fn, run_fn):
        aindex = "act_"+id_generator()
        self.actions[aindex] = [action_name, show_fn, run_fn]
