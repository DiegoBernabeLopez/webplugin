import gzip
import logging as log
from io import StringIO, BytesIO
from bottle import (run, get, post, request, route, response, abort, hook,
                    error, HTTPResponse, static_file)

from .tree_handler import WebTreeHandler, NodeActions, TreeStyle



LOADED_TREES = {}
COMPRESS_DATA = True
COMPRESS_MIN_BYTES = 10000
TREE_HANDLER = WebTreeHandler

def web_return(html, response):
    if COMPRESS_DATA and len(html) >= COMPRESS_MIN_BYTES:
        chtmlF = BytesIO()
        z = gzip.GzipFile(fileobj=chtmlF, mode='w')
        
        z.write(bytes(html,'utf-8'))
        z.close()
        chtmlF.seek(0)
        html = chtmlF.read()
        log.info('returning compressed %0.3f KB' %(len(html)/1024.))
        response.set_header( 'Content-encoding', 'gzip')
        response.set_header( 'Content-length', len(html))
    else:
        log.info('returning %0.3f KB' %(len(html)/1024.))
    return html

# THESE ARE THE WEB SERVICES PROVIDING DATA TO THE WEB AND API
@error(405)
def method_not_allowed(res):
    if request.method == 'OPTIONS':
        new_res = HTTPResponse()
        new_res.headers['Access-Control-Allow-Origin'] = '*'
        new_res.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, PUT'
        new_res.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        return new_res
    res.headers['Allow'] += ', OPTIONS'
    return request.app.default_error_handler(res)

@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, PUT'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'

@route('/')
def index():
    return static_file("index.html", root='/var/www/etediff.ddns.net')

@route('/status')
def server_status():
    return web_return('alive', response)


@post('/load_trees')
def load_trees():
    ''' Requires a POST param "newick" containing the tree to be loaded. '''

    if request.json:
        source_dict = request.json
    else:
        source_dict = request.POST
        
    
    newick1 = source_dict.get('newick1', '').strip()
    alg1 = source_dict.get('alg1', '').strip()
    treeid1 = source_dict.get('treeid1', '').strip()
    
    taxid1 = source_dict.get('taxid1', '').strip()

    if not newick1 or not treeid1:
        return web_return('No source tree provided', response)


    h1 = TREE_HANDLER(newick1, alg1, taxid1, treeid1, DEFAULT_ACTIONS, DEFAULT_STYLE, PREDRAW_FN)
    LOADED_TREES[h1.treeid] = h1
    
    
    
    newick2 = source_dict.get('newick2', '').strip()
    alg2 = source_dict.get('alg2', '').strip()
    treeid2 = source_dict.get('treeid2', '').strip()
    
    taxid2 = source_dict.get('taxid2', '').strip()

    if not newick2 or not treeid2:
        return web_return('No target tree provided', response)


    h2 = TREE_HANDLER(newick2, alg2, taxid2, treeid2, DEFAULT_ACTIONS, DEFAULT_STYLE, PREDRAW_FN)
    LOADED_TREES[h2.treeid] = h2
    
    
    
    # do ete diff stuff
    h1.diff(h2)
    h2.diff(h1)

@post('/draw_tree')
def draw_tree():
    if request.json:
        source_dict = request.json
    else:
        source_dict = request.POST
        
    treeid = source_dict.get('treeid', '').strip()

    if treeid:
        h = LOADED_TREES[treeid]
        img = h.redraw()

    return web_return(img, response)

@post('/get_actions')
def get_action():
    if request.json:
        source_dict = request.json
    else:
        source_dict = request.POST
        
    treeid = source_dict.get('treeid', '').strip()
    nodeid = source_dict.get('nodeid', '').strip()
    if treeid and nodeid:
        html = "<ul class='ete_action_list'>"
        h = LOADED_TREES[treeid]
        for aindex, aname in h.get_avail_actions(nodeid):
            html += """<li><a  onClick="run_action('%s', '%s', '%s', '%s');" >%s</a></li>""" %(treeid, nodeid, '', aindex, aname)
        html += "</ul>"
    return web_return(html, response)

