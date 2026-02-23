/**
 * Reserve Capture Cloud Function
 * 
 * This function handles the atomic reservation of a photo capture slot.
 * It uses Firestore transactions to ensure thread-safety and prevent race conditions.
 */

import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';
import { Event, ReserveCaptureRequest, ReserveCaptureResponse } from '../../../shared/types/index';
import { validateCapture, getHourFromTimestamp, shouldExpireEvent } from './utils/validation';

const db = admin.firestore();

/**
 * Reserve a capture slot for an event
 * 
 * This function:
 * 1. Validates the event exists and is active
 * 2. Checks photo limits and date ranges
 * 3. Atomically increments the capture counter
 * 4. Updates analytics (peak hour, total captures)
 * 5. Auto-expires event if limit reached or date passed
 */
export const reserveCapture = functions.https.onCall(
    async (data: ReserveCaptureRequest, context): Promise<ReserveCaptureResponse> => {
        const { eventId } = data;

        if (!eventId) {
            throw new functions.https.HttpsError(
                'invalid-argument',
                'Event ID is required'
            );
        }

        const eventRef = db.collection('events').doc(eventId);

        try {
            // Use transaction for atomic operations
            const result = await db.runTransaction(async (transaction) => {
                const eventDoc = await transaction.get(eventRef);

                if (!eventDoc.exists) {
                    throw new functions.https.HttpsError(
                        'not-found',
                        'Event not found'
                    );
                }

                const event = eventDoc.data() as Event;

                // Validate if capture is allowed
                const validation = validateCapture(event);

                if (!validation.canCapture) {
                    return {
                        success: false,
                        message: validation.reason,
                        event: validation.event
                    };
                }

                // Calculate new values
                const newCaptureCount = event.captureCount + 1;
                const currentHour = getHourFromTimestamp(new Date().toISOString());
                const now = new Date().toISOString();

                // Update analytics
                const analytics = event.analytics || {
                    totalCaptures: 0,
                    peakHour: currentHour,
                    lastCaptureAt: now
                };

                analytics.totalCaptures += 1;
                analytics.lastCaptureAt = now;

                // Update peak hour if this hour has more captures
                // (simplified: we just track the hour of the latest capture)
                analytics.peakHour = currentHour;

                // Prepare update data
                const updateData: Partial<Event> = {
                    captureCount: newCaptureCount,
                    analytics,
                    updatedAt: now
                };

                // Check if event should be auto-expired
                const updatedEvent = { ...event, ...updateData };
                if (shouldExpireEvent(updatedEvent)) {
                    updateData.status = 'expired';

                    // Set gallery expiration date (15 days from now)
                    const galleryExpiresAt = new Date();
                    galleryExpiresAt.setDate(galleryExpiresAt.getDate() + 15);
                    updateData.galleryExpiresAt = galleryExpiresAt.toISOString();
                }

                // Perform atomic update
                transaction.update(eventRef, updateData);

                return {
                    success: true,
                    captureNumber: newCaptureCount,
                    event: {
                        captureCount: newCaptureCount,
                        photoLimit: event.photoLimit,
                        status: updateData.status || event.status
                    }
                };
            });

            return result;

        } catch (error: any) {
            console.error('Error in reserveCapture:', error);

            // Re-throw HttpsError
            if (error instanceof functions.https.HttpsError) {
                throw error;
            }

            // Wrap other errors
            throw new functions.https.HttpsError(
                'internal',
                'Failed to reserve capture slot',
                error.message
            );
        }
    }
);

/**
 * Reserve a capture slot with retry buffer
 * 
 * This version reserves a slot temporarily to handle network retries.
 * The reserved slot is released after a timeout if not confirmed.
 */
