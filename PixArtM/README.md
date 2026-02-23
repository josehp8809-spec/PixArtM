# PixArtM

**Internal tool for creating and managing digital photo frames for events**

PixArtM is a comprehensive solution consisting of a desktop application for event operators and a web runtime for end users to capture photos at events via QR codes.

## 🏗️ Architecture

### Components

1. **Desktop Application (Electron + React + TypeScript)**
   - Internal tool for operators
   - Project management and frame design
   - QR code generation and customization
   - Firebase deployment
   - Gemini AI assistant

2. **Web Runtime (React + TypeScript + Vite + PWA)**
   - Camera capture page (`/e/<slug>`)
   - Gallery viewing page (`/g/<token>`)
   - Progressive Web App for better mobile experience

3. **Firebase Backend**
   - Firestore: Event configurations and counters
   - Storage: Photo uploads (Pro/Premium plans)
   - Cloud Functions: Business logic and validation
   - Hosting: Web runtime deployment

## 📋 Plans & Limits

| Plan | Photos | Validity | Cloud Album | Use Case |
|------|--------|----------|-------------|----------|
| Free | 10 | 3 days | ❌ | Testing/Demo |
| Basic | 100 | 10 days | ❌ | Small events |
| Pro | 500 | 14 days | ✅ | Medium events |
| Premium | 5000 | 90 days | ✅ | Large events |

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Firebase CLI (`npm install -g firebase-tools`)
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd PixArtM

# Install desktop app dependencies
cd desktop
npm install

# Install web runtime dependencies
cd ../web
npm install

# Install Firebase Functions dependencies
cd ../firebase/functions
npm install
```

### Firebase Setup

1. Create a Firebase project at https://console.firebase.google.com
2. Enable Firestore, Storage, Functions, and Hosting
3. Download service account credentials for desktop app
4. Initialize Firebase in the project:

```bash
cd firebase
firebase login
firebase use --add  # Select your project
```

### Development

#### Desktop App
```bash
cd desktop
npm run dev
```

#### Web Runtime
```bash
cd web
npm run dev
```

#### Firebase Functions (with emulators)
```bash
cd firebase/functions
npm run serve
```

## 📁 Project Structure

```
PixArtM/
├── desktop/              # Electron desktop application
│   ├── src/
│   │   ├── main/        # Electron main process
│   │   ├── renderer/    # React UI
│   │   └── shared/      # Shared utilities
│   └── package.json
├── web/                  # Web runtime (PWA)
│   ├── src/
│   │   ├── pages/       # Camera & Gallery pages
│   │   ├── components/  # React components
│   │   ├── hooks/       # Custom hooks
│   │   ├── services/    # Firebase services
│   │   └── utils/       # Utilities
│   └── package.json
├── firebase/             # Firebase backend
│   ├── functions/       # Cloud Functions
│   ├── firestore.rules  # Security rules
│   ├── storage.rules    # Storage rules
│   └── firebase.json    # Firebase config
└── shared/              # Shared TypeScript types
    └── types/
        └── index.ts
```

## 🔑 Key Features

### Desktop App
- ✅ Project management (CRUD operations)
- ✅ Frame editor (9:16 canvas with Fabric.js)
- ✅ QR code generator with customization
- ✅ Calendar scheduling
- ✅ Plan configuration
- ✅ Gemini AI assistant
- ✅ Firebase deployment
- ✅ Event monitoring and notifications

### Web Runtime
- ✅ Camera capture with timer
- ✅ Image compression (max 1920px, 85% quality)
- ✅ Device save (always)
- ✅ Cloud upload (Pro/Premium)
- ✅ Gallery with lazy loading
- ✅ ZIP album download
- ✅ PWA support
- ✅ Camera fallback UI

### Firebase Backend
- ✅ Atomic capture reservation
- ✅ Photo limit enforcement
- ✅ Date range validation
- ✅ ZIP generation with caching
- ✅ Auto-cleanup (15 days after event ends)
- ✅ Analytics tracking

## 🔒 Security

- **Firestore:** Public read for active events, no client writes
- **Storage:** Token-based read access, no public writes
- **Functions:** Input validation, atomic operations
- **Desktop:** Firebase Admin SDK with secure credentials

## 📊 Cost Optimization

- **Image Compression:** ~500KB per photo (from ~2MB)
- **Estimated Storage:** Premium (5000 photos) = ~2.5GB = $0.065/month
- **Auto-Cleanup:** Deletes photos 15 days after event ends
- **ZIP Caching:** 24-hour cache to reduce bandwidth costs

## 🧪 Testing

```bash
# Desktop app tests
cd desktop
npm run test

# Web runtime tests
cd web
npm run test

# Firebase Functions tests
cd firebase/functions
npm run test
```

## 🚢 Deployment

### Web Runtime
```bash
cd web
npm run build
cd ../firebase
firebase deploy --only hosting
```

### Cloud Functions
```bash
cd firebase
firebase deploy --only functions
```

### Desktop App
```bash
cd desktop
npm run electron:build
```

## 📖 Documentation

- [Architecture Overview](./ARCHITECTURE.md)
- [Implementation Plan](./docs/implementation_plan.md)
- [Task Breakdown](./docs/task.md)

## 🤝 Contributing

This is an internal tool. For questions or issues, contact the development team.

## 📄 License

MIT License - See LICENSE file for details

---

**PixArtM** - Transforming events into memorable experiences 📸
