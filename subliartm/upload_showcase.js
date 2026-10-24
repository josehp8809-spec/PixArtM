import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SUPABASE_URL = 'https://yzykzfzxvngjycmfansk.supabase.co';
const SUPABASE_KEY = 'sb_publishable_kP5I2bwqJ_NzbWyF8grDbA_gEtX-VRS';

const showcaseItems = [
  {
    localRelPath: 'assets/gallery/Navidad/Esferas Navidad/597163560_1705274750825013_6593804504117716524_n.jpg',
    storageName: 'esferas_navidenas_mdf_familia.jpg',
    title: 'Esferas Navideñas Caladas con Nombre en MDF',
    category: 'Corte Láser MDF & Acrílico',
    price_range: '$35 - $45 MXN c/u (Docena $380)',
    description: 'Hermosas esferas navideñas cortadas con láser de alta precisión en MDF de 3mm. Personalizadas con el nombre de cada miembro de la familia o mascotas. Acabado natural o pintado, listas para colgar.',
    tags: ['esferas', 'navidad', 'mdf', 'personalizado', 'familia'],
    is_seasonal: true,
    season_name: 'Navidad & Fin de Año',
    in_carousel: true
  },
  {
    localRelPath: 'assets/gallery/Noche de Muertos/Corte MDF/571219292_1665359128149909_299478580876282292_n.jpg',
    storageName: 'catrina_portavelas_dia_muertos.jpg',
    title: 'Catrinas & Portavelas de Día de Muertos en MDF',
    category: 'Corte Láser MDF & Acrílico',
    price_range: '$120 - $220 MXN',
    description: 'Piezas artísticas caladas en madera MDF con motivos tradicionales de Catrinas y flores de cempasúchil. Ideales para centros de ofrenda y decoración de altar.',
    tags: ['dia de muertos', 'catrinas', 'ofrenda', 'mdf', 'tradicion'],
    is_seasonal: true,
    season_name: 'Día de Muertos',
    in_carousel: true
  },
  {
    localRelPath: 'assets/gallery/Sublimado/Plaquitas de perro/493888437_1501869611165529_8583002891082813399_n.jpg',
    storageName: 'plaquitas_mascotas_sublimadas.jpg',
    title: 'Plaquitas de Identificación para Mascotas Sublimadas',
    category: 'Sublimación',
    price_range: '$90 - $130 MXN',
    description: 'Plaquitas de aluminio brillante sublimadas a todo color por ambos lados. Diseños únicos con nombre de tu perrito o gatito, teléfonos de emergencia y código QR de contacto.',
    tags: ['plaquitas', 'mascotas', 'sublimacion', 'perros', 'aluminio'],
    is_seasonal: false,
    season_name: null,
    in_carousel: true
  },
  {
    localRelPath: 'assets/gallery/Corte Laser MDF/649256268_1779367573415730_6769473533035576908_n.jpg',
    storageName: 'letrero_relieve_eventos_mdf.jpg',
    title: 'Letreros y Centros de Mesa en Relieve para Fiestas',
    category: 'Corte Láser MDF & Acrílico',
    price_range: '$150 - $350 MXN (según medidas)',
    description: 'Letreros de nombres, números para aniversarios y centros de mesa calados con tecnología láser. Se entregan listos con base estable y acabado impecable.',
    tags: ['letreros', 'centros de mesa', 'xv anos', 'boda', 'mdf'],
    is_seasonal: false,
    season_name: null,
    in_carousel: true
  },
  {
    localRelPath: 'assets/gallery/Corte Vinil/Porta Retratos/493542470_1500823831270107_7614183923073551356_n.jpg',
    storageName: 'portarretratos_conmemorativo_vinil.jpg',
    title: 'Portarretratos Conmemorativo con Vinil de Precisión',
    category: 'Vinil & Gran Formato',
    price_range: '$180 - $280 MXN',
    description: 'Portarretratos para fotos familiares, bautizos o graduaciones. Detalles calados y rotulados con vinil de máxima adherencia y acabado elegante.',
    tags: ['portaretratos', 'vinil', 'recuerdos', 'decoracion'],
    is_seasonal: false,
    season_name: null,
    in_carousel: true
  },
  {
    localRelPath: 'assets/gallery/Sublimado/491781277_1491663315519492_7290809830409117115_n.jpg',
    storageName: 'tazas_ceramica_sublimadas.jpg',
    title: 'Tazas Cerámicas Personalizadas de Alta Definición',
    category: 'Sublimación',
    price_range: '$110 - $150 MXN (Mayoreo desde $85)',
    description: 'Tazas de cerámica premium de 11oz y 15oz con colores vivos, brillo fotográfico y total resistencia a microondas y lavavajillas. El regalo personalizado que nunca pasa de moda.',
    tags: ['tazas', 'sublimacion', 'regalos', 'eventos'],
    is_seasonal: false,
    season_name: null,
    in_carousel: true
  },
  {
    localRelPath: 'assets/gallery/Corte Vinil/680632406_1821061859246301_1274965717417219020_n.jpg',
    storageName: 'termos_cilindros_vinil_metalico.jpg',
    title: 'Cilindros y Termos con Vinil Metálico / Holográfico',
    category: 'Vinil & Gran Formato',
    price_range: '$95 - $170 MXN',
    description: 'Termos y vasos térmicos personalizados para despedidas de soltera, cumpleaños y eventos corporativos con vinil adhesivo premium resistente al agua y al uso diario.',
    tags: ['termos', 'cilindros', 'vinil', 'personalizado'],
    is_seasonal: false,
    season_name: null,
    in_carousel: true
  },
  {
    localRelPath: 'assets/gallery/Impresiones/492881747_1500811111271379_1288989329935996726_n.jpg',
    storageName: 'stickers_troquelados_marcas.jpg',
    title: 'Stickers Troquelados & Etiquetas Adhesivas para Marcas',
    category: 'Vinil & Gran Formato',
    price_range: 'Desde $180 MXN planilla',
    description: 'Etiquetas adhesivas troqueladas con corte exacto a la silueta de tu logo o diseño. Resistentes al agua y fricción, ideales para empaques comerciales y productos.',
    tags: ['stickers', 'etiquetas', 'impresion', 'marcas'],
    is_seasonal: false,
    season_name: null,
    in_carousel: false
  },
  {
    localRelPath: 'assets/gallery/Navidad/Corte Vinil Navidad/473600956_1739933910138298_3120124301865956960_n.jpg',
    storageName: 'cajas_detalles_navidad_vinil.jpg',
    title: 'Cajas de Regalo & Detalles Navideños con Vinil',
    category: 'Vinil & Gran Formato',
    price_range: '$75 - $160 MXN',
    description: 'Cajas finas y esferas personalizadas con vinil calado dorado, blanco y glitter para regalos corporativos y cenas familiares navideñas.',
    tags: ['navidad', 'cajas', 'vinil', 'regalos'],
    is_seasonal: true,
    season_name: 'Navidad & Fin de Año',
    in_carousel: false
  },
  {
    localRelPath: 'assets/gallery/Noche de Muertos/Corte MDF/557154681_1639237744095381_1560963508545909912_n.jpg',
    storageName: 'nicho_altar_dia_muertos_mdf.jpg',
    title: 'Nichos y Marcos de Altar Día de Muertos en MDF',
    category: 'Corte Láser MDF & Acrílico',
    price_range: '$180 - $320 MXN',
    description: 'Estructuras caladas y nichos para retratos de seres queridos con flores tradicionales de cempasúchil caladas en madera MDF.',
    tags: ['altar', 'dia de muertos', 'mdf', 'tradicion'],
    is_seasonal: true,
    season_name: 'Día de Muertos',
    in_carousel: false
  }
];

