/*  it requires jquery loaded */
var ete_webplugin_URL = "http://localhost:8989";
var loading_img = '<img border=0 src="loader.gif">';

function update_server_status(){
  /**
  Updates server status
  
  Parameters:
    None
  */
  console.log('updating');
  $('#server_status').load(ete_webplugin_URL+"/status");

}


function get_tree_diff(newick1, recipient1, newick2, recipient2){
  /**
  Generates trees and tree images
  
  Parameters:
    newick1: text representation of tree
    recipient1: tag of the element where the tree image reconstructed from newick1 information will be displayed
    newick2: text representation of tree
    recipient2: tag of the element where the tree image reconstructed from newick2 information will be displayed
  */
  clear_all();
    
  var treeid1 = makeid();
  $(recipient1).html('<div id="' + treeid1 + '">' + loading_img + '</div>'); //Loading gif
  var treeid2 = makeid();
  $(recipient2).html('<div id="' + treeid2 + '">' + loading_img + '</div>'); //Loading gif

    
  // Get trees from text
  var params = {'newick1':newick1, 'treeid1':treeid1,'newick2':newick2, 'treeid2':treeid2};

    
  $.post(ete_webplugin_URL+'/load_trees', params);

    
  // Draw trees
  var params = {"treeid": treeid1};
  $('#'+treeid1).load(ete_webplugin_URL+'/draw_tree', params,
    function() {
            $('#'+treeid1).fadeTo(0, 0.0);
            $('#'+treeid1).fadeTo(1000, 1);
  });
    
  var params = {"treeid": treeid2};
  $('#'+treeid2).load(ete_webplugin_URL+'/draw_tree', params,
    function() {
            $('#'+treeid2).fadeTo(0, 0.0);
            $('#'+treeid2).fadeTo(1000, 1);
  });
}



function run_action(treeid1, treeid2, nodeid1, nodeid2, faceid, aindex){
  /**
  Runs action on both trees and updates their images and updates server status
  
  Parameters:
    treeid1: source tree id
    treeid2: target tree id
    nodeid1: selected source node id
    nodeid2: target node id linked to nodeid1
    faceid: face id
    aindex: action index
  */
  $("#popup").hide();
  $("#popup2").hide(); 
  $('#server_status').html(loading_img);
  console.log(treeid1, treeid2, nodeid1, nodeid2, faceid, aindex, $('#'+treeid1), $('#'+treeid2));
  
  clear_elements();
    
  var params = {"treeid": treeid1, "nodeid": nodeid1, "side" : "source", "faceid": faceid, "aindex": aindex};
  $('#'+treeid1).load(ete_webplugin_URL+'/run_action', params,
    function() {
      console.log('run action');
            $('#'+treeid1).fadeTo(0, 1);
  });
    
  var params = {"treeid": treeid2, "nodeid": nodeid1, "side" : "target", "faceid": faceid, "aindex": aindex};
  $('#'+treeid2).load(ete_webplugin_URL+'/run_action', params,
    function() {
      console.log('run action');
            $('#'+treeid2).fadeTo(0, 1);
  });
    
  $('#server_status').load(ete_webplugin_URL+"/status");
}


function show_actions(treeid, nodeid, faceid){
  /**
  Shows available actions for selected node
  
  Parameters:
    treeid: source tree id
    nodeid: selected source node id
    faceid: face id
  */
  $("#popup").html(loading_img);
  
  var params = {"treeid": treeid, "nodeid": nodeid, "faceid": faceid};
  $('#popup').load(ete_webplugin_URL+'/get_actions', params);
}


