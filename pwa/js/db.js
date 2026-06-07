/**
 * GILL VEDIO PWA — IndexedDB Manager
 * Stores videos, ideas, and publish logs locally
 */

const DB_NAME = 'GillVedioDB';
const DB_VERSION = 1;

let db = null;

export async function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (e) => {
      const db = e.target.result;

      // Videos store
      if (!db.objectStoreNames.contains('videos')) {
        const vs = db.createObjectStore('videos', { keyPath: 'id', autoIncrement: true });
        vs.createIndex('status', 'status');
        vs.createIndex('createdAt', 'createdAt');
      }

      // Ideas store
      if (!db.objectStoreNames.contains('ideas')) {
        const is = db.createObjectStore('ideas', { keyPath: 'id', autoIncrement: true });
        is.createIndex('topic', 'topic');
        is.createIndex('createdAt', 'createdAt');
      }

      // Publish logs
      if (!db.objectStoreNames.contains('publish_logs')) {
        db.createObjectStore('publish_logs', { keyPath: 'id', autoIncrement: true });
      }
    };

    request.onsuccess = (e) => { db = e.target.result; resolve(db); };
    request.onerror = () => reject(request.error);
  });
}

// ─── VIDEO CRUD ──────────────────────────────────────────────
export async function saveVideo(videoData) {
  const database = db || await openDB();
  return new Promise((resolve, reject) => {
    const tx = database.transaction('videos', 'readwrite');
    const req = tx.objectStore('videos').add({
      ...videoData,
      createdAt: Date.now()
    });
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

export async function getAllVideos() {
  const database = db || await openDB();
  return new Promise((resolve, reject) => {
    const tx = database.transaction('videos', 'readonly');
    const req = tx.objectStore('videos').getAll();
    req.onsuccess = () => resolve(req.result.reverse());
    req.onerror = () => reject(req.error);
  });
}

export async function getVideo(id) {
  const database = db || await openDB();
  return new Promise((resolve, reject) => {
    const tx = database.transaction('videos', 'readonly');
    const req = tx.objectStore('videos').get(id);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

export async function deleteVideo(id) {
  const database = db || await openDB();
  return new Promise((resolve, reject) => {
    const tx = database.transaction('videos', 'readwrite');
    const req = tx.objectStore('videos').delete(id);
    req.onsuccess = () => resolve(true);
    req.onerror = () => reject(req.error);
  });
}

export async function getVideoStats() {
  const videos = await getAllVideos();
  return {
    total: videos.length,
    processed: videos.filter(v => v.status === 'processed').length,
    published: videos.filter(v => v.status === 'published').length,
    today: videos.filter(v => {
      const d = new Date(v.createdAt);
      const now = new Date();
      return d.toDateString() === now.toDateString();
    }).length
  };
}

// ─── IDEAS CRUD ──────────────────────────────────────────────
export async function saveIdeas(ideas) {
  const database = db || await openDB();
  return new Promise((resolve, reject) => {
    const tx = database.transaction('ideas', 'readwrite');
    const store = tx.objectStore('ideas');
    let lastId = null;
    ideas.forEach(idea => {
      const req = store.add({ ...idea, createdAt: Date.now() });
      req.onsuccess = (e) => { lastId = e.target.result; };
    });
    tx.oncomplete = () => resolve(lastId);
    tx.onerror = () => reject(tx.error);
  });
}

export async function getAllIdeas() {
  const database = db || await openDB();
  return new Promise((resolve, reject) => {
    const tx = database.transaction('ideas', 'readonly');
    const req = tx.objectStore('ideas').getAll();
    req.onsuccess = () => resolve(req.result.reverse());
    req.onerror = () => reject(req.error);
  });
}
