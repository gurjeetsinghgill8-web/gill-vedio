/**
 * GILL VEDIO PWA — Main Application
 * Screens: Home | Edit | Ideas | Gallery | Settings
 */

import { openDB, saveVideo, getAllVideos, getVideoStats, deleteVideo, saveIdeas, getAllIdeas } from './db.js';
import { generateIdeas, generateCaption, setApiKey, getApiKey } from './gemini.js';
import { loadFFmpeg, processVideos, applyEffects, isFFmpegLoaded } from './ffmpeg-processor.js';

// ═══════════════════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════════════════
const State = {
  currentScreen: 'home',
  selectedFiles: [],
  processedResult: null,
  generatedIdeas: [],
  selectedIdeas: new Set(),
  currentEffectsBlob: null,
  effects: { brightness: 0, contrast: 0, saturation: 0, speed: 1.0, textOverlay: '' },
  galleryVideos: [],
  installPrompt: null
};

// ═══════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', async () => {
  await openDB();
  initServiceWorker();
  initNav();
  initInstallBanner();
  loadSettings();
  await renderHome();
  navigateTo('home');
});

// ═══════════════════════════════════════════════════════════════
// SERVICE WORKER
// ═══════════════════════════════════════════════════════════════
function initServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./sw.js')
      .then(() => console.log('[SW] Registered'))
      .catch(err => console.warn('[SW] Failed:', err));
  }
}

// ═══════════════════════════════════════════════════════════════
// PWA INSTALL
// ═══════════════════════════════════════════════════════════════
function initInstallBanner() {
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    State.installPrompt = e;
    const banner = document.getElementById('install-banner');
    if (banner) banner.classList.add('show');
  });

  document.getElementById('install-banner')?.addEventListener('click', async () => {
    if (!State.installPrompt) return;
    State.installPrompt.prompt();
    const { outcome } = await State.installPrompt.userChoice;
    if (outcome === 'accepted') {
      document.getElementById('install-banner')?.classList.remove('show');
      showToast('App installed! ✓', 'success');
    }
    State.installPrompt = null;
  });
}

// ═══════════════════════════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════════════════════════
function initNav() {
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => navigateTo(item.dataset.screen));
  });

  // Hash routing
  window.addEventListener('hashchange', () => {
    const hash = location.hash.replace('#', '');
    if (hash) navigateTo(hash);
  });

  const hash = location.hash.replace('#', '');
  if (hash) navigateTo(hash);
}

function navigateTo(screen) {
  State.currentScreen = screen;
  location.hash = screen;

  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(`screen-${screen}`)?.classList.add('active');

  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.toggle('active', item.dataset.screen === screen);
  });

  // Update header title
  const titles = {
    home: '🎬 GILL VEDIO',
    edit: '✂️ Auto-Edit',
    ideas: '💡 Ideas',
    gallery: '📁 Gallery',
    settings: '⚙️ Settings'
  };
  document.getElementById('header-title').textContent = titles[screen] || 'GILL VEDIO';

  // Screen-specific init
  if (screen === 'gallery') renderGallery();
  if (screen === 'home') renderHome();
}

// ═══════════════════════════════════════════════════════════════
// HOME SCREEN
// ═══════════════════════════════════════════════════════════════
async function renderHome() {
  const stats = await getVideoStats();

  document.getElementById('stat-total').textContent = stats.total;
  document.getElementById('stat-processed').textContent = stats.processed;
  document.getElementById('stat-published').textContent = stats.published;
  document.getElementById('stat-today').textContent = stats.today;

  // Recent videos
  const videos = await getAllVideos();
  const recentEl = document.getElementById('recent-videos');
  if (!recentEl) return;

  if (!videos.length) {
    recentEl.innerHTML = `
      <div class="empty-state" style="padding:30px 0">
        <div class="empty-icon">🎬</div>
        <p style="font-size:13px;color:var(--text3)">No videos yet. Upload your first video!</p>
      </div>`;
    return;
  }

  recentEl.innerHTML = videos.slice(0, 6).map(v => `
    <div class="gallery-item" onclick="viewVideo(${v.id})" style="min-width:130px;flex-shrink:0">
      <div class="gallery-thumb">
        <span>🎞️</span>
        <span class="gallery-duration">${formatDuration(v.finalDuration || v.duration || 0)}</span>
        <span class="gallery-status ${v.status}">${v.status}</span>
      </div>
      <div class="gallery-info">
        <div class="gallery-name">${v.name || 'Video'}</div>
        <div class="gallery-meta">${formatDate(v.createdAt)}</div>
      </div>
    </div>
  `).join('');
}

