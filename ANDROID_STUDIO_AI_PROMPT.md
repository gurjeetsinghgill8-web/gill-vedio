# 🤖 ANDROID STUDIO AI — COMPLETE PROMPT FOR GILL VEDIO ANDROID APP
## (Copy this ENTIRE document and paste it into Android Studio Gemini AI Chat)

---

## ⚠️ HOW TO USE THIS PROMPT
1. Open **Android Studio** (latest version — Meerkat or newer)
2. Click **"Gemini"** panel on the right side (or press `Alt+G`)
3. Copy everything below the "--- START COPY HERE ---" line
4. Paste it into the Gemini chat box
5. Press Enter and let Gemini generate all files for you

---

--- START COPY HERE ---

# 🎬 BUILD REQUEST: GILL VEDIO — AI Video Creator Android App

I need you to build a **complete, production-ready Android application** called **"GILL VEDIO"**. This is a professional AI-powered video creation and social media automation app. Build everything from scratch with full code — no placeholders, no TODOs, no incomplete functions.

---

## PART 1: PROJECT SETUP

### App Details
- **App Name:** GILL VEDIO
- **Package Name:** com.gillvedio.app
- **Min SDK:** API 26 (Android 8.0)
- **Target SDK:** API 35 (Android 15)
- **Language:** Kotlin
- **Architecture:** MVVM + Clean Architecture + Repository Pattern
- **UI Framework:** Jetpack Compose (Material Design 3)
- **Build System:** Gradle (Kotlin DSL — build.gradle.kts)

### Required Dependencies (add ALL to build.gradle.kts)

```kotlin
// Core
implementation("androidx.core:core-ktx:1.13.1")
implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.3")
implementation("androidx.activity:activity-compose:1.9.0")

// Compose BOM
implementation(platform("androidx.compose:compose-bom:2024.06.00"))
implementation("androidx.compose.ui:ui")
implementation("androidx.compose.ui:ui-graphics")
implementation("androidx.compose.material3:material3")
implementation("androidx.compose.material:material-icons-extended")

// Navigation
implementation("androidx.navigation:navigation-compose:2.7.7")

// ViewModel
implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.3")

// Room Database
implementation("androidx.room:room-runtime:2.6.1")
implementation("androidx.room:room-ktx:2.6.1")
kapt("androidx.room:room-compiler:2.6.1")

// Retrofit + OkHttp
implementation("com.squareup.retrofit2:retrofit:2.11.0")
implementation("com.squareup.retrofit2:converter-gson:2.11.0")
implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

// Coroutines
implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.1")

// Coil (Image loading)
implementation("io.coil-kt:coil-compose:2.6.0")

// ExoPlayer (Video playback)
implementation("androidx.media3:media3-exoplayer:1.3.1")
implementation("androidx.media3:media3-ui:1.3.1")

// WorkManager (Background processing)
implementation("androidx.work:work-runtime-ktx:2.9.0")

// DataStore (Preferences)
implementation("androidx.datastore:datastore-preferences:1.1.1")

// Security (Encrypted SharedPreferences)
implementation("androidx.security:security-crypto:1.1.0-alpha06")

// Lottie (Animations)
implementation("com.airbnb.android:lottie-compose:6.4.0")

// Splash Screen
implementation("androidx.core:core-splashscreen:1.0.1")

// FFmpeg Kit (Video Processing - LOCAL on-device, no internet)
implementation("com.arthenica:ffmpeg-kit-full:6.0-2")

// Google AI SDK (Gemini)
implementation("com.google.ai.client.generativeai:generativeai:0.9.0")

// In-App Review (Google Play)
implementation("com.google.android.play:review-ktx:2.0.1")
```

---

## PART 2: COMPLETE FILE STRUCTURE

Create this EXACT directory structure:

