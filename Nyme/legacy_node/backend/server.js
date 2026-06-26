// backend/server.js
require('dotenv').config();
const express = require('express');
const { handleWebhook, verifySignature } = require('./controllers/webhookController');
const checkQuota = require('./middleware/quotaMiddleware');
const metaService = require('./services/metaService');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware para obtener el raw body (necesario para validar la firma de Meta)
app.use(express.json({
    verify: (req, res, buf, encoding) => {
        if (req.originalUrl.startsWith('/webhook')) {
            req.rawBody = buf;
        }
    }
}));

// --- RUTAS ---

// 1. Webhook (Validación y Recepción)
app.all('/webhook', handleWebhook);

// 2. Envío de Mensajes (Con control de cuotas)
app.post('/api/messages/send', checkQuota, async (req, res) => {
    const { to, type, body, templateName, components } = req.body;

    try {
        let result;
        if (type === 'OUTBOUND_INIT') {
            result = await metaService.sendTemplate(to, templateName, 'es_MX', components);
            // IMPORTANTE: Aquí guardarías el log en quota_logs
        } else {
            result = await metaService.sendText(to, body);
        }

        res.status(200).json({ success: true, data: result });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Health Check
app.get('/health', (req, res) => res.send('Nyme Backend Online 🚀'));

app.listen(PORT, () => {
    console.log(`Servidor Nyme corriendo en http://localhost:${PORT}`);
});