// ═══════════════════════════════════════════════════════════════
// EDIT SCREEN — File Selection
// ═══════════════════════════════════════════════════════════════
function initEditScreen() {
  const fileInput = document.getElementById('file-input');
  const uploadZone = document.getElementById('upload-zone');

  uploadZone?.addEventListener('click', () => fileInput?.click());
  fileInput?.addEventListener('change', (e) => handleFilesSelected(Array.from(e.target.files)));

  // Drag and drop
  uploadZone?.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
  });
  uploadZone?.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
  uploadZone?.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('video/'));
    handleFilesSelected(files);
  });
}

function handleFilesSelected(files) {
  const newFiles = files.filter(f => f.type.startsWith('video/'));
  if (!newFiles.length) { showToast('Please select video files only', 'error'); return; }

  State.selectedFiles = [...State.selectedFiles, ...newFiles];
  State.processedResult = null;
  renderVideoList();
  document.getElementById('process-btn')?.removeAttribute('disabled');

  // Hide success state when new files added
  document.getElementById('success-state')?.classList.add('hidden');
}

function renderVideoList() {
  const list = document.getElementById('video-list');
  if (!list) return;

  if (!State.selectedFiles.length) {
    list.innerHTML = '';
    document.getElementById('process-btn')?.setAttribute('disabled', '');
    return;
  }

  list.innerHTML = State.selectedFiles.map((file, i) => `
    <div class="video-item" id="video-item-${i}">
      <div class="video-thumb">🎞️</div>
      <div class="video-info">
        <div class="video-name">${file.name}</div>
        <div class="video-meta">${formatSize(file.size)} • ${file.type.split('/')[1]?.toUpperCase()}</div>
      </div>
      <button class="video-remove" onclick="removeFile(${i})">✕</button>
    </div>
  `).join('');
}

window.removeFile = function(index) {
  State.selectedFiles.splice(index, 1);
  renderVideoList();
  if (!State.selectedFiles.length) {
    document.getElementById('process-btn')?.setAttribute('disabled', '');
  }
};

// ═══════════════════════════════════════════════════════════════
// PROCESS VIDEOS — Main Feature
// ═══════════════════════════════════════════════════════════════
window.startProcessing = async function() {
  if (!State.selectedFiles.length) { showToast('Select at least one video', 'error'); return; }

  // Show processing state
  document.getElementById('upload-section')?.classList.add('hidden');
  document.getElementById('features-section')?.classList.add('hidden');
  document.getElementById('processing-state')?.classList.remove('hidden');
  document.getElementById('success-state')?.classList.add('hidden');

  try {
    // Load FFmpeg if not loaded
    if (!isFFmpegLoaded()) {
      updateProcessingStep('Loading video engine (first time only)...', 5);
      await loadFFmpeg((p) => updateProcessingStep('Loading engine...', Math.round(p * 20)));
    }

    const result = await processVideos(
      State.selectedFiles,
      (step) => updateProcessingStep(step),
      (p) => updateProcessingProgress(Math.round(20 + p * 75))
    );

    State.processedResult = result;

    // Save to IndexedDB
    const videoId = await saveVideo({
      name: `GillVedio_${Date.now()}.mp4`,
      originalDuration: result.originalDuration,
      finalDuration: result.finalDuration,
      silencesRemoved: result.silencesRemoved,
      savedSeconds: result.savedSeconds,
      sizeBytes: result.sizeBytes,
      status: 'processed',
      blobUrl: result.url
    });

    State.processedResult.videoId = videoId;
    updateProcessingProgress(100);
    showSuccessState(result);

  } catch (err) {
    document.getElementById('processing-state')?.classList.add('hidden');
    document.getElementById('upload-section')?.classList.remove('hidden');
    document.getElementById('features-section')?.classList.remove('hidden');
    showToast(err.message || 'Processing failed', 'error');
    console.error('[Process Error]', err);
  }
};

function updateProcessingStep(text, progress) {
  const el = document.getElementById('processing-step');
  if (el) el.textContent = text;
  if (progress !== undefined) updateProcessingProgress(progress);
}

function updateProcessingProgress(pct) {
  const bar = document.getElementById('proc-progress-bar');
  const txt = document.getElementById('proc-progress-pct');
  if (bar) bar.style.width = `${pct}%`;
  if (txt) txt.textContent = `${pct}%`;
}