```
app/src/main/
├── AndroidManifest.xml
├── java/com/gillvedio/app/
│   ├── MainActivity.kt
│   ├── GillVedioApp.kt
│   │
│   ├── data/
│   │   ├── local/
│   │   │   ├── AppDatabase.kt
│   │   │   ├── dao/VideoDao.kt
│   │   │   ├── dao/IdeaDao.kt
│   │   │   ├── dao/PublishLogDao.kt
│   │   │   ├── entities/VideoEntity.kt
│   │   │   ├── entities/IdeaEntity.kt
│   │   │   └── entities/PublishLogEntity.kt
│   │   ├── remote/GeminiApiService.kt
│   │   └── repository/VideoRepository.kt
│   │
│   ├── domain/
│   │   ├── model/Video.kt
│   │   ├── model/VideoIdea.kt
│   │   └── usecase/ProcessVideoUseCase.kt
│   │
│   ├── presentation/
│   │   ├── navigation/NavGraph.kt
│   │   ├── navigation/Screen.kt
│   │   ├── screens/home/HomeScreen.kt
│   │   ├── screens/home/HomeViewModel.kt
│   │   ├── screens/ideas/IdeaGeneratorScreen.kt
│   │   ├── screens/ideas/IdeaGeneratorViewModel.kt
│   │   ├── screens/videoedit/VideoEditScreen.kt
│   │   ├── screens/videoedit/VideoEditViewModel.kt
│   │   ├── screens/videoflow/VideoFlowScreen.kt
│   │   ├── screens/videoflow/VideoFlowViewModel.kt
│   │   ├── screens/gallery/GalleryScreen.kt
│   │   ├── screens/gallery/GalleryViewModel.kt
│   │   ├── screens/publish/PublishScreen.kt
│   │   ├── screens/publish/PublishViewModel.kt
│   │   └── screens/settings/SettingsScreen.kt
│   │
│   ├── service/VideoProcessingWorker.kt
│   └── utils/Constants.kt
│
└── res/
    ├── values/strings.xml
    ├── values/themes.xml
    └── xml/file_paths.xml
```

---

## PART 3: ANDROIDMANIFEST.XML

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />
    <uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"
        android:maxSdkVersion="28" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"
        android:maxSdkVersion="32" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />

    <application
        android:name=".GillVedioApp"
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.GillVedio"
        android:largeHeap="true">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.GillVedio.SplashScreen">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service
            android:name=".service.VideoProcessingService"
            android:enabled="true"
            android:exported="false"
            android:foregroundServiceType="dataSync" />

        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>

    </application>
</manifest>
```

---

## PART 4: THEME — PREMIUM DARK MODE

File: ui/theme/Theme.kt

Build a premium dark theme with these EXACT colors:
- Background: #0A0A0F (deep space black)
- Surface: #13131A
- Primary: #7C4DFF (electric purple)
- Secondary: #FF6B35 (fire orange)
- Tertiary/Accent: #00E5FF (cyan glow)
- OnPrimary: #FFFFFF
- Error: #FF4444
- Success: #00E676

Apply gradient backgrounds throughout using Brush.verticalGradient from #0A0A0F to #1A0A2E.
Apply glassmorphism effect on all cards: semi-transparent background + subtle purple/cyan border stroke.
Use Google Font "Inter" or "Outfit" for typography.
Add subtle animations on button presses (scale 0.95 on press, spring animation back to 1.0).

---

## PART 5: HOME SCREEN — HomeScreen.kt

Build the home dashboard:

Layout description:
- Top App Bar with "GILL VEDIO" title and gradient background, settings icon on right
- Quick Stats glass card: Total Videos, Published, Pending, Today count
- Quick Actions section with 4 animated buttons (Upload Video, Auto-Edit, Generate Ideas, Publish)
- Recent Videos horizontal scroll with thumbnail cards
- Animated floating action button at bottom right

Technical requirements:
- Use LazyColumn for main scroll content
- Use LazyRow for recent video thumbnails
- Each Quick Action button has an icon + text + gradient background
- Cards use Box with translucent background (alpha=0.15) + rounded corners + border stroke
- Show empty state animation when no videos exist

---

## PART 6: VIDEO AUTO-EDIT SCREEN (MAIN FEATURE)
### Files: VideoEditScreen.kt + VideoEditViewModel.kt

This is the MOST IMPORTANT feature. Build it with COMPLETE working code.

### PURPOSE:
User uploads one or more raw videos → App automatically:
1. Detects all silent/pause sections using FFmpeg silencedetect filter
2. Removes those silent parts from the video
3. If multiple videos were uploaded, joins/merges them all into ONE final video
4. Entire processing happens ON THE DEVICE using phone RAM — no internet, no cloud

### VideoEditViewModel.kt — COMPLETE IMPLEMENTATION:

```kotlin
package com.gillvedio.app.presentation.screens.videoedit

import android.app.ActivityManager
import android.content.Context
import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.arthenica.ffmpegkit.FFmpegKit
import com.arthenica.ffmpegkit.FFprobeKit
import com.arthenica.ffmpegkit.ReturnCode
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.io.File

class VideoEditViewModel(private val context: Context) : ViewModel() {

    data class VideoEditState(
        val selectedVideos: List<Uri> = emptyList(),
        val isProcessing: Boolean = false,
        val processingProgress: Float = 0f,
        val processingStep: String = "",
        val outputVideoPath: String? = null,
        val error: String? = null,
        val originalDurationSec: Double = 0.0,
        val finalDurationSec: Double = 0.0,
        val pausesRemovedSec: Double = 0.0,
        val showLowMemoryWarning: Boolean = false
    )

