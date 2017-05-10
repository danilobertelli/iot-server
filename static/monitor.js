var content;
window.onload = function () {
  document.getElementsByClassName('title')[0].innerHTML = document.domain;
  content = document.getElementsByClassName('content')[0];
  setTimeout(getClientList, 2000);
}

function getClientList() {
  var oReq = new XMLHttpRequest();
  oReq.open("GET", "/get_keys", true);
  oReq.onload =  function (oEvent) {
    var list = oReq.responseText; // Note: not oReq.responseText
    console.log(list);
    if (list) {
      var dict = JSON.parse(list);
      content.innerHTML = "";
      for (var i = 0; i < dict.length; i++) {
        content.innerHTML += "<div class=\"client\">\
                                <div class=\"name\">" + dict[i]["name"] + "</div>\
                                <div class=\"ip\">" + dict[i]["ip"] + "</div>\
                              </div>";
      }
    }
    setTimeout(getClientList, 1000);
  };
  oReq.send()
}
