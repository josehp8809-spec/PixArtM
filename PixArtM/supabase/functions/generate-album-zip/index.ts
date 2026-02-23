/**
 * Generate Album ZIP — Supabase Edge Function
 * Replaces: Firebase Cloud Function 'generateAlbumZip'
 * 
 * Creates a downloadable ZIP of all event photos from Supabase Storage.
 * Implements 24-hour caching to reduce bandwidth costs.
 */

import { serve } from 'https://deno.land/std@0.177.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import { JSZip } from 'https://esm.sh/jszip@3.10.1';

const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req: Request) => {
    if (req.method === 'OPTIONS') {
        return new Response('ok', { headers: corsHeaders });
    }

    try {
        const { eventId, galleryToken } = await req.json();

        if (!eventId || !galleryToken) {
            return new Response(
                JSON.stringify({ success: false, message: 'Event ID and gallery token are required' }),
                { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        const supabase = createClient(
            Deno.env.get('SUPABASE_URL')!,
            Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
        );

        // Fetch and validate event
        const { data: event, error: eventError } = await supabase
            .from('events')
            .select('*')
            .eq('id', eventId)
            .single();

        if (eventError || !event) {
            return new Response(
                JSON.stringify({ success: false, message: 'Event not found' }),
                { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        // Validate gallery token
        if (event.gallery_token !== galleryToken) {
            return new Response(
                JSON.stringify({ success: false, message: 'Invalid gallery token' }),
                { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        if (!event.has_cloud_album) {
            return new Response(
                JSON.stringify({ success: false, message: 'This event does not have cloud album feature' }),
                { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        if (event.status === 'cleaned') {
            return new Response(
                JSON.stringify({ success: false, message: 'Gallery has been cleaned up' }),
                { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        const now = new Date();
        if (event.gallery_expires_at && now > new Date(event.gallery_expires_at)) {
            return new Response(
                JSON.stringify({ success: false, message: 'Gallery has expired' }),
                { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        // Check if cached ZIP exists (< 24 hours old)
        const zipPath = `${eventId}/album.zip`;
        const { data: existingZip } = await supabase.storage
            .from('zips')
            .createSignedUrl(zipPath, 86400); // 24h

        if (existingZip?.signedUrl) {
            return new Response(
                JSON.stringify({
                    success: true,
                    downloadUrl: existingZip.signedUrl,
                    expiresAt: new Date(now.getTime() + 86400000).toISOString(),
                    message: 'Using cached ZIP'
                }),
                { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        // Fetch all cloud captures
        const { data: captures, error: capturesError } = await supabase
            .from('captures')
            .select('*')
            .eq('event_id', eventId)
            .eq('uploaded_to_cloud', true)
            .order('capture_number', { ascending: true });

        if (capturesError || !captures || captures.length === 0) {
            return new Response(
                JSON.stringify({ success: false, message: 'No photos found in cloud album' }),
                { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        // Create ZIP using JSZip
        const zip = new JSZip();
        let photoCount = 0;

        for (const capture of captures) {
            if (capture.storage_path) {
                try {
                    const { data: photoData, error: downloadError } = await supabase.storage
                        .from('photos')
                        .download(capture.storage_path);

                    if (!downloadError && photoData) {
                        const fileName = `photo_${String(capture.capture_number).padStart(4, '0')}.jpg`;
                        const arrayBuffer = await photoData.arrayBuffer();
                        zip.file(fileName, arrayBuffer);
                        photoCount++;
                    }
                } catch (err) {
                    console.error(`Error adding photo ${capture.capture_number}:`, err);
                }
            }
        }

        if (photoCount === 0) {
            return new Response(
                JSON.stringify({ success: false, message: 'No accessible photos found' }),
                { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        // Generate ZIP blob
        const zipBlob = await zip.generateAsync({ type: 'arraybuffer', compression: 'DEFLATE', compressionOptions: { level: 6 } });

        // Upload ZIP to storage
        const { error: uploadError } = await supabase.storage
            .from('zips')
            .upload(zipPath, zipBlob, {
                contentType: 'application/zip',
                upsert: true
            });

        if (uploadError) {
            console.error('Error uploading ZIP:', uploadError);
            return new Response(
                JSON.stringify({ success: false, message: 'Failed to create ZIP archive' }),
                { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        // Generate signed download URL (24 hours)
        const { data: signedUrl } = await supabase.storage
            .from('zips')
            .createSignedUrl(zipPath, 86400);

        return new Response(
            JSON.stringify({
                success: true,
                downloadUrl: signedUrl?.signedUrl || '',
                expiresAt: new Date(now.getTime() + 86400000).toISOString(),
                message: `ZIP created with ${photoCount} photos`
            }),
            { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );

    } catch (error: unknown) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        console.error('Error in generate-album-zip:', message);

        return new Response(
            JSON.stringify({ success: false, message: 'Internal server error' }),
            { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
    }
});
