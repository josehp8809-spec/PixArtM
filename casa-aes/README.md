# 🌮 Casa Aes - Carnitas Estilo Quiroga
### Menú Digital Mobile-First, Checkout por WhatsApp y Panel de Control de Cocina / POS con IA

Plataforma gastronómica integral diseñada para **Casa Aes**. Permite a los comensales ordenar desde su celular con una experiencia fluida y a la dueña gestionar comandas en vivo desde la computadora del mostrador.

---

## 🌟 Características Principales

### 📱 1. Vista Pública de Clientes (`index.html` - Móvil)
* **Diseño e Identidad Casa Aes:** Basado en la paleta oficial (Cantera `#F6F3EC`, Verde Oliva `#4D5B31`, Cobre de cazo `#B2542D` y Mariposa Dorada `#C49A6C`).
* **Doble Menú:**
  * **Fin de Semana:** Taco de carnitas ($35), Cemita ($45), Kilo ($350), 1/2 Kilo ($175), Chilaquiles Aes ($75), Quesacazo ($55), Empanada ($35).
  * **Comida del Día:** Guisados, sopas caseras y aguas frescas actualizables al día.
* **Personalizador de carne:** Selección de maciza, surtida, costilla, cuerito, buche o campechano.
* **Carrito Flotante & Prerregistro:** Guarda datos del cliente para compras recurrentes.
* **Despacho Directo a WhatsApp:** Abre WhatsApp con el mensaje estructurado para confirmación inmediata al `522212811095`.

### 🖥️ 2. Panel de Control de Cocina / POS (`admin.html` - Computadora)
* **Tablero Kanban en Tiempo Real:** 4 columnas dinámicas (*Nuevos por Confirmar*, *En Cocina*, *Por Entregar / En Camino*, *Concluidos*).
* **Alerta Sonora de Cocina:** Campana sintetizada mediante Web Audio API cuando entra un pedido.
* **Botón Copiar para DiDi / Uber Envíos:** Copia al portapapeles en 1 clic los datos del cliente formateados para cotizar o pedir el viaje en la app de repartos.
* **Botón `[ ✅ Concluir Pedido ]`:** Cierre ágil sin comprobantes engorrosos.
* **Punto de Venta para Mostrador (`+ Venta en Local`):** Para registrar comandas físicas o por llamada.
* **Gestor de Menú:** Switch de disponible/agotado en segundos.
* **Escaner con IA Gemini Vision (`📸 Actualizar Menú con Foto`):** La dueña toma foto a su pizarrón o libreta y la IA extrae los platillos del día automáticamente.
* **Directorio de Clientes:** Reconocimiento de clientes frecuentes y direcciones.

---

## 📁 Estructura del Proyecto

```
casa-aes/
├── index.html            # Menú público para clientes (100% Mobile-First)
├── admin.html            # Panel de cocina y control de pedidos (Desktop-First)
├── api/
│   └── ai.js             # Vercel Serverless Function (Gemini Vision OCR y platillos)
├── assets/
│   ├── hero-cazo.jpg     # Foto tradicional del cazo de carnitas
│   └── menu-flyer.jpg    # Foto oficial del menú y chilaquiles
├── supabase_schema.sql   # Script SQL con tablas, RLS y Realtime
├── package.json          # Configuración del proyecto
├── vercel.json           # Configuración de despliegue en Vercel
└── README.md             # Documentación
```

---

## 🚀 Despliegue en Vercel

1. Sube esta carpeta `casa-aes` a tu repositorio de GitHub.
2. En tu panel de **Vercel**, haz clic en **Add New Project** y selecciona el repositorio.
3. (Opcional) En las variables de entorno de Vercel agrega:
   * `GEMINI_API_KEY`: Tu clave de Gemini para el escaneo de pizarrón con IA.
4. Presiona **Deploy**. ¡Tu menú público estará en vivo en `tu-proyecto.vercel.app` y la administración en `tu-proyecto.vercel.app/admin.html`!
