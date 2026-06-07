/**
 * GILL VEDIO PWA — FFmpeg Video Processor
 * Runs FFmpeg entirely in-browser using WebAssembly
 * NO internet needed for video processing
 */

import { FFmpeg } from 'https://cdn.jsdelivr.net/npm/@ffmpeg/ffmpeg@0.12.10/dist/esm/index.js';
import { fetchFile, toBlobURL } from 'https://cdn.jsdelivr.net/npm/@ffmpeg/util@0.12.1/dist/esm/index.js';

let ffmpeg = null;
let isLoaded = false;

// ─── LOAD FFMPEG ──────────────────────────────────────────────
export async function loadFFmpeg(onProgress) {
  if (isLoaded) return;

  ffmpeg = new FFmpeg();

  ffmpeg.on('log', ({ message }) => {
    console.log('[FFmpeg]', message);
  });

  ffmpeg.on('progress', ({ progress }) => {
    if (onProgress) onProgress(progress);
  });

  const baseURL = 'https://cdn.jsdelivr.net/npm/@ffmpeg/core@0.12.6/dist/esm';

  await ffmpeg.load({
    coreURL: await toBlobURL(`${baseURL}/ffmpeg-core.js`, 'text/javascript'),
    wasmURL: await toBlobURL(`${baseURL}/ffmpeg-core.wasm`, 'application/wasm'),
  });

  isLoaded = true;
  console.log('[FFmpeg] Loaded successfully');
}

/**
 * ─── DETECT SILENCE ──────────────────────────────────────────
 * Analyzes audio track for silent segments
 * Returns array of {start, end} objects (in seconds)
 * threshold: -30dB | minDuration: 0.5s
 */
export async function detectSilence(inputFile, threshold = -30, minDuration = 0.5) {
  if (!isLoaded) throw new Error('FFmpeg not loaded');

  const inputName = 'input_detect.mp4';
  await ffmpeg.writeFile(inputName, await fetchFile(inputFile));

  const logs = [];
  const logHandler = ({ message }) => logs.push(message);
  ffmpeg.on('log', logHandler);

  try {
    await ffmpeg.exec([
      '-i', inputName,
      '-af', `silencedetect=noise=${threshold}dB:d=${minDuration}`,
      '-f', 'null',
      '-'
    ]);
  } catch (e) {
    // silencedetect outputs to stderr which FFmpeg treats as non-zero exit — that's OK
  }

  ffmpeg.off('log', logHandler);
  await ffmpeg.deleteFile(inputName);

  // Parse silence segments from logs
  const silences = [];
  let currentStart = null;

  for (const log of logs) {
    const startMatch = log.match(/silence_start:\s*([\d.]+)/);
    const endMatch = log.match(/silence_end:\s*([\d.]+)/);

    if (startMatch) currentStart = parseFloat(startMatch[1]);
    if (endMatch && currentStart !== null) {
      const end = parseFloat(endMatch[1]);
      if (end > currentStart) {
        silences.push({ start: currentStart, end });
      }
      currentStart = null;
    }
  }

  return silences;
}

/**
 * ─── GET VIDEO DURATION ──────────────────────────────────────
 * Returns duration in seconds
 */
export async function getVideoDuration(inputFile) {
  if (!isLoaded) throw new Error('FFmpeg not loaded');

  const inputName = 'input_dur.mp4';
  await ffmpeg.writeFile(inputName, await fetchFile(inputFile));

  let duration = 0;
  const logHandler = ({ message }) => {
    const m = message.match(/Duration:\s*(\d+):(\d+):([\d.]+)/);
    if (m) {
      duration = parseInt(m[1]) * 3600 + parseInt(m[2]) * 60 + parseFloat(m[3]);
    }
  };
  ffmpeg.on('log', logHandler);

  try {
    await ffmpeg.exec(['-i', inputName, '-f', 'null', '-']);
  } catch (e) { /* expected */ }

  ffmpeg.off('log', logHandler);
  await ffmpeg.deleteFile(inputName);
  return duration;
}

/**
 * ─── BUILD KEEP SEGMENTS ─────────────────────────────────────
 * Inverts silence list to get speaking parts to KEEP
 */