function showSuccessState(result) {
  document.getElementById('processing-state')?.classList.add('hidden');
  document.getElementById('success-state')?.classList.remove('hidden');

  document.getElementById('stat-original').textContent = formatDuration(result.originalDuration);
  document.getElementById('stat-final').textContent = formatDuration(result.finalDuration);
  document.getElementById('stat-saved').textContent = formatDuration(result.savedSeconds);
  document.getElementById('stat-pauses').textContent = result.silencesRemoved;

  // Set video preview
  const preview = document.getElementById('result-preview');
  if (preview) { preview.src = result.url; preview.load(); }

  showToast('Video processed successfully! ✓', 'success');
  renderHome();
}

window.previewResult = function() {
  const wrap = document.getElementById('preview-wrap');
  const video = document.getElementById('result-preview');
  if (!wrap || !video) return;
  wrap.classList.toggle('show');
  if (wrap.classList.contains('show')) video.play();
  else video.pause();
};

window.downloadResult = async function() {
  if (!State.processedResult?.url) return;
  const a = document.createElement('a');
  a.href = State.processedResult.url;
  a.download = `GillVedio_${Date.now()}.mp4`;
  a.click();
  showToast('Video saved! ✓', 'success');
};

window.shareResult = async function() {
  if (!State.processedResult?.blob) { showToast('No video to share', 'error'); return; }
  try {
    if (navigator.share) {
      const file = new File([State.processedResult.blob], 'GillVedio.mp4', { type: 'video/mp4' });
      await navigator.share({ title: 'GILL VEDIO', files: [file] });
    } else {
      window.downloadResult();
    }
  } catch(e) {
    if (e.name !== 'AbortError') showToast('Share failed', 'error');
  }
};

window.resetEdit = function() {
  State.selectedFiles = [];
  State.processedResult = null;
  renderVideoList();
  document.getElementById('upload-section')?.classList.remove('hidden');
  document.getElementById('features-section')?.classList.remove('hidden');
  document.getElementById('processing-state')?.classList.add('hidden');
  document.getElementById('success-state')?.classList.add('hidden');
  document.getElementById('preview-wrap')?.classList.remove('show');
  document.getElementById('file-input').value = '';
};

// ═══════════════════════════════════════════════════════════════
// IDEAS SCREEN
// ═══════════════════════════════════════════════════════════════
window.generateVideoIdeas = async function() {
  const topic = document.getElementById('idea-topic')?.value?.trim();
  if (!topic) { showToast('Enter a topic first', 'error'); return; }

  const niche = document.getElementById('idea-niche')?.value || 'Lifestyle';
  const language = document.getElementById('idea-lang')?.value || 'Hindi';
  const platform = document.getElementById('idea-platform')?.value || 'Instagram';
  const apiKey = getApiKey();

  if (!apiKey) { showToast('Add your Gemini API key in Settings first', 'error'); return; }

  // Show loading
  const btn = document.getElementById('generate-ideas-btn');
  if (btn) { btn.disabled = true; btn.textContent = '⏳ Generating...'; }

  const ideasList = document.getElementById('ideas-list');
  if (ideasList) {
    ideasList.innerHTML = `
      <div class="shimmer"></div>
      <div class="shimmer" style="height:80px"></div>
      <div class="shimmer"></div>
    `;
  }

  try {
    const ideas = await generateIdeas({ topic, niche, language, platform });
    State.generatedIdeas = ideas;
    State.selectedIdeas.clear();
    renderIdeas(ideas);
    await saveIdeas(ideas.map(i => ({ ...i, topic })));
    showToast(`${ideas.length} ideas generated! ✓`, 'success');
  } catch (err) {
    if (ideasList) ideasList.innerHTML = `
      <div class="card" style="text-align:center;color:var(--error)">
        <p>⚠️ ${err.message}</p>
      </div>`;
    showToast(err.message, 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = '🚀 Generate 10 Viral Ideas'; }
  }
};

function renderIdeas(ideas) {
  const list = document.getElementById('ideas-list');
  if (!list) return;

  if (!ideas.length) {
    list.innerHTML = '<div class="empty-state"><div class="empty-icon">💡</div><h3>No ideas yet</h3><p>Enter a topic and generate ideas</p></div>';
    return;
  }

  list.innerHTML = ideas.map((idea, i) => `
    <div class="idea-card" id="idea-card-${i}" onclick="toggleIdea(${i})">
      <div class="idea-header">
        <div class="idea-num">${i + 1}</div>
        <div class="idea-title">${idea.title}</div>
        <div class="idea-checkbox" id="idea-check-${i}"></div>
        <div class="idea-score">🔥 ${idea.viral_score}/10</div>
      </div>
      <div class="idea-hook">"${idea.hook}"</div>
      <div class="idea-tags">
        ${(idea.hashtags || []).map(h => `<span class="idea-tag">${h}</span>`).join('')}
      </div>
    </div>
  `).join('');

  updateGenerateBtn();
}

