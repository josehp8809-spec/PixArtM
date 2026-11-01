/**
 * Casa Aes - Serverless Function: Gestión y Sincronización de Pedidos en la Nube
 * 
 * Permite recibir pedidos desde el celular de cualquier cliente (POST),
 * consultar todos los pedidos para la administración (GET),
 * o consultar un pedido individual para el rastreo del cliente (GET ?id=AES-XXXX).
 * Cuenta con auto-restauración para tolerar los reinicios fríos (cold starts) de Vercel.
 */

// Memoria global temporal compartida por instancia de Vercel
let cloudOrders = [];

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,POST,PUT,DELETE');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization'
  );

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // 1. GET: Consultar todos los pedidos O consultar uno específico por id/folio
  if (req.method === 'GET') {
    const { id, folio } = req.query || {};
    const searchKey = id || folio;

    // Si el cliente pide rastrear un pedido específico
    if (searchKey) {
      const cleanKey = searchKey.trim().toUpperCase();
      const numOnly = cleanKey.replace(/\D/g, '');

      const target = cloudOrders.find(o => 
        (o.folio && o.folio.toUpperCase() === cleanKey) ||
        (o.id && o.id.toUpperCase() === cleanKey) ||
        (o.folio && numOnly && o.folio.replace(/\D/g, '') === numOnly) ||
        (o.folio && cleanKey.includes(o.folio.toUpperCase()))
      );

      if (target) {
        return res.status(200).json({ success: true, order: target });
      } else {
        return res.status(404).json({ success: false, error: 'Pedido no encontrado en la instancia activa' });
      }
    }

    // Retornar lista completa para el panel de administración
    return res.status(200).json({
      success: true,
      orders: cloudOrders,
      total: cloudOrders.length
    });
  }

  // 2. POST: Crear o sincronizar un nuevo pedido desde el celular del cliente
  if (req.method === 'POST') {
    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch { body = {}; }
    } else if (!body) {
      body = {};
    }

    // Sincronización masiva desde el panel de la dueña para mantener la nube caliente
    if (body.action === 'sync_all' && Array.isArray(body.orders)) {
      body.orders.forEach(incoming => {
        const inFolio = incoming.folio || '';
        const inNum = inFolio.replace(/\D/g, '');
        const idx = cloudOrders.findIndex(o => 
          (o.folio && o.folio === inFolio) ||
          (o.id && o.id === incoming.id) ||
          (o.folio && inNum && o.folio.replace(/\D/g, '') === inNum)
        );
        if (idx >= 0) {
          cloudOrders[idx] = { ...cloudOrders[idx], ...incoming };
        } else {
          cloudOrders.push(incoming);
        }
      });
      return res.status(200).json({ success: true, total: cloudOrders.length });
    }

    const { order } = body;
    if (!order || !order.folio) {
      return res.status(400).json({ error: 'Datos del pedido incompletos' });
    }

    // Verificar si ya existe por id o folio para no duplicar
    const cleanFolio = order.folio.toUpperCase();
    const numOnly = cleanFolio.replace(/\D/g, '');
    const existingIndex = cloudOrders.findIndex(o => 
      (o.folio && o.folio.toUpperCase() === cleanFolio) ||
      (o.id && o.id === order.id) ||
      (o.folio && numOnly && o.folio.replace(/\D/g, '') === numOnly)
    );

    if (existingIndex >= 0) {
      cloudOrders[existingIndex] = { ...cloudOrders[existingIndex], ...order };
    } else {
      cloudOrders.unshift(order);
    }

    if (cloudOrders.length > 300) {
      cloudOrders = cloudOrders.slice(0, 300);
    }

    return res.status(200).json({
      success: true,
      message: 'Pedido recibido en la nube exitosamente',
      order: order
    });
  }

  // 3. PUT: Actualizar estado de un pedido con auto-restauración anti-reinicio
  if (req.method === 'PUT') {
    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch { body = {}; }
    }
    const { id, folio, estado } = body;
    const searchKey = (folio || id || '').trim().toUpperCase();
    const numOnly = searchKey.replace(/\D/g, '');

    const target = cloudOrders.find(o => 
      (o.id && o.id.toUpperCase() === searchKey) ||
      (o.folio && o.folio.toUpperCase() === searchKey) ||
      (o.folio && numOnly && o.folio.replace(/\D/g, '') === numOnly)
    );

    if (target) {
      target.estado = estado;
      return res.status(200).json({ success: true, order: target });
    }

    // Auto-restaurar si el contenedor de Vercel reinició en frío
    if (searchKey) {
      const restored = {
        id: id || 'ord_' + Date.now(),
        folio: folio || searchKey,
        estado: estado,
        fecha: new Date().toISOString()
      };
      cloudOrders.unshift(restored);
      return res.status(200).json({ success: true, order: restored, restored: true });
    }

    return res.status(404).json({ error: 'Pedido no encontrado' });
  }

  return res.status(405).json({ error: 'Método no permitido' });
}