function buildKeepSegments(silences, totalDuration) {
  if (!silences.length) return [{ start: 0, end: totalDuration }];

  const segments = [];
  let cursor = 0;

  for (const { start, end } of silences) {
    if (start > cursor + 0.05) {
      segments.push({ start: cursor, end: start });
    }
    cursor = end;
  }

  if (cursor < totalDuration - 0.05) {
    segments.push({ start: cursor, end: totalDuration });
  }

  return segments;
}

/**
 * ─── REMOVE PAUSES FROM SINGLE VIDEO ────────────────────────
 * Cuts out silent parts and returns a cleaned Blob
 */
async function removeVideoSilence(inputFile, inputName, outputName, onStep) {
  // Write input
  await ffmpeg.writeFile(inputName, await fetchFile(inputFile));

  if (onStep) onStep('Detecting pauses...');

  // Detect silence
  const silences = await detectSilence(inputFile);
  const duration = await getVideoDuration(inputFile);

  if (onStep) onStep(`Found ${silences.length} pause(s). Cutting...`);

  const keepSegments = buildKeepSegments(silences, duration);

  if (keepSegments.length <= 1 && !silences.length) {
    // No silences — return original
    if (onStep) onStep('No pauses found. Using original.');
    return { outputName: inputName, duration, silencesRemoved: 0 };
  }

  // Build filter_complex for trimming
  const videoFilters = keepSegments.map((s, i) =>
    `[0:v]trim=start=${s.start.toFixed(3)}:end=${s.end.toFixed(3)},setpts=PTS-STARTPTS[v${i}]`
  );
  const audioFilters = keepSegments.map((s, i) =>
    `[0:a]atrim=start=${s.start.toFixed(3)}:end=${s.end.toFixed(3)},asetpts=PTS-STARTPTS[a${i}]`
  );

  const concatInputs = keepSegments.map((_, i) => `[v${i}][a${i}]`).join('');
  const filterComplex = [
    ...videoFilters,
    ...audioFilters,
    `${concatInputs}concat=n=${keepSegments.length}:v=1:a=1[outv][outa]`
  ].join(';');

  if (onStep) onStep('Merging speech segments...');

  await ffmpeg.exec([
    '-i', inputName,
    '-filter_complex', filterComplex,
    '-map', '[outv]',
    '-map', '[outa]',
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-crf', '23',
    '-c:a', 'aac',
    '-b:a', '128k',
    outputName, '-y'
  ]);

  const originalDuration = duration;
  const cleanedDuration = keepSegments.reduce((sum, s) => sum + (s.end - s.start), 0);

  return {
    outputName,
    originalDuration,
    cleanedDuration,
    silencesRemoved: silences.length,
    savedSeconds: originalDuration - cleanedDuration
  };
}

/**
 * ─── MAIN EXPORT: PROCESS VIDEOS ─────────────────────────────
 * Takes array of File objects
 * Returns: { blob, originalDuration, finalDuration, silencesRemoved }
 */
