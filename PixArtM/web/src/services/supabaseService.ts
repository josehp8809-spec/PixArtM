/**
 * Supabase Service for Web Runtime
 * Replaces: firebaseService.ts (Firebase SDK)
 * 
 * Handles all Supabase operations for the camera and gallery pages.
 */

import { createClient } from '@supabase/supabase-js';
import { Event, Capture, ReserveCaptureResponse, GenerateZipResponse } from '../../../shared/types/index';

// Supabase configuration
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

// Initialize Supabase client
const supabase = createClient(supabaseUrl, supabaseAnonKey);

// ============================================================================
// Type mapping helpers (snake_case DB → camelCase TypeScript)
// ============================================================================

function mapEventFromDB(row: Record<string, unknown>): Event {
    return {
        id: row.id as string,
        slug: row.slug as string,
        name: row.name as string,
        plan: row.plan as Event['plan'],
        photoLimit: row.photo_limit as number,
        validityDays: row.validity_days as number,
        hasCloudAlbum: row.has_cloud_album as boolean,
        startDate: row.start_date as string,
        endDate: row.end_date as string,
        status: row.status as Event['status'],
        captureCount: row.capture_count as number,
        reservedCount: row.reserved_count as number,
        frameDesign: row.frame_design as Event['frameDesign'],
        galleryToken: row.gallery_token as string,
        galleryExpiresAt: row.gallery_expires_at as string,
        analytics: row.analytics as Event['analytics'],
        createdAt: row.created_at as string,
        updatedAt: row.updated_at as string,
        deployedAt: row.deployed_at as string | undefined,
    };
}

function mapCaptureFromDB(row: Record<string, unknown>): Capture {
    return {
        id: row.id as string,
        eventId: row.event_id as string,
        captureNumber: row.capture_number as number,
        timestamp: row.timestamp as string,
        storageUrl: row.storage_url as string | undefined,
        storagePath: row.storage_path as string | undefined,
        deviceSaved: row.device_saved as boolean,
        uploadedToCloud: row.uploaded_to_cloud as boolean,
        originalSize: row.original_size as number | undefined,
        compressedSize: row.compressed_size as number | undefined,
        dimensions: row.width && row.height
            ? { width: row.width as number, height: row.height as number }
            : undefined,
    };
}

// ============================================================================
// EVENT QUERIES
// ============================================================================

/**
 * Get event by slug (Camera page uses this)
 */
export async function getEventBySlug(slug: string): Promise<Event | null> {
    try {
        const { data, error } = await supabase
            .from('events')
            .select('*')
            .eq('slug', slug)
            .single();

        if (error || !data) return null;
        return mapEventFromDB(data);
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
        const { data, error } = await supabase
            .from('events')
            .select('*')
            .eq('id', eventId)
            .single();

        if (error || !data) return null;
        return mapEventFromDB(data);
    } catch (error) {
        console.error('Error getting event by ID:', error);
        throw error;
    }
}

// ============================================================================
// CAPTURE OPERATIONS (via Edge Functions)
// ============================================================================

/**
 * Reserve a capture slot (calls Edge Function)
 */
export async function reserveCapture(eventId: string): Promise<ReserveCaptureResponse> {
    try {
        const { data, error } = await supabase.functions.invoke('reserve-capture', {
            body: { eventId }
        });

        if (error) throw new Error(error.message || 'Failed to reserve capture slot');
        return data as ReserveCaptureResponse;
    } catch (error: unknown) {
        const message = error instanceof Error ? error.message : 'Failed to reserve capture slot';
        console.error('Error reserving capture:', error);
        throw new Error(message);
    }
}

/**
 * Upload photo to Supabase Storage
 */
export async function uploadPhoto(
    eventId: string,
    captureNumber: number,
    photoBlob: Blob
): Promise<string> {
    try {
        const filename = `${captureNumber}_${Date.now()}.jpg`;
        const storagePath = `${eventId}/${filename}`;

        // Upload to 'photos' bucket
        const { error: uploadError } = await supabase.storage
            .from('photos')
            .upload(storagePath, photoBlob, {
                contentType: 'image/jpeg',
                upsert: false
            });

        if (uploadError) throw uploadError;

        // Get public URL
        const { data: urlData } = supabase.storage
            .from('photos')
            .getPublicUrl(storagePath);

        return urlData.publicUrl;
    } catch (error) {
        console.error('Error uploading photo:', error);
        throw error;
    }
}

// ============================================================================
// GALLERY OPERATIONS
// ============================================================================

/**
 * Get all captures for an event (Gallery page)
 */
export async function getEventCaptures(eventId: string): Promise<Capture[]> {
    try {
        const { data, error } = await supabase
            .from('captures')
            .select('*')
            .eq('event_id', eventId)
            .eq('uploaded_to_cloud', true)
            .order('capture_number', { ascending: true });

        if (error) throw error;
        return (data || []).map(mapCaptureFromDB);
    } catch (error) {
        console.error('Error getting event captures:', error);
        throw error;
    }
}

/**
 * Generate album ZIP (calls Edge Function)
 */
export async function generateAlbumZip(
    eventId: string,
    galleryToken: string
): Promise<GenerateZipResponse> {
    try {
        const { data, error } = await supabase.functions.invoke('generate-album-zip', {
            body: { eventId, galleryToken }
        });

        if (error) throw new Error(error.message || 'Failed to generate album ZIP');
        return data as GenerateZipResponse;
    } catch (error: unknown) {
        const message = error instanceof Error ? error.message : 'Failed to generate album ZIP';
        console.error('Error generating album ZIP:', error);
        throw new Error(message);
    }
}

// ============================================================================
// HELPER FUNCTIONS (unchanged from firebaseService.ts)
// ============================================================================

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