    private val _state = MutableStateFlow(VideoEditState())
    val state: StateFlow<VideoEditState> = _state.asStateFlow()

    fun onVideosSelected(uris: List<Uri>) {
        _state.value = _state.value.copy(selectedVideos = uris, outputVideoPath = null, error = null)
    }

    fun removeVideo(uri: Uri) {
        _state.value = _state.value.copy(
            selectedVideos = _state.value.selectedVideos.filter { it != uri }
        )
    }

    fun processVideos() {
        val videos = _state.value.selectedVideos
        if (videos.isEmpty()) return

        // Check available RAM before starting
        val availableMemMb = getAvailableMemoryMb()
        if (availableMemMb < 500) {
            _state.value = _state.value.copy(showLowMemoryWarning = true)
        }

        viewModelScope.launch(Dispatchers.IO) {
            try {
                _state.value = _state.value.copy(
                    isProcessing = true,
                    processingProgress = 0f,
                    processingStep = "Preparing to analyze videos...",
                    error = null
                )

                val outputDir = File(context.cacheDir, "gill_processed")
                outputDir.mkdirs()

                val processedParts = mutableListOf<String>()
                var totalOriginalDuration = 0.0
                var totalFinalDuration = 0.0

                // STEP 1: Process each video — detect and remove pauses
                videos.forEachIndexed { index, uri ->
                    _state.value = _state.value.copy(
                        processingStep = "Analyzing video ${index + 1} of ${videos.size}...",
                        processingProgress = (index.toFloat() / videos.size) * 0.7f
                    )

                    val inputPath = getRealPathFromUri(context, uri) ?: run {
                        // Try content URI direct path
                        copyUriToCache(context, uri, index)
                    }

                    val originalDuration = getVideoDuration(inputPath)
                    totalOriginalDuration += originalDuration

                    _state.value = _state.value.copy(
                        processingStep = "Detecting pauses in video ${index + 1}..."
                    )

                    val silenceSegments = detectSilence(inputPath)
                    val keepSegments = buildKeepSegments(silenceSegments, originalDuration)

                    val cleanedPath = File(outputDir, "cleaned_${index}_${System.currentTimeMillis()}.mp4").absolutePath

                    _state.value = _state.value.copy(
                        processingStep = "Removing ${silenceSegments.size} pauses from video ${index + 1}..."
                    )

                    val success = if (keepSegments.size > 1) {
                        cutAndMergeSegments(inputPath, keepSegments, cleanedPath)
                    } else {
                        // No pauses found or entire video is speech — copy as-is
                        File(inputPath).copyTo(File(cleanedPath), overwrite = true)
                        true
                    }

                    if (success && File(cleanedPath).exists()) {
                        processedParts.add(cleanedPath)
                        totalFinalDuration += getVideoDuration(cleanedPath)
                    } else {
                        processedParts.add(inputPath)
                        totalFinalDuration += originalDuration
                    }
                }

                // STEP 2: Merge all processed clips into one final video
                _state.value = _state.value.copy(
                    processingStep = if (videos.size > 1) "Merging ${videos.size} videos into one..." else "Finalizing video...",
                    processingProgress = 0.85f
                )

                val finalOutputPath = File(
                    context.getExternalFilesDir(null),
                    "GillVedio_${System.currentTimeMillis()}.mp4"
                ).absolutePath

                val mergeSuccess = if (processedParts.size == 1) {
                    File(processedParts[0]).copyTo(File(finalOutputPath), overwrite = true)
                    true
                } else {
                    concatenateVideos(processedParts, finalOutputPath)
                }

                // Cleanup temp files
                outputDir.listFiles()?.forEach { it.delete() }

                if (mergeSuccess && File(finalOutputPath).exists()) {
                    _state.value = _state.value.copy(
                        isProcessing = false,
                        processingProgress = 1f,
                        processingStep = "Done!",
                        outputVideoPath = finalOutputPath,
                        originalDurationSec = totalOriginalDuration,
                        finalDurationSec = totalFinalDuration,
                        pausesRemovedSec = totalOriginalDuration - totalFinalDuration
                    )
                } else {
                    _state.value = _state.value.copy(
                        isProcessing = false,
                        error = "Processing failed. Please try again with a smaller video."
                    )
                }

            } catch (e: Exception) {
                _state.value = _state.value.copy(
                    isProcessing = false,
                    error = "Error: ${e.message}"
                )
            }
        }
    }