window.toggleIdea = function(index) {
  if (State.selectedIdeas.has(index)) {
    State.selectedIdeas.delete(index);
    document.getElementById(`idea-card-${index}`)?.classList.remove('selected');
    document.getElementById(`idea-check-${index}`)?.removeAttribute('data-checked');
    document.getElementById(`idea-check-${index}`).textContent = '';
  } else {
    State.selectedIdeas.add(index);
    document.getElementById(`idea-card-${index}`)?.classList.add('selected');
    document.getElementById(`idea-check-${index}`).textContent = '✓';
  }
  updateGenerateBtn();
};

function updateGenerateBtn() {
  const btn = document.getElementById('gen-videos-btn');
  if (!btn) return;
  const count = State.selectedIdeas.size;
  btn.textContent = count ? `🎬 Generate Videos (${count} selected)` : '🎬 Generate Videos';
  btn.disabled = count === 0;
}

// ═══════════════════════════════════════════════════════════════
// GALLERY SCREEN
// ═══════════════════════════════════════════════════════════════
async function renderGallery() {
  const grid = document.getElementById('gallery-grid');
  if (!grid) return;

  const videos = await getAllVideos();
  State.galleryVideos = videos;

  if (!videos.length) {
    grid.innerHTML = `
      <div class="empty-state" style="grid-column:1/-1">
        <div class="empty-icon">📁</div>
        <h3>No videos yet</h3>
        <p>Upload and process your first video<br>using the Edit tab</p>
      </div>`;
    return;
  }

  grid.innerHTML = videos.map(v => `
    <div class="gallery-item" onclick="openVideoModal(${v.id})">
      <div class="gallery-thumb">
        <span>🎞️</span>
        <span class="gallery-duration">${formatDuration(v.finalDuration || v.duration || 0)}</span>
        <span class="gallery-status ${v.status}">${v.status}</span>
      </div>
      <div class="gallery-info">
        <div class="gallery-name">${v.name || 'Video'}</div>
        <div class="gallery-meta">${formatDate(v.createdAt)} • ${formatSize(v.sizeBytes)}</div>
      </div>
    </div>
  `).join('');
}

window.openVideoModal = function(id) {
  const video = State.galleryVideos.find(v => v.id === id);
  if (!video) return;

  const modal = document.getElementById('video-modal');
  const overlay = document.getElementById('modal-overlay');
  if (!modal || !overlay) return;

  document.getElementById('modal-title').textContent = video.name || 'Video';
  document.getElementById('modal-video').src = video.blobUrl || '';
  document.getElementById('modal-video-id').value = id;

  const statsEl = document.getElementById('modal-stats');
  if (statsEl) {
    statsEl.innerHTML = `
      <div class="success-stat"><div class="val">${formatDuration(video.originalDuration)}</div><div class="lbl">Original</div></div>
      <div class="success-stat"><div class="val">${formatDuration(video.finalDuration)}</div><div class="lbl">Final</div></div>
      <div class="success-stat"><div class="val">${video.silencesRemoved || 0}</div><div class="lbl">Pauses cut</div></div>
    `;
  }

  overlay.classList.add('show');
};

window.closeModal = function() {
  document.getElementById('modal-overlay')?.classList.remove('show');
  document.getElementById('modal-video')?.pause();
};

window.deleteCurrentVideo = async function() {
  const id = parseInt(document.getElementById('modal-video-id')?.value);
  if (!id) return;
  if (!confirm('Delete this video?')) return;

  await deleteVideo(id);
  closeModal();
  renderGallery();
  showToast('Video deleted', 'success');
};

window.shareCurrentVideo = async function() {
  const video = document.getElementById('modal-video');
  if (!video?.src) return;
  try {
    const res = await fetch(video.src);
    const blob = await res.blob();
    const file = new File([blob], 'GillVedio.mp4', { type: 'video/mp4' });
    if (navigator.share && navigator.canShare({ files: [file] })) {
      await navigator.share({ title: 'GILL VEDIO', files: [file] });
    } else {
      const a = document.createElement('a');
      a.href = video.src;
      a.download = 'GillVedio.mp4';
      a.click();
    }
  } catch(e) {
    if (e.name !== 'AbortError') showToast('Share failed', 'error');
  }
};