export const reserveCaptureWithBuffer = functions.https.onCall(
    async (data: ReserveCaptureRequest, context): Promise<ReserveCaptureResponse> => {
        const { eventId } = data;

        if (!eventId) {
            throw new functions.https.HttpsError(
                'invalid-argument',
                'Event ID is required'
            );
        }

        const eventRef = db.collection('events').doc(eventId);

        try {
            const result = await db.runTransaction(async (transaction) => {
                const eventDoc = await transaction.get(eventRef);

                if (!eventDoc.exists) {
                    throw new functions.https.HttpsError(
                        'not-found',
                        'Event not found'
                    );
                }

                const event = eventDoc.data() as Event;

                // Validate if capture is allowed
                const validation = validateCapture(event);

                if (!validation.canCapture) {
                    return {
                        success: false,
                        message: validation.reason,
                        event: validation.event
                    };
                }

                // Reserve a slot (increment reservedCount)
                const newReservedCount = (event.reservedCount || 0) + 1;
                const now = new Date().toISOString();

                transaction.update(eventRef, {
                    reservedCount: newReservedCount,
                    updatedAt: now
                });

                return {
                    success: true,
                    captureNumber: event.captureCount + newReservedCount,
                    event: {
                        captureCount: event.captureCount,
                        photoLimit: event.photoLimit,
                        status: event.status
                    }
                };
            });

            return result;

        } catch (error: any) {
            console.error('Error in reserveCaptureWithBuffer:', error);

            if (error instanceof functions.https.HttpsError) {
                throw error;
            }

            throw new functions.https.HttpsError(
                'internal',
                'Failed to reserve capture slot',
                error.message
            );
        }
    }
);

/**
 * Confirm a reserved capture
 * 
 * Converts a reserved slot into an actual capture.
 */
export const confirmCapture = functions.https.onCall(
    async (data: { eventId: string }, context): Promise<ReserveCaptureResponse> => {
        const { eventId } = data;

        if (!eventId) {
            throw new functions.https.HttpsError(
                'invalid-argument',
                'Event ID is required'
            );
        }

        const eventRef = db.collection('events').doc(eventId);

        try {
            const result = await db.runTransaction(async (transaction) => {
                const eventDoc = await transaction.get(eventRef);

                if (!eventDoc.exists) {
                    throw new functions.https.HttpsError(
                        'not-found',
                        'Event not found'
                    );
                }

                const event = eventDoc.data() as Event;

                // Convert reserved slot to actual capture
                const newCaptureCount = event.captureCount + 1;
                const newReservedCount = Math.max(0, (event.reservedCount || 0) - 1);
                const currentHour = getHourFromTimestamp(new Date().toISOString());
                const now = new Date().toISOString();

                // Update analytics
                const analytics = event.analytics || {
                    totalCaptures: 0,
                    peakHour: currentHour,
                    lastCaptureAt: now
                };

                analytics.totalCaptures += 1;
                analytics.lastCaptureAt = now;
                analytics.peakHour = currentHour;

                const updateData: Partial<Event> = {
                    captureCount: newCaptureCount,
                    reservedCount: newReservedCount,
                    analytics,
                    updatedAt: now
                };

                // Check if event should be auto-expired
                const updatedEvent = { ...event, ...updateData };
                if (shouldExpireEvent(updatedEvent)) {
                    updateData.status = 'expired';

                    const galleryExpiresAt = new Date();
                    galleryExpiresAt.setDate(galleryExpiresAt.getDate() + 15);
                    updateData.galleryExpiresAt = galleryExpiresAt.toISOString();
                }

                transaction.update(eventRef, updateData);

                return {
                    success: true,
                    captureNumber: newCaptureCount,
                    event: {
                        captureCount: newCaptureCount,
                        photoLimit: event.photoLimit,
                        status: updateData.status || event.status
                    }
                };
            });

            return result;

        } catch (error: any) {
            console.error('Error in confirmCapture:', error);

            if (error instanceof functions.https.HttpsError) {
                throw error;
            }

            throw new functions.https.HttpsError(
                'internal',
                'Failed to confirm capture',
                error.message
            );
        }
    }
);
