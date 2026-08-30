/**
 * SatSort - Website Interactive Scripts
 * Handles installation tabs switching and 1-click clipboard copy.
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Installation Tabs Switching
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");

      // Update button active state
      tabButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      // Update content active state
      tabContents.forEach((content) => {
        if (content.id === targetId) {
          content.classList.add("active");
        } else {
          content.classList.remove("active");
        }
      });
    });
  });

  // 2. Code Copy to Clipboard
  const copyButtons = document.querySelectorAll(".copy-btn");

  copyButtons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const codeBox = btn.closest(".code-box");
      if (!codeBox) return;

      const codeBlock = codeBox.querySelector(".code-block code");
      if (!codeBlock) return;

      // Extract raw code excluding any extra whitespace
      const codeToCopy = codeBlock.innerText.trim();

      try {
        await navigator.clipboard.writeText(codeToCopy);
        const originalHtml = btn.innerHTML;
        btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg> Kopyalandı!`;
        btn.classList.add("copied");

        setTimeout(() => {
          btn.innerHTML = originalHtml;
          btn.classList.remove("copied");
        }, 2000);
      } catch (err) {
        console.error("Panoya kopyalama başarısız oldu:", err);
      }
    });
  });

  // 3. Theme Toggle (Dark / Light)
  const themeToggleBtn = document.getElementById("theme-toggle-btn");

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("satsort_theme", theme);
  }

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
      const nextTheme = currentTheme === "dark" ? "light" : "dark";
      applyTheme(nextTheme);
    });
  }

  // Listen to OS scheme changes if user hasn't explicitly set a preference
  if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: light)").addEventListener("change", (e) => {
      if (!localStorage.getItem("satsort_theme")) {
        applyTheme(e.matches ? "light" : "dark");
      }
    });
  }
});