    /**
     * SILENCE DETECTION
     * Uses FFmpeg silencedetect filter
     * noise=-30dB means: sounds quieter than -30dB = silence/pause
     * d=0.5 means: pause must be at least 0.5 seconds long to be removed
     * Shorter pauses (under 0.5s) are kept for natural speech rhythm
     */
    private fun detectSilence(inputPath: String): List<Pair<Double, Double>> {
        val silenceSegments = mutableListOf<Pair<Double, Double>>()

        val session = FFmpegKit.execute(
            "-i \"$inputPath\" -af silencedetect=noise=-30dB:d=0.5 -f null -"
        )

        val logs = session.allLogsAsString ?: return emptyList()

        val startPattern = Regex("""silence_start:\s*([\d.]+)""")
        val endPattern = Regex("""silence_end:\s*([\d.]+)""")

        val starts = startPattern.findAll(logs).map { it.groupValues[1].toDoubleOrNull() ?: 0.0 }.toList()
        val ends = endPattern.findAll(logs).map { it.groupValues[1].toDoubleOrNull() ?: 0.0 }.toList()

        for (i in starts.indices) {
            if (i < ends.size && ends[i] > starts[i]) {
                silenceSegments.add(Pair(starts[i], ends[i]))
            }
        }

        return silenceSegments
    }

    /**
     * Builds list of time ranges to KEEP (the non-silent speaking parts)
     */
    private fun buildKeepSegments(
        silenceSegments: List<Pair<Double, Double>>,
        totalDuration: Double
    ): List<Pair<Double, Double>> {
        if (silenceSegments.isEmpty()) return listOf(Pair(0.0, totalDuration))

        val keepSegments = mutableListOf<Pair<Double, Double>>()
        var cursor = 0.0

        for ((silStart, silEnd) in silenceSegments) {
            if (silStart > cursor + 0.05) {
                keepSegments.add(Pair(cursor, silStart))
            }
            cursor = silEnd
        }

        if (cursor < totalDuration - 0.05) {
            keepSegments.add(Pair(cursor, totalDuration))
        }

        return keepSegments
    }

    /**
     * Cuts video to keep only non-silent segments and merges them
     * Uses FFmpeg filter_complex with trim + concat
     */
    private fun cutAndMergeSegments(
        inputPath: String,
        keepSegments: List<Pair<Double, Double>>,
        outputPath: String
    ): Boolean {
        if (keepSegments.isEmpty()) return false

        val videoFilters = mutableListOf<String>()
        val audioFilters = mutableListOf<String>()
        val concatInputs = StringBuilder()

        keepSegments.forEachIndexed { i, (start, end) ->
            videoFilters.add("[0:v]trim=start=${start}:end=${end},setpts=PTS-STARTPTS[v$i]")
            audioFilters.add("[0:a]atrim=start=${start}:end=${end},asetpts=PTS-STARTPTS[a$i]")
            concatInputs.append("[v$i][a$i]")
        }

        val allFilters = (videoFilters + audioFilters).joinToString(";")
        val filterComplex = "$allFilters;${concatInputs}concat=n=${keepSegments.size}:v=1:a=1[outv][outa]"

        val cmd = "-i \"$inputPath\" " +
                "-filter_complex \"$filterComplex\" " +
                "-map [outv] -map [outa] " +
                "-c:v libx264 -preset fast -crf 23 " +
                "-c:a aac -b:a 128k " +
                "\"$outputPath\" -y"

        val session = FFmpegKit.execute(cmd)
        return ReturnCode.isSuccess(session.returnCode)
    }

    /**
     * Joins multiple cleaned video files into one using FFmpeg concat demuxer
     */
    private fun concatenateVideos(videoPaths: List<String>, outputPath: String): Boolean {
        val concatFile = File(context.cacheDir, "concat_list_${System.currentTimeMillis()}.txt")
        val content = videoPaths.joinToString("\n") { "file '${it.replace("'", "\\'")}'" }
        concatFile.writeText(content)

        val cmd = "-f concat -safe 0 -i \"${concatFile.absolutePath}\" " +
                "-c:v libx264 -preset fast -crf 23 " +
                "-c:a aac -b:a 128k " +
                "\"$outputPath\" -y"

        val session = FFmpegKit.execute(cmd)
        concatFile.delete()
        return ReturnCode.isSuccess(session.returnCode)
    }

    /**
     * Gets video duration in seconds using FFprobe
     */
    private fun getVideoDuration(videoPath: String): Double {
        val session = FFprobeKit.execute(
            "-v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"$videoPath\""
        )
        return session.output?.trim()?.toDoubleOrNull() ?: 0.0
    }

