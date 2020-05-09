/*  it requires jquery loaded */
var ete_webplugin_URL = "http://localhost:8989";
var loading_img = '<img border=0 src="loader.gif">';

function update_server_status(){
  console.log('updating');
  $('#server_status').load(ete_webplugin_URL+"/status");

}


function get_tree_diff(newick1, recipient1, newick2, recipient2){
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
            $('#'+treeid1).fadeIn(1000);
  });
    
  var params = {"treeid": treeid2};
  $('#'+treeid2).load(ete_webplugin_URL+'/draw_tree', params,
    function() {
            $('#'+treeid2).fadeIn('slow');
  });
}



function run_action(treeid, nodeid, faceid, aindex){
  $("#popup").hide();
  $("#popup2").hide(); 
  $('#'+treeid).html(loading_img);
  console.log(treeid, nodeid, faceid, aindex, $('#'+treeid));
  
  clear_elements();
    
  var params = {"treeid": treeid, "nodeid": nodeid, "faceid": faceid, "aindex":aindex};
  $('#'+treeid).load(ete_webplugin_URL+'/run_action', params,
    function() {
      console.log('run action');
            $('#'+treeid).fadeTo(100, 0.9);
  });
}


function show_actions(treeid, nodeid, faceid){
  $("#popup").html(loading_img);
  
  var params = {"treeid": treeid, "nodeid": nodeid, "faceid": faceid};
  $('#popup').load(ete_webplugin_URL+'/get_actions', params);
}


function bind_popup(){


    var onmousestop = function (e){
                        if($("#popup").is(":hidden")) {
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
  $('#popup').hide();
}

function hide_diff(){
  $('#popup2').hide();
}



function highlight_node(treeid1, treeid2, nodeid1, nodeid2, faceid, x1, y1, width1, height1, x2, y2, width2, height2){

    console.log(treeid1, treeid2, nodeid1, nodeid2, faceid, x1, y1, width1, height1, x2, y2, width2, height2);
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



    var test = $("#popup").is(":visible")

    var params = {"treeid1": treeid1, "nodeid1": nodeid1, "nodeid2": nodeid2, 'side' : 'source'};
    $('#'+treeid1)[0].onmousemove = (function() {
        var onmousestop = function() {
             $('#'+treeid1).load(ete_webplugin_URL+'/color_nodes', params,
                function() {
                console.log('color nodes');
                $('#'+treeid1).fadeTo(100, 0.9);
      });
        }, thread;

        return function() {
            clearTimeout(thread);
            thread = setTimeout(onmousestop, 500);
        };
    })();
    
    var params = {"treeid1": treeid1, "nodeid1": nodeid1, "nodeid2": nodeid2, 'side' : 'source'};
    $('#'+treeid2)[0].onmousemove = (function() {
        var onmousestop = function() {
             $('#'+treeid1).load(ete_webplugin_URL+'/color_nodes', params,
                function() {
                console.log('color nodes');
                $('#'+treeid2).fadeTo(100, 0.9);
      });
        }, thread;

        return function() {
            clearTimeout(thread);
            thread = setTimeout(onmousestop, 500);
        };
    })();
    
    if (test == true){
      $("#popup").hide();
    };

    

}
function unhighlight_node(){
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
    $(".column").html("");
    $("#popup").hide();
    $("#popup2").hide();
    $("#highlighter1").hide();
    $("#highlighter2").hide();
}

function clear_elements(){
    $("#popup").hide();
    $("#popup2").hide();
    $("#highlighter1").hide();
    $("#highlighter2").hide();
}


$(document).ready(function(){
  hide_popup();
  hide_diff();
  update_server_status();
});
