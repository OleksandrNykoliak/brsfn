(function () {
  "use strict";

  var year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();

  var revealEls = document.querySelectorAll(".reveal");
  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reducedMotion || !("IntersectionObserver" in window)) {
    revealEls.forEach(function (element) { element.classList.add("is-visible"); });
  } else {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -60px 0px" });
    revealEls.forEach(function (element) { observer.observe(element); });
  }

  document.querySelectorAll(".faq-groups").forEach(function (group) {
    var items = group.querySelectorAll("details.faq-item");
    items.forEach(function (item) {
      item.addEventListener("toggle", function () {
        if (item.open) items.forEach(function (other) {
          if (other !== item) other.removeAttribute("open");
        });
      });
    });
  });

  document.querySelectorAll("[data-tabgroup]").forEach(function (group) {
    group.querySelectorAll(".tab-btn").forEach(function (button) {
      button.addEventListener("click", function () {
        group.querySelectorAll(".tab-btn").forEach(function (item) { item.classList.remove("active"); });
        group.querySelectorAll(".tab-panel").forEach(function (panel) { panel.classList.remove("active"); });
        button.classList.add("active");
        var panel = group.querySelector("#panel-" + button.dataset.tab);
        if (panel) panel.classList.add("active");
      });
    });

    var hashTab = window.location.hash.replace("#", "");
    var hashButton = group.querySelector('[data-tab="join-' + hashTab + '"]');
    if (hashButton) {
      hashButton.click();
    }
  });

  document.querySelectorAll("[data-partner-carousel]").forEach(function (carousel) {
    var track = carousel.querySelector(".partner-track");
    var cards = carousel.querySelectorAll(".partner-card");
    var dots = carousel.querySelector("[data-partner-dots]");
    var previous = carousel.querySelector("[data-partner-prev]");
    var next = carousel.querySelector("[data-partner-next]");
    if (!track || !cards.length || !dots) return;

    var getStep = function () {
      return cards[0].getBoundingClientRect().width + parseFloat(getComputedStyle(track).gap || 0);
    };
    var pageCount = function () {
      return Math.max(1, Math.ceil((track.scrollWidth - track.clientWidth) / getStep()) + 1);
    };
    var activePage = function () {
      return Math.min(pageCount() - 1, Math.round(track.scrollLeft / getStep()));
    };
    var renderDots = function () {
      dots.innerHTML = "";
      for (var index = 0; index < pageCount(); index += 1) {
        var dot = document.createElement("button");
        dot.className = "partner-dot" + (index === activePage() ? " active" : "");
        dot.type = "button";
        dot.setAttribute("aria-label", "Go to partner page " + (index + 1));
        dot.addEventListener("click", function (event) {
          track.scrollTo({ left: Number(event.currentTarget.dataset.page) * getStep(), behavior: "smooth" });
        });
        dot.dataset.page = index;
        dots.appendChild(dot);
      }
    };
    var scrollByPage = function (direction) {
      var target = Math.max(0, Math.min(pageCount() - 1, activePage() + direction));
      track.scrollTo({ left: target * getStep(), behavior: "smooth" });
    };
    if (previous) previous.addEventListener("click", function () { scrollByPage(-1); });
    if (next) next.addEventListener("click", function () { scrollByPage(1); });
    track.addEventListener("scroll", function () {
      dots.querySelectorAll(".partner-dot").forEach(function (dot, index) {
        dot.classList.toggle("active", index === activePage());
      });
    }, { passive: true });
    renderDots();
    window.addEventListener("resize", renderDots);

    var isPaused = false;
    carousel.addEventListener("mouseenter", function () { isPaused = true; });
    carousel.addEventListener("mouseleave", function () { isPaused = false; });
    if (!reducedMotion && pageCount() > 1) {
      track.style.scrollBehavior = "auto";
      track.style.scrollSnapType = "none";
      window.setInterval(function () {
        if (isPaused || document.hidden) return;
        var end = track.scrollWidth - track.clientWidth;
        track.scrollLeft += 1;
        if (track.scrollLeft >= end - 1) track.scrollLeft = 0;
      }, 16);
    }
  });

  document.querySelectorAll("[data-project-carousel]").forEach(function (carousel) {
    var track = carousel.querySelector(".proj-scroll");
    var cards = carousel.querySelectorAll(".proj-card");
    var dots = carousel.querySelector("[data-project-dots]");
    var previous = carousel.querySelector("[data-project-prev]");
    var next = carousel.querySelector("[data-project-next]");
    if (!track || !cards.length || !dots) return;
    var step = function () { return cards[0].getBoundingClientRect().width + parseFloat(getComputedStyle(track).gap || 0); };
    var pages = function () { return Math.max(1, Math.ceil((track.scrollWidth - track.clientWidth) / step()) + 1); };
    var active = function () { return Math.min(pages() - 1, Math.round(track.scrollLeft / step())); };
    var render = function () {
      dots.innerHTML = "";
      for (var index = 0; index < pages(); index += 1) {
        var dot = document.createElement("button");
        dot.type = "button";
        dot.className = "project-dot" + (index === active() ? " active" : "");
        dot.dataset.page = index;
        dot.setAttribute("aria-label", "Go to project page " + (index + 1));
        dot.addEventListener("click", function (event) { track.scrollTo({ left: Number(event.currentTarget.dataset.page) * step(), behavior: "smooth" }); });
        dots.appendChild(dot);
      }
    };
    var move = function (direction) { track.scrollTo({ left: Math.max(0, Math.min(pages() - 1, active() + direction)) * step(), behavior: "smooth" }); };
    if (previous) previous.addEventListener("click", function () { move(-1); });
    if (next) next.addEventListener("click", function () { move(1); });
    track.addEventListener("scroll", function () { dots.querySelectorAll(".project-dot").forEach(function (dot, index) { dot.classList.toggle("active", index === active()); }); }, { passive: true });
    render();
    window.addEventListener("resize", render);
  });

  var newsletter = document.getElementById("nlForm");
  var newsletterMessage = document.getElementById("nlMsg");
  if (newsletter && newsletterMessage) newsletter.addEventListener("submit", function (event) {
    event.preventDefault();
    if (!newsletter.checkValidity()) {
      newsletter.reportValidity();
      return;
    }
    newsletterMessage.classList.add("is-shown");
    newsletter.reset();
  });
})();





document.addEventListener("DOMContentLoaded", () => {

  const toggle = document.getElementById("heroSupportToggle");
  const panel = document.getElementById("heroDonatePanel");
  const amountInput = document.getElementById("heroDonateAmount");

  if (toggle && panel) {
    toggle.addEventListener("click", () => {
      const open = panel.classList.toggle("is-open");

      toggle.setAttribute(
        "aria-expanded",
        open ? "true" : "false"
      );

      panel.setAttribute(
        "aria-hidden",
        open ? "false" : "true"
      );
    });
  }


  /* One-time / monthly */

  document.querySelectorAll(".hero-donate-tab").forEach(tab => {
    tab.addEventListener("click", () => {

      document
        .querySelectorAll(".hero-donate-tab")
        .forEach(item => item.classList.remove("is-active"));

      tab.classList.add("is-active");

    });
  });


  /* Quick amounts */

  document.querySelectorAll("[data-hero-amount]").forEach(button => {
    button.addEventListener("click", () => {

      const amount = button.dataset.heroAmount;

      if (amountInput) {
        amountInput.value = amount;
      }

      document
        .querySelectorAll("[data-hero-amount]")
        .forEach(item => item.classList.remove("is-selected"));

      button.classList.add("is-selected");

    });
  });


  /* Bank details */

  const detailsToggle =
    document.getElementById("heroDonateDetailsToggle");

  const details =
    document.getElementById("heroDonateDetails");

  if (detailsToggle && details) {

    detailsToggle.addEventListener("click", () => {

      detailsToggle.classList.toggle("is-open");
      details.classList.toggle("is-open");

    });

  }


  /* Copy IBAN */

  document.querySelectorAll(".hero-bank-copy").forEach(button => {

    button.addEventListener("click", async () => {

      const selector = button.dataset.copy;
      const element = document.querySelector(selector);

      if (!element) return;

      await navigator.clipboard.writeText(
        element.textContent.trim()
      );

      button.textContent = "Copied";

      setTimeout(() => {
        button.textContent = "Copy";
      }, 1200);

    });

  });


  /* Donate */

  const donateButton =
    document.getElementById("heroDonateSubmit");

  if (donateButton) {

    donateButton.addEventListener("click", () => {

      const amount =
        Number(amountInput?.value || 0);

      const type =
        document
          .querySelector(".hero-donate-tab.is-active")
          ?.dataset.donateType || "once";

      console.log({
        amount: amount,
        currency: "EUR",
        type: type
      });

      /*
       * Тут підключимо реальну оплату:
       * Stripe / PayPal / інший payment provider.
       */

    });

  }

});