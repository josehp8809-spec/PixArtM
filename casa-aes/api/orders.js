/**
 * Casa Aes - Serverless Function: Gestión y Sincronización de Pedidos en la Nube
 * 
 * Permite recibir pedidos desde el celular de cualquier cliente (POST),
 * consultar todos los pedidos para la administración (GET),
 * o consultar un pedido individual para el rastreo del cliente (GET ?id=AES-XXXX).
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
      const target = cloudOrders.find(o => 
        (o.folio && o.folio.toUpperCase() === cleanKey) ||
        (o.id && o.id.toUpperCase() === cleanKey) ||
        (o.folio && o.folio.toUpperCase() === 'AES-' + cleanKey) ||
        (o.folio && cleanKey.includes(o.folio.toUpperCase()))
      );

      if (target) {
        return res.status(200).json({ success: true, order: target });
      } else {
        return res.status(404).json({ success: false, error: 'Pedido no encontrado en el sistema activo' });
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
      try {
        body = JSON.parse(body);
      } catch {
        body = {};
      }
    } else if (!body) {
      body = {};
    }

    const { order } = body;
    if (!order || !order.folio) {
      return res.status(400).json({ error: 'Datos del pedido incompletos' });
    }

    // Verificar si ya existe por id o folio para no duplicar
    const existingIndex = cloudOrders.findIndex(o => o.id === order.id || o.folio === order.folio);
    if (existingIndex >= 0) {
      cloudOrders[existingIndex] = { ...cloudOrders[existingIndex], ...order };
    } else {
      cloudOrders.unshift(order);
    }

    // Mantener un historial razonable de los últimos 200 pedidos
    if (cloudOrders.length > 200) {
      cloudOrders = cloudOrders.slice(0, 200);
    }

    return res.status(200).json({
      success: true,
      message: 'Pedido recibido en la nube exitosamente',
      order: order
    });
  }

  // 3. PUT: Actualizar estado de un pedido (ej. de 'pendiente' a 'cocina', 'en_camino', 'concluido' o 'cancelado')
  if (req.method === 'PUT') {
    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch { body = {}; }
    }
    const { id, estado } = body;
    const target = cloudOrders.find(o => o.id === id || o.folio === id);
    if (target) {
      target.estado = estado;
      return res.status(200).json({ success: true, order: target });
    }
    return res.status(404).json({ error: 'Pedido no encontrado' });
  }

  return res.status(405).json({ error: 'Método no permitido' });
}
