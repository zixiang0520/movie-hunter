/* ═══════════════════════════════════════════════════════════════
   Movie Hunter — Frontend Application
   ═══════════════════════════════════════════════════════════════ */

(function () {
  "use strict";

  // ── State ──────────────────────────────────────────────────────
  let API_BASE = "/api/image/";  // Proxy through backend to bypass GFW
  let state = {
    settings: null,
    currentView: "search",
    lastQuery: "",
  };

  // ── DOM refs ───────────────────────────────────────────────────
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  const els = {
    searchInput: $("#searchInput"),
    searchBtn: $("#searchBtn"),
    searchResults: $("#searchResults"),
    resultGrid: $("#resultGrid"),
    resultLoading: $("#resultLoading"),
    resultError: $("#resultError"),
    resultEmpty: $("#resultEmpty"),
    searchView: $("#searchView"),
    detailView: $("#detailView"),
    detailContent: $("#detailContent"),
    settingsBtn: $("#settingsBtn"),
    settingsModal: $("#settingsModal"),
    settingsClose: $("#settingsClose"),
    settingsCancel: $("#settingsCancel"),
    settingsSave: $("#settingsSave"),
    setApiKey: $("#setApiKey"),
    setLang: $("#setLang"),
    setProxyEnabled: $("#setProxyEnabled"),
    proxyFields: $("#proxyFields"),
    setProxyProto: $("#setProxyProto"),
    setProxyHost: $("#setProxyHost"),
    setProxyPort: $("#setProxyPort"),
    setProxyUser: $("#setProxyUser"),
    setProxyPass: $("#setProxyPass"),
    testConnection: $("#testConnection"),
    testResult: $("#testResult"),
    setPassword: $("#setPassword"),
    toggleApiKey: $("#toggleApiKey"),
    // Password auth modal
    passwordModal: $("#passwordModal"),
    passwordInput: $("#passwordInput"),
    passwordClose: $("#passwordClose"),
    passwordCancel: $("#passwordCancel"),
    passwordConfirm: $("#passwordConfirm"),
    passwordError: $("#passwordError"),
    backBtn: $("#backBtn"),
    toast: $("#toast"),
  };

  // ── Helpers ────────────────────────────────────────────────────

  function posterUrl(path, size = "w500") {
    if (!path) return null;
    return API_BASE + size + path;
  }

  function typeIcon(mediaType) {
    switch (mediaType) {
      case "movie": return "🎬";
      case "tv": return "📺";
      case "person": return "👤";
      default: return "📋";
    }
  }

  function typeLabel(mediaType) {
    switch (mediaType) {
      case "movie": return "电影";
      case "tv": return "电视剧";
      case "person": return "人物";
      default: return mediaType;
    }
  }

  function ratingStars(rating) {
    if (!rating) return "";
    const stars = Math.round(rating / 2);
    return "⭐ " + rating.toFixed(1);
  }

  function escHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function truncate(str, max) {
    if (!str) return "";
    return str.length > max ? str.slice(0, max) + "..." : str;
  }

  function formatDate(d) {
    if (!d) return "未知";
    return d.split("-")[0];
  }

  function showToast(msg, isError) {
    els.toast.textContent = msg;
    els.toast.className = "toast show" + (isError ? " error" : "");
    clearTimeout(els.toast._t);
    els.toast._t = setTimeout(() => els.toast.classList.remove("show"), 3000);
  }

  // ── API ────────────────────────────────────────────────────────

  async function apiGet(path, params) {
    const url = new URL(path, window.location.origin);
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== null && v !== undefined && v !== "") url.searchParams.set(k, v);
      });
    }
    const resp = await fetch(url);
    if (!resp.ok) {
      const body = await resp.json().catch(() => ({}));
      throw new Error(body.detail || `请求失败 (${resp.status})`);
    }
    return resp.json();
  }

  async function apiPost(path, data) {
    const resp = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!resp.ok) throw new Error(`保存失败 (${resp.status})`);
    return resp.json();
  }

  async function loadConfig() {
    try {
      await apiGet("/api/config");
      // Keep API_BASE as the local proxy — images are proxied by the backend
    } catch (_) {
      // Config fetch is best-effort; images still go through /api/image/
    }
  }

  async function loadSettings() {
    state.settings = await apiGet("/api/settings");
  }

  // ── Search ─────────────────────────────────────────────────────

  async function doSearch(query) {
    if (!query.trim()) return;
    state.lastQuery = query.trim();

    els.resultGrid.innerHTML = "";
    els.resultError.className = "error-msg hidden";
    els.resultEmpty.className = "empty-msg hidden";
    els.resultLoading.className = "loading";

    try {
      await loadConfig();
      const data = await apiGet("/api/search", { q: state.lastQuery });
      const results = data.results || [];

      els.resultLoading.className = "loading hidden";

      if (results.length === 0) {
        els.resultEmpty.className = "empty-msg";
        return;
      }

      results.forEach((item) => {
        if (item.media_type === "person") {
          // Only show people with profile
          // Always show but less prominent
        }
        const card = document.createElement("div");
        card.className = "result-card";
        card.dataset.id = item.id;
        card.dataset.type = item.media_type;

        const title = item.title || item.name || "";
        const date = item.release_date || item.first_air_date || "";
        const poster = item.poster_path ? posterUrl(item.poster_path, "w342") : null;

        let mediaHtml = "";
        if (poster) {
          mediaHtml = `<img class="result-card-poster" src="${poster}" alt="${escHtml(title)}">`;
        } else if (item.media_type === "person") {
          mediaHtml = `<div class="result-card-poster placeholder">👤</div>`;
        } else {
          mediaHtml = `<div class="result-card-poster placeholder">${typeIcon(item.media_type)}</div>`;
        }

        card.innerHTML = `
          ${mediaHtml}
          <div class="result-card-info">
            <div class="result-card-type">${typeIcon(item.media_type)} ${typeLabel(item.media_type)}</div>
            <div class="result-card-title">${escHtml(title)}</div>
            <div class="result-card-date">${formatDate(date)}</div>
            <div class="result-card-rating">${ratingStars(item.vote_average)}</div>
          </div>
        `;

        card.addEventListener("click", () => showDetail(item.media_type, item.id));
        els.resultGrid.appendChild(card);
      });
    } catch (e) {
      els.resultLoading.className = "loading hidden";
      els.resultError.textContent = "❌ " + e.message;
      els.resultError.className = "error-msg";
    }
  }

  // ── Detail ─────────────────────────────────────────────────────

  async function showDetail(type, id) {
    els.searchView.classList.add("hidden");
    els.detailView.classList.remove("hidden");
    state.currentView = "detail";
    els.detailContent.innerHTML = '<div class="loading"><div class="spinner"></div><span>加载中...</span></div>';
    window.scrollTo({ top: 0, behavior: "smooth" });

    try {
      await loadConfig();
      let data;
      if (type === "movie") {
        data = await apiGet("/api/movie/" + id);
        renderMovie(data.detail, data.images, data.videos);
      } else if (type === "tv") {
        data = await apiGet("/api/tv/" + id);
        renderTV(data.detail, data.seasons_detail, data.images, data.videos);
      } else if (type === "person") {
        data = await apiGet("/api/person/" + id);
        renderPerson(data.detail, data.movie_credits);
      }
    } catch (e) {
      els.detailContent.innerHTML = `<div class="error-msg">❌ ${escHtml(e.message)}</div>`;
    }
  }

  function renderMovie(d, images, videos) {
    const runtimeStr = d.runtime ? `${Math.floor(d.runtime / 60)}h ${d.runtime % 60}m` : "未知时长";
    const budgetStr = d.budget > 0 ? `$${(d.budget / 1000000).toFixed(1)}M` : "—";
    const revenueStr = d.revenue > 0 ? `$${(d.revenue / 1000000).toFixed(1)}M` : "—";

    els.detailContent.innerHTML = `
      <div class="detail-page">
        <div class="detail-hero">
          ${d.backdrop_path ? `<img class="detail-backdrop" src="${posterUrl(d.backdrop_path, 'w1280')}" alt="">` : ""}
          <div class="detail-hero-content">
            ${d.poster_path
              ? `<img class="detail-poster" src="${posterUrl(d.poster_path, 'w500')}" alt="">`
              : `<div class="detail-poster" style="display:flex;align-items:center;justify-content:center;background:var(--bg-secondary);font-size:3rem;">🎬</div>`}
            <div class="detail-main">
              <h1 class="detail-title">${escHtml(d.title)}</h1>
              ${d.original_title && d.original_title !== d.title ? `<div class="detail-original">${escHtml(d.original_title)}</div>` : ""}
              <div class="detail-meta">
                <span class="meta-badge rating">⭐ ${d.vote_average.toFixed(1)}</span>
                <span class="meta-badge">📅 ${formatDate(d.release_date)}</span>
                <span class="meta-badge">⏱ ${runtimeStr}</span>
                ${d.status ? `<span class="meta-badge">📌 ${escHtml(d.status)}</span>` : ""}
              </div>
              ${d.tagline ? `<p class="detail-tagline">"${escHtml(d.tagline)}"</p>` : ""}
              <div class="detail-meta">
                ${d.genres.map(g => `<span class="meta-badge genre">${escHtml(g.name)}</span>`).join("")}
              </div>
            </div>
          </div>
        </div>

        <div class="detail-sections">
          ${d.overview
            ? `<div class="detail-section">
                 <div class="detail-section-title">📝 剧情简介</div>
                 <p class="detail-overview">${escHtml(d.overview)}</p>
               </div>` : ""}

          <div class="detail-section">
            <div class="detail-section-title">📊 详细信息</div>
            <div class="info-grid">
              ${d.budget > 0 ? `<div class="info-item"><span class="info-label">预算</span><span class="info-value">${budgetStr}</span></div>` : ""}
              ${d.revenue > 0 ? `<div class="info-item"><span class="info-label">票房</span><span class="info-value">${revenueStr}</span></div>` : ""}
              ${d.production_countries?.length ? `<div class="info-item"><span class="info-label">制片国家</span><span class="info-value">${d.production_countries.map(c => c.name).join(", ")}</span></div>` : ""}
              ${d.spoken_languages?.length ? `<div class="info-item"><span class="info-label">语言</span><span class="info-value">${d.spoken_languages.map(l => l.name).join(", ")}</span></div>` : ""}
              ${d.production_companies?.length ? `<div class="info-item"><span class="info-label">制作公司</span><span class="info-value">${d.production_companies.map(c => c.name).join(", ")}</span></div>` : ""}
              ${d.original_language ? `<div class="info-item"><span class="info-label">原始语言</span><span class="info-value">${escHtml(d.original_language)}</span></div>` : ""}
            </div>
          </div>

          ${d.cast.length ? `
            <div class="detail-section">
              <div class="detail-section-title">🎭 演员表 <span style="color:var(--text-muted);font-weight:400;font-size:0.8rem;">(${d.cast.length}人)</span></div>
              <div class="cast-grid">
                ${d.cast.slice(0, 30).map(c => `
                  <div class="cast-card" data-person-id="${c.id}">
                    ${c.profile_path
                      ? `<img class="cast-avatar" src="${posterUrl(c.profile_path, 'w185')}" alt="">`
                      : `<div class="cast-avatar placeholder">👤</div>`}
                    <div class="cast-name">${escHtml(c.name)}</div>
                    <div class="cast-char">${escHtml(c.character || "未知角色")}</div>
                  </div>
                `).join("")}
              </div>
            </div>` : ""}

          ${d.crew.length ? `
            <div class="detail-section">
              <div class="detail-section-title">🎬 幕后团队</div>
              <div class="crew-list">
                ${d.crew.slice(0, 15).map(c => `
                  <span class="crew-chip" data-person-id="${c.id}">
                    <strong>${escHtml(c.name)}</strong>
                    <span class="crew-chip-role">${escHtml(c.job)}</span>
                  </span>
                `).join("")}
              </div>
            </div>` : ""}

          ${d.similar.length ? `
            <div class="detail-section">
              <div class="detail-section-title">🔗 相似影片</div>
              <div class="similar-scroll">
                ${d.similar.slice(0, 15).map(s => `
                  <div class="similar-card" data-type="movie" data-id="${s.id}">
                    ${s.poster_path
                      ? `<img src="${posterUrl(s.poster_path, 'w185')}" alt="">`
                      : `<div style="width:140px;height:210px;background:var(--bg-secondary);border-radius:8px;display:flex;align-items:center;justify-content:center;">🎬</div>`}
                    <div class="s-title">${escHtml(s.title || s.name)}</div>
                  </div>
                `).join("")}
              </div>
            </div>` : ""}
        </div>
      </div>
    `;

    // Bind cast/crew clicks
    els.detailContent.querySelectorAll('[data-person-id]').forEach(el => {
      el.addEventListener("click", () => showDetail("person", el.dataset.personId));
    });
    els.detailContent.querySelectorAll('.similar-card').forEach(el => {
      el.addEventListener("click", () => showDetail(el.dataset.type, parseInt(el.dataset.id)));
    });
  }

  function renderTV(d, seasonsDetail, images, videos) {
    els.detailContent.innerHTML = `
      <div class="detail-page">
        <div class="detail-hero">
          ${d.backdrop_path ? `<img class="detail-backdrop" src="${posterUrl(d.backdrop_path, 'w1280')}" alt="">` : ""}
          <div class="detail-hero-content">
            ${d.poster_path
              ? `<img class="detail-poster" src="${posterUrl(d.poster_path, 'w500')}" alt="">`
              : `<div class="detail-poster" style="display:flex;align-items:center;justify-content:center;background:var(--bg-secondary);font-size:3rem;">📺</div>`}
            <div class="detail-main">
              <h1 class="detail-title">${escHtml(d.name)}</h1>
              ${d.original_name && d.original_name !== d.name ? `<div class="detail-original">${escHtml(d.original_name)}</div>` : ""}
              <div class="detail-meta">
                <span class="meta-badge rating">⭐ ${d.vote_average.toFixed(1)}</span>
                <span class="meta-badge">📅 ${formatDate(d.first_air_date)}</span>
                <span class="meta-badge">📺 ${d.number_of_seasons}季 ${d.number_of_episodes}集</span>
                ${d.status ? `<span class="meta-badge">📌 ${escHtml(d.status)}</span>` : ""}
              </div>
              <div class="detail-meta">
                ${d.genres.map(g => `<span class="meta-badge genre">${escHtml(g.name)}</span>`).join("")}
              </div>
            </div>
          </div>
        </div>

        <div class="detail-sections">
          ${d.overview
            ? `<div class="detail-section">
                 <div class="detail-section-title">📝 剧情简介</div>
                 <p class="detail-overview">${escHtml(d.overview)}</p>
               </div>` : ""}

          <div class="detail-section">
            <div class="detail-section-title">📊 详细信息</div>
            <div class="info-grid">
              ${d.production_countries?.length ? `<div class="info-item"><span class="info-label">制片国家</span><span class="info-value">${d.production_countries.map(c => c.name).join(", ")}</span></div>` : ""}
              ${d.episode_run_time?.length ? `<div class="info-item"><span class="info-label">单集时长</span><span class="info-value">${d.episode_run_time.join("/")}分钟</span></div>` : ""}
              ${d.original_language ? `<div class="info-item"><span class="info-label">原始语言</span><span class="info-value">${escHtml(d.original_language)}</span></div>` : ""}
            </div>
          </div>

          ${d.cast.length ? `
            <div class="detail-section">
              <div class="detail-section-title">🎭 演员表</div>
              <div class="cast-grid">
                ${d.cast.slice(0, 30).map(c => `
                  <div class="cast-card" data-person-id="${c.id}">
                    ${c.profile_path
                      ? `<img class="cast-avatar" src="${posterUrl(c.profile_path, 'w185')}" alt="">`
                      : `<div class="cast-avatar placeholder">👤</div>`}
                    <div class="cast-name">${escHtml(c.name)}</div>
                    <div class="cast-char">${escHtml(c.character || "未知角色")}</div>
                  </div>
                `).join("")}
              </div>
            </div>` : ""}

          ${d.crew.length ? `
            <div class="detail-section">
              <div class="detail-section-title">🎬 幕后团队</div>
              <div class="crew-list">
                ${d.crew.slice(0, 15).map(c => `
                  <span class="crew-chip" data-person-id="${c.id}">
                    <strong>${escHtml(c.name)}</strong>
                    <span class="crew-chip-role">${escHtml(c.job)}</span>
                  </span>
                `).join("")}
              </div>
            </div>` : ""}

          ${d.seasons.length ? `
            <div class="detail-section">
              <div class="detail-section-title">📺 剧集列表</div>
              <div class="season-tabs">
                ${d.seasons.map(s => `<button class="season-tab${s.season_number === 1 ? ' active' : ''}" data-season="${s.season_number}">${s.name}</button>`).join("")}
              </div>
              <div id="episodeArea" class="episode-list">
                ${renderEpisodes(seasonsDetail && seasonsDetail[0])}
              </div>
            </div>` : ""}

          ${d.similar.length ? `
            <div class="detail-section">
              <div class="detail-section-title">🔗 相似剧集</div>
              <div class="similar-scroll">
                ${d.similar.slice(0, 15).map(s => `
                  <div class="similar-card" data-type="tv" data-id="${s.id}">
                    ${s.poster_path
                      ? `<img src="${posterUrl(s.poster_path, 'w185')}" alt="">`
                      : `<div style="width:140px;height:210px;background:var(--bg-secondary);border-radius:8px;display:flex;align-items:center;justify-content:center;">📺</div>`}
                    <div class="s-title">${escHtml(s.name || s.title)}</div>
                  </div>
                `).join("")}
              </div>
            </div>` : ""}
        </div>
      </div>
    `;

    // Bind events
    els.detailContent.querySelectorAll('[data-person-id]').forEach(el => {
      el.addEventListener("click", () => showDetail("person", el.dataset.personId));
    });
    els.detailContent.querySelectorAll('.similar-card').forEach(el => {
      el.addEventListener("click", () => showDetail(el.dataset.type, parseInt(el.dataset.id)));
    });
    els.detailContent.querySelectorAll('.season-tab').forEach(el => {
      el.addEventListener("click", async function () {
        $$(".season-tab").forEach(t => t.classList.remove("active"));
        this.classList.add("active");
        const season = this.dataset.season;
        $("#episodeArea").innerHTML = '<div class="loading"><div class="spinner"></div></div>';
        try {
          const data = await apiGet("/api/tv/" + d.id + "?season=" + season);
          $("#episodeArea").innerHTML = renderEpisodes(data.seasons_detail?.[0]);
        } catch (e) {
          $("#episodeArea").innerHTML = `<div class="error-msg">❌ ${escHtml(e.message)}</div>`;
        }
      });
    });
  }

  function renderEpisodes(season) {
    if (!season || !season.episodes || !season.episodes.length) {
      return '<div class="empty-msg">暂无剧集信息</div>';
    }
    return season.episodes.map(ep => `
      <div class="episode-item">
        ${ep.still_path
          ? `<img class="episode-still" src="${posterUrl(ep.still_path, 'w300')}" alt="">`
          : `<div class="episode-still placeholder">第${ep.episode_number}集</div>`}
        <div class="episode-info">
          <div class="episode-name">S${season.season_number}E${ep.episode_number} — ${escHtml(ep.name || "无标题")}</div>
          <div class="episode-overview">${escHtml(truncate(ep.overview, 200))}</div>
          <div class="episode-meta">
            ${ep.air_date ? `<span>📅 ${formatDate(ep.air_date)}</span>` : ""}
            ${ep.runtime ? `<span>⏱ ${ep.runtime}分钟</span>` : ""}
            ${ep.vote_average ? `<span>⭐ ${ep.vote_average.toFixed(1)}</span>` : ""}
          </div>
        </div>
      </div>
    `).join("");
  }

  function renderPerson(d, movieCredits) {
    const genderMap = { 0: "未知", 1: "女性", 2: "男性", 3: "非二元" };

    els.detailContent.innerHTML = `
      <div class="detail-page">
        <div class="person-hero">
          ${d.profile_path
            ? `<img class="person-avatar" src="${posterUrl(d.profile_path, 'w500')}" alt="">`
            : `<div class="person-avatar placeholder">👤</div>`}
          <div class="person-main">
            <h1 class="person-name">${escHtml(d.name)}</h1>
            <div class="detail-meta">
              ${d.known_for_department ? `<span class="meta-badge">🏷 ${escHtml(d.known_for_department)}</span>` : ""}
              ${d.birthday ? `<span class="meta-badge">🎂 ${d.birthday}</span>` : ""}
              ${d.place_of_birth ? `<span class="meta-badge">🌍 ${escHtml(d.place_of_birth)}</span>` : ""}
              <span class="meta-badge">${genderMap[d.gender] || "未知"}</span>
            </div>
            ${d.also_known_as?.length ? `<div style="margin-top:8px;color:var(--text-muted);font-size:0.85rem;">又名：${d.also_known_as.map(a => escHtml(a)).join("、")}</div>` : ""}
          </div>
        </div>

        <div class="detail-sections">
          ${d.biography
            ? `<div class="detail-section">
                 <div class="detail-section-title">📝 个人简介</div>
                 <p class="detail-overview">${escHtml(d.biography)}</p>
               </div>` : ""}

          ${movieCredits && movieCredits.length ? `
            <div class="detail-section">
              <div class="detail-section-title">🎬 参演作品（电影）</div>
              <div class="similar-scroll">
                ${movieCredits.slice(0, 20).map(c => `
                  <div class="similar-card" data-type="movie" data-id="${c.id}">
                    ${c.poster_path
                      ? `<img src="${posterUrl(c.poster_path, 'w185')}" alt="">`
                      : `<div style="width:140px;height:210px;background:var(--bg-secondary);border-radius:8px;display:flex;align-items:center;justify-content:center;">🎬</div>`}
                    <div class="s-title">${escHtml(c.title || c.name)}</div>
                  </div>
                `).join("")}
              </div>
            </div>` : ""}
        </div>
      </div>
    `;

    els.detailContent.querySelectorAll('.similar-card').forEach(el => {
      el.addEventListener("click", () => showDetail(el.dataset.type, parseInt(el.dataset.id)));
    });
  }

  // ── Password Auth ──────────────────────────────────────────────

  function showPasswordModal() {
    els.passwordInput.value = "";
    els.passwordError.classList.add("hidden");
    els.passwordModal.classList.remove("hidden");
    setTimeout(() => els.passwordInput.focus(), 100);
  }

  function hidePasswordModal() {
    els.passwordModal.classList.add("hidden");
    els.passwordInput.value = "";
    els.passwordError.classList.add("hidden");
  }

  async function onPasswordConfirm() {
    const pw = els.passwordInput.value;
    if (!pw) {
      els.passwordError.textContent = "请输入密码";
      els.passwordError.classList.remove("hidden");
      return;
    }

    try {
      const resp = await fetch("/api/settings/check-password?admin_password=" + encodeURIComponent(pw));
      const data = await resp.json();
      if (data.ok) {
        // Auth passed — close password modal, open settings
        hidePasswordModal();
        openSettings(true);
      } else {
        els.passwordError.textContent = "❌ 密码错误，请重试";
        els.passwordError.classList.remove("hidden");
        els.passwordInput.value = "";
        els.passwordInput.focus();
      }
    } catch (e) {
      els.passwordError.textContent = "❌ 网络错误，请重试";
      els.passwordError.classList.remove("hidden");
    }
  }

  // ── Settings Modal ─────────────────────────────────────────────

  function openSettings(authenticated) {
    if (!state.settings) { state.settings = { tmdb_api_key: "", language: "zh-CN", proxy: { enabled: false } }; }
    els.setApiKey.value = state.settings.tmdb_api_key || "";
    els.setLang.value = state.settings.language || "zh-CN";
    els.setProxyEnabled.checked = !!state.settings.proxy?.enabled;
    toggleProxyFields();
    els.setProxyProto.value = state.settings.proxy?.protocol || "http";
    els.setProxyHost.value = state.settings.proxy?.host || "";
    els.setProxyPort.value = state.settings.proxy?.port || "";
    els.setProxyUser.value = state.settings.proxy?.username || "";
    els.setProxyPass.value = state.settings.proxy?.password || "";
    els.setPassword.value = "";
    els.testResult.className = "test-result hidden";
    els.settingsModal.classList.remove("hidden");
  }

  function onSettingsOpen() {
    // First check if a password is set
    if (state.settings?.has_password) {
      showPasswordModal();
    } else {
      openSettings(true);
    }
  }

  function closeSettings() {
    els.settingsModal.classList.add("hidden");
    hidePasswordModal();
  }

  function toggleProxyFields() {
    // Always show proxy fields - no-op
  }

  async function saveSettings() {
    const newPassword = els.setPassword.value;

    const settings = {
      tmdb_api_key: els.setApiKey.value.trim(),
      language: els.setLang.value,
      proxy: els.setProxyEnabled.checked
        ? {
            enabled: true,
            protocol: els.setProxyProto.value,
            host: els.setProxyHost.value.trim(),
            port: parseInt(els.setProxyPort.value) || 0,
            username: els.setProxyUser.value.trim(),
            password: els.setProxyPass.value.trim(),
          }
        : { enabled: false },
    };

    // If user wants to change the admin password
    if (newPassword) {
      settings._set_password = newPassword;
    }

    try {
      const resp = await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings),
      });
      const data = await resp.json();
      if (data.ok) {
        state.settings = settings;
        // Refresh has_password state
        try {
          const checkResp = await fetch("/api/settings");
          state.settings.has_password = (await checkResp.json()).has_password;
        } catch (_) {}
        showToast("✅ 设置已保存");
        closeSettings();
      } else {
        showToast("❌ 保存失败: " + (data.detail || "未知错误"), true);
      }
    } catch (e) {
      showToast("❌ 保存失败: " + e.message, true);
    }
  }

  async function testConnection() {
    els.testResult.className = "test-result";
    els.testResult.textContent = "⏳ 测试中...";
    els.testResult.classList.remove("hidden");

    try {
      await loadConfig();
      els.testResult.textContent = "✅ 连接成功！";
      els.testResult.classList.add("success");
      showToast("✅ TMDB 连接正常");
    } catch (e) {
      els.testResult.textContent = "❌ " + e.message;
      els.testResult.classList.add("error");
      showToast("❌ 连接失败: " + e.message, true);
    }
  }

  // ── Navigation ─────────────────────────────────────────────────

  function goHome() {
    els.detailView.classList.add("hidden");
    els.searchView.classList.remove("hidden");
    state.currentView = "search";
    els.searchInput.value = "";
    els.resultGrid.innerHTML = "";
    els.resultError.className = "error-msg hidden";
    els.resultEmpty.className = "empty-msg hidden";
    els.searchInput.focus();
  }

  // ── Init ───────────────────────────────────────────────────────

  function init() {
    loadSettings();

    // Search
    els.searchBtn.addEventListener("click", () => doSearch(els.searchInput.value));
    els.searchInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") doSearch(els.searchInput.value);
    });

    // Navigation
    els.backBtn.addEventListener("click", goHome);

    // Settings
    els.settingsBtn.addEventListener("click", onSettingsOpen);
    els.settingsClose.addEventListener("click", closeSettings);
    els.settingsCancel.addEventListener("click", closeSettings);
    els.settingsSave.addEventListener("click", saveSettings);
    els.setProxyEnabled.addEventListener("change", toggleProxyFields);
    els.testConnection.addEventListener("click", testConnection);
    els.toggleApiKey.addEventListener("click", () => {
      const input = els.setApiKey;
      if (input.type === "password") {
        input.type = "text";
        els.toggleApiKey.textContent = "🙈";
      } else {
        input.type = "password";
        els.toggleApiKey.textContent = "👁️";
      }
    });

    // Password modal
    els.passwordClose.addEventListener("click", hidePasswordModal);
    els.passwordCancel.addEventListener("click", hidePasswordModal);
    els.passwordConfirm.addEventListener("click", onPasswordConfirm);
    els.passwordInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") onPasswordConfirm();
    });

    // Close modals on overlay click
    els.settingsModal.addEventListener("click", (e) => {
      if (e.target === els.settingsModal) closeSettings();
    });
    els.passwordModal.addEventListener("click", (e) => {
      if (e.target === els.passwordModal) hidePasswordModal();
    });

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        if (!els.passwordModal.classList.contains("hidden")) hidePasswordModal();
        else if (!els.settingsModal.classList.contains("hidden")) closeSettings();
        else if (state.currentView === "detail") goHome();
      }
      if (e.key === "/" && document.activeElement !== els.searchInput && document.activeElement !== els.passwordInput) {
        e.preventDefault();
        els.searchInput.focus();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
