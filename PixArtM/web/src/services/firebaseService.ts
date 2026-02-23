/**
 * Firebase Service for Web Runtime
 * 
 * Handles all Firebase operations for the camera and gallery pages
 */

import { initializeApp } from 'firebase/app';
import { getFirestore, doc, getDoc, collection, query, where, orderBy, getDocs } from 'firebase/firestore';
import { getStorage, ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { getFunctions, httpsCallable } from 'firebase/functions';
import { Event, Capture, ReserveCaptureRequest, ReserveCaptureResponse, GenerateZipRequest, GenerateZipResponse } from '../../../shared/types/index';

// Firebase configuration
// TODO: Replace with your Firebase config
const firebaseConfig = {
    apiKey: process.env.VITE_FIREBASE_API_KEY || '',
    authDomain: process.env.VITE_FIREBASE_AUTH_DOMAIN || '',
    projectId: process.env.VITE_FIREBASE_PROJECT_ID || '',
    storageBucket: process.env.VITE_FIREBASE_STORAGE_BUCKET || '',
    messagingSenderId: process.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '',
    appId: process.env.VITE_FIREBASE_APP_ID || ''
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const storage = getStorage(app);
const functions = getFunctions(app);

/**
 * Get event by slug
 */
export async function getEventBySlug(slug: string): Promise<Event | null> {
    try {
        const eventsRef = collection(db, 'events');
        const q = query(eventsRef, where('slug', '==', slug));
        const querySnapshot = await getDocs(q);

        if (querySnapshot.empty) {
            return null;
        }

        const eventDoc = querySnapshot.docs[0];
        return { id: eventDoc.id, ...eventDoc.data() } as Event;
    } catch (error) {
        console.error('Error getting event by slug:', error);
        throw error;
    }
}

/**
 * Get event by ID
 */
export async function getEventById(eventId: string): Promise<Event | null> {
    try {
        const eventRef = doc(db, 'events', eventId);
        const eventDoc = await getDoc(eventRef);

        if (!eventDoc.exists()) {
            return null;
        }

        return { id: eventDoc.id, ...eventDoc.data() } as Event;
    } catch (error) {
        console.error('Error getting event by ID:', error);
        throw error;
    }
}

/**
 * Reserve a capture slot
 */
export async function reserveCapture(eventId: string): Promise<ReserveCaptureResponse> {
    try {
        const reserveCaptureFunction = httpsCallable<ReserveCaptureRequest, ReserveCaptureResponse>(
            functions,
            'reserveCapture'
        );

        const result = await reserveCaptureFunction({ eventId });
        return result.data;
    } catch (error: any) {
        console.error('Error reserving capture:', error);
        throw new Error(error.message || 'Failed to reserve capture slot');
    }
}

/**
 * Upload photo to Firebase Storage
 */
export async function uploadPhoto(
    eventId: string,
    captureNumber: number,
    photoBlob: Blob
): Promise<string> {
    try {
        const filename = `${captureNumber}_${Date.now()}.jpg`;
        const storagePath = `events/${eventId}/${filename}`;
        const storageRef = ref(storage, storagePath);

        // Upload with metadata
        const metadata = {
            contentType: 'image/jpeg',
            customMetadata: {
                eventId,
                captureNumber: captureNumber.toString(),
                uploadedAt: new Date().toISOString()
            }
        };

        await uploadBytes(storageRef, photoBlob, metadata);

        // Get download URL
        const downloadURL = await getDownloadURL(storageRef);

        return downloadURL;
    } catch (error) {
        console.error('Error uploading photo:', error);
        throw error;
    }
}

/**
 * Get all captures for an event (for gallery)
 */
export async function getEventCaptures(eventId: string): Promise<Capture[]> {
    try {
        const capturesRef = collection(db, 'events', eventId, 'captures');
        const q = query(capturesRef, where('uploadedToCloud', '==', true), orderBy('captureNumber', 'asc'));
        const querySnapshot = await getDocs(q);

        return querySnapshot.docs.map(doc => ({
            id: doc.id,
            ...doc.data()
        })) as Capture[];
    } catch (error) {
        console.error('Error getting event captures:', error);
        throw error;
    }
}

/**
 * Generate album ZIP
 */
export async function generateAlbumZip(
    eventId: string,
    galleryToken: string
): Promise<GenerateZipResponse> {
    try {
        const generateZipFunction = httpsCallable<GenerateZipRequest, GenerateZipResponse>(
            functions,
            'generateAlbumZip'
        );

        const result = await generateZipFunction({ eventId, galleryToken });
        return result.data;
    } catch (error: any) {
        console.error('Error generating album ZIP:', error);
        throw new Error(error.message || 'Failed to generate album ZIP');
    }
}

/**
 * Check if event is currently active
 */
export function isEventActive(event: Event): boolean {
    const now = new Date();
    const startDate = new Date(event.startDate);
    const endDate = new Date(event.endDate);

    return (
        event.status === 'active' &&
        now >= startDate &&
        now <= endDate
    );
}

/**
 * Check if event has reached photo limit
 */
export function hasReachedLimit(event: Event): boolean {
    return event.captureCount >= event.photoLimit;
}

/**
 * Get remaining photos count
 */
export function getRemainingPhotos(event: Event): number {
    return Math.max(0, event.photoLimit - event.captureCount);
}

/**
 * Format event status for display
 */
export function getEventStatusMessage(event: Event): string {
    if (event.status === 'cleaned') {
        return 'Este evento ha sido archivado';
    }

    if (event.status === 'expired') {
        return 'Este evento ha finalizado';
    }

    if (!isEventActive(event)) {
        const now = new Date();
        const startDate = new Date(event.startDate);

        if (now < startDate) {
            return `El evento comenzará el ${startDate.toLocaleDateString()}`;
        } else {
            return 'El evento ha finalizado';
        }
    }

    if (hasReachedLimit(event)) {
        return 'Se ha alcanzado el límite de fotos';
    }

    return `${getRemainingPhotos(event)} fotos disponibles`;
}
