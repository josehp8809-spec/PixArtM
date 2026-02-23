/**
 * Auto-Cleanup Scheduled Function
 * 
 * Runs daily to clean up expired galleries and delete photos from Storage.
 * Critical for cost control.
 */

import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';
import { Event } from '../../../shared/types/index';
import { shouldCleanGallery } from './utils/validation';

const db = admin.firestore();
const storage = admin.storage();

/**
 * Auto-cleanup function that runs daily
 * 
 * This function:
 * 1. Finds all expired events with galleries past expiration (15 days)
 * 2. Deletes all photos from Storage
 * 3. Deletes ZIP archives
 * 4. Updates event status to 'cleaned'
 * 5. Logs cleanup operations
 */
export const autoCleanup = functions.pubsub
    .schedule('every day 02:00') // Runs at 2 AM daily
    .timeZone('America/Mexico_City')
    .onRun(async (context) => {
        console.log('Starting auto-cleanup process...');

        const now = new Date();
        const bucket = storage.bucket();

        let eventsProcessed = 0;
        let eventsCleanedSuccess = 0;
        let eventsCleanedFailed = 0;
        let totalPhotosDeleted = 0;
        let totalZipsDeleted = 0;

        try {
            // Find all expired events that need cleanup
            const expiredEventsSnapshot = await db
                .collection('events')
                .where('status', '==', 'expired')
                .get();

            console.log(`Found ${expiredEventsSnapshot.size} expired events to check`);

            for (const eventDoc of expiredEventsSnapshot.docs) {
                eventsProcessed++;
                const event = eventDoc.data() as Event;

                // Check if gallery should be cleaned
                if (!shouldCleanGallery(event)) {
                    console.log(`Event ${event.id} not ready for cleanup yet`);
                    continue;
                }

                console.log(`Cleaning up event: ${event.id} (${event.name})`);

                try {
                    // Delete all photos from Storage
                    const photosPath = `events/${event.id}/`;
                    const [files] = await bucket.getFiles({ prefix: photosPath });

                    let photosDeleted = 0;
                    for (const file of files) {
                        try {
                            await file.delete();
                            photosDeleted++;
                        } catch (error) {
                            console.error(`Error deleting file ${file.name}:`, error);
                        }
                    }

                    console.log(`Deleted ${photosDeleted} photos from event ${event.id}`);
                    totalPhotosDeleted += photosDeleted;

                    // Delete ZIP archive if exists
                    const zipPath = `zips/${event.id}/album.zip`;
                    const zipFile = bucket.file(zipPath);

                    try {
                        const [exists] = await zipFile.exists();
                        if (exists) {
                            await zipFile.delete();
                            totalZipsDeleted++;
                            console.log(`Deleted ZIP archive for event ${event.id}`);
                        }
                    } catch (error) {
                        console.error(`Error deleting ZIP for event ${event.id}:`, error);
                    }

                    // Update event status to 'cleaned'
                    await db.collection('events').doc(event.id).update({
                        status: 'cleaned',
                        updatedAt: now.toISOString()
                    });

                    // Delete captures subcollection (optional, for data cleanup)
                    const capturesSnapshot = await db
                        .collection('events')
                        .doc(event.id)
                        .collection('captures')
                        .get();

                    const batch = db.batch();
                    let batchCount = 0;

                    for (const captureDoc of capturesSnapshot.docs) {
                        batch.delete(captureDoc.ref);
                        batchCount++;

                        // Firestore batch limit is 500
                        if (batchCount >= 500) {
                            await batch.commit();
                            batchCount = 0;
                        }
                    }

                    if (batchCount > 0) {
                        await batch.commit();
                    }

                    console.log(`Successfully cleaned event ${event.id}`);
                    eventsCleanedSuccess++;

                } catch (error) {
                    console.error(`Error cleaning event ${event.id}:`, error);
                    eventsCleanedFailed++;

                    // Log error to Firestore for monitoring
                    await db.collection('cleanup_errors').add({
                        eventId: event.id,
                        eventName: event.name,
                        error: error instanceof Error ? error.message : String(error),
                        timestamp: now.toISOString()
                    });
                }
            }

            // Log summary
            const summary = {
                timestamp: now.toISOString(),
                eventsProcessed,
                eventsCleanedSuccess,
                eventsCleanedFailed,
                totalPhotosDeleted,
                totalZipsDeleted
            };

            console.log('Cleanup summary:', summary);

            // Store summary in Firestore for monitoring
            await db.collection('cleanup_logs').add(summary);

            return summary;

        } catch (error) {
            console.error('Fatal error in auto-cleanup:', error);

            // Log fatal error
            await db.collection('cleanup_errors').add({
                error: error instanceof Error ? error.message : String(error),
                timestamp: now.toISOString(),
                fatal: true
            });

            throw error;
        }
    });

/**
 * Manual cleanup trigger (for testing or emergency cleanup)
 * 
 * Can be called via HTTP to manually trigger cleanup for a specific event
 */
export const manualCleanup = functions.https.onCall(
    async (data: { eventId: string }, context) => {
        // Only allow authenticated admin users
        if (!context.auth || !context.auth.token.admin) {
            throw new functions.https.HttpsError(
                'permission-denied',
                'Only admins can manually trigger cleanup'
            );
        }

        const { eventId } = data;

        if (!eventId) {
            throw new functions.https.HttpsError(
                'invalid-argument',
                'Event ID is required'
            );
        }

        const bucket = storage.bucket();
        const now = new Date();

        try {
            const eventDoc = await db.collection('events').doc(eventId).get();

            if (!eventDoc.exists) {
                throw new functions.https.HttpsError(
                    'not-found',
                    'Event not found'
                );
            }

            const event = eventDoc.data() as Event;

            // Delete photos
            const photosPath = `events/${eventId}/`;
            const [files] = await bucket.getFiles({ prefix: photosPath });

            let photosDeleted = 0;
            for (const file of files) {
                await file.delete();
                photosDeleted++;
            }

            // Delete ZIP
            const zipPath = `zips/${eventId}/album.zip`;
            const zipFile = bucket.file(zipPath);
            const [exists] = await zipFile.exists();

            if (exists) {
                await zipFile.delete();
            }

            // Update status
            await db.collection('events').doc(eventId).update({
                status: 'cleaned',
                updatedAt: now.toISOString()
            });

            // Delete captures
            const capturesSnapshot = await db
                .collection('events')
                .doc(eventId)
                .collection('captures')
                .get();

            const batch = db.batch();
            for (const captureDoc of capturesSnapshot.docs) {
                batch.delete(captureDoc.ref);
            }
            await batch.commit();

            return {
                success: true,
                eventId,
                photosDeleted,
                message: `Successfully cleaned event ${event.name}`
            };

        } catch (error: any) {
            console.error('Error in manual cleanup:', error);

            if (error instanceof functions.https.HttpsError) {
                throw error;
            }

            throw new functions.https.HttpsError(
                'internal',
                'Failed to clean event',
                error.message
            );
        }
    }
);
