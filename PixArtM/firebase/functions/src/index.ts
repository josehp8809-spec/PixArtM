/**
 * Firebase Cloud Functions for PixArtM
 * 
 * Entry point for all Cloud Functions
 */

import * as admin from 'firebase-admin';

// Initialize Firebase Admin SDK
admin.initializeApp();

// Export all functions
export {
    reserveCapture,
    reserveCaptureWithBuffer,
    confirmCapture
} from './reserveCapture';

export {
    generateAlbumZip
} from './generateAlbumZip';

export {
    autoCleanup,
    manualCleanup
} from './autoCleanup';
