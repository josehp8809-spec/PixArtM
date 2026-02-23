/**
 * Image Processing Utilities
 * 
 * Handles image compression and resizing for optimal storage and bandwidth usage.
 * Target: Max 1920px width, 85% quality, ~500KB per image
 */

export interface ImageCompressionResult {
    blob: Blob;
    originalSize: number;
    compressedSize: number;
    dimensions: {
        width: number;
        height: number;
    };
    compressionRatio: number;
}

/**
 * Compress an image to reduce file size
 * 
 * @param blob - Original image blob
 * @param maxWidth - Maximum width (default: 1920px)
 * @param quality - JPEG quality 0-1 (default: 0.85)
 * @returns Compressed image blob with metadata
 */
export async function compressImage(
    blob: Blob,
    maxWidth: number = 1920,
    quality: number = 0.85
): Promise<ImageCompressionResult> {
    return new Promise((resolve, reject) => {
        const originalSize = blob.size;

        // Create image element
        const img = new Image();
        const reader = new FileReader();

        reader.onload = (e) => {
            if (!e.target?.result) {
                reject(new Error('Failed to read image file'));
                return;
            }

            img.onload = () => {
                try {
                    // Calculate new dimensions
                    let width = img.width;
                    let height = img.height;

                    if (width > maxWidth) {
                        height = Math.round((height * maxWidth) / width);
                        width = maxWidth;
                    }

                    // Create canvas
                    const canvas = document.createElement('canvas');
                    canvas.width = width;
                    canvas.height = height;

                    const ctx = canvas.getContext('2d');
                    if (!ctx) {
                        reject(new Error('Failed to get canvas context'));
                        return;
                    }

                    // Draw and compress
                    ctx.drawImage(img, 0, 0, width, height);

                    canvas.toBlob(
                        (blob) => {
                            if (!blob) {
                                reject(new Error('Failed to create blob'));
                                return;
                            }

                            const compressedSize = blob.size;
                            const compressionRatio = originalSize / compressedSize;

                            resolve({
                                blob,
                                originalSize,
                                compressedSize,
                                dimensions: { width, height },
                                compressionRatio
                            });
                        },
                        'image/jpeg',
                        quality
                    );
                } catch (error) {
                    reject(error);
                }
            };

            img.onerror = () => {
                reject(new Error('Failed to load image'));
            };

            img.src = e.target.result as string;
        };

        reader.onerror = () => {
            reject(new Error('Failed to read file'));
        };

        reader.readAsDataURL(blob);
    });
}

/**
 * Apply frame overlay to an image
 * 
 * @param imageBlob - Compressed image blob
 * @param frameUrl - URL to frame overlay image
 * @returns New blob with frame applied
 */
export async function applyFrameOverlay(
    imageBlob: Blob,
    frameUrl: string
): Promise<Blob> {
    return new Promise((resolve, reject) => {
        const img = new Image();
        const frame = new Image();

        let imageLoaded = false;
        let frameLoaded = false;

        const checkBothLoaded = () => {
            if (imageLoaded && frameLoaded) {
                try {
                    // Create canvas with image dimensions
                    const canvas = document.createElement('canvas');
                    canvas.width = img.width;
                    canvas.height = img.height;

                    const ctx = canvas.getContext('2d');
                    if (!ctx) {
                        reject(new Error('Failed to get canvas context'));
                        return;
                    }

                    // Draw image first
                    ctx.drawImage(img, 0, 0);

                    // Draw frame overlay on top
                    ctx.drawImage(frame, 0, 0, canvas.width, canvas.height);

                    canvas.toBlob(
                        (blob) => {
                            if (!blob) {
                                reject(new Error('Failed to create blob with frame'));
                                return;
                            }
                            resolve(blob);
                        },
                        'image/jpeg',
                        0.85
                    );
                } catch (error) {
                    reject(error);
                }
            }
        };

        img.onload = () => {
            imageLoaded = true;
            checkBothLoaded();
        };

        frame.onload = () => {
            frameLoaded = true;
            checkBothLoaded();
        };

        img.onerror = () => reject(new Error('Failed to load image'));
        frame.onerror = () => reject(new Error('Failed to load frame'));

        // Load image from blob
        const imageUrl = URL.createObjectURL(imageBlob);
        img.src = imageUrl;

        // Load frame
        frame.src = frameUrl;
    });
}

/**
 * Download blob to device
 * 
 * @param blob - Image blob
 * @param filename - Filename for download
 */
export function downloadToDevice(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Convert blob to File
 * 
 * @param blob - Image blob
 * @param filename - Filename
 * @returns File object
 */
export function blobToFile(blob: Blob, filename: string): File {
    return new File([blob], filename, { type: blob.type });
}

/**
 * Format file size for display
 * 
 * @param bytes - Size in bytes
 * @returns Formatted string (e.g., "1.5 MB")
 */
export function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}