    /**
     * Tries to get the real file path from a content URI
     */
    private fun getRealPathFromUri(context: Context, uri: Uri): String? {
        return try {
            val projection = arrayOf(android.provider.MediaStore.Video.Media.DATA)
            val cursor = context.contentResolver.query(uri, projection, null, null, null)
            cursor?.use {
                if (it.moveToFirst()) {
                    val columnIndex = it.getColumnIndexOrThrow(android.provider.MediaStore.Video.Media.DATA)
                    it.getString(columnIndex)
                } else null
            }
        } catch (e: Exception) {
            null
        }
    }

    /**
     * Copies content URI to cache when direct path is not available
     */
    private fun copyUriToCache(context: Context, uri: Uri, index: Int): String {
        val tempFile = File(context.cacheDir, "input_video_${index}_${System.currentTimeMillis()}.mp4")
        context.contentResolver.openInputStream(uri)?.use { input ->
            tempFile.outputStream().use { output ->
                input.copyTo(output)
            }
        }
        return tempFile.absolutePath
    }

    /**
     * Checks available device RAM in MB
     */
    private fun getAvailableMemoryMb(): Long {
        val memInfo = ActivityManager.MemoryInfo()
        (context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager).getMemoryInfo(memInfo)
        return memInfo.availMem / (1024 * 1024)
    }
}
```

### VideoEditScreen.kt — UI Layout:

Build the screen with these Compose components:

TOP SECTION — "Select Videos":
- Title: "Auto-Edit Video" with back arrow
- Subtitle: "Removes pauses & merges clips automatically"
- OutlinedButton "+ Add Videos" that opens ActivityResultContracts.GetMultipleContents("video/*")
- LazyColumn showing selected videos as dismissible cards with video name, size, and remove button
- Each card has a video icon + filename + duration + remove (X) button

MIDDLE SECTION — "What will happen" info card:
- Glass-style card showing:
  - Checkmark icon + "Silent pauses will be removed"
  - Checkmark icon + "All videos merged into 1 file"
  - Checkmark icon + "Processed on YOUR phone — no internet"
  - Checkmark icon + "Original files kept safe"

ACTION BUTTON — Large gradient button:
- Color: gradient from #7C4DFF to #9C27B0
- Text: "START AUTO-EDIT"
- Disabled and shows spinner if isProcessing == true
- Enabled only when selectedVideos is not empty

PROCESSING STATE — AnimatedVisibility when isProcessing == true:
- Animated pulsing card
- CircularProgressIndicator (indeterminate)
- LinearProgressIndicator showing processingProgress (0.0 to 1.0)
- Text showing processingStep
- Text showing percentage: "${(processingProgress * 100).toInt()}%"

SUCCESS STATE — AnimatedVisibility when outputVideoPath != null:
- Green checkmark icon with animation
- "Processing Complete!" title
- Stats row: "Original: X:XX | Final: Y:YY | Saved: Z:ZZ"
- Three buttons in a Row: "Preview" (opens ExoPlayer), "Save to Gallery", "Share"
- ExoPlayer inline preview (collapsed by default, expands on "Preview" click)

OPTIONAL EFFECTS — Secondary button at bottom:
- Outlined button: "Add Effects (Optional)"
- Icon: sparkles/magic wand
- Navigates to VideoFlowScreen passing outputVideoPath

---

## PART 7: VIDEO EFFECTS SCREEN (VideoFlowScreen.kt)

This screen allows users to optionally add effects to their processed video.

Build with TabRow containing 5 tabs:
1. MUSIC TAB — RadioGroup with 5 built-in royalty-free music options + Volume slider
2. TEXT TAB — TextField for overlay text + Animation style picker (Fade/Slide/Bounce) + Position picker (Top/Center/Bottom)
3. FILTER TAB — 4 Sliders: Brightness (-50 to +50), Contrast (-50 to +50), Saturation (-50 to +50), Warmth (-50 to +50)
4. SPEED TAB — RadioGroup: 0.5x, 0.75x, 1.0x, 1.25x, 1.5x, 2.0x
5. TRIM TAB — Range slider for start/end time with time display in MM:SS format

ExoPlayer preview at top showing live preview of original video.
"APPLY ALL EFFECTS" button at bottom — applies all selected effects via FFmpeg.

FFmpeg commands to use for effects:
- Brightness/Contrast/Saturation: -vf "eq=brightness=0.1:contrast=1.1:saturation=1.2"
- Speed: -filter:v "setpts=0.5*PTS" -filter:a "atempo=2.0"  
- Music: -i music.mp3 -filter_complex "[0:a][1:a]amix=inputs=2:duration=first:weights=1 0.5[a]"
- Text overlay: -vf "drawtext=text='YOUR TEXT':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=h-50"

---

## PART 8: IDEA GENERATOR SCREEN (IdeaGeneratorScreen.kt)

Uses Gemini AI (requires API key from settings) to generate 10 viral video ideas.

Layout:
- Topic TextField with label "Enter your video topic..."
- Dropdown: Niche (Lifestyle, Motivation, Education, Comedy, Tech, Cooking, Fitness, Business)
- Dropdown: Language (Hindi, English, Punjabi, Hinglish)
- Dropdown: Platform (Instagram, YouTube Shorts, Facebook, All platforms)
- Large gradient button: "GENERATE 10 VIRAL IDEAS"
- Loading shimmer animation while waiting for AI response
- LazyColumn of 10 idea cards when response arrives:
  - Each card: Checkbox + Title + Viral Score badge + Hook text (collapsed) + "Generate Video" button
- "Generate Videos (X selected)" button at bottom

Gemini prompt to use:
```
Generate 10 viral short video ideas in [language] optimized for [platform].
Topic: [user_input]
Niche: [niche]

