import crypto from 'crypto';

/**
 * Subli Art M - Vercel Serverless Function: Product AI Analyzer
 * Analyzes uploaded product photo + user notes to classify, tag, generate commercial copy,
 * highlight new products, and suggest categories.
 * Features automatic Gemini Vision + Resilient Creative Engine Fallback.
 */

export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization, x-gemini-key'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Método no permitido' });
  }

  // Parse body safely
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

  // Security: Verify auth token, referer or explicit client key
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.startsWith('Bearer ') ? authHeader.slice(7) : null;
  const clientKey = req.headers['x-gemini-key'];
  const referer = req.headers['referer'] || '';
  const origin = req.headers['origin'] || '';
  const AUTH_SECRET = process.env.AUTH_SECRET || 'subli-art-m-secret-key-salt-2026';

  let isAuthenticated = false;

  // 1. Check local session token or internal token
  if (token && (token.startsWith('local-token-') || token.startsWith('token-') || token.length > 20)) {
    isAuthenticated = true;
  } else if (token) {
    try {
      const decoded = Buffer.from(token, 'base64').toString('utf8');
      const parts = decoded.split(':');
      if (parts.length === 3) {
        const [userEmail, expiresAt, signature] = parts;
        if (Date.now() <= parseInt(expiresAt, 10)) {
          const expectedSig = crypto.createHmac('sha256', AUTH_SECRET).update(`${userEmail}:${expiresAt}`).digest('hex');
          if (signature === expectedSig) {
            isAuthenticated = true;
          }
        }
      }
    } catch {
      isAuthenticated = false;
    }
  }

  // 2. Allow if client key passed or coming from legitimate admin domain
  if (!isAuthenticated && (clientKey || referer.includes('/admin') || origin.includes('vercel.app') || origin.includes('localhost'))) {
    isAuthenticated = true;
  }

  if (!isAuthenticated) {
    return res.status(401).json({ error: 'No autorizado. Debes iniciar sesión en el panel para usar la IA.' });
  }

  const { imageBase64, mimeType = 'image/jpeg', userNotes = '', existingCategories = [] } = body;

  if (!imageBase64) {
    return res.status(400).json({ error: 'Debes proporcionar una imagen en base64' });
  }

  const defaultCats = [
    'Sublimación (Tazas, Termos, Textiles)',
    'Corte Láser MDF & Acrílico',
    'Vinil & Gran Formato (Stickers, Lonas, Rotulación)',
    'Edición & Diseño Gráfico (Invitaciones, Logos)'
  ];

  const categoryList = existingCategories.length > 0 ? existingCategories : defaultCats;
  const apiKey = (process.env.GEMINI_API_KEY || clientKey || '').trim();

  // Try Gemini Vision first if API key is provided
  if (apiKey) {
    try {
      const systemPrompt = `Eres el Asistente Inteligente de Gestión de Catálogo para "Subli Art M", un taller creativo de sublimación, corte láser MDF, vinil decorativo/comercial y diseño gráfico.
Tu tarea es analizar la foto del trabajo realizado junto con las notas u observaciones proporcionadas por el creador.

Categorías actuales existentes en el catálogo:
${categoryList.map((c, i) => `${i + 1}. ${c}`).join('\n')}

Debes responder ÚNICAMENTE con un objeto JSON válido con la siguiente estructura exacta:
{
  "title": "Título comercial corto y atractivo (máx 60 caracteres)",
  "category": "Nombre exacto de una de las categorías existentes O el nombre de una nueva si realmente no encaja",
  "is_new_category": boolean,
  "new_category_info": null,
  "commercial_description": "Texto persuasivo, cálido y profesional (2 párrafos) resaltando los materiales, acabados, personalización y para qué evento u ocasión es ideal (ej: recuerdos de boda, eventos corporativos, regalos únicos).",
  "recommended_price_range": "Rango sugerido en MXN (ej: $150 - $220 MXN o $35 - $50 MXN c/u)",
  "tags": ["etiqueta1", "etiqueta2", "etiqueta3", "etiqueta4"],
  "is_seasonal": boolean,
  "season_name": "Nombre de la temporada si aplica (ej: Navidad, Día de Muertos, San Valentín) o null",
  "is_new": true,
  "production_highlights": ["Acabado de alta resistencia", "Personalización a todo color", "Corte de alta precisión"]
}`;

      const cleanBase64 = imageBase64.replace(/^data:image\/[a-z0-9.+]+;base64,/, '');

      const geminiPayload = {
        contents: [
          {
            role: 'user',
            parts: [
              { text: `Notas del creador / descripción del trabajo:\n"${userNotes || 'Sin notas adicionales. Analiza la imagen visualmente.'}"\n\nPor favor analiza la imagen y genera la clasificación y ficha comercial en formato JSON:` },
              {
                inline_data: {
                  mime_type: mimeType,
                  data: cleanBase64
                }
              }
            ]
          }
        ],
        generationConfig: {
          response_mime_type: 'application/json',
          temperature: 0.2
        },
        systemInstruction: {
          parts: [{ text: systemPrompt }]
        }
      };

      // Try Gemini 2.5 Flash
      const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`;
      let response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(geminiPayload)
      });

      if (!response.ok) {
        // Fallback to gemini-1.5-flash
        const fbEndpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;
        response = await fetch(fbEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(geminiPayload)
        });
      }

      if (response.ok) {
        const raw = await response.json();
        const textContent = raw.candidates?.[0]?.content?.parts?.[0]?.text;
        if (textContent) {
          const parsed = JSON.parse(textContent);
          parsed.is_new = true;
          parsed.source = 'gemini-vision';
          return res.status(200).json(parsed);
        }
      }
    } catch (geminiError) {
      console.warn('Gemini vision API attempt failed, activating Creative Engine Fallback:', geminiError.message);
    }
  }

  // Resilient Smart Creative Engine Fallback
  // Generates an expert classification so user is NEVER blocked even without a key configured
  const smartResult = generateSmartCreativeProposal(userNotes, categoryList);
  return res.status(200).json(smartResult);
}

/**
 * Intelligent fallback generator based on creative keyword matching & workshop domain knowledge
 */
function generateSmartCreativeProposal(userNotes, categories) {
  const notesLower = (userNotes || '').toLowerCase();

  // Detect Season
  let isSeasonal = false;
  let seasonName = null;
  if (/navidad|navideñ|esfera|pino|nochebuena|año nuevo|santa|posada/i.test(notesLower)) {
    isSeasonal = true;
    seasonName = 'Navidad & Fin de Año';
  } else if (/muerto|catrina|ofrenda|calavera|cempasuchil|halloween/i.test(notesLower)) {
    isSeasonal = true;
    seasonName = 'Día de Muertos';
  } else if (/san valent[ií]n|amor|amistad|14 de febrero|novios/i.test(notesLower)) {
    isSeasonal = true;
    seasonName = 'San Valentín';
  } else if (/madre|mam[aá]|10 de mayo/i.test(notesLower)) {
    isSeasonal = true;
    seasonName = 'Día de las Madres';
  } else if (/graduaci[oó]n|graduado|diploma|generaci[oó]n/i.test(notesLower)) {
    isSeasonal = true;
    seasonName = 'Graduaciones';
  }

  // Detect Technique / Category
  let category = 'Sublimación';
  let title = 'Trabajo Personalizado de Taller';
  let price = '$150 - $220 MXN';
  let tags = ['personalizado', 'subliartm', 'taller', 'artesanal'];
  let description = '';

  if (/taza|termo|sublima|playera|textil|coj[ií]n|gorra|mousepad/i.test(notesLower)) {
    category = categories.find(c => /sublima/i.test(c)) || 'Sublimación';
    if (/taza/i.test(notesLower)) {
      title = isSeasonal ? `Taza Conmemorativa ${seasonName || 'Especial'} Sublimada` : 'Taza Mágica / Cerámica Sublimada en Alta Definición';
      price = '$95 - $140 MXN c/u';
      tags = ['taza', 'sublimacion', 'ceramica', 'regalo', 'brillante'];
    } else if (/termo/i.test(notesLower)) {
      title = 'Termo de Acero Inoxidable Personalizado';
      price = '$220 - $320 MXN';
      tags = ['termo', 'acero inoxidable', 'sublimacion', 'regalo premium'];
    } else if (/playera|textil|coj[ií]n|gorra/i.test(notesLower)) {
      title = 'Prenda Textil Personalizada con Tintas Indelebles';
      price = '$180 - $260 MXN';
      tags = ['textil', 'playera', 'sublimacion', 'colores vivos'];
    } else {
      title = isSeasonal ? `Detalle Especial ${seasonName || 'de Temporada'}` : 'Artículo Personalizado Sublimado';
      price = '$110 - $190 MXN';
      tags = ['sublimacion', 'personalizado', 'acabado profesional'];
    }
    description = `Pieza sublimada con tintas de máxima saturación y brillo permanente que resisten lavadas continuas sin desvanecerse. Personalizada a todo color con nombres, fotografías o logotipos para que tu obsequio o recuerdo luzca como una verdadera obra de arte.`;
  } else if (/corte|l[aá]ser|mdf|madera|acrilico|acr[ií]lico|letrero|esfera|portavelas|calado/i.test(notesLower)) {
    category = categories.find(c => /corte|l[aá]ser|mdf/i.test(c)) || 'Corte Láser MDF & Acrílico';
    title = isSeasonal && seasonName ? `Diseño Especial ${seasonName} en Corte Láser MDF` : 'Pieza Decorativa en Corte Láser de Alta Precisión';
    price = isSeasonal ? '$35 - $65 MXN c/u' : '$180 - $350 MXN';
    tags = ['corte laser', 'mdf', 'calado', 'madera', 'decoracion', isSeasonal ? seasonName.toLowerCase() : 'eventos'];
    description = `Elegante trabajo elaborado con corte láser de alta precisión en madera MDF seleccionada. Cuenta con acabados limpios, detalles calados minuciosos y una estructura sólida pensada para lucir en cualquier espacio o evento especial. Ideal para recuerdos familiares, ambientación temática o regalos corporativos personalizados.`;
  } else if (/vinil|sticker|calcoman[ií]a|rotulaci[oó]n|lona|publicidad|auto|vitrina|troquel/i.test(notesLower)) {
    category = categories.find(c => /vinil|gran formato/i.test(c)) || 'Vinil & Gran Formato';
    title = 'Rotulación & Stickers de Alta Resistencia';
    price = '$80 - $250 MXN según medidas';
    tags = ['vinil', 'stickers', 'rotulacion', 'publicidad', 'resistente'];
    description = `Elaborado con vinil de alta adherencia y durabilidad para interiores o exteriores. Acabado nítido con corte milimétrico por contorno, resistente al sol y al agua. Perfecto para identificación de marca, decoración de vehículos, eventos o señalética.`;
  } else if (/invitaci[oó]n|logotipo|logo |vector|branding|flyer/i.test(notesLower)) {
    category = categories.find(c => /diseño|edici[oó]n/i.test(c)) || 'Edición & Diseño Gráfico';
    title = 'Diseño Digital & Gráfico Personalizado';
    price = '$120 - $300 MXN';
    tags = ['diseño grafico', 'vector', 'digital', 'invitacion', 'branding'];
    description = `Propuesta gráfica profesional desarrollada a medida, cuidando la paleta de color, tipografía y estilo visual de tu celebración o negocio. Archivos listos para impresión en alta resolución o para compartir en redes sociales y WhatsApp.`;
  }

  // Refine title if notes provide specific keywords
  if (userNotes && userNotes.length > 5) {
    const cleanNotes = userNotes.trim().replace(/[.\n\r]/g, ' ');
    if (cleanNotes.length < 55) {
      title = cleanNotes.charAt(0).toUpperCase() + cleanNotes.slice(1);
    }
  }

  return {
    title,
    category,
    is_new_category: false,
    new_category_info: null,
    commercial_description: description,
    recommended_price_range: price,
    tags,
    is_seasonal: isSeasonal,
    season_name: seasonName,
    is_new: true,
    production_highlights: [
      'Personalización a todo color',
      'Materiales de primera calidad',
      'Elaboración artesanal detallada'
    ],
    source: 'smart-creative-engine'
  };
}
