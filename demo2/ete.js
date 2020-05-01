/*  it requires jquery loaded */
var ete_webplugin_URL = "http://localhost:8989";
var loading_img = '<img border=0 src="loader.gif">';

function update_server_status(){
  console.log('updating');
  $('#server_status').load(ete_webplugin_URL+"/status");

}


function get_tree_diff(newick1, recipient1, newick2, recipient2){
  var treeid1 = makeid();
  $(recipient1).html('<div id="' + treeid1 + '">' + loading_img + '</div>'); //Loading gif
  var treeid2 = makeid();
  $(recipient2).html('<div id="' + treeid2 + '">' + loading_img + '</div>'); //Loading gif

  var params = {'newick':newick1, 'treeid':treeid1,'newick2':newick2, 'treeid2':treeid2};
    
  $('#'+treeid1).load(ete_webplugin_URL+'/get_tree_diff', params,
    function() {
            $('#'+treeid1).fadeTo(100, 0.9);
  });
}


function get_tree_image2(newick1, recipient1, newick2, recipient2){
  var treeid1 = makeid();
  $(recipient1).html('<div id="' + treeid1 + '">' + loading_img + '</div>');
  //$(recipient).fadeTo(500, 0.2);
  var params = {'newick':newick1, 'treeid':treeid1};
  $('#'+treeid1).load(ete_webplugin_URL+'/get_tree_image', params,
    function() {
            $('#'+treeid1).fadeTo(100, 0.9);
  });
    
  var treeid2 = makeid();
  $(recipient2).html('<div id="' + treeid2 + '">' + loading_img + '</div>');
  //$(recipient).fadeTo(500, 0.2);
  var params = {'newick':newick2, 'treeid':treeid2};
  $('#'+treeid2).load(ete_webplugin_URL+'/get_tree_image', params,
    function() {
            $('#'+treeid2).fadeTo(100, 0.9);
  });
}

function get_tree_image(newick, recipient){
  var treeid = makeid();
  $(recipient).html('<div id="' + treeid + '">' + loading_img + '</div>');
  //$(recipient).fadeTo(500, 0.2);
  var params = {'newick':newick, 'treeid':treeid};
  $('#'+treeid).load(ete_webplugin_URL+'/get_tree_image', params,
    function() {
            $('#'+treeid).fadeTo(100, 0.9);
  });
}

function show_actions(treeid, nodeid, faceid){
  $("#popup").html(loading_img);
  var params = {"treeid": treeid, "nodeid": nodeid, "faceid": faceid};
  $('#popup').load(ete_webplugin_URL+'/get_actions', params);
}

function run_action(treeid, nodeid, faceid, aindex){
  $("#popup").hide();
  $('#'+treeid).html(loading_img);
  console.log(treeid, nodeid, faceid, aindex, $('#'+treeid));
  var params = {"treeid": treeid, "nodeid": nodeid, "faceid": faceid, "aindex":aindex};
  $('#'+treeid).load(ete_webplugin_URL+'/run_action', params,
    function() {
      console.log('run action');
            $('#'+treeid).fadeTo(100, 0.9);
  });
}


function bind_popup(){
  $(".ete_tree_img").bind('click',function(e){
                          $("#popup").css('left',e.pageX-2 );
                          $("#popup").css('top',e.pageY-2 );
                          $("#popup").css('position',"absolute" );
                          $("#popup").css('background-color',"#fff" );
                          $("#popup").draggable({ cancel: 'span,li' });
                          $("#popup").show();
                            });
}
function hide_popup(){
  $('#popup').hide();
}

function highlight_node(treeid, nodeid, faceid, x, y, width, height){
  return;
  console.log(treeid, nodeid, x, y, width, height);
  var img = $('#img_'+treeid);
  var offset = img.offset();
  console.log(img);
  console.log(offset);

  $("#highlighter").show();
  $("#highlighter").css("top", offset.top+y-1);
  $("#highlighter").css("left", offset.left+x-1);
  $("#highlighter").css("width", width+1);
  $("#highlighter").css("height", height+1);

}
function unhighlight_node(){
  console.log("unhighlight");
  $("#highlighter").hide();
}

function makeid()
{
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 5; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
}


$(document).ready(function(){
  hide_popup();
  update_server_status();
});
