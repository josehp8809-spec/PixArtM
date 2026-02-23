# PixArtM - Architecture Overview

## System Components

PixArtM consists of three main components:

### 1. Desktop Application (Electron)
**Purpose:** Internal tool for operators to create and manage event photo frames

**Technology Stack:**
- Electron (cross-platform desktop)
- React + TypeScript (UI)
- SQLite (local storage)
- Fabric.js (canvas editor)

**Key Features:**
- Project management (CRUD)
- Frame editor (9:16 canvas)
- QR code generator with customization
- Calendar scheduling
- Plan configuration
- Gemini AI assistant
- Firebase deployment

### 2. Web Runtime (Firebase Hosting)
**Purpose:** Public-facing pages accessed via QR codes

**Technology Stack:**
- React + TypeScript
- Vite (build tool)
- Firebase SDK

**Pages:**
- `/e/<slug>` - Camera capture page
- `/g/<token>` - Gallery viewing page

### 3. Firebase Backend
**Services:**
- **Firestore:** Event configurations and counters
- **Storage:** Photo uploads (Pro/Premium only)
- **Cloud Functions:** Business logic and validation
- **Hosting:** Web runtime deployment

---

## Data Flow

### Event Creation Flow
```
Desktop App
    ↓ Create Project
SQLite (local storage)
    ↓ Configure & Design
Desktop App
    ↓ Deploy Event
Firebase Firestore
    ↓ Generate QR
Desktop App (export QR)
```

### Photo Capture Flow
```
User scans QR
    ↓
Web Runtime (/e/<slug>)
    ↓ Request capture
Cloud Function (reserveCapture)
    ↓ Validate & increment counter
Firestore (update captureCount)
    ↓ Success
Web Runtime
    ↓ Capture photo
Device Storage (always)
    ↓ If Pro/Premium
Firebase Storage (upload)
```

### Gallery Access Flow
```
User accesses /g/<token>
    ↓
Web Runtime (Gallery)
    ↓ Validate token
Firestore (get event)
    ↓ Load photos
Firebase Storage
    ↓ Display
Web Runtime (photo grid)
    ↓ Download ZIP
Cloud Function (generateAlbumZip)
```

---

## Event Lifecycle

### States
1. **Draft** - Created in desktop, not deployed
2. **Active** - Deployed to Firebase, accepting captures
3. **Expired** - Reached end date or photo limit
4. **Cleaned** - Gallery expired, files deleted

### Timeline
```
Day 0: Event created (Desktop)
Day 0: Event deployed (Firebase)
Day X: Event starts (auto-activation)
Day Y: Event ends OR limit reached (auto-deactivation)
    → QR becomes inactive
    → Gallery remains active
Day Y+15: Gallery expires
    → Auto-cleanup runs
    → Photos deleted from Storage
```

---

## Plans & Limits

| Plan | Photos | Validity | Cloud Album | Use Case |
|------|--------|----------|-------------|----------|
| Free | 10 | 3 days | ❌ | Testing/Demo |
| Basic | 100 | 10 days | ❌ | Small events |
| Pro | 500 | 14 days | ✅ | Medium events |
| Premium | 5000 | 90 days | ✅ | Large events |

**Cloud Album Benefits:**
- Automatic photo backup
- Gallery access for downloads
- ZIP album generation

---

## Security Model

### Desktop App
- Local-only access
- Firebase Admin SDK credentials (secure storage)
- No public API exposure

### Web Runtime
- No authentication required (token-based access)
- Read-only operations
- Rate limiting on Cloud Functions

### Firebase
- **Firestore Rules:** Public read for active events, no write access
- **Storage Rules:** Token-based read, no public write
- **Functions:** Validate all inputs, atomic operations

---

## URL Structure

### Camera Page
```
https://DOMAIN.app/e/<slug>
```
- `slug`: Human-readable event identifier (e.g., "boda-maria-2024")
- Public access during event active period

### Gallery Page
```
https://DOMAIN.app/g/<galleryToken>
```
- `galleryToken`: Random secure token (e.g., UUID)
- Access valid for 15 days after event closure

---

## QR Code Specifications

### Technical Details
- **Format:** QR Code (ISO/IEC 18004)
- **Error Correction:** M (15%) or H (30%) for logo embedding
- **Size:** Minimum 300x300px for print quality
- **Export Formats:** PNG, SVG, PDF

### Customization Options
- **Colors:** Custom dark/light colors or gradients
- **Logo:** Central logo embedding (max 20% of QR area)
- **Style:** Square or rounded corners

### Validation (via Gemini)
- Contrast ratio check
- Scannability verification
- Color palette suggestions

---

## Gemini AI Assistant Features

### 1. Color Palette Suggestions
**Input:** Event theme/description
**Output:** 3-5 safe color combinations for QR codes

### 2. Contrast Validation
**Input:** Selected dark/light colors
**Output:** Pass/fail + recommendations

### 3. Copy Generation
**Input:** Event details
**Output:** Short promotional text (max 50 chars)

### 4. Frame Style Suggestions
**Input:** Event type (wedding, corporate, birthday, etc.)
**Output:** Design recommendations

---

## Storage Strategy

### Desktop (SQLite)
- **Projects:** All event configurations
- **Designs:** Frame layouts, QR settings
- **History:** Export logs, version history

### Firebase (Firestore)
- **Events:** Active event configurations only
- **Captures:** Metadata for each photo taken
- **Minimal data:** Only what's needed for runtime

### Firebase (Storage)
- **Photos:** Pro/Premium plan uploads only
- **Path structure:** `/events/{eventId}/{captureId}.jpg`
- **Auto-cleanup:** After gallery expiration

---

## Performance Considerations

### Desktop App
- SQLite for fast local queries
- Lazy loading for project lists
- Canvas optimization for large images

### Web Runtime
- Lazy loading for gallery images
- Progressive image loading
- Optimized camera stream handling

### Firebase
- Indexed queries for fast lookups
- Atomic counter updates
- Batch operations for cleanup

---

## Deployment Architecture

```
Desktop App
    ↓ Build
Electron Installer (.exe, .dmg, .AppImage)
    ↓ Install
User's Computer (Windows/Mac/Linux)

Web Runtime
    ↓ Build (Vite)
Static Files (HTML, JS, CSS)
    ↓ Deploy
Firebase Hosting

Cloud Functions
    ↓ Deploy
Firebase Functions (Node.js runtime)
```

---

## Development Environment

### Prerequisites
- Node.js 18+
- npm or yarn
- Firebase CLI
- SQLite3
- Git

### Setup Commands
```bash
# Desktop app
cd desktop
npm install
npm run dev

# Web runtime
cd web
npm install
npm run dev

# Firebase functions
cd firebase/functions
npm install
npm run serve
```

---

## Monitoring & Maintenance

### Metrics to Track
- Active events count
- Total captures per event
- Storage usage
- Function execution times
- Error rates

### Scheduled Tasks
- Daily cleanup check (Cloud Function)
- Weekly storage audit
- Monthly usage reports

---

## Future Considerations (Out of Scope for MVP)

- Multi-language support
- Advanced frame templates
- Video capture support
- Real-time photo feed
- Analytics dashboard
- White-label customization

**Note:** These features are NOT part of the current specification and should not be implemented without explicit approval.