export async function processVideos(files, onStep, onProgress) {
  if (!isLoaded) await loadFFmpeg(onProgress);

  const processedFiles = [];
  let totalOriginal = 0;
  let totalFinal = 0;
  let totalSilences = 0;

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const inputName = `input_${i}.mp4`;
    const outputName = `cleaned_${i}.mp4`;

    if (onStep) onStep(`Processing video ${i + 1} of ${files.length}...`);
    if (onProgress) onProgress((i / files.length) * 0.7);

    const result = await removeVideoSilence(
      file, inputName, outputName,
      (msg) => { if (onStep) onStep(`Video ${i+1}: ${msg}`); }
    );

    processedFiles.push(result.outputName);
    totalOriginal += result.originalDuration || 0;
    totalFinal += result.cleanedDuration || result.originalDuration || 0;
    totalSilences += result.silencesRemoved || 0;

    // Clean up input
    try { await ffmpeg.deleteFile(inputName); } catch(e) {}
  }

  let finalOutputName = 'final_output.mp4';

  if (processedFiles.length === 1) {
    // Single video — just rename
    if (onStep) onStep('Finalizing video...');
    if (onProgress) onProgress(0.9);

    // Copy cleaned to final
    const data = await ffmpeg.readFile(processedFiles[0]);
    await ffmpeg.writeFile(finalOutputName, data);

  } else {
    // Multiple videos — concatenate
    if (onStep) onStep(`Merging ${processedFiles.length} videos into one final video...`);
    if (onProgress) onProgress(0.85);

    // Create concat list
    const concatList = processedFiles.map(f => `file '${f}'`).join('\n');
    await ffmpeg.writeFile('concat_list.txt', concatList);

    await ffmpeg.exec([
      '-f', 'concat',
      '-safe', '0',
      '-i', 'concat_list.txt',
      '-c:v', 'libx264',
      '-preset', 'fast',
      '-crf', '23',
      '-c:a', 'aac',
      '-b:a', '128k',
      finalOutputName, '-y'
    ]);

    // Cleanup
    try { await ffmpeg.deleteFile('concat_list.txt'); } catch(e) {}
    for (const f of processedFiles) {
      try { await ffmpeg.deleteFile(f); } catch(e) {}
    }
  }

  if (onStep) onStep('Reading output file...');
  if (onProgress) onProgress(0.97);

  // Read final output
  const outputData = await ffmpeg.readFile(finalOutputName);
  const blob = new Blob([outputData.buffer], { type: 'video/mp4' });

  // Cleanup
  try { await ffmpeg.deleteFile(finalOutputName); } catch(e) {}

  if (onProgress) onProgress(1);

  return {
    blob,
    url: URL.createObjectURL(blob),
    originalDuration: totalOriginal,
    finalDuration: totalFinal,
    silencesRemoved: totalSilences,
    savedSeconds: totalOriginal - totalFinal,
    sizeBytes: blob.size
  };
}

/**
 * ─── APPLY EFFECTS ───────────────────────────────────────────
 * Applies brightness/contrast/saturation + speed + text
 */
export async function applyEffects(inputFile, effects, onStep) {
  if (!isLoaded) await loadFFmpeg();

  const inputName = 'effects_input.mp4';
  const outputName = 'effects_output.mp4';

  await ffmpeg.writeFile(inputName, await fetchFile(inputFile));

  if (onStep) onStep('Applying effects...');

  const { brightness = 0, contrast = 0, saturation = 0, speed = 1.0, textOverlay = '' } = effects;

  const filters = [];

  // Color correction
  if (brightness !== 0 || contrast !== 0 || saturation !== 0) {
    const b = (brightness / 100).toFixed(2);
    const c = (1 + contrast / 100).toFixed(2);
    const s = (1 + saturation / 100).toFixed(2);
    filters.push(`eq=brightness=${b}:contrast=${c}:saturation=${s}`);
  }

  // Speed
  if (speed !== 1.0) {
    const pts = (1 / speed).toFixed(3);
    filters.push(`setpts=${pts}*PTS`);
  }

  // Text overlay
  if (textOverlay.trim()) {
    const safe = textOverlay.replace(/'/g, "\\'");
    filters.push(`drawtext=text='${safe}':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=h-80:box=1:boxcolor=black@0.5:boxborderw=8`);
  }

  const vfStr = filters.length ? filters.join(',') : 'copy';

  const audioFilters = [];
  if (speed !== 1.0) {
    // atempo only works between 0.5 and 2.0
    const clampedSpeed = Math.min(2.0, Math.max(0.5, speed));
    audioFilters.push(`atempo=${clampedSpeed.toFixed(2)}`);
  }
  const afStr = audioFilters.length ? audioFilters.join(',') : 'acopy';

  await ffmpeg.exec([
    '-i', inputName,
    '-vf', vfStr,
    '-af', afStr,
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-crf', '23',
    '-c:a', 'aac',
    '-b:a', '128k',
    outputName, '-y'
  ]);

  const outputData = await ffmpeg.readFile(outputName);
  const blob = new Blob([outputData.buffer], { type: 'video/mp4' });

  await ffmpeg.deleteFile(inputName);
  await ffmpeg.deleteFile(outputName);

  return { blob, url: URL.createObjectURL(blob) };
}

export function isFFmpegLoaded() {
  return isLoaded;
}
