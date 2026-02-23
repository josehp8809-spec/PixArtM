/**
 * Generate Album ZIP Cloud Function
 * 
 * Creates a downloadable ZIP file containing all photos from an event.
 * Implements caching to reduce bandwidth costs.
 */

import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';
import archiver from 'archiver';
import { Event, GenerateZipRequest, GenerateZipResponse } from '../../../shared/types/index';

const db = admin.firestore();
const storage = admin.storage();

/**
 * Generate a ZIP file of all event photos
 * 
 * This function:
 * 1. Validates gallery token
 * 2. Checks if ZIP is already cached
 * 3. Fetches all photos from Storage
 * 4. Creates ZIP archive
 * 5. Uploads ZIP to Storage
 * 6. Returns signed download URL (valid for 24 hours)
 */
export const generateAlbumZip = functions
    .runWith({
        timeoutSeconds: 540, // 9 minutes (max for HTTP functions)
        memory: '2GB' // Increased memory for large albums
    })
    .https.onCall(
        async (data: GenerateZipRequest, context): Promise<GenerateZipResponse> => {
            const { eventId, galleryToken } = data;

            if (!eventId || !galleryToken) {
                throw new functions.https.HttpsError(
                    'invalid-argument',
                    'Event ID and gallery token are required'
                );
            }

            try {
                // Validate event and gallery token
                const eventDoc = await db.collection('events').doc(eventId).get();

                if (!eventDoc.exists) {
                    throw new functions.https.HttpsError(
                        'not-found',
                        'Event not found'
                    );
                }

                const event = eventDoc.data() as Event;

                // Verify gallery token
                if (event.galleryToken !== galleryToken) {
                    throw new functions.https.HttpsError(
                        'permission-denied',
                        'Invalid gallery token'
                    );
                }

                // Check if event has cloud album
                if (!event.hasCloudAlbum) {
                    throw new functions.https.HttpsError(
                        'failed-precondition',
                        'This event does not have cloud album feature'
                    );
                }

                // Check if gallery is still accessible
                if (event.status === 'cleaned') {
                    throw new functions.https.HttpsError(
                        'failed-precondition',
                        'Gallery has been cleaned up'
                    );
                }

                const now = new Date();
                const galleryExpiresAt = event.galleryExpiresAt ? new Date(event.galleryExpiresAt) : new Date();

                if (now > galleryExpiresAt) {
                    throw new functions.https.HttpsError(
                        'failed-precondition',
                        'Gallery has expired'
                    );
                }

                // Check if ZIP already exists and is recent (< 24 hours)
                const zipPath = `zips/${eventId}/album.zip`;
                const bucket = storage.bucket();
                const zipFile = bucket.file(zipPath);

                try {
                    const [exists] = await zipFile.exists();
                    if (exists) {
                        const [metadata] = await zipFile.getMetadata();
                        const createdAt = metadata.timeCreated ? new Date(metadata.timeCreated) : new Date();
                        const ageHours = (now.getTime() - createdAt.getTime()) / (1000 * 60 * 60);

                        // If ZIP is less than 24 hours old, return cached version
                        if (ageHours < 24) {
                            const [url] = await zipFile.getSignedUrl({
                                action: 'read',
                                expires: Date.now() + 24 * 60 * 60 * 1000 // 24 hours
                            });

                            const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000);

                            return {
                                success: true,
                                downloadUrl: url,
                                expiresAt: expiresAt.toISOString(),
                                message: 'Using cached ZIP'
                            };
                        }
                    }
                } catch (error) {
                    // ZIP doesn't exist, continue to create it
                    console.log('No cached ZIP found, creating new one');
                }

                // Fetch all captures for this event
                const capturesSnapshot = await db
                    .collection('events')
                    .doc(eventId)
                    .collection('captures')
                    .where('uploadedToCloud', '==', true)
                    .orderBy('captureNumber', 'asc')
                    .get();

                if (capturesSnapshot.empty) {
                    throw new functions.https.HttpsError(
                        'not-found',
                        'No photos found in cloud album'
                    );
                }

                // Create ZIP archive
                const archive = archiver('zip', {
                    zlib: { level: 6 } // Compression level (0-9)
                });

                const zipStream = zipFile.createWriteStream({
                    metadata: {
                        contentType: 'application/zip',
                        metadata: {
                            eventId,
                            createdAt: now.toISOString(),
                            photoCount: capturesSnapshot.size.toString()
                        }
                    }
                });

                // Pipe archive to upload stream
                archive.pipe(zipStream);

                // Add each photo to the archive
                let photoCount = 0;
                for (const captureDoc of capturesSnapshot.docs) {
                    const capture = captureDoc.data();

                    if (capture.storagePath) {
                        try {
                            const photoFile = bucket.file(capture.storagePath);
                            const [photoExists] = await photoFile.exists();

                            if (photoExists) {
                                const photoStream = photoFile.createReadStream();
                                const fileName = `photo_${String(capture.captureNumber).padStart(4, '0')}.jpg`;

                                archive.append(photoStream, { name: fileName });
                                photoCount++;
                            }
                        } catch (error) {
                            console.error(`Error adding photo ${capture.captureNumber}:`, error);
                            // Continue with other photos
                        }
                    }
                }

                if (photoCount === 0) {
                    throw new functions.https.HttpsError(
                        'not-found',
                        'No accessible photos found'
                    );
                }

                // Finalize the archive
                await archive.finalize();

                // Wait for upload to complete
                await new Promise((resolve, reject) => {
                    zipStream.on('finish', resolve);
                    zipStream.on('error', reject);
                });

                // Generate signed URL
                const [url] = await zipFile.getSignedUrl({
                    action: 'read',
                    expires: Date.now() + 24 * 60 * 60 * 1000 // 24 hours
                });

                const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000);

                return {
                    success: true,
                    downloadUrl: url,
                    expiresAt: expiresAt.toISOString(),
                    message: `ZIP created with ${photoCount} photos`
                };

            } catch (error: any) {
                console.error('Error in generateAlbumZip:', error);

                if (error instanceof functions.https.HttpsError) {
                    throw error;
                }

                throw new functions.https.HttpsError(
                    'internal',
                    'Failed to generate album ZIP',
                    error.message
                );
            }
        }
    );