For EACH idea provide:
1. title: catchy, hook-based title
2. hook: exact first 3 seconds opening line
3. outline: 4-5 bullet points for the video
4. viral_score: number 1-10
5. hashtags: array of 5 trending hashtags

Respond ONLY with valid JSON array. Example format:
[{"title":"...", "hook":"...", "outline":["...","..."], "viral_score":9, "hashtags":["#tag1"]}]
```

---

## PART 9: GALLERY SCREEN (GalleryScreen.kt)

- LazyVerticalGrid with GridCells.Fixed(2)
- Each cell: Video thumbnail + duration badge + status chip (Raw/Processed/Published)
- Tap: opens fullscreen ExoPlayer with controls
- Long press: shows ModalBottomSheet with actions: Edit, Share, Delete, Publish, Info
- Filter chips at top: All, Processed, Published, Raw
- Sort dropdown: Date (Newest), Date (Oldest), Size, Duration
- Empty state: illustration + "No videos yet. Upload your first video!" text

---

## PART 10: PUBLISH SCREEN (PublishScreen.kt)

- Video thumbnail preview at top
- AI Caption Generator: Button calls Gemini with prompt "Generate a viral social media caption for a video about [topic] for [platform]. Include emojis. Under 150 characters."
- Editable caption TextField
- AI Hashtag suggestions (5-10 tags)
- Platform selection with checkboxes: Instagram Reels, Facebook, YouTube Shorts, WhatsApp Status, Twitter/X
- Schedule picker: Now / After 3 hours / After 6 hours / Custom time
- "PUBLISH NOW" button — opens ShareSheet for manual posting OR uses platform APIs if configured

---

## PART 11: SETTINGS SCREEN (SettingsScreen.kt)

Sections with dividers:
1. PROFILE: Name field, Niche dropdown
2. API KEYS (stored with EncryptedSharedPreferences):
   - Gemini API Key: password field + "Test" button
   - Show status: Connected / Not configured
3. VIDEO DEFAULTS:
   - Auto-remove pauses toggle (default ON)
   - Silence threshold: -20dB / -30dB / -40dB (radio group)
   - Min pause duration: 0.3s / 0.5s / 1.0s (radio group)
   - Output quality: Low/Medium/High/Ultra
4. STORAGE:
   - Show used space
   - "Clear Cache" button
   - "Clear All Videos" button with confirmation dialog
5. ABOUT:
   - App version
   - Rate App button (triggers Google Play In-App Review)

---

## PART 12: ROOM DATABASE

AppDatabase.kt:
```kotlin
@Database(
    entities = [VideoEntity::class, IdeaEntity::class, PublishLogEntity::class],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun videoDao(): VideoDao
    abstract fun ideaDao(): IdeaDao
    abstract fun publishLogDao(): PublishLogDao
}

// VideoEntity
@Entity(tableName = "videos")
data class VideoEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val originalPath: String,
    val processedPath: String? = null,
    val title: String,
    val durationSec: Double,
    val fileSizeBytes: Long,
    val status: String,        // "raw", "processed", "published"
    val pausesRemovedSec: Double = 0.0,
    val thumbnailPath: String? = null,
    val createdAt: Long = System.currentTimeMillis()
)

// IdeaEntity
@Entity(tableName = "ideas")
data class IdeaEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val topic: String,
    val title: String,
    val hook: String,
    val scriptOutline: String,
    val viralScore: Int,
    val hashtags: String,
    val platform: String,
    val isSelected: Boolean = false,
    val createdAt: Long = System.currentTimeMillis()
)

