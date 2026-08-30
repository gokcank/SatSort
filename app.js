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

  // 4. In-Browser Live SDX Parser & Demo Viewer
  const SAMPLE_SDX_CONTENT = `SATCODX105TURKSAT 42E       TMPG40110540000TRT 1 HD0420TUR     ______300003____________106050160501705160----______                 
SATCODX105TURKSAT 42E       TMPG40110540000TRT SPOR0420TUR     ______300003____________106060160601706160----______ HD              
SATCODX105TURKSAT 42E       TMPG40110540000TRT HABE0420TUR     ______300003____________106070160701707160----______R HD             
SATCODX105TURKSAT 42E       TMPG40110540000TRT BELG0420TUR     ______300003____________106080160801708160----______ESEL HD          
SATCODX105TURKSAT 42E       TMPG40110540000TRT COCU0420TUR     ______300003____________106090160901709160----______K HD             
SATCODX105TURKSAT 42E       TMPG41120530000ATV HD  0420TUR     ______275003____________103010130101401130----______                 
SATCODX105TURKSAT 42E       TMPG41120530000A HABER 0420TUR     ______275003____________103020130201402130----______HD               
SATCODX105TURKSAT 42E       TMPG41120530000A SPOR H0420TUR     ______275003____________103030130301403130----______D                
SATCODX105TURKSAT 42E       TMPG41122450000KANAL D 0420TUR     ______275003____________102010120101301120----______HD               
SATCODX105TURKSAT 42E       TMPG41122450000CNN TURK0420TUR     ______275003____________102020120201302120----______ HD              
SATCODX105TURKSAT 42E       TMPG41122450000TEVE2 HD0420TUR     ______275003____________102030120301303120----______                 
SATCODX105TURKSAT 42E       TMPG41120150000STAR TV 0420TUR     ______275003____________101010110101201110----______HD               
SATCODX105TURKSAT 42E       TMPG41120150000NTV HD  0420TUR     ______275003____________101020110201202110----______                 
SATCODX105TURKSAT 42E       TMPG41122090000SHOW TV 0420TUR     ______100003____________104010140101501140----______HD               
SATCODX105TURKSAT 42E       TMPG41122090000HABERTUR0420TUR     ______100003____________104020140201502140----______K HD             
SATCODX105TURKSAT 42E       TMPG41123560000TV8 HD  0420TUR     ______071003____________105010150101601150----______                 
SATCODX105TURKSAT 42E       TMPG41123290000NOW HD  0420TUR     ______066663____________107010170101801170----______                 
SATCODX105TURKSAT 42E       TMPG40123800000BEYAZ TV0420TUR     ______275003____________108010180101901180----______ HD              
SATCODX105TURKSAT 42E       TMPG40126850000HALK TV 0420TUR     ______300003____________109010190102001190----______HD               
SATCODX105TURKSAT 42E       TMPG40126850000TELE 1 H0420TUR     ______300003____________109020190202002190----______D                
SATCODX105TURKSAT 42E       TMPG40126850000SOZCU TV0420TUR     ______300003____________109030190302003190----______ HD              
SATCODX105TURKSAT 42E       RMPG40110540000TRT FM  0420TUR     ______300003____________106100000001710171----______                 
SATCODX105TURKSAT 42E       RMPG40110540000TRT RADY0420TUR     ______300003____________106110000001711171----______O 1              
SATCODX105TURKSAT 42E       RMPG41120150000KRAL FM 0420TUR     ______275003____________101030000001203120----______                 `;

  const dropzone = document.getElementById("demo-dropzone");
  const fileInput = document.getElementById("demo-file-input");
  const chooseBtn = document.getElementById("demo-choose-btn");
  const sampleBtn = document.getElementById("demo-sample-btn");
  const viewer = document.getElementById("demo-viewer");
  const tableBody = document.getElementById("demo-table-body");
  const statsText = document.getElementById("demo-stats-text");
  const searchInput = document.getElementById("demo-search-input");

  let parsedChannels = [];

  function parseSdxContent(text) {
    const lines = text.split(/\r?\n/);
    const channels = [];

    lines.forEach((line) => {
      if (!line || line.trim().length < 30) return;
      const padded = line.padEnd(132, " ");

      const sat = padded.substring(10, 28).trim();
      const typeCode = padded.charAt(28);
      const isRadio = typeCode === "R";
      const pol = padded.charAt(33) === "0" ? "V" : "H";
      const freq = padded.substring(34, 39).trim();
      const rawName = (padded.substring(43, 51) + padded.substring(115, 132))
        .replace(/[\x00\x05]/g, "")
        .trim();
      const sym = padded.substring(69, 74).trim();

      channels.push({
        name: rawName || "İsimsiz Kanal",
        type: isRadio ? "Radyo" : "TV",
        isRadio: isRadio,
        satellite: sat || "TURKSAT",
        freq: freq,
        pol: pol,
        symbol: sym,
      });
    });

    return channels;
  }

  function renderTable(channels) {
    if (!tableBody) return;
    tableBody.innerHTML = "";

    if (channels.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 24px;">Eşleşen kanal bulunamadı.</td></tr>`;
      return;
    }

    channels.forEach((ch, idx) => {
      const tr = document.createElement("tr");
      const badgeClass = ch.isRadio ? "badge-channel-radio" : "badge-channel-tv";
      tr.innerHTML = `
        <td style="font-weight: 600; color: var(--text-muted);">${idx + 1}</td>
        <td style="font-weight: 600; color: var(--text);">${escapeHtml(ch.name)}</td>
        <td><span class="${badgeClass}">${ch.type}</span></td>
        <td style="color: var(--text-muted);">${escapeHtml(ch.satellite)}</td>
        <td style="font-family: var(--font-mono);">${ch.freq} MHz</td>
        <td style="font-weight: 600;">${ch.pol}</td>
        <td style="font-family: var(--font-mono); color: var(--text-muted);">${ch.symbol}</td>
      `;
      tableBody.appendChild(tr);
    });
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function displayChannels(channels, sourceLabel) {
    parsedChannels = channels;
    const tvCount = channels.filter((c) => !c.isRadio).length;
    const radioCount = channels.filter((c) => c.isRadio).length;

    if (statsText) {
      statsText.textContent = `${channels.length} Kanal (${tvCount} TV, ${radioCount} Radyo) - ${sourceLabel}`;
    }

    if (searchInput) {
      searchInput.value = "";
    }

    renderTable(parsedChannels);

    if (viewer) {
      viewer.style.display = "block";
      viewer.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }

  if (sampleBtn) {
    sampleBtn.addEventListener("click", () => {
      const channels = parseSdxContent(SAMPLE_SDX_CONTENT);
      displayChannels(channels, "Örnek Türksat 42°E Listesi");
    });
  }

  if (chooseBtn && fileInput) {
    chooseBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      fileInput.click();
    });
  }

  if (dropzone && fileInput) {
    dropzone.addEventListener("click", () => fileInput.click());

    ["dragenter", "dragover"].forEach((eventName) => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add("dragover");
      });
    });

    ["dragleave", "drop"].forEach((eventName) => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove("dragover");
      });
    });

    dropzone.addEventListener("drop", (e) => {
      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        handleFile(files[0]);
      }
    });

    fileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFile(e.target.files[0]);
      }
    });
  }

  function handleFile(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target.result;
      const channels = parseSdxContent(content);
      displayChannels(channels, file.name);
    };
    reader.readAsText(file, "ISO-8859-9");
  }

  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const query = e.target.value.toLowerCase().trim();
      if (!query) {
        renderTable(parsedChannels);
        return;
      }
      const filtered = parsedChannels.filter(
        (ch) =>
          ch.name.toLowerCase().includes(query) ||
          ch.freq.includes(query) ||
          ch.satellite.toLowerCase().includes(query) ||
          ch.type.toLowerCase().includes(query)
      );
      renderTable(filtered);
    });
  }

  // 5. Live GitHub API Integration (Latest Release & Repo Stats)
  const CACHE_TTL_MS = 3600 * 1000; // 1 hour in milliseconds

  async function fetchWithCache(url, cacheKey) {
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      try {
        const parsed = JSON.parse(cached);
        if (Date.now() - parsed.timestamp < CACHE_TTL_MS) {
          return parsed.data;
        }
      } catch (e) {
        localStorage.removeItem(cacheKey);
      }
    }

    const response = await fetch(url, { headers: { Accept: "application/vnd.github.v3+json" } });
    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status}`);
    }
    const data = await response.json();
    localStorage.setItem(cacheKey, JSON.stringify({ timestamp: Date.now(), data }));
    return data;
  }

  async function loadLatestRelease() {
    try {
      const release = await fetchWithCache(
        "https://api.github.com/repos/gokcank/SatSort/releases/latest",
        "satsort_gh_release"
      );
      if (!release || !release.tag_name) return;

      const tag = release.tag_name;

      currentReleaseTag = tag;

      // 1. Update version badge in navbar
      const versionBadge = document.getElementById("release-version-badge");
      if (versionBadge) {
        versionBadge.textContent = tag;
      }

      // 2. Find AppImage and .deb assets
      const assets = release.assets || [];
      const appImageAsset = assets.find((a) => a.name.endsWith(".AppImage"));
      const debAsset = assets.find((a) => a.name.endsWith(".deb") && !a.name.includes("1.0.1"));

      // 3. Update Hero AppImage button
      const heroBtn = document.getElementById("hero-appimage-btn");
      if (appImageAsset && heroBtn) {
        heroBtn.href = appImageAsset.browser_download_url;
      }

      // 4. Update Tab AppImage button
      const tabAppImageBtn = document.getElementById("tab-appimage-download-btn");
      if (appImageAsset && tabAppImageBtn) {
        tabAppImageBtn.href = appImageAsset.browser_download_url;
      }

      // 5. Update Tab .deb button
      const tabDebBtn = document.getElementById("tab-deb-download-btn");
      if (debAsset && tabDebBtn) {
        tabDebBtn.href = debAsset.browser_download_url;
      }

      // Refresh localized button labels with new tag
      setLanguage(currentLang);
    } catch (err) {
      console.debug("GitHub Release API offline or rate limited, using static fallbacks:", err);
    }
  }

  async function loadRepoStats() {
    try {
      const repo = await fetchWithCache(
        "https://api.github.com/repos/gokcank/SatSort",
        "satsort_gh_repo"
      );
      if (!repo) return;

      const stars = repo.stargazers_count;
      if (typeof stars === "number") {
        const starPill = document.getElementById("gh-stars-pill");
        const starCount = document.getElementById("gh-stars-count");
        if (starPill && starCount) {
          starCount.textContent = stars;
          starPill.style.display = "inline-flex";
        }
      }
    } catch (err) {
      console.debug("GitHub Repo Stats API offline or rate limited:", err);
    }
  }

  // 6. Multilingual Localization Controller (TR, EN, DE, FR, ES)
  let currentReleaseTag = "v1.1.0";
  let currentLang = "tr";

  function setLanguage(lang) {
    if (typeof LOCALES === "undefined" || !LOCALES[lang]) {
      lang = "tr";
    }
    currentLang = lang;
    localStorage.setItem("satsort_lang", lang);
    document.documentElement.setAttribute("lang", lang);

    const langSelect = document.getElementById("lang-select");
    if (langSelect) {
      langSelect.value = lang;
    }

    const dict = LOCALES[lang];
    if (!dict) return;

    // 1. Text elements
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (dict[key]) {
        el.textContent = dict[key];
      }
    });

    // 2. Titles and aria-labels
    document.querySelectorAll("[data-i18n-title]").forEach((el) => {
      const key = el.getAttribute("data-i18n-title");
      if (dict[key]) {
        el.setAttribute("title", dict[key]);
        el.setAttribute("aria-label", dict[key]);
      }
    });

    // 3. Placeholders
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const key = el.getAttribute("data-i18n-placeholder");
      if (dict[key]) {
        el.setAttribute("placeholder", dict[key]);
      }
    });

    // 4. Update download buttons with localized text + tag
    const heroText = document.getElementById("hero-appimage-text");
    if (heroText && dict.hero_btn_appimage) {
      heroText.textContent = `${dict.hero_btn_appimage} (${currentReleaseTag})`;
    }

    const tabAppImageText = document.getElementById("tab-appimage-download-text");
    if (tabAppImageText && dict.tab_appimage_btn) {
      tabAppImageText.textContent = `${dict.tab_appimage_btn} (${currentReleaseTag})`;
    }

    const tabDebText = document.getElementById("tab-deb-download-text");
    if (tabDebText && dict.tab_deb_btn) {
      tabDebText.textContent = `${dict.tab_deb_btn} (${currentReleaseTag})`;
    }

    // 5. Update Mockup Screenshot to match the active language
    const mockupImg = document.getElementById("mockup-img");
    if (mockupImg) {
      mockupImg.src = `app_screenshot_${lang}.png`;
    }
  }

  const langSelect = document.getElementById("lang-select");
  if (langSelect) {
    langSelect.addEventListener("change", (e) => {
      setLanguage(e.target.value);
    });
  }

  // Detect preferred language: saved -> navigator -> fallback (tr)
  function detectInitialLanguage() {
    const saved = localStorage.getItem("satsort_lang");
    if (saved && typeof LOCALES !== "undefined" && LOCALES[saved]) {
      return saved;
    }
    const navLang = (navigator.language || navigator.userLanguage || "tr").toLowerCase();
    if (navLang.startsWith("en")) return "en";
    if (navLang.startsWith("de")) return "de";
    if (navLang.startsWith("fr")) return "fr";
    if (navLang.startsWith("es")) return "es";
    return "tr";
  }

  // Initialize language
  setLanguage(detectInitialLanguage());

  // Trigger live updates asynchronously
  loadLatestRelease();
  loadRepoStats();
});
