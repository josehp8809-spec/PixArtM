/**
 * Auto-Cleanup — Supabase Edge Function
 * Replaces: Firebase Cloud Function 'autoCleanup'
 * 
 * Deletes expired galleries and photos from Storage.
 * Designed to be called by pg_cron or an external scheduler.
 * 
 * Schedule: Daily at 2 AM (configure via Supabase Dashboard → Database → Extensions → pg_cron)
 * Example cron: SELECT cron.schedule('auto-cleanup', '0 2 * * *', $$SELECT net.http_post(...)$$);
 */

import { serve } from 'https://deno.land/std@0.177.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req: Request) => {
    if (req.method === 'OPTIONS') {
        return new Response('ok', { headers: corsHeaders });
    }

    try {
        const supabase = createClient(
            Deno.env.get('SUPABASE_URL')!,
            Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
        );

        const now = new Date();
        let eventsProcessed = 0;
        let eventsCleanedSuccess = 0;
        let eventsCleanedFailed = 0;
        let totalPhotosDeleted = 0;
        let totalZipsDeleted = 0;

        console.log('Starting auto-cleanup process...');

        // Find expired events whose gallery has passed expiration
        const { data: expiredEvents, error: fetchError } = await supabase
            .from('events')
            .select('*')
            .eq('status', 'expired')
            .lt('gallery_expires_at', now.toISOString());

        if (fetchError) {
            throw new Error(`Failed to fetch expired events: ${fetchError.message}`);
        }

        console.log(`Found ${expiredEvents?.length || 0} expired events to clean`);

        for (const event of (expiredEvents || [])) {
            eventsProcessed++;

            try {
                // List and delete all photos for this event
                const { data: files } = await supabase.storage
                    .from('photos')
                    .list(event.id);

                if (files && files.length > 0) {
                    const filePaths = files.map((f: { name: string }) => `${event.id}/${f.name}`);
                    const { error: deleteError } = await supabase.storage
                        .from('photos')
                        .remove(filePaths);

                    if (!deleteError) {
                        totalPhotosDeleted += files.length;
                        console.log(`Deleted ${files.length} photos from event ${event.id}`);
                    } else {
                        console.error(`Error deleting photos for event ${event.id}:`, deleteError);
                    }
                }

                // Delete ZIP archive if exists
                const { error: zipDeleteError } = await supabase.storage
                    .from('zips')
                    .remove([`${event.id}/album.zip`]);

                if (!zipDeleteError) {
                    totalZipsDeleted++;
                }

                // Delete captures from database
                const { error: capturesDeleteError } = await supabase
                    .from('captures')
                    .delete()
                    .eq('event_id', event.id);

                if (capturesDeleteError) {
                    console.error(`Error deleting captures for event ${event.id}:`, capturesDeleteError);
                }

                // Update event status to 'cleaned'
                await supabase
                    .from('events')
                    .update({ status: 'cleaned' })
                    .eq('id', event.id);

                console.log(`Successfully cleaned event ${event.id} (${event.name})`);
                eventsCleanedSuccess++;

            } catch (err) {
                console.error(`Error cleaning event ${event.id}:`, err);
                eventsCleanedFailed++;

                // Log error
                await supabase.from('cleanup_errors').insert({
                    event_id: event.id,
                    event_name: event.name,
                    error: err instanceof Error ? err.message : String(err),
                });
            }
        }

        // Log cleanup summary
        const summary = {
            events_processed: eventsProcessed,
            events_cleaned_success: eventsCleanedSuccess,
            events_cleaned_failed: eventsCleanedFailed,
            total_photos_deleted: totalPhotosDeleted,
            total_zips_deleted: totalZipsDeleted,
        };

        await supabase.from('cleanup_logs').insert(summary);

        console.log('Cleanup summary:', summary);

        return new Response(
            JSON.stringify({ success: true, ...summary }),
            { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );

    } catch (error: unknown) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        console.error('Fatal error in auto-cleanup:', message);

        return new Response(
            JSON.stringify({ success: false, message: 'Cleanup failed' }),
            { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
    }
});