// PublishLogEntity
@Entity(tableName = "publish_logs")
data class PublishLogEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val videoId: Long,
    val platform: String,
    val status: String,        // "scheduled", "published", "failed"
    val caption: String,
    val scheduledAt: Long,
    val publishedAt: Long? = null
)
```

---

## PART 13: BACKGROUND PROCESSING — WorkManager

VideoProcessingWorker.kt:
- Extends CoroutineWorker
- Input: video URI strings
- Shows persistent notification: "GILL VEDIO — Processing video..."
- Runs the same FFmpegKit silence detection + cut + merge logic
- Updates notification progress
- On completion: shows success notification with "Open Result" action
- On failure: shows error notification

Notification channels to create in GillVedioApp.kt:
- "VIDEO_PROCESSING" channel: name "Video Processing", importance HIGH
- "PUBLISH_STATUS" channel: name "Publish Status", importance DEFAULT

---

## PART 14: NAVIGATION SETUP

Screen.kt:
```kotlin
sealed class Screen(val route: String) {
    object Home : Screen("home")
    object VideoEdit : Screen("video_edit")
    object VideoFlow : Screen("video_flow/{videoPath}") {
        fun createRoute(videoPath: String) = "video_flow/${Uri.encode(videoPath)}"
    }
    object IdeaGenerator : Screen("idea_generator")
    object Gallery : Screen("gallery")
    object Publish : Screen("publish/{videoPath}") {
        fun createRoute(videoPath: String) = "publish/${Uri.encode(videoPath)}"
    }
    object Settings : Screen("settings")
}
```

NavGraph.kt:
- NavigationBar (bottom nav) with 5 items: Home, Edit, Ideas, Gallery, Settings
- Each nav item has an icon and label
- Selected item shows filled icon, unselected shows outlined icon
- Route transitions: use fadeIn/fadeOut animations

Bottom Nav Items:
- Home: Icons.Filled.Home / Icons.Outlined.Home
- Edit: Icons.Filled.ContentCut / Icons.Outlined.ContentCut
- Ideas: Icons.Filled.Lightbulb / Icons.Outlined.Lightbulb
- Gallery: Icons.Filled.VideoLibrary / Icons.Outlined.VideoLibrary
- Settings: Icons.Filled.Settings / Icons.Outlined.Settings

---

## PART 15: CONSTANTS

utils/Constants.kt:
```kotlin
object Constants {
    const val SILENCE_THRESHOLD_DB = -30
    const val SILENCE_MIN_DURATION_SEC = 0.5
    const val VIDEO_CRF = 23
    const val VIDEO_PRESET = "fast"
    const val AUDIO_BITRATE = "128k"
    const val LOW_MEMORY_WARNING_MB = 500
    const val CHANNEL_VIDEO_PROCESSING = "VIDEO_PROCESSING"
    const val CHANNEL_PUBLISH = "PUBLISH_STATUS"
    const val GEMINI_MODEL = "gemini-1.5-pro"
    const val DB_NAME = "gill_vedio_db"
    
