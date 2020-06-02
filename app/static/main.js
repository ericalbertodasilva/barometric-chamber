var data1;
var data2;
var data3;
var options;
var chart_data;
var pres = [0,0,0]
var temp = [0,0]
var humi = [0,0]
﻿function toggleFullScreen() {
  if ((document.fullScreenElement && document.fullScreenElement !== null) ||    
  (!document.mozFullScreen && !document.webkitIsFullScreen)) {
      if (document.documentElement.requestFullScreen) {  
      document.documentElement.requestFullScreen();  
      } else if (document.documentElement.mozRequestFullScreen) {  
      document.documentElement.mozRequestFullScreen();  
      } else if (document.documentElement.webkitRequestFullScreen) {  
      document.documentElement.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT);  
      }  
  } else {  
      if (document.cancelFullScreen) {  
      document.cancelFullScreen();  
      } else if (document.mozCancelFullScreen) {  
      document.mozCancelFullScreen();  
      } else if (document.webkitCancelFullScreen) {  
      document.webkitCancelFullScreen();  
      }  
  }  
}


var c=1;
$(document).ready(function() {
  $.post('http://127.0.0.1:5000/_get_ensaios_nomes', function(data) {
    r = data
    if (c==1){
      for(var i=0 in r) {
        $("#selecionar_experimento").append("<option>"+r[i]+"</option>");
      }
      c=2;
    }
  });
})
/*
$("#selecionar_experimento").click(function(){
  $(document).ready(function(){
    $.post('http://127.0.0.1:5000/_get_ensaios_nomes', function(data) {
      r = data
      if (c==1){
        for(var i=0 in r) {
          $("#selecionar_experimento").append("<option>"+r[i]+"</option>");
        }
        c=2;
      }
    });
  });
})
*/

$("#atualizar").click(function(){
  var nm = $('select option:selected').text()
  $.post('http://127.0.0.1:5000/_get_ensaio_escolhido',{
    nome:nm
  }, function(data) {
    tt=data;
    $("#nome").val(data["nome"]);
    $("#pressao_referencia").val(data["pressao_referencia"]);
    $("#tempo_atingir_referencia").val(data["tempo_atingir_referencia"]);
    $("#tempo_estavel_referencia").val(data["tempo_estavel_referencia"]);
    $("#pressao_de_ensaio").val(data["pressao_de_ensaio"]);
    $("#tempo_atingir_ensaio").val(data["tempo_atingir_ensaio"]);
    $("#ativacao_data").val(data["ativacao_data"]);
    $("#ativacao_hora").val(data["ativacao_hora"]);
    $("#desativacao_data").val(data["desativacao_data"]);
    $("#desativacao_hora").val(data["desativacao_hora"]);
  });
});

$("#gerar_proj").click(function(){
  $(document).ready(function(){
    var nm = $('select.selecionar_experimento option:selected').text()
    $.post('http://127.0.0.1:5000/gerar_grafico_proj',{
      nome:nm
    }, function(data) {
      tt=data;
    });
  });
});

k=0
var rrr

$("#ligar_bomba").click(function(){
  var nm = "ligar_bomba"
  $.post('http://127.0.0.1:5000/ligar_bomba',{
  nome:nm
  }, function(data) {
  });
});
$("#desligar_bomba").click(function(){
  var nm = "desligar_bomba"
  $.post('http://127.0.0.1:5000/desligar_bomba',{
  nome:nm
  }, function(data) {
  });
});
$("#ligar_pid").click(function(){
  var nm = "ligar_pid"
  $.post('http://127.0.0.1:5000/ligar_pid',{
  nome:nm
  }, function(data) {
  });
});
$("#desligar_pid").click(function(){
  var nm = "desligar_pid"
  $.post('http://127.0.0.1:5000/desligar_pid',{
  nome:nm
  }, function(data) {
  });
});
$("#gravar_v_pressao").click(function(){
  var nm = $('#ppressao').val()
  $.post('http://127.0.0.1:5000/valvula_pressao',{
  ppressao:nm
  }, function(data) {
  });
});
$("#gravar_v_vacuo").click(function(){
  var nm = $('#pvacuo').val()
  $.post('http://127.0.0.1:5000/valvula_vacuo',{
  pvacuo:nm
  }, function(data) {
  });
});