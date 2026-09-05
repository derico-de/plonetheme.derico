/* header.js — the search box's close gestures and its one piece of focus
 * management. Opening and closing are pure CSS on the `.opener` checkbox in
 * browser/templates/searchbox.pt, styled by header.css; this file only does
 * what a stylesheet cannot: it puts the caret in the field when the search
 * opens, closes it on Escape or a click elsewhere, and keeps the bar to one
 * open thing at a time — a mega panel or the narrow menu opening closes the
 * search, and the search opening closes them. The same sprinkle, for the
 * same reasons, as Clara's clara.js is for the mega menu.
 */
(function () {
  function init() {
    var box = document.querySelector("#portal-searchbox");
    if (!box) return;
    var opener = box.querySelector("#portal-searchbox-opener");
    var field = box.querySelector("#searchGadget");
    if (!opener || !field) return;

    var nav = document.querySelector("#portal-globalnav");
    var menuOpener = document.querySelector(".element-globalnav > .opener");

    function panelOpeners() {
      return nav ? nav.querySelectorAll(":scope > .nav-item > .opener") : [];
    }
    function close() {
      opener.checked = false;
    }

    // opening the search: nothing else stays open, and the caret is ready
    opener.addEventListener("change", function () {
      if (!opener.checked) return;
      panelOpeners().forEach(function (o) {
        o.checked = false;
      });
      if (menuOpener) menuOpener.checked = false;
      field.focus();
    });

    // a mega panel opening closes the search (clara.js keeps the panels to
    // one at a time among themselves)
    if (nav) {
      nav.addEventListener("change", function (e) {
        if (e.target.matches(".opener") && e.target.checked) close();
      });
    }
    // so does the narrow menu
    if (menuOpener) {
      menuOpener.addEventListener("change", function () {
        if (menuOpener.checked) close();
      });
    }

    // a click anywhere outside the search closes it; the field keeps its text
    document.addEventListener("click", function (e) {
      if (opener.checked && !box.contains(e.target)) close();
    });

    // Escape closes and hands focus back to the toggle. Only when the search
    // is open: clara.js owns Escape for the mega panels.
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape" || !opener.checked) return;
      close();
      opener.focus();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
