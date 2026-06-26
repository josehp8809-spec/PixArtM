// backend/middleware/quotaMiddleware.js
// Nota: Se asume que tienes un pool de base de datos (db) configurado
const db = require('../database/db'); 

const checkQuota = async (req, res, next) => {
    const { type } = req.body;

    if (type === 'OUTBOUND_INIT') {
        const currentMonth = new Date().getMonth() + 1;
        const currentYear = new Date().getFullYear();

        try {
            const result = await db.query(
                `SELECT COUNT(*) FROM quota_logs 
                 WHERE type = 'OUTBOUND_INIT' 
                 AND EXTRACT(MONTH FROM sent_at) = $1 
                 AND EXTRACT(YEAR FROM sent_at) = $2`,
                [currentMonth, currentYear]
            );

            const count = parseInt(result.rows[0].count);
            if (count >= 15) {
                return res.status(403).json({ 
                    error: 'Cuota mensual excedida', 
                    message: 'Has alcanzado el límite de 15 mensajes proactivos (templates) este mes.' 
                });
            }
        } catch (error) {
            return res.status(500).json({ error: 'Error verificando cuota' });
        }
    }
    next();
};

module.exports = checkQuota;
