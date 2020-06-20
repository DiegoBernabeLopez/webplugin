import time
import string
import random
import logging as log
from ete3 import PhyloTree, TreeStyle, NCBITaxa, Tree
from ete3.parser.newick import NewickError
from ete3.tools.ete_diff import *

def timeit(f):
    '''
    Calculates the elapsed time taken by a function decarated


    Parameters:
        f: function to measure

    Returns:
        float: elapsed time
    '''
    def a_wrapper_accepting_arguments(*args, **kargs):
        t1 = time.time()
        r = f(*args, **kargs)
        print ("%s: %0.3f secs " %(f.__name__, time.time() - t1))
        return r
    return a_wrapper_accepting_arguments

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))



class WebTreeHandler(object):
    '''
    Tree object handler
    '''
    def __init__(self, newick, alg, tid, actions, style, predraw_fn=None):
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

        self.treeid = tid
        self.mapid = "map_" + tid
        self.imgid = "img_" + tid
        self.boxid = 'box_' + tid
        # Initialze node internal IDs
        for index, n in enumerate(self.tree.traverse('preorder')):
            n._nid = index
            n.diffdict = {'target_nodeid' : -1, 'distance' : None, 'side1' : None, 'side2' : None, 'diff' : set()}
            self.diffdict['nodes'][n._nid] = {'target_nodeid' : -1, 'distance' : None, 'side1' : None, 'side2' : None, 'diff' : set()}

    def diff(self, ht, attr1 = 'name', attr2 = 'name', dist_fn=EUCL_DIST, support=None, reduce_matrix=False, extended=False, jobs=1, parallel=None):
        '''
        Calculates treediff for self handler and a target tree and loads the data into handler properties

        Parameters:
            self: self handler
            ht: target tree handler, as tree handler object
            attr1: observed attribute for the reference node, as string
            attr2: observed attribute for the target node, as string
            dist_fn: distance function that will be used to calculate the distances between nodes, as python function
            support: whether to use support values for the different calculations, as boolean
            reduce_matrix: whether to reduce the distances matrix removing columns and rows where observations equal to 0 (perfect matches) are found, as boolean
            extended: whether to use an extension function, as python function
            jobs: maximum number of parallel jobs to use if parallel argument is given, as integer
            parallel: parallelization method, as string. Options are:
                async for asyncronous parallelization
                sync for asyncronous parallelization

        Returns:
            None
        '''

        result = treediff(self.tree, ht.tree, attr1 = attr1, attr2 = attr2, dist_fn=dist_fn, support=support, reduce_matrix=reduce_matrix, extended=extended, jobs=jobs)
        
        self.diffdict['target'] = ht
        
        for r in result:
            node = self.tree.search_nodes(_nid=int(r[-2]._nid))[0]
            target = ht.tree.search_nodes(_nid=int(r[-1]._nid))[0]
            dist = r[0]
            side1 = r[2]
            side2 = r[3]
            diff = r[4]
            
            node.diffdict = {'target_nodeid' : target._nid, 'distance' : dist, 'side1' : side1, 'side2' : side2, 'diff' : diff} 
            
            self.diffdict['nodes'][node._nid] = {'target_nodeid' : target._nid, 'distance' : dist, 'side1' : side1, 'side2' : side2, 'diff' : diff} 
            
            
                    
    def redraw(self):
        '''
        Generates the html tree image and related information

        Parameters:
            self: self handler

        Returns:
            html text: Tree image and related information
        '''
        base64_img, img_map = self.tree.render("%%return.PNG", tree_style=self.tree.tree_style)
        _, target_map = self.diffdict['target'].tree.render("%%return.PNG", tree_style=self.tree.tree_style)
        base64_img = base64_img.data().decode("utf-8")
        
        html_map = self.get_html_map(img_map,target_map)

        html_img = """<img id="%s" class="ete_tree_img" USEMAP="#%s" onLoad="javascript:bind_popup();" src="data:image/gif;base64,%s">""" %(self.imgid, self.mapid, base64_img)
        ete_link = '<div style="margin:0px;padding:0px;text-align:left;"><a href="http://etetoolkit.org" style="font-size:7pt;" target="_blank" >Powered by etetoolkit</a></div>'

        tree_div_id = self.boxid
        return html_map+ '<div id="%s" >'%tree_div_id + html_img + ete_link + "</div>"

    def get_html_map(self, img_map, target_map):
        '''
        Generates the html tree map

        Parameters:
            self: self handler
            img_map: self tree image map from tree.render
            target_map: target tree image map from tree.render

        Returns:
            html: html map for self tree image web representation
        '''
        
        html_map = '<MAP NAME="%s" class="ete_tree_img">' %(self.mapid)
        if img_map["nodes"]:
            for x1, y1, x2, y2, nodeid, text in img_map["nodes"]:
                
                text = "" if not text else text
                area = img_map["node_areas"].get(int(nodeid), [0,0,0,0])
                area2 = target_map["node_areas"].get(int(self.diffdict['nodes'][nodeid]['target_nodeid']), [0,0,0,0])
                html_map += """ <AREA SHAPE="rect" COORDS="%s,%s,%s,%s" 
                                onMouseLeave='hide_diff();'
                                onMouseEnter='highlight_node("%s", "%s", "%s", "%s", "%s", %s, %s, %s, %s, %s, %s, %s, %s, %.2f);'
                                onClick='show_actions("%s", "%s", "%s");'
                                href="javascript:void('%s');">""" %\
                    (int(x1), int(y1), int(x2), int(y2), # coords
                     self.treeid, self.diffdict['target'].treeid, nodeid, self.diffdict['nodes'][nodeid]['target_nodeid'], text, area[0], area[1], area[2]-area[0], area[3]-area[1], area2[0], area2[1], area2[2]-area2[0], area2[3]-area2[1], self.diffdict['nodes'][nodeid]['distance'], # highlight_node
                     self.treeid, nodeid, text, # show_actions
                     nodeid) # javascript:void

        if img_map["faces"]:
            for x1, y1, x2, y2, nodeid, text in img_map["faces"]:
                text = "" if not text else text
                area = img_map["node_areas"].get(int(nodeid), [0,0,0,0])
                area2 = target_map["node_areas"].get(int(self.diffdict['nodes'][nodeid]['target_nodeid']), [0,0,0,0])
                html_map += """ <AREA SHAPE="rect" COORDS="%s,%s,%s,%s"
                                onMouseLeave='hide_diff();'
                                onMouseEnter='highlight_node("%s", "%s", "%s", "%s", "%s", %s, %s, %s, %s, %s, %s, %s, %s, %.2f);'
                                onClick='show_actions("%s", "%s", "%s");'
                                href='javascript:void("%s");'>""" %\
                    (int(x1),int(y1),int(x2),int(y2),
                     self.treeid, self.diffdict['target'].treeid, nodeid, self.diffdict['nodes'][nodeid]['target_nodeid'], text, area[0], area[1], area[2]-area[0], area[3]-area[1], area2[0], area2[1], area2[2]-area2[0], area2[3]-area2[1], self.diffdict['nodes'][nodeid]['distance'],
                     self.treeid, nodeid, text,
                     text)
        html_map += '</MAP>'
        return html_map

    def get_avail_actions(self, nodeid):
        '''
        Fetches available actions to apply on try

        Parameters:
            self: self handler
            nodeid: selected node id

        Returns:
            list: action list
        '''
        target = self.tree.search_nodes(_nid=int(nodeid))[0]
        action_list = []
        for aindex, aname, show_fn, run_fn in self.tree.actions:
            if show_fn(target):
                action_list.append([aindex, aname])
        return action_list

    def run_action(self, aindex, nodeid, side = 'source'):

        if side == 'source':
            node = self.tree.search_nodes(_nid=int(nodeid))[0]
            diff = node.diffdict['diff']
        elif side == 'target':
            nodeid = self.diffdict['target'].diffdict['nodes'][int(nodeid)]['target_nodeid']
            node = self.tree.search_nodes(_nid=int(nodeid))[0]
            diff = self.diffdict['nodes'][int(nodeid)]['diff']
        else: 
            node = None
            diff = None
        run_fn = self.tree.actions.actions[aindex][2]
        return run_fn(self.tree, node, diff)
    
class NodeActions(object):
    '''
    Actions handler
    '''
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
        '''
        Clears all actions

        Parameters:
            self: self handler

        Returns:
            None
        '''
        self.actions = {}

    def add_action(self, action_name, show_fn, run_fn):
        '''
        Adds an action to the actions handler object

        Parameters:
            self: self handler
            action_name: action name, as string
            show_fn: function used to show the action, as function
            run_fn: function used when running the action, as function

        Returns:
            None
        '''
        aindex = "act_"+id_generator()
        self.actions[aindex] = [action_name, show_fn, run_fn]
