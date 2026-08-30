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
});
