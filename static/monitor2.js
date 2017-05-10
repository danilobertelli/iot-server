var content, clients = {};
window.onload = function () {
  document.getElementsByClassName('title')[0].innerHTML = document.domain;
  content = document.getElementsByClassName('content')[0];
  setTimeout(updateAverageTemperature, 1000);
  setTimeout(getClientList, 1000);
}
updateEnabled = true;

function getClientList() {
  if(!updateEnabled){
    return;
  }
  var oReq = new XMLHttpRequest();
  oReq.open("GET", "/get_keys", true);
  oReq.onload =  function (oEvent) {
    var list = oReq.responseText;
    console.log(list);
    if (list) {
      var dict = JSON.parse(list);
      content.innerHTML = "";
      clients = {}
      for (var i = 0; i < dict.length; i++) {
        content.innerHTML += "<div class=\"client\" id=\""+ dict[i]["name"] +"\" onclick=getTemperature(this)>\
                                <div class=\"name\">" + dict[i]["name"] + "</div>\
                                <div class=\"ip\">" + dict[i]["ip"] + "</div>\
                              </div>";
        clients[dict[i]["name"]] = undefined;
      }
    }
  };
  oReq.send()
  setTimeout(getClientList, 1000);
}

function updateIP(ip) {
  var oReq = new XMLHttpRequest();
  oReq.open("GET", "/update_ip?ip=" + ip, true);
  oReq.onload = function (oEvent) {
    console.log(oReq.responseText);
  }
  oReq.send()
}

function updateIPs(){
  var oReq = new XMLHttpRequest();
  oReq.open("GET", "/update_ip", true);
  oReq.onload = function (oEvent) {
    console.log(oReq.responseText);
  }
  oReq.send()
}

function getTemperature(element){
  updateEnabled = false;
  var name = element.id;
  var oReq = new XMLHttpRequest();
  oReq.open("GET", "/get_temp?name=" + name, true);
  oReq.onload =  function (oEvent) {
    var temp = oReq.responseText;
    if (temp) {
      tempN = parseInt(temp)
      if(!isNaN(tempN)){
        clients[name] = tempN;
        temp = "Temperature: " + temp + "°C"
      }
      element.innerHTML = "<div class=\"name\">" + name + "</div>\
                           <div class=\"ip\">" + temp + "</div>";

    }
  };
  oReq.send()
  element.innerHTML = "<div class=\"name\">" + name + "</div>\
                       <div class=\"ip\"> Connecting... </div>";
}

function getAverageTemperature() {
  for (var c in clients) {
    if(clients[c] == undefined){
      getTemperature(document.getElementById(c));
    }
  }
}

function updateAverageTemperature(){
  var sum = 0, total = 0;
  for (var c in clients) {
    if(clients[c] != undefined){
      sum += clients[c];
      total += 1;
    }
  }
  document.getElementsByClassName('temp')[0].innerHTML = (sum/total).toString() + "°";
  setTimeout(updateAverageTemperature, 1000);
}
