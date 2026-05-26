// OmniLogic Healthcare · main.js
// Shared utilities — module-specific JS lives in each template

// Highlight current nav link
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".nav-links a").forEach(link => {
    if (link.getAttribute("href") === window.location.pathname) {
      link.classList.add("active");
    }
  });
});