@post('/run_action')
def run_action():
    if request.json:
        source_dict = request.json
    else:
        source_dict = request.POST
        
    treeid = source_dict.get('treeid', '').strip()
    nodeid = source_dict.get('nodeid', '').strip()
    faceid = source_dict.get('faceid', '').strip()
    aindex = source_dict.get('aindex', '').strip()

    if treeid and nodeid and aindex:
        h = LOADED_TREES[treeid]
        h.run_action(aindex, nodeid)
        img = h.redraw()

    return web_return(img, response)

@post('/get_dist')
def get_dist():
    if request.json:
        source_dict = request.json
    else:
        source_dict = request.POST
        
    treeid = source_dict.get('treeid', '').strip()
    nodeid = source_dict.get('nodeid', '').strip()
    if treeid and nodeid:
        html = "<ul class='ete_action_list'>"
        h = LOADED_TREES[treeid]
        html += """<li><a>Distance: %s</a></li>""" %(h.diffdict['nodes'][int(nodeid)]['distance'])
        html += "</ul>"
    return web_return(html, response)

DEFAULT_ACTIONS = None
DEFAULT_STYLE = None
PREDRAW_FN = None

@post('/color_nodes')
def color_nodes():
    if request.json:
        source_dict = request.json
    else:
        source_dict = request.POST
        
    treeid1 = source_dict.get('treeid1', '').strip()
    nodeid1 = source_dict.get('nodeid1', '').strip()
    nodeid2 = source_dict.get('nodeid2', '').strip()
    side = source_dict.get('side', '').strip()
    
    
    if side == 'source':
        if treeid1 and nodeid1 and nodeid2:
            h = LOADED_TREES[treeid1]

            source = h.tree.search_nodes(_nid=int(nodeid1))[0]

            # Clean background
            for leaf in h.tree.iter_leaves():
                leaf.img_style['bgcolor'] = 'white'
                leaf.img_style['size'] = 0
                leaf.img_style['hz_line_width'] = 0

            # Paint background
            for leaf in source.iter_leaves():
                attrib = getattr(leaf, 'name')
                if attrib in h.diffdict['nodes'][int(nodeid1)]['diff']:
                    leaf.img_style['bgcolor'] = 'pink'
                    leaf.img_style['size'] = 8
                    leaf.img_style['hz_line_width'] = 4

            img = h.redraw()
            
    elif side == 'target':
        if treeid1 and nodeid1 and nodeid2:
            h1 = LOADED_TREES[treeid1]
            h2 = h1.diffdict['target']

            source = h1.tree.search_nodes(_nid=int(nodeid1))[0]
            target = h2.tree.search_nodes(_nid=int(nodeid2))[0]

            # Clean background
            for leaf in h2.tree.iter_leaves():
                leaf.img_style['bgcolor'] = 'white'
                leaf.img_style['size'] = 0
                leaf.img_style['hz_line_width'] = 0

            # Paint background
            for leaf in target.iter_leaves():
                attrib = getattr(leaf, 'name')
                if attrib in h1.diffdict['nodes'][int(nodeid2)]['diff']:
                    leaf.img_style['bgcolor'] = 'pink'
                    leaf.img_style['size'] = 8
                    leaf.img_style['hz_line_width'] = 4

            img = h2.redraw()

    return web_return(img, response)




def start_server(node_actions=None, tree_style=None, predraw_fn=None, host="localhost", port=8989):
    global DEFAULT_STYLE, DEFAULT_ACTIONS, PREDRAW_FN
    
    
    if node_actions:
        DEFAULT_ACTIONS = node_actions
    else:
        DEFAULT_ACTIONS = NodeActions()

    if tree_style:
        DEFAULT_STYLE = tree_style
    else:
        DEFAULT_STYLE = TreeStyle()
        
    PREDRAW_FN = predraw_fn

    run(host=host, port=port)
