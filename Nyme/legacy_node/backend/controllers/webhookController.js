// backend/controllers/webhookController.js
const crypto = require('crypto');

const verifySignature = (req, res, buf, encoding) => {
    const signature = req.headers['x-hub-signature-256'];
    if (!signature) return false;

    const hash = crypto
        .createHmac('sha256', process.env.META_APP_SECRET)
        .update(buf)
        .digest('hex');

    return signature === `sha256=${hash}`;
};

const handleWebhook = async (req, res) => {
    // 1. Verificación de reto (Verification Request) para la configuración inicial
    if (req.query['hub.mode'] === 'subscribe') {
        if (req.query['hub.verify_token'] === process.env.META_VERIFY_TOKEN) {
            return res.status(200).send(req.query['hub.challenge']);
        }
        return res.sendStatus(403);
    }

    // 2. Procesamiento de Mensajes (Event Notifications)
    const body = req.body;

    if (body.object === 'whatsapp_business_account') {
        // Responder 200 inmediatamente como pide Meta
        res.status(200).send('EVENT_RECEIVED');

        // Procesar asíncronamente
        processIncoming(body);
    } else {
        res.sendStatus(404);
    }
};

const processIncoming = (data) => {
    try {
        const entry = data.entry?.[0];
        const changes = entry?.changes?.[0];
        const value = changes?.value;

        if (value?.messages) {
            const message = value.messages[0];
            const contact = value.contacts?.[0];

            console.log('--- NUEVO MENSAJE RECIBIDO (INBOUND) ---');
            console.log(`De: ${contact?.wa_id} (${contact?.profile?.name})`);
            console.log(`Contenido: ${message.text?.body || 'Multimedia/Otro'}`);
            
            // Aquí se dispararía la lógica de base de datos y Socket.io
        }
        
        if (value?.statuses) {
            // Manejar confirmaciones de lectura/entrega
            console.log('Actualización de estado de mensaje:', value.statuses[0].status);
        }
    } catch (error) {
        console.error('Error procesando webhook data:', error);
    }
};

module.exports = { handleWebhook, verifySignature };
