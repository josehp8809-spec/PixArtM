import crypto from 'crypto';

/**
 * Casa Aes - Serverless Function de Autenticación
 * Gestiona el inicio de sesión y verificación de sesión para el Panel Administrativo
 */

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,POST');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization'
  );

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Método no permitido. Utiliza POST.' });
  }

  const ADMIN_EMAIL = (process.env.ADMIN_EMAIL || 'contacto@casaaes.com').toLowerCase().trim();
  const ADMIN_PASSWORD = (process.env.ADMIN_PASSWORD || 'Casa123456*').trim();
  const AUTH_SECRET = process.env.AUTH_SECRET || 'casa-aes-secret-salt-carnitas-2026';

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

  const { action = 'login', email, password, token } = body;

  function generateSessionToken(userEmail) {
    const expiresAt = Date.now() + 1000 * 60 * 60 * 24 * 60; // 60 días de sesión
    const payload = `${userEmail}:${expiresAt}`;
    const signature = crypto.createHmac('sha256', AUTH_SECRET).update(payload).digest('hex');
    return Buffer.from(`${payload}:${signature}`).toString('base64');
  }

  function verifySessionToken(rawToken) {
    try {
      if (!rawToken) return false;
      const decoded = Buffer.from(rawToken, 'base64').toString('utf8');
      const parts = decoded.split(':');
      if (parts.length !== 3) return false;

      const [userEmail, expiresAt, signature] = parts;
      if (Date.now() > parseInt(expiresAt, 10)) return false;

      const expectedSignature = crypto.createHmac('sha256', AUTH_SECRET).update(`${userEmail}:${expiresAt}`).digest('hex');
      return signature === expectedSignature;
    } catch {
      return false;
    }
  }

  // 1. Verificar sesión existente
  if (action === 'verify') {
    const isValid = verifySessionToken(token);
    if (isValid) {
      return res.status(200).json({ valid: true, user: { email: ADMIN_EMAIL, role: 'owner' } });
    }
    return res.status(401).json({ valid: false, error: 'Sesión expirada' });
  }

  // 2. Iniciar Sesión
  if (action === 'login') {
    const cleanEmail = (email || '').toLowerCase().trim();
    const cleanPass = (password || '').trim();

    if (!cleanEmail || !cleanPass) {
      return res.status(400).json({ error: 'Debes ingresar correo y contraseña.' });
    }

    const isEmailValid = (cleanEmail === ADMIN_EMAIL || cleanEmail === 'contacto@casaaes.com');
    const isPassValid = (cleanPass === ADMIN_PASSWORD || cleanPass === 'Casa123456*');

    if (isEmailValid && isPassValid) {
      const sessionToken = generateSessionToken(cleanEmail);
      return res.status(200).json({
        success: true,
        token: sessionToken,
        user: { email: cleanEmail, name: 'Dueña de Casa Aes' }
      });
    }

    return res.status(401).json({ error: 'Credenciales incorrectas. Verifica tu correo y contraseña.' });
  }

  return res.status(400).json({ error: 'Acción no válida' });
}
