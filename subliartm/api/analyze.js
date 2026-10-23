/**
 * Subli Art M - Vercel Serverless Function: Gemini Flash Product Analyzer
 * Analyzes uploaded product photo + user notes to classify, tag, generate commercial copy,
 * and suggest new categories if needed.
 */

export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.GEMINI_API_KEY || req.headers['x-gemini-key'];
  if (!apiKey) {
    return res.status(400).json({
      error: 'Falta la clave API de Gemini. Configúrala en Vercel (GEMINI_API_KEY) o en la app.'
    });
  }

  try {
    const { imageBase64, mimeType = 'image/jpeg', userNotes = '', existingCategories = [] } = req.body || {};

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

    const systemPrompt = `Eres el Asistente Inteligente de Gestión de Catálogo para "Subli Art M", un taller creativo de sublimación, corte láser MDF, vinil decorativo/comercial y diseño gráfico.
Tu tarea es analizar la foto del trabajo realizado junto con las notas u observaciones proporcionadas por el creador.

Categorías actuales existentes en el catálogo:
${categoryList.map((c, i) => `${i + 1}. ${c}`).join('\n')}

Debes responder ÚNICAMENTE con un objeto JSON válido con la siguiente estructura:
{
  "title": "Título comercial corto y atractivo (máx 60 caracteres)",
  "category": "Nombre exacto de una de las categorías existentes O el nombre de una nueva si realmente no encaja",
  "is_new_category": boolean (true si el producto pertenece a una categoría completamente nueva no cubierta por las actuales, false en caso contrario),
  "new_category_info": {
    "name": "Nombre de la nueva categoría (solo si is_new_category es true, sino null)",
    "description": "Breve descripción de la nueva categoría (solo si is_new_category es true, sino null)",
    "icon": "emoji o clase lucide (ej: Sparkles, Scissors, Shirt, Gift)"
  },
  "commercial_description": "Texto persuasivo, cálido y profesional (2-3 párrafos cortos) resaltando los materiales, acabados, personalización y para qué evento u ocasión es ideal (ej: recuerdos de boda, eventos corporativos, regalos únicos).",
  "recommended_price_range": "Rango sugerido en MXN (ej: $150 - $220 MXN o A cotizar según volumen)",
  "tags": ["etiqueta1", "etiqueta2", "etiqueta3", "etiqueta4"],
  "is_seasonal": boolean (true si es alusivo a una fecha especial: Día de Muertos, Navidad, San Valentín, Día de las Madres, Graduaciones, etc.),
  "season_name": "Nombre de la temporada si aplica (ej: Navidad 2026, Día de Muertos, San Valentín) o null",
  "production_highlights": ["Acabado de alta resistencia", "Personalización a todo color", "Corte de alta precisión"]
}`;

    // Clean base64 if data URI prefix was sent
    const cleanBase64 = imageBase64.replace(/^data:image\/[a-z]+;base64,/, '');

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

    // Use Gemini 2.5 Flash / 1.5 Flash
    const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`;

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(geminiPayload)
    });

    if (!response.ok) {
      // Fallback to gemini-1.5-flash if 2.5 is not accessible with key
      const fallbackEndpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;
      const fallbackResp = await fetch(fallbackEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(geminiPayload)
      });

      if (!fallbackResp.ok) {
        const errData = await fallbackResp.text();
        return res.status(500).json({ error: 'Error al contactar con Gemini AI', details: errData });
      }

      const fbData = await fallbackResp.json();
      const textOutput = fbData.candidates?.[0]?.content?.parts?.[0]?.text;
      return res.status(200).json(JSON.parse(textOutput));
    }

    const data = await response.json();
    const textOutput = data.candidates?.[0]?.content?.parts?.[0]?.text;
    const parsed = JSON.parse(textOutput);

    return res.status(200).json(parsed);
  } catch (error) {
    console.error('Error processing AI request:', error);
    return res.status(500).json({ error: 'Error interno procesando la solicitud', details: error.message });
  }
}
