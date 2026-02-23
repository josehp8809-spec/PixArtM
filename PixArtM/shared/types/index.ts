/**
 * Shared TypeScript types for PixArtM
 * Used across Desktop App, Web Runtime, and Firebase Functions
 */

// ============================================================================
// ENUMS & TYPES
// ============================================================================

export type PlanType = 'free' | 'basic' | 'pro' | 'premium';
export type EventStatus = 'draft' | 'active' | 'expired' | 'cleaned';
export type ExportFormat = 'png' | 'svg' | 'pdf';
export type ErrorCorrection = 'L' | 'M' | 'Q' | 'H';
export type CornerStyle = 'square' | 'rounded';

// ============================================================================
// PLAN CONFIGURATION
// ============================================================================

export interface PlanConfig {
  name: PlanType;
  photoLimit: number;
  validityDays: number;
  hasCloudAlbum: boolean;
  displayName: string;
  description: string;
}

export const PLANS: Record<PlanType, PlanConfig> = {
  free: {
    name: 'free',
    photoLimit: 10,
    validityDays: 3,
    hasCloudAlbum: false,
    displayName: 'Free / Prueba',
    description: 'Ideal para probar la plataforma'
  },
  basic: {
    name: 'basic',
    photoLimit: 100,
    validityDays: 10,
    hasCloudAlbum: false,
    displayName: 'Básico',
    description: 'Perfecto para eventos pequeños'
  },
  pro: {
    name: 'pro',
    photoLimit: 500,
    validityDays: 14,
    hasCloudAlbum: true,
    displayName: 'Pro',
    description: 'Para eventos medianos con álbum en la nube'
  },
  premium: {
    name: 'premium',
    photoLimit: 5000,
    validityDays: 90,
    hasCloudAlbum: true,
    displayName: 'Premium',
    description: 'Para eventos grandes con almacenamiento extendido'
  }
};

// ============================================================================
// QR CODE SETTINGS
// ============================================================================

export interface QRSettings {
  darkColor: string;
  lightColor: string;
  hasGradient: boolean;
  gradientColors?: string[];
  logoUrl?: string;
  errorCorrection: ErrorCorrection;
  cornerStyle: CornerStyle;
}

export const DEFAULT_QR_SETTINGS: QRSettings = {
  darkColor: '#000000',
  lightColor: '#FFFFFF',
  hasGradient: false,
  errorCorrection: 'M',
  cornerStyle: 'square'
};

// ============================================================================
// FRAME DESIGN
// ============================================================================

export interface FrameDesign {
  canvasData: string;  // Fabric.js JSON serialized
  overlayUrl?: string; // URL to frame overlay image
}

// ============================================================================
// PROJECT (Desktop App)
// ============================================================================

export interface Project {
  id: string;
  name: string;
  slug: string;
  plan: PlanType;
  photoLimit: number;
  validityDays: number;
  hasCloudAlbum: boolean;
  startDate: string;  // ISO 8601
  endDate: string;    // ISO 8601
  status: EventStatus;
  frameDesign?: FrameDesign;
  galleryToken: string;
  createdAt: string;
  updatedAt: string;
  deployedAt?: string;
}

// ============================================================================
// EVENT (Firestore)
// ============================================================================

export interface Event {
  id: string;
  slug: string;
  name: string;
  plan: PlanType;
  
  // Limits
  photoLimit: number;
  validityDays: number;
  hasCloudAlbum: boolean;
  
  // Scheduling
  startDate: string;  // ISO 8601 or Firestore Timestamp
  endDate: string;
  
  // Status
  status: EventStatus;
  captureCount: number;
  reservedCount: number;
  
  // Frame design
  frameDesign: FrameDesign;
  
  // Gallery
  galleryToken: string;
  galleryExpiresAt: string;
  
  // Analytics
  analytics?: {
    totalCaptures: number;
    peakHour?: number;
    lastCaptureAt?: string;
  };
  
  // Metadata
  createdAt: string;
  updatedAt: string;
  deployedAt?: string;
}

// ============================================================================
// CAPTURE (Firestore subcollection)
// ============================================================================

export interface Capture {
  id: string;
  eventId: string;
  captureNumber: number;
  timestamp: string;
  storageUrl?: string;
  storagePath?: string;
  deviceSaved: boolean;
  uploadedToCloud: boolean;
  
  // Image metadata
  originalSize?: number;
  compressedSize?: number;
  dimensions?: {
    width: number;
    height: number;
  };
}

// ============================================================================
// API RESPONSES
// ============================================================================

export interface ReserveCaptureRequest {
  eventId: string;
}

export interface ReserveCaptureResponse {
  success: boolean;
  captureNumber?: number;
  message?: string;
  event?: {
    captureCount: number;
    photoLimit: number;
    status: EventStatus;
  };
}

export interface GenerateZipRequest {
  eventId: string;
  galleryToken: string;
}

export interface GenerateZipResponse {
  success: boolean;
  downloadUrl?: string;
  expiresAt?: string;
  message?: string;
}

// ============================================================================
// EXPORT HISTORY (Desktop App)
// ============================================================================

export interface ExportHistory {
  id: string;
  projectId: string;
  exportType: ExportFormat;
  qrSettings: QRSettings;
  exportedAt: string;
}

// ============================================================================
// GEMINI AI REQUESTS/RESPONSES
// ============================================================================

export interface ColorPaletteSuggestion {
  name: string;
  darkColor: string;
  lightColor: string;
  description: string;
}

export interface ContrastValidationResult {
  isValid: boolean;
  contrastRatio: number;
  recommendation?: string;
}

export interface FrameStyleSuggestion {
  style: string;
  description: string;
  colors: string[];
}
