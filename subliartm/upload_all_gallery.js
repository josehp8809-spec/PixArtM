import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SUPABASE_URL = 'https://yzykzfzxvngjycmfansk.supabase.co';
const SUPABASE_KEY = 'sb_publishable_kP5I2bwqJ_NzbWyF8grDbA_gEtX-VRS';

function getFilesRecursively(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  list.forEach(file => {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat && stat.isDirectory()) {
      results = results.concat(getFilesRecursively(fullPath));
    } else if (/\.(jpe?g|png|webp)$/i.test(file)) {
      results.push(fullPath);
    }
  });
  return results;
}

function determineMetadata(filePath) {
  const norm = filePath.replace(/\\/g, '/');
  
  if (norm.includes('Navidad/Esferas Navidad')) {
    return {
      category: 'Corte Láser MDF & Acrílico',
      title: 'Esferas Navideñas Caladas en Madera MDF',
      price: '$35 - $45 MXN c/u',
      desc: 'Esferas cortadas con láser y personalizadas con nombres de familia y mascotas para el árbol navideño.',
      is_seasonal: true,
      season_name: 'Navidad & Fin de Año',
      tags: ['esferas', 'navidad', 'mdf', 'familia']
    };
  }
  if (norm.includes('Navidad/Corte Vinil Navidad') || norm.includes('Navidad/')) {
    return {
      category: 'Vinil & Gran Formato',
      title: 'Detalles Navideños Personalizados en Vinil',
      price: '$65 - $140 MXN',
      desc: 'Cajas de regalo y artículos navideños con vinil de corte dorado y brillante.',
      is_seasonal: true,
      season_name: 'Navidad & Fin de Año',
      tags: ['navidad', 'cajas', 'vinil', 'regalos']
    };
  }
  if (norm.includes('Noche de Muertos/Corte MDF') || norm.includes('Noche de Muertos')) {
    return {
      category: 'Corte Láser MDF & Acrílico',
      title: 'Catrinas & Decoración de Día de Muertos en MDF',
      price: '$120 - $250 MXN',
      desc: 'Diseños de Catrinas, portavelas y estructuras de ofrenda caladas con láser en MDF.',
      is_seasonal: true,
      season_name: 'Día de Muertos',
      tags: ['dia de muertos', 'catrinas', 'ofrenda', 'mdf']
    };
  }
  if (norm.includes('Sublimado/Plaquitas de perro')) {
    return {
      category: 'Sublimación',
      title: 'Plaquita de Identificación para Mascota Sublimada',
      price: '$90 - $130 MXN',
      desc: 'Plaquita de aluminio brillante indeleble con nombre, teléfono y diseño a todo color.',
      is_seasonal: false,
      season_name: null,
      tags: ['plaquitas', 'mascotas', 'perros', 'aluminio']
    };
  }
  if (norm.includes('Sublimado')) {
    return {
      category: 'Sublimación',
      title: 'Trabajo Personalizado en Sublimación de Alta Definición',
      price: '$110 - $180 MXN',
      desc: 'Tazas, termos térmicos o textiles sublimados con colores brillantes y tintas de alta duración.',
      is_seasonal: false,
      season_name: null,
      tags: ['sublimacion', 'tazas', 'regalos', 'personalizado']
    };
  }
  if (norm.includes('Corte Vinil/Porta Retratos')) {
    return {
      category: 'Vinil & Gran Formato',
      title: 'Portarretratos Personalizado con Vinil de Corte',
      price: '$180 - $280 MXN',
      desc: 'Portarretratos calados con dedicatorias familiares y siluetas con vinil de precisión.',
      is_seasonal: false,
      season_name: null,
      tags: ['portaretratos', 'recuerdos', 'vinil', 'decoracion']
    };
  }
  if (norm.includes('Corte Vinil')) {
    return {
      category: 'Vinil & Gran Formato',
      title: 'Rotulación & Termos Personalizados con Vinil',
      price: '$85 - $160 MXN',
      desc: 'Vinil adhesivo de máxima adherencia para termos, vasos, señalética y vehículos.',
      is_seasonal: false,
      season_name: null,
      tags: ['vinil', 'termos', 'rotulacion', 'stickers']
    };
  }
  if (norm.includes('Corte Laser MDF')) {
    return {
      category: 'Corte Láser MDF & Acrílico',
      title: 'Letrero & Pieza Calada con Corte Láser MDF',
      price: '$140 - $350 MXN',
      desc: 'Letreros calados, centros de mesa y cajas armables en MDF de 3mm a 6mm.',
      is_seasonal: false,
      season_name: null,
      tags: ['corte laser', 'mdf', 'letreros', 'centros de mesa']
    };
  }
  if (norm.includes('Impresiones')) {
    return {
      category: 'Vinil & Gran Formato',
      title: 'Impresión de Stickers & Lonas Publicitarias',
      price: 'A cotizar por medida',
      desc: 'Stickers troquelados a la silueta, microperforado, lonas y papelería comercial.',
      is_seasonal: false,
      season_name: null,
      tags: ['impresion', 'stickers', 'lonas', 'publicidad']
    };
  }

  return {
    category: 'Sublimación',
    title: 'Creación Personalizada Subli Art M',
    price: 'A cotizar',
    desc: 'Trabajo personalizado elaborado con alta atención al detalle en Subli Art M.',
    is_seasonal: false,
    season_name: null,
    tags: ['personalizado', 'diseño', 'taller']
  };
}

