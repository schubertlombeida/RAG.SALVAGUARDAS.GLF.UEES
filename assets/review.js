"use strict";
(() => {
  const catalog = JSON.parse(document.getElementById("document-catalog").textContent);
  const views = { documentacion: document.getElementById("documentation-view"), reader: document.getElementById("reader-view"), portal: document.getElementById("portal-view") };
  const normalize = (text) => text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const index = catalog.map(doc => ({ ...doc, searchable: normalize(doc.title + " " + doc.description + " " + doc.text) }));
  const search = document.getElementById("document-search");
  function filter() {
    const terms = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
    let count = 0;
    index.forEach(doc => {
      const visible = terms.every(term => doc.searchable.includes(term));
      document.querySelector(`[data-card="${doc.id}"]`).hidden = !visible;
      if (visible) count++;
    });
    document.getElementById("search-status").textContent = terms.length ? `${count} de 7 informes coinciden con la búsqueda` : "7 informes disponibles";
    document.getElementById("no-results").hidden = count !== 0;
  }
  search.addEventListener("input", filter);
  search.form.addEventListener("submit", event => event.preventDefault());
  search.form.addEventListener("reset", () => { search.value = ""; filter(); search.focus(); });
  function route(moveFocus = true) {
    const hash = location.hash.slice(1);
    const doc = hash.startsWith("informe=") ? catalog.find(item => item.id === hash.slice(8)) : null;
    const name = doc ? "reader" : hash === "portal" ? "portal" : "documentacion";
    if (name !== "documentacion" && !views.documentacion.hidden) {
      document.querySelectorAll(".video-player").forEach(player => { player.src = player.src; });
      document.querySelectorAll(".video-card video").forEach(player => player.pause());
    }
    Object.entries(views).forEach(([key, element]) => element.hidden = key !== name);
    document.querySelectorAll("[data-main]").forEach(link => {
      if (link.dataset.main === (name === "reader" ? "documentacion" : name)) link.setAttribute("aria-current", "page"); else link.removeAttribute("aria-current");
    });
    document.querySelectorAll("[data-report]").forEach(el => el.hidden = el.dataset.report !== doc?.id);
    document.querySelectorAll("[data-outline]").forEach(el => {
      if (el.dataset.outline === doc?.id) el.setAttribute("aria-current", "page"); else el.removeAttribute("aria-current");
    });
    document.title = doc ? `${doc.title} · RAG GLF` : name === "portal" ? "Portal GLF · Asistente RAG" : "RAG de salvaguardas GLF · Grupo 10";
    if (doc) {
      const position = catalog.indexOf(doc), previous = document.getElementById("previous-report"), next = document.getElementById("next-report");
      previous.href = position ? `#informe=${catalog[position-1].id}` : "#documentacion";
      previous.textContent = position ? `← ${catalog[position-1].title}` : "← Todos los informes";
      next.href = position < catalog.length-1 ? `#informe=${catalog[position+1].id}` : "#portal";
      next.textContent = position < catalog.length-1 ? `${catalog[position+1].title} →` : "Explorar el portal GLF →";
    }
    if (moveFocus) {
      const videoTarget = hash === "videos" && !document.getElementById("video-section").hidden;
      const target = videoTarget ? document.getElementById("video-title") : doc ? document.querySelector(`#report-${doc.id} h2`) : views[name].querySelector("h1");
      target.setAttribute("tabindex", "-1"); target.focus({ preventScroll: true });
      if (videoTarget) target.scrollIntoView({ behavior: "instant", block: "start" });
      else window.scrollTo({ top: 0, behavior: "instant" });
    }
  }
  window.addEventListener("hashchange", () => route());
  document.querySelectorAll("[data-print]").forEach(button => button.addEventListener("click", () => window.print()));
  function videoURL(value) {
    if (typeof value !== "string" || !value.trim()) return null;
    try {
      const url = new URL(value, location.href);
      const localPath = !/^[a-z][a-z\d+.-]*:/i.test(value) && !value.startsWith("//") && !value.startsWith("/") && !value.includes("..");
      return url.protocol === "https:" || (localPath && /\.mp4$/i.test(url.pathname)) ? url : null;
    } catch { return null; }
  }
  const videos = (Array.isArray(window.GLF_REVIEW_VIDEOS) ? window.GLF_REVIEW_VIDEOS : []).filter(item => videoURL(item.url));
  if (videos.length) {
    document.getElementById("video-section").hidden = false;
    const container = document.getElementById("video-cards");
    videos.forEach(item => {
      const url = videoURL(item.url), card = document.createElement("article"), title = document.createElement("h3"), desc = document.createElement("p"), link = document.createElement("a"), actions = document.createElement("div");
      card.className = "video-card"; title.textContent = item.title; desc.textContent = item.description;
      const youtubeId = url.hostname === "youtu.be" ? url.pathname.slice(1) : ["youtube.com", "www.youtube.com"].includes(url.hostname) ? url.searchParams.get("v") : null;
      const isYouTube = /^[\w-]{11}$/.test(youtubeId || "");
      link.href = url.href; link.className = "button secondary"; link.target = "_blank"; link.rel = "noopener noreferrer"; link.textContent = `${isYouTube ? "Ver en YouTube" : "Ver video"}${item.duration ? " · " + item.duration : ""} ↗`;
      link.setAttribute("aria-label", `${link.textContent}: ${item.title}`);
      actions.className = "video-actions";
      card.append(title, desc);
      if (isYouTube) {
        const player = document.createElement("iframe");
        player.className = "video-player";
        player.src = `https://www.youtube-nocookie.com/embed/${youtubeId}`;
        player.title = `Reproducir ${item.title}`;
        player.loading = "lazy";
        player.referrerPolicy = "strict-origin-when-cross-origin";
        player.allow = "encrypted-media; picture-in-picture; fullscreen";
        player.allowFullscreen = true;
        card.append(player);
      }
      if (/\.mp4$/i.test(url.pathname)) {
        const video = document.createElement("video"); video.controls = true; video.preload = "none"; video.src = url.href; video.setAttribute("aria-label", item.title); video.textContent = "Utilice el enlace Ver video para abrir la grabación."; card.append(video);
      }
      actions.append(link);
      const downloadURL = videoURL(item.downloadUrl);
      if (downloadURL) {
        const download = document.createElement("a"), detail = document.createElement("small");
        download.href = downloadURL.href;
        download.className = "button primary video-download";
        download.textContent = "Descargar desde GitHub";
        download.setAttribute("aria-label", `Descargar ${item.title} desde GitHub${item.downloadLabel ? ": " + item.downloadLabel : ""}`);
        detail.textContent = item.downloadLabel || "Archivo MP4";
        download.append(detail);
        actions.append(download);
      }
      card.append(actions);
      container.append(card);
    });
  }
  route(location.hash === "#videos");
})();
