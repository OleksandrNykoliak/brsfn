(function () {
  "use strict";

  document.querySelectorAll("[data-project-gallery]").forEach(function (gallery) {
    var track = gallery.querySelector(".project-gallery-track");
    var items = Array.from(gallery.querySelectorAll("[data-gallery-item]"));
    var scrollButtons = gallery.querySelectorAll("[data-gallery-scroll]");
    var viewer = gallery.querySelector("[data-photo-viewer]");
    var image = viewer.querySelector("[data-photo-image]");
    var caption = viewer.querySelector("[data-photo-caption]");
    var counter = viewer.querySelector("[data-photo-count]");
    var current = 0;
    var previousOverflow = "";
    var trigger = null;
    var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    function updateScrollButtons() {
      scrollButtons.forEach(function (button) {
        button.disabled = Number(button.dataset.galleryScroll) < 0
          ? track.scrollLeft <= 1
          : track.scrollLeft + track.clientWidth >= track.scrollWidth - 1;
      });
    }

    scrollButtons.forEach(function (button) {
      button.addEventListener("click", function () {
        track.scrollBy({
          left: Number(button.dataset.galleryScroll) * track.clientWidth * .85,
          behavior: reducedMotion.matches ? "instant" : "smooth"
        });
      });
    });
    track.addEventListener("scroll", updateScrollButtons, {passive: true});
    if ("ResizeObserver" in window) new ResizeObserver(updateScrollButtons).observe(track);
    else window.addEventListener("resize", updateScrollButtons);
    updateScrollButtons();

    // The image links remain usable when native dialogs are unavailable.
    if (typeof viewer.showModal !== "function") return;

    function showPhoto(index) {
      current = (index + items.length) % items.length;
      var item = items[current];
      image.src = item.href;
      image.alt = item.querySelector("img").alt;
      caption.textContent = item.dataset.caption || "";
      counter.textContent = (current + 1) + " / " + items.length;
    }

    items.forEach(function (item, index) {
      item.addEventListener("click", function (event) {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        trigger = item;
        showPhoto(index);
        previousOverflow = document.body.style.overflow;
        viewer.showModal();
        document.body.style.overflow = "hidden";
      });
    });

    viewer.querySelectorAll("[data-photo-step]").forEach(function (button) {
      button.hidden = items.length < 2;
      button.addEventListener("click", function () {
        showPhoto(current + Number(button.dataset.photoStep));
      });
    });
    function restorePage() {
      document.body.style.overflow = previousOverflow;
      image.removeAttribute("src");
      if (trigger) {
        var target = trigger;
        trigger = null;
        target.focus({preventScroll: true});
      }
    }
    function closeViewer() {
      viewer.close();
      restorePage();
    }
    viewer.querySelector("[data-photo-close]").addEventListener("click", closeViewer);
    viewer.addEventListener("click", function (event) {
      if (event.target === viewer) closeViewer();
    });
    viewer.addEventListener("cancel", function (event) {
      event.preventDefault();
      closeViewer();
    });
    viewer.addEventListener("close", function () {
      if (!viewer.open) restorePage();
    });
    viewer.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        event.preventDefault();
        showPhoto(current + (event.key === "ArrowRight" ? 1 : -1));
      }
    });

    var touchStart = null;
    image.addEventListener("touchstart", function (event) {
      touchStart = event.touches.length === 1 ? {x: event.touches[0].clientX, y: event.touches[0].clientY} : null;
    }, {passive: true});
    image.addEventListener("touchend", function (event) {
      if (!touchStart || !event.changedTouches.length) return;
      var dx = event.changedTouches[0].clientX - touchStart.x;
      var dy = event.changedTouches[0].clientY - touchStart.y;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) showPhoto(current + (dx < 0 ? 1 : -1));
      touchStart = null;
    }, {passive: true});
  });
})();