async function run() {
  console.log(`Starting showcase upload to Supabase... Total items: ${showcaseItems.length}`);

  for (const item of showcaseItems) {
    const fullLocalPath = path.join(__dirname, item.localRelPath);
    if (!fs.existsSync(fullLocalPath)) {
      console.warn(`File not found: ${fullLocalPath}`);
      continue;
    }

    const fileBytes = fs.readFileSync(fullLocalPath);
    const storageUrl = `${SUPABASE_URL}/storage/v1/object/product-images/${item.storageName}`;

    console.log(`Uploading ${item.storageName} to Supabase Storage...`);
    const uploadRes = await fetch(storageUrl, {
      method: 'POST',
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'image/jpeg',
        'x-upsert': 'true'
      },
      body: fileBytes
    });

    if (!uploadRes.ok) {
      const errTxt = await uploadRes.text();
      console.error(`Failed uploading ${item.storageName}:`, errTxt);
    } else {
      console.log(`Uploaded ${item.storageName} successfully!`);
    }

    const publicImageUrl = `${SUPABASE_URL}/storage/v1/object/public/product-images/${item.storageName}`;

    // Insert into Supabase Products DB table
    const dbPayload = {
      title: item.title,
      category: item.category,
      price_range: item.price_range,
      description: item.description,
      tags: item.tags,
      is_seasonal: item.is_seasonal,
      season_name: item.season_name,
      in_carousel: item.in_carousel,
      image_url: publicImageUrl,
      user_notes: 'Selección estelar de trabajos reales Subli Art M'
    };

    console.log(`Inserting product "${item.title}" into Supabase products table...`);
    const dbRes = await fetch(`${SUPABASE_URL}/rest/v1/products`, {
      method: 'POST',
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
      },
      body: JSON.stringify(dbPayload)
    });

    if (!dbRes.ok) {
      const dbErr = await dbRes.text();
      console.error(`Error inserting "${item.title}":`, dbErr);
    } else {
      const saved = await dbRes.json();
      console.log(`Saved product with ID: ${saved[0]?.id}`);
    }
  }

  console.log('Finished uploading showcase!');
}

run().catch(console.error);
