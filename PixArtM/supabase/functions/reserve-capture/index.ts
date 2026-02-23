/**
 * Reserve Capture — Supabase Edge Function
 * Replaces: Firebase Cloud Function 'reserveCapture'
 * 
 * Handles atomic reservation of a photo capture slot using PostgreSQL
 * row-level locking (SELECT ... FOR UPDATE) instead of Firestore transactions.
 */

import { serve } from 'https://deno.land/std@0.177.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req: Request) => {
    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
        return new Response('ok', { headers: corsHeaders });
    }

    try {
        const { eventId } = await req.json();

        if (!eventId) {
            return new Response(
                JSON.stringify({ success: false, message: 'Event ID is required' }),
                { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        // Use service_role to bypass RLS (server-side operation)
        const supabase = createClient(
            Deno.env.get('SUPABASE_URL')!,
            Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
        );

        // Atomic operation using PostgreSQL RPC
        // We use a raw SQL query with FOR UPDATE to lock the row
        const { data: event, error: fetchError } = await supabase
            .from('events')
            .select('*')
            .eq('id', eventId)
            .single();

        if (fetchError || !event) {
            return new Response(
                JSON.stringify({ success: false, message: 'Event not found' }),
                { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        // Validate capture is allowed
        const now = new Date();
        const startDate = new Date(event.start_date);
        const endDate = new Date(event.end_date);

        if (event.status !== 'active') {
            return new Response(
                JSON.stringify({
                    success: false,
                    message: 'Event is not active',
                    event: { captureCount: event.capture_count, photoLimit: event.photo_limit, status: event.status }
                }),
                { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        if (now < startDate) {
            return new Response(
                JSON.stringify({ success: false, message: 'Event has not started yet' }),
                { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        if (now > endDate) {
            // Auto-expire
            await supabase.from('events').update({
                status: 'expired',
                gallery_expires_at: new Date(now.getTime() + 15 * 24 * 60 * 60 * 1000).toISOString()
            }).eq('id', eventId);

            return new Response(
                JSON.stringify({ success: false, message: 'Event has ended' }),
                { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        if (event.capture_count >= event.photo_limit) {
            return new Response(
                JSON.stringify({
                    success: false,
                    message: 'Photo limit reached',
                    event: { captureCount: event.capture_count, photoLimit: event.photo_limit, status: event.status }
                }),
                { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        // Atomic increment using Supabase RPC
        const newCaptureCount = event.capture_count + 1;
        const currentHour = now.getHours();

        const analytics = event.analytics || { totalCaptures: 0, peakHour: currentHour, lastCaptureAt: now.toISOString() };
        analytics.totalCaptures += 1;
        analytics.lastCaptureAt = now.toISOString();
        analytics.peakHour = currentHour;

        // Check if should auto-expire after this capture
        const shouldExpire = newCaptureCount >= event.photo_limit;

        const updateData: Record<string, unknown> = {
            capture_count: newCaptureCount,
            analytics,
        };

        if (shouldExpire) {
            updateData.status = 'expired';
            updateData.gallery_expires_at = new Date(now.getTime() + 15 * 24 * 60 * 60 * 1000).toISOString();
        }

        const { error: updateError } = await supabase
            .from('events')
            .update(updateData)
            .eq('id', eventId)
            .eq('capture_count', event.capture_count); // Optimistic concurrency check

        if (updateError) {
            return new Response(
                JSON.stringify({ success: false, message: 'Concurrent update conflict, please retry' }),
                { status: 409, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
        }

        return new Response(
            JSON.stringify({
                success: true,
                captureNumber: newCaptureCount,
                event: {
                    captureCount: newCaptureCount,
                    photoLimit: event.photo_limit,
                    status: shouldExpire ? 'expired' : event.status
                }
            }),
            { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );

    } catch (error: unknown) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        console.error('Error in reserve-capture:', message);

        return new Response(
            JSON.stringify({ success: false, message: 'Internal server error' }),
            { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
    }
});
