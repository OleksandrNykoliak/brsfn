(function () {
  "use strict";

  document.querySelectorAll("[data-support-tab]").forEach(function (tab) {
    tab.addEventListener("click", function () {
      var card = tab.closest(".support-card");
      card.querySelectorAll("[data-support-tab]").forEach(function (item) { item.classList.remove("is-active"); });
      card.querySelectorAll("[data-support-tab]").forEach(function (item) { item.setAttribute("aria-selected", "false"); });
      tab.classList.add("is-active");
      tab.setAttribute("aria-selected", "true");
      var isMonthly = tab.dataset.supportTab === "monthly";
      var note = card.querySelector("[data-mode-note]");
      if (note) note.textContent = isMonthly ? "Monthly contribution" : "One-time contribution";
      var submitLabel = card.querySelector("[data-support-submit-label]");
      if (submitLabel) submitLabel.textContent = isMonthly ? "Support monthly" : "Support once";
      var alternative = card.querySelector("[data-subscription-alternative]");
      if (alternative) alternative.hidden = !isMonthly;
    });
  });

  document.querySelectorAll("[data-requisite-tab]").forEach(function (tab) {
    tab.addEventListener("click", function () {
      var card = tab.closest(".support-card");
      card.querySelectorAll("[data-requisite-tab]").forEach(function (item) { item.classList.remove("is-active"); });
      card.querySelectorAll("[data-requisite-tab]").forEach(function (item) { item.setAttribute("aria-selected", "false"); });
      card.querySelectorAll("[data-requisite-panel]").forEach(function (panel) { panel.classList.remove("is-active"); });
      tab.classList.add("is-active");
      tab.setAttribute("aria-selected", "true");
      var panel = card.querySelector('[data-requisite-panel="' + tab.dataset.requisiteTab + '"]');
      if (panel) panel.classList.add("is-active");
    });
  });

  document.querySelectorAll("[data-amount]").forEach(function (button) {
    button.addEventListener("click", function () {
      var form = button.closest("[data-donation-form]");
      var input = form && form.querySelector("[data-donation-input]");
      if (input) input.value = Number(input.value || 0) + Number(button.dataset.amount);
    });
  });

  var copyIban = document.querySelector("[data-copy-iban]");
  if (copyIban) copyIban.addEventListener("click", function () {
    navigator.clipboard.writeText("To be confirmed");
    copyIban.textContent = "Copied";
  });

  var shareButton = document.querySelector("[data-share-project]");
  if (shareButton) shareButton.addEventListener("click", function () {
    var popover = document.querySelector("[data-share-popover]");
    if (!popover) return;
    popover.hidden = !popover.hidden;
    shareButton.setAttribute("aria-expanded", popover.hidden ? "false" : "true");
  });

  var closeShare = document.querySelector("[data-close-share]");
  if (closeShare) closeShare.addEventListener("click", function () {
    var popover = document.querySelector("[data-share-popover]");
    if (popover) popover.hidden = true;
    if (shareButton) shareButton.setAttribute("aria-expanded", "false");
  });

  var copyProjectLink = document.querySelector("[data-copy-project-link]");
  if (copyProjectLink) copyProjectLink.addEventListener("click", function () {
    navigator.clipboard.writeText(window.location.href);
    copyProjectLink.innerHTML = '<span class="share-brand">&#10003;</span>Copied';
  });
})();