window.viewVideo = function(id) {
  navigateTo('gallery');
  setTimeout(() => openVideoModal(id), 300);
};

// ═══════════════════════════════════════════════════════════════
// EFFECTS SCREEN
// ═══════════════════════════════════════════════════════════════
window.switchEffectsTab = function(tab) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelector(`[data-tab="${tab}"]`)?.classList.add('active');
  document.querySelectorAll('.effects-panel').forEach(p => p.classList.add('hidden'));
  document.getElementById(`effects-${tab}`)?.classList.remove('hidden');
};

window.updateEffect = function(key, value) {
  State.effects[key] = parseFloat(value);
  const display = document.getElementById(`${key}-val`);
  if (display) display.textContent = value;
};

window.setSpeed = function(speed) {
  State.effects.speed = parseFloat(speed);
  document.querySelectorAll('.speed-btn').forEach(b => {
    b.classList.toggle('active', parseFloat(b.dataset.speed) === State.effects.speed);
  });
};

window.applyAllEffects = async function() {
  if (!State.processedResult?.blob) {
    showToast('Process a video first', 'error');
    return;
  }

  const btn = document.getElementById('apply-effects-btn');
  if (btn) { btn.disabled = true; btn.textContent = '⏳ Applying...'; }

  try {
    const result = await applyEffects(
      State.processedResult.blob,
      State.effects,
      (step) => console.log('[Effects]', step)
    );

    State.processedResult.blob = result.blob;
    State.processedResult.url = result.url;

    const preview = document.getElementById('effects-preview');
    if (preview) { preview.src = result.url; preview.load(); }

    showToast('Effects applied! ✓', 'success');
  } catch (err) {
    showToast(err.message || 'Effects failed', 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = '✅ Apply All Effects'; }
  }
};

// ═══════════════════════════════════════════════════════════════
// SETTINGS SCREEN
// ═══════════════════════════════════════════════════════════════
function loadSettings() {
  const key = localStorage.getItem('gill_gemini_key') || '';
  const nameEl = document.getElementById('setting-name');
  const nicheEl = document.getElementById('setting-niche');
  const keyEl = document.getElementById('setting-apikey');
  const thresholdEl = document.getElementById('setting-threshold');

  if (nameEl) nameEl.value = localStorage.getItem('gill_name') || '';
  if (nicheEl) nicheEl.value = localStorage.getItem('gill_niche') || 'Lifestyle';
  if (keyEl) keyEl.value = key;
  if (thresholdEl) thresholdEl.value = localStorage.getItem('gill_threshold') || '-30';

  if (key) setApiKey(key);
}

window.saveSettings = function() {
  const name = document.getElementById('setting-name')?.value || '';
  const niche = document.getElementById('setting-niche')?.value || '';
  const apiKey = document.getElementById('setting-apikey')?.value?.trim() || '';
  const threshold = document.getElementById('setting-threshold')?.value || '-30';

  localStorage.setItem('gill_name', name);
  localStorage.setItem('gill_niche', niche);
  localStorage.setItem('gill_gemini_key', apiKey);
  localStorage.setItem('gill_threshold', threshold);

  if (apiKey) setApiKey(apiKey);

  showToast('Settings saved! ✓', 'success');
};

window.clearCache = async function() {
  if (!confirm('Clear all cached data?')) return;
  const cacheNames = await caches.keys();
  await Promise.all(cacheNames.map(name => caches.delete(name)));
  showToast('Cache cleared ✓', 'success');
};

window.togglePassword = function(inputId) {
  const input = document.getElementById(inputId);
  if (!input) return;
  input.type = input.type === 'password' ? 'text' : 'password';
};

// ═══════════════════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════════════════
function formatDuration(seconds) {
  if (!seconds || isNaN(seconds)) return '0:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function formatSize(bytes) {
  if (!bytes) return '0 B';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function formatDate(ts) {
  if (!ts) return '';
  return new Date(ts).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}

let toastTimer = null;
function showToast(message, type = '') {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.className = `show ${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show', type), 3000);
}

// Make showToast global for inline use
window.showToast = showToast;

// Init edit screen when tab is clicked
document.querySelector('[data-screen="edit"]')?.addEventListener('click', () => {
  setTimeout(initEditScreen, 100);
});

// Init on load too
initEditScreen();