function bind_popup(){
  /**
  Binds popup to tree image
  
  Parameters:
    None
  */


    var onmousestop = function (e){
                        if($("#popup").is(":hidden") && $("#highlighter1").is(":visible")) {
                            $("#popup2").show();
                        };
                }, thread;
    
    $('.ete_tree_img').bind('mouseenter',function (e){
                        onmousestop(e);
                }).bind('mousemove',function (e){
        
                        $("#popup2").css('left',e.pageX + 15);
                        $("#popup2").css('top',e.pageY );
                        $("#popup2").css('position',"absolute" );
                        $("#popup2").css('background-color',"#fff" );
                        $("#popup2").draggable({ cancel: 'span,li' });
                        $("#popup2").hide();
                        thread&&clearTimeout(thread);
                        thread = setTimeout(onmousestop, 1000);
                        });    
    
    
    $(".ete_tree_img").mouseout(function(e){ 
                          $("#popup2").hide();
                          });

    $(".ete_tree_img").bind('click',function(e){
                          $("#popup").css('left',e.pageX-2 );
                          $("#popup").css('top',e.pageY-2 );
                          $("#popup").css('position',"absolute" );
                          $("#popup").css('background-color',"#fff" );
                          $("#popup").draggable({ cancel: 'span,li' });
                          $("#popup").show();
                          $("#popup2").hide();
                          });    
}

function hide_popup(){
  /**
  Hides popup
  
  Parameters:
    None
  */
  $('#popup').hide();
}

function hide_diff(){
  /**
  Hides popup2
  
  Parameters:
    None
  */
  $('#popup2').hide();
}



function highlight_node(treeid1, treeid2, nodeid1, nodeid2, faceid, x1, y1, width1, height1, x2, y2, width2, height2, dist){
  /**
  highlights hovered node and matching node with a square box
  
  Parameters:
    treeid1: source tree id
    treeid2: target tree id
    nodeid1: selected source node id
    nodeid2: target node id linked to nodeid1
    faceid: face id
    x1: x origin of the first higlighting box
    y1: y origin of the first higlighting box
    width1: width of the first higlighting box
    height1: height of the first higlighting box
    x2: x origin of the second higlighting box
    y2: y origin of the second higlighting box
    width2: width of the second higlighting box
    height2: height of the second higlighting box
    dist: distance between selected nodes
  */

    console.log(treeid1, treeid2, nodeid1, nodeid2, faceid, x1, y1, width1, height1, x2, y2, width2, height2, dist);
    var img1 = $('#'+treeid1);
    var offset1 = img1.offset();
    console.log(img1);
    console.log(offset1);

    $("#highlighter1").show();
    $("#highlighter1").css("visibility", 'visible');
    $("#highlighter1").css("top", offset1.top+y1-1);
    $("#highlighter1").css("left", offset1.left+x1-1);
    $("#highlighter1").css("width", width1+1);
    $("#highlighter1").css("height", height1+1);

    var img2 = $('#'+treeid2);
    var offset2 = img2.offset();
    console.log(img2);
    console.log(offset2);

    $("#highlighter2").show();
    $("#highlighter2").css("visibility", 'visible');
    $("#highlighter2").css("top", offset2.top+y2-1);
    $("#highlighter2").css("left", offset2.left+x2-1);
    $("#highlighter2").css("width", width2+1);
    $("#highlighter2").css("height", height2+1);


    var params = {"treeid": treeid1, "nodeid": nodeid1};
    $('#popup2').load(ete_webplugin_URL+'/get_dist', params);

    hide_popup();

    

}
function unhighlight_node(){
  /**
  Hides highlighters
  
  Parameters:
    None
  */
  console.log("unhighlight");
  $("#highlighter1").hide();
  $("#highlighter2").hide();
}

function makeid()
{
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 5; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
}

function clear_all(){
  /**
  Clears popup, popup2, highlighter1, highlighter2 and tree images
  
  Parameters:
    None
  */
    hide_popup();
    hide_diff();
    unhighlight_node();
    $(".column").html("");
}

function clear_elements(){
  /**
  Clears popup, popup2, highlighter1, highlighter2
  
  Parameters:
    None
  */
    hide_popup();
    hide_diff();
    unhighlight_node();
}


$(document).ready(function(){
  /**
  Clears popup, popup2 and updates server status
  
  Parameters:
    None
  */
  hide_popup();
  hide_diff();
  update_server_status();
});
