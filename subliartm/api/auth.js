import crypto from 'crypto';

/**
 * Subli Art M - Authentication Serverless Function
 * Handles secure login and session verification for the Admin Studio
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
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Método no permitido' });
  }

  // Get credentials from environment or default fallbacks
  const ADMIN_EMAIL = (process.env.ADMIN_EMAIL || 'contacto@subliartm.com').toLowerCase().trim();
  const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'SubliArtM2026!';
  const AUTH_SECRET = process.env.AUTH_SECRET || 'subli-art-m-secret-key-salt-2026';

  const { action = 'login', email, password, token } = req.body || {};

  // Helper to generate a verifiable signed token
  function generateSessionToken(userEmail) {
    const expiresAt = Date.now() + 1000 * 60 * 60 * 24 * 30; // 30 days
    const payload = `${userEmail}:${expiresAt}`;
    const signature = crypto.createHmac('sha256', AUTH_SECRET).update(payload).digest('hex');
    return Buffer.from(`${payload}:${signature}`).toString('base64');
  }

  // Helper to verify a token
  function verifySessionToken(rawToken) {
    try {
      if (!rawToken) return false;
      const decoded = Buffer.from(rawToken, 'base64').toString('utf8');
      const parts = decoded.split(':');
      if (parts.length !== 3) return false;

      const [userEmail, expiresAt, signature] = parts;
      if (Date.now() > parseInt(expiresAt, 10)) return false; // Expired

      const expectedSignature = crypto.createHmac('sha256', AUTH_SECRET).update(`${userEmail}:${expiresAt}`).digest('hex');
      return signature === expectedSignature;
    } catch {
      return false;
    }
  }

  // 1. Verify existing session
  if (action === 'verify') {
    const isValid = verifySessionToken(token);
    if (isValid) {
      return res.status(200).json({ valid: true, user: { email: ADMIN_EMAIL, role: 'owner' } });
    }
    return res.status(401).json({ valid: false, error: 'Sesión expirada o inválida' });
  }

  // 2. Perform Login
  if (action === 'login') {
    const cleanEmail = (email || '').toLowerCase().trim();
    const cleanPass = (password || '').trim();

    if (!cleanEmail || !cleanPass) {
      return res.status(400).json({ error: 'Debes ingresar correo y contraseña.' });
    }

    if (cleanEmail === ADMIN_EMAIL && cleanPass === ADMIN_PASSWORD) {
      const sessionToken = generateSessionToken(cleanEmail);
      return res.status(200).json({
        success: true,
        token: sessionToken,
        user: { email: cleanEmail, name: 'Administradora Subli Art M' }
      });
    }

    return res.status(401).json({ error: 'Credenciales incorrectas. Verifica tu correo y contraseña.' });
  }

  return res.status(400).json({ error: 'Acción no válida' });
}