async function uploadAll() {
  const galleryDir = path.join(__dirname, 'assets', 'gallery');
  const allFiles = getFilesRecursively(galleryDir);
  console.log(`Found ${allFiles.length} photos in gallery.`);

  // Get existing products in DB to avoid duplicates
  const existingRes = await fetch(`${SUPABASE_URL}/rest/v1/products?select=image_url`, {
    headers: { 'apikey': SUPABASE_KEY, 'Authorization': `Bearer ${SUPABASE_KEY}` }
  });
  const existingRows = await existingRes.json();
  const existingUrls = new Set(existingRows.map(r => r.image_url));

  let count = 0;
  for (const filePath of allFiles) {
    count++;
    const baseName = path.basename(filePath);
    const cleanStorageName = `gal_${count}_${baseName.replace(/[^a-zA-Z0-9._-]/g, '_')}`;
    const publicImageUrl = `${SUPABASE_URL}/storage/v1/object/public/product-images/${cleanStorageName}`;

    // Skip if already in DB
    if (existingUrls.has(publicImageUrl)) {
      console.log(`[${count}/${allFiles.length}] Already in DB, skipping: ${baseName}`);
      continue;
    }

    const fileBytes = fs.readFileSync(filePath);
    const storageEndpoint = `${SUPABASE_URL}/storage/v1/object/product-images/${cleanStorageName}`;

    // 1. Upload to Supabase Storage
    try {
      const upRes = await fetch(storageEndpoint, {
        method: 'POST',
        headers: {
          'apikey': SUPABASE_KEY,
          'Authorization': `Bearer ${SUPABASE_KEY}`,
          'Content-Type': 'image/jpeg',
          'x-upsert': 'true'
        },
        body: fileBytes
      });

      if (!upRes.ok && upRes.status !== 409) {
        console.warn(`[${count}/${allFiles.length}] Upload issue for ${cleanStorageName}`);
      }
    } catch (e) {
      console.warn(`[${count}/${allFiles.length}] Storage error: ${e.message}`);
    }

    // 2. Insert into DB
    const meta = determineMetadata(filePath);
    const dbPayload = {
      title: `${meta.title} #${count}`,
      category: meta.category,
      price_range: meta.price,
      description: meta.desc,
      tags: meta.tags,
      is_seasonal: meta.is_seasonal,
      season_name: meta.season_name,
      in_carousel: false, // The top 8 are in the carousel; the rest in the full gallery!
      image_url: publicImageUrl,
      user_notes: 'Foto del archivo histórico de Subli Art M'
    };

    try {
      const insRes = await fetch(`${SUPABASE_URL}/rest/v1/products`, {
        method: 'POST',
        headers: {
          'apikey': SUPABASE_KEY,
          'Authorization': `Bearer ${SUPABASE_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(dbPayload)
      });
      if (insRes.ok) {
        console.log(`[${count}/${allFiles.length}] Saved to DB: ${meta.title} #${count}`);
      }
    } catch (e) {
      console.warn(`Error inserting row ${count}:`, e.message);
    }
  }

  console.log('All gallery photos synced to Supabase!');
}

uploadAll().catch(console.error);
