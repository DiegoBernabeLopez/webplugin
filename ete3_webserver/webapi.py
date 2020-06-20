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
    '''
    Generates the web return information

    Parameters:
        html: html code
        response: response code

    Returns:
        html: information to be returned
    '''
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


# WEB SERVICES PROVIDING DATA TO THE WEB AND API
@error(405)
def method_not_allowed(res):
    '''
    Generates the web return information

    Parameters:
        res: resource

    Returns:
        error code
    '''
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
    '''
    Enables cross-origin resource sharing

    Parameters:
        None

    Returns:
        None
    '''
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, PUT'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'

@route('/')
def index():
    '''
    Returns index page when no subdomain is introduced

    Parameters:
        None

    Returns:
        Index document
    '''
    return static_file("index.html", root='/home/diego/www/')

@route('/status')
def server_status():
    '''
    Returns "alive" as webreturn

    Parameters:
        None

    Returns:
        html
    '''
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

    if not newick1 or not treeid1:
        return web_return('No source tree provided', response)


    h1 = TREE_HANDLER(newick1, alg1, treeid1, DEFAULT_ACTIONS, DEFAULT_STYLE, PREDRAW_FN)
    LOADED_TREES[h1.treeid] = h1
    
    
    
    newick2 = source_dict.get('newick2', '').strip()
    alg2 = source_dict.get('alg2', '').strip()
    treeid2 = source_dict.get('treeid2', '').strip()

    if not newick2 or not treeid2:
        return web_return('No target tree provided', response)


    h2 = TREE_HANDLER(newick2, alg2, treeid2, DEFAULT_ACTIONS, DEFAULT_STYLE, PREDRAW_FN)
    LOADED_TREES[h2.treeid] = h2
    
    
    
    # do ete diff stuff
    h1.diff(h2)
    h2.diff(h1)
    
    return web_return('', response)

@post('/draw_tree')
def draw_tree():
    '''
    Generates tree image as web return

    Parameters:
        None

    Returns:
        html: web return containing tree image and response
    '''
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
    '''
    Generates available actions text as web return

    Parameters:
        None

    Returns:
        html: web return containing available actions and response
    '''
    if request.json:
        source_dict = request.json
    else:
        source_dict = request.POST
        
    treeid1 = source_dict.get('treeid', '').strip()
    nodeid1 = source_dict.get('nodeid', '').strip()
    
    
    
    if treeid1 and nodeid1:
        html = "<ul class='ete_action_list'>"
        h = LOADED_TREES[treeid1]
        treeid2 = h.diffdict['target'].treeid
        nodeid2 = h.diffdict['nodes'][int(nodeid1)]['target_nodeid']
        for aindex, aname in h.get_avail_actions(nodeid1):
            html += """<li><a  onClick="run_action('%s', '%s', '%s', '%s', '%s', '%s');" >%s</a></li>""" %(treeid1, treeid2, nodeid1, nodeid2, '', aindex, aname)
        html += "</ul>"
    return web_return(html, response)

@post('/run_action')
def run_action():
    '''
    Generates runs actions and generates response as web return

    Parameters:
        None

    Returns:
        html: web return containing tree image and response
    '''
    if request.json:
        source_dict = request.json
    else:
        source_dict = request.POST
        
    treeid = source_dict.get('treeid', '').strip()
    nodeid = source_dict.get('nodeid', '').strip()
    faceid = source_dict.get('faceid', '').strip()
    aindex = source_dict.get('aindex', '').strip()
    side = source_dict.get('side', '').strip()

    if treeid and nodeid and aindex:
        h = LOADED_TREES[treeid]
        h.run_action(aindex, nodeid, side)
        img = h.redraw()

    return web_return(img, response)

@post('/get_dist')
def get_dist():
    '''
    Access tree handler information and fetches distance between selected node and matched node

    Parameters:
        None

    Returns:
        html: web return containing distance text and response
    '''
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


def start_server(node_actions=None, tree_style=None, predraw_fn=None, host="localhost", port=8989):
    '''
    Starts server

    Parameters:
        node_actions: Node actions handler object
        tree_style: Tree style, as function
        predraw_fn: wether to use tree predraw
        host: host ip
        port: listening port

    Returns:
        None
    '''
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
