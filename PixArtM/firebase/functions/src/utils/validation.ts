/**
 * Validation utilities for Firebase Cloud Functions
 */

import { Event, EventStatus } from '../../../../shared/types/index';

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
 * Check if event has available slots (considering reserved slots)
 */
export function hasAvailableSlots(event: Event): boolean {
    const totalUsed = event.captureCount + (event.reservedCount || 0);
    return totalUsed < event.photoLimit;
}

/**
 * Validate if a capture can be reserved
 */
export interface CaptureValidationResult {
    canCapture: boolean;
    reason?: string;
    event?: {
        captureCount: number;
        photoLimit: number;
        status: EventStatus;
    };
}

export function validateCapture(event: Event | null): CaptureValidationResult {
    if (!event) {
        return {
            canCapture: false,
            reason: 'Event not found'
        };
    }

    if (event.status === 'cleaned') {
        return {
            canCapture: false,
            reason: 'Event has been cleaned up',
            event: {
                captureCount: event.captureCount,
                photoLimit: event.photoLimit,
                status: event.status
            }
        };
    }

    if (event.status === 'expired') {
        return {
            canCapture: false,
            reason: 'Event has expired',
            event: {
                captureCount: event.captureCount,
                photoLimit: event.photoLimit,
                status: event.status
            }
        };
    }

    if (!isEventActive(event)) {
        const now = new Date();
        const startDate = new Date(event.startDate);

        if (now < startDate) {
            return {
                canCapture: false,
                reason: 'Event has not started yet',
                event: {
                    captureCount: event.captureCount,
                    photoLimit: event.photoLimit,
                    status: event.status
                }
            };
        } else {
            return {
                canCapture: false,
                reason: 'Event has ended',
                event: {
                    captureCount: event.captureCount,
                    photoLimit: event.photoLimit,
                    status: event.status
                }
            };
        }
    }

    if (hasReachedLimit(event)) {
        return {
            canCapture: false,
            reason: 'Photo limit reached',
            event: {
                captureCount: event.captureCount,
                photoLimit: event.photoLimit,
                status: event.status
            }
        };
    }

    if (!hasAvailableSlots(event)) {
        return {
            canCapture: false,
            reason: 'No available slots (some are reserved)',
            event: {
                captureCount: event.captureCount,
                photoLimit: event.photoLimit,
                status: event.status
            }
        };
    }

    return {
        canCapture: true,
        event: {
            captureCount: event.captureCount,
            photoLimit: event.photoLimit,
            status: event.status
        }
    };
}

/**
 * Calculate peak hour from timestamp
 */
export function getHourFromTimestamp(timestamp: string): number {
    const date = new Date(timestamp);
    return date.getHours();
}

/**
 * Check if event should be auto-expired
 */
export function shouldExpireEvent(event: Event): boolean {
    if (event.status !== 'active') {
        return false;
    }

    const now = new Date();
    const endDate = new Date(event.endDate);

    return now > endDate || hasReachedLimit(event);
}

/**
 * Check if gallery should be cleaned
 */
export function shouldCleanGallery(event: Event): boolean {
    if (event.status !== 'expired') {
        return false;
    }

    const now = new Date();
    const galleryExpiresAt = new Date(event.galleryExpiresAt);

    return now > galleryExpiresAt;
}
