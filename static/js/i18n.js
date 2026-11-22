(function () {
  "use strict";
  var element = document.getElementById("site-ui-messages");
  var messages = element ? JSON.parse(element.textContent) : {};
  window.boristeneText = function (key) { return messages[key] || key; };
})();