    // EncryptedSharedPreferences keys
    const val PREF_FILE = "gill_vedio_secure_prefs"
    const val KEY_GEMINI_API = "gemini_api_key"
    const val KEY_USER_NAME = "user_name"
    const val KEY_USER_NICHE = "user_niche"
    const val KEY_AUTO_REMOVE_PAUSES = "auto_remove_pauses"
    const val KEY_SILENCE_THRESHOLD = "silence_threshold"
    const val KEY_MIN_PAUSE_DURATION = "min_pause_duration"
}
```

---

## PART 16: PROGUARD RULES

proguard-rules.pro:
```
-keep class com.arthenica.ffmpegkit.** { *; }
-keep class com.arthenica.smartexception.** { *; }
-keep class com.google.ai.client.generativeai.** { *; }
-keepattributes Signature
-keepattributes *Annotation*
-dontwarn com.arthenica.**
-dontwarn okhttp3.**
-keepclassmembers class * extends androidx.room.RoomDatabase {
    public static ** INSTANCE;
}
```

---

## PART 17: GOOGLE PLAY STORE SETUP

Signing config in build.gradle.kts:
```kotlin
android {
    signingConfigs {
        create("release") {
            keyAlias = "gill_vedio"
            keyPassword = "YOUR_KEY_PASSWORD"
            storeFile = file("keystore/gill_vedio_release.jks")
            storePassword = "YOUR_STORE_PASSWORD"
        }
    }
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

App Store listing information:
- Short description: "Auto-remove video pauses & merge clips — 100% on your phone"
- Category: Video Players & Editors
- Content Rating: Everyone
- Keywords: video editor, remove silence, merge videos, AI video, content creator

---

## PART 18: FILE PATHS XML

res/xml/file_paths.xml:
```xml
<?xml version="1.0" encoding="utf-8"?>
<paths>
    <external-files-path name="videos" path="." />
    <cache-path name="cache" path="." />
    <external-cache-path name="external_cache" path="." />
</paths>
```

---

## PART 19: STRINGS.XML (COMPLETE)

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">GILL VEDIO</string>
    <string name="app_tagline">AI Video Creator</string>
    <string name="home_greeting">Ready to create?</string>
    <string name="quick_actions_title">Quick Actions</string>
    <string name="btn_upload">Upload Video</string>
    <string name="btn_auto_edit">Auto-Edit</string>
    <string name="btn_generate">Generate Ideas</string>
    <string name="btn_publish">Publish</string>
    <string name="auto_edit_title">Auto-Edit Video</string>
    <string name="auto_edit_subtitle">Removes pauses and merges clips automatically</string>
    <string name="select_videos_label">Select Videos</string>
    <string name="btn_add_videos">+ Add Video Files</string>
    <string name="btn_start">START AUTO-EDIT</string>
    <string name="what_happens_title">What will happen:</string>
    <string name="feature_remove_pauses">Silent pauses will be removed</string>
    <string name="feature_merge">All videos merged into 1 file</string>
    <string name="feature_offline">Processed on YOUR phone — no internet</string>
    <string name="feature_safe">Original files kept safe</string>
    <string name="processing_title">Processing...</string>
    <string name="done_title">Processing Complete!</string>
    <string name="btn_preview">Preview</string>
    <string name="btn_save">Save to Gallery</string>
    <string name="btn_share">Share</string>
    <string name="btn_effects">Add Effects (Optional)</string>
    <string name="effects_title">Effects Editor</string>
    <string name="btn_apply_effects">APPLY ALL EFFECTS</string>
    <string name="ideas_title">Viral Idea Generator</string>
    <string name="topic_hint">Enter your video topic...</string>
    <string name="btn_generate_ideas">GENERATE 10 VIRAL IDEAS</string>
    <string name="gallery_title">My Videos</string>
    <string name="gallery_empty">No videos yet.\nUpload your first video!</string>
    <string name="publish_title">Publish Video</string>
    <string name="btn_generate_caption">Generate AI Caption</string>
    <string name="btn_publish_now">PUBLISH NOW</string>
    <string name="settings_title">Settings</string>
    <string name="settings_profile">Profile</string>
    <string name="settings_api_keys">API Keys</string>
    <string name="settings_video_defaults">Video Defaults</string>
    <string name="settings_storage">Storage</string>
    <string name="error_no_videos_selected">Please select at least one video</string>
    <string name="error_processing_failed">Processing failed. Please try again.</string>
    <string name="warning_low_memory">Low memory detected. Processing may take longer for large videos.</string>
    <string name="error_permission_needed">Storage permission is needed to access your videos</string>
</resources>
```

---

## FINAL INSTRUCTIONS TO ANDROID STUDIO GEMINI AI:

1. Generate ALL files completely with no placeholder comments or TODOs
2. Every Kotlin function must be fully implemented and compilable
3. Use Material Design 3 components (M3) throughout — no deprecated Material 2 components
4. Apply the premium dark theme colors exactly as specified (#0A0A0F background, #7C4DFF primary)
5. Add smooth animations: AnimatedVisibility, animate*AsState, spring animations
6. Handle all edge cases: empty state, error state, loading state, permission denied state
7. The VideoEditViewModel FFmpegKit code is the most critical — implement it exactly as shown
8. All video processing must work OFFLINE — FFmpegKit does not need internet
9. Use EncryptedSharedPreferences (NOT plain SharedPreferences) for API key storage
10. The app must run on Android 8.0 (API 26) and higher without crashes

--- END COPY HERE ---

---

## 📌 ADDITIONAL NOTES FOR YOU (GURLEEN/GURJAS):

### Steps to follow after getting the code from Android Studio Gemini:

1. **Create new Android project** in Android Studio
   - Select "Empty Activity (Compose)"
   - Package: com.gillvedio.app
   - Min SDK: 26
   - Language: Kotlin

2. **Paste the generated code** into respective files

3. **Get your Gemini API key** from https://aistudio.google.com (free)

4. **Build and test on your phone** using USB cable or WiFi debugging

5. **For Google Play publishing:**
   - Create keystore: Build > Generate Signed Bundle/APK
   - Create Google Play Console account (one-time $25 fee)
   - Upload the AAB file (not APK)
   - Fill in the store listing with the description above

### Key feature reminder:
- The AUTO-EDIT feature works 100% OFFLINE using FFmpegKit
- It removes all pauses/silence from videos using your phone's own processor and RAM
- No video data leaves your phone during editing
- The Gemini AI features (idea generation) DO need internet but video editing does NOT
