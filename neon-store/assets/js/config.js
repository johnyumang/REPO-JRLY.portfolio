/* ==========================================================================
   SITE CONFIG — the only file you need to edit for brand, prices and copy.
   ---------------------------------------------------------------------------
   - Replace every [BRAND NAME] / [PLACEHOLDER] value below.
   - Prices are plain numbers in your store currency (see `currency`).
   - Text can use tokens: {brand} {freeShipping} {flatRate} {returnDays}
     {processingDays} {email}. They are filled in automatically.
   - Product photos: put files in images/products/ and list them in a
     product's `images` array. Empty array = neon placeholder artwork.
   - After changing brand name / SEO text, run `node tools/apply-meta.mjs`
     so link previews (Open Graph) pick up the new values.
   ========================================================================== */
window.SITE = {
  brand: {
    name: '[BRAND NAME]',
    tagline: 'Compression gear for the night shift',
    email: '[HELLO@YOURBRAND.COM]',
    siteUrl: 'https://johnyumang.github.io/REPO-JRLY.portfolio/neon-store',
    founded: '[YEAR]',
    city: '[CITY, COUNTRY]'
  },

  currency: { code: 'USD', locale: 'en-US' },

  shipping: {
    freeShipping: 75,            // [FREE SHIPPING THRESHOLD] — order subtotal for free shipping
    flatRate: 6,                 // [FLAT SHIPPING RATE] — below the threshold
    processingDays: '1–2',       // [PROCESSING TIME]
    returnDays: 30               // [RETURN WINDOW]
  },

  announcement: 'Free shipping on orders over {freeShipping} · New drop live now',

  nav: [
    { label: 'Shop', href: 'shop.html' },
    { label: 'Sleeves', href: 'shop.html?category=sleeves' },
    { label: 'Tops', href: 'shop.html?category=tops' },
    { label: 'Leggings', href: 'shop.html?category=leggings' },
    { label: 'Lookbook', href: 'lookbook.html' },
    { label: 'Our story', href: 'about.html' }
  ],

  social: [
    { label: 'Instagram', url: 'https://instagram.com/[HANDLE]' },
    { label: 'TikTok', url: 'https://tiktok.com/@[HANDLE]' },
    { label: 'Facebook', url: 'https://facebook.com/[PAGE]' },
    { label: 'YouTube', url: 'https://youtube.com/@[HANDLE]' }
  ],

  /* ---------- SEO + Open Graph (written into each page by tools/apply-meta.mjs) ---------- */
  seo: {
    'index.html':    { title: '{brand} — Cyberpunk compression sleeves, tops & leggings', description: 'Neon-lit compression wear: arm sleeves, compression tops and leggings with 4-way stretch and sweat-wicking fabric. Shop the drop.', image: 'images/social/social_sq_athlete_man_compression_top_01.jpg', type: 'website' },
    'shop.html':     { title: 'Shop compression sleeves, tops & leggings — {brand}', description: 'Shop arm compression sleeves, compression tops and leggings in Circuit, Glitch, Grid and Stealth designs. Filter by size, colour and design.', image: 'images/social/social_sq_products_activewear_flatlay_01.jpg', type: 'website' },
    'product.html':  { title: 'Product — {brand}', description: 'Cyberpunk compression wear with graduated compression, 4-way stretch and sweat-wicking fabric. Choose your size and colour.', image: 'images/social/social_sq_products_activewear_flatlay_01.jpg', type: 'product' },
    'lookbook.html': { title: 'Lookbook — {brand}', description: 'Drop 01 lookbook: compression sleeves, tops and leggings shot under neon after dark.', image: 'images/social/social_4x5_model_black_bodysuit_neon_01.jpg', type: 'website' },
    'about.html':    { title: 'Our story — {brand}', description: "How {brand} designs, cuts and packs cyberpunk compression wear — from the founder's first rack to Drop 01.", image: 'images/operations/ops_founder_rack_laptop_01.jpg', type: 'website' },
    'shipping.html': { title: 'Shipping, returns & FAQ — {brand}', description: 'Shipping times, free-shipping threshold, returns and exchanges, and answers to common questions about compression wear.', image: 'images/packaging/packaging_unboxing_clothing_box_01.jpg', type: 'website' },
    'contact.html':  { title: 'Contact — {brand}', description: 'Questions about sizing, orders or wholesale? Get in touch with {brand}.', image: 'images/social/social_sq_athlete_man_compression_top_01.jpg', type: 'website' },
    '404.html':      { title: 'Signal lost — {brand}', description: 'This page does not exist.', image: 'images/social/social_sq_athlete_man_compression_top_01.jpg', type: 'website', noindex: true }
  },

  /* ---------- Catalogue ---------- */
  categories: [
    { id: 'sleeves', label: 'Arm sleeves' },
    { id: 'tops', label: 'Compression tops' },
    { id: 'leggings', label: 'Leggings' }
  ],

  colours: {
    sand:  { label: 'Sand',  accent: '#C9A97A' },
    mocha: { label: 'Mocha', accent: '#7A5C38' },
    bone:  { label: 'Bone',  accent: '#BBA98C' },
    onyx:  { label: 'Onyx',  accent: '#2A2420' }
  },

  designs: {
    circuit: 'Circuit',
    glitch: 'Glitch',
    grid: 'Grid',
    stealth: 'Stealth'
  },

  sizes: {
    apparel: ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
    sleeves: ['S', 'M', 'L', 'XL']
  },

  products: [
    { id: 'circuit-arm-sleeve', name: 'Circuit Arm Sleeve', category: 'sleeves', design: 'circuit', price: 19, compareAt: null, badge: 'New',
      colours: ['sand', 'mocha', 'bone'], sizes: ['S', 'M', 'L', 'XL'], images: [],
      short: 'Graduated-compression arm sleeve with a reflective circuit print.' },
    { id: 'glitch-arm-sleeve', name: 'Glitch Arm Sleeve', category: 'sleeves', design: 'glitch', price: 19, compareAt: null, badge: null,
      colours: ['mocha', 'sand'], sizes: ['S', 'M', 'L', 'XL'], images: [],
      short: 'Split-signal glitch pattern, UPF 50+, stays put through every rep.' },
    { id: 'grid-arm-sleeve-pair', name: 'Grid Arm Sleeve — Pair', category: 'sleeves', design: 'grid', price: 32, compareAt: 38, badge: 'Bundle',
      colours: ['bone', 'sand', 'onyx'], sizes: ['S', 'M', 'L', 'XL'], images: [],
      short: 'Two sleeves, one price. Wireframe grid knit for full-arm support.' },
    { id: 'stealth-arm-sleeve', name: 'Stealth Arm Sleeve', category: 'sleeves', design: 'stealth', price: 17, compareAt: null, badge: null,
      colours: ['onyx'], sizes: ['S', 'M', 'L', 'XL'], images: [],
      short: 'All-black, no logo noise. Silicone grip band at the bicep.' },

    { id: 'circuit-compression-top-ls', name: 'Circuit Compression Top LS', category: 'tops', design: 'circuit', price: 49, compareAt: null, badge: 'New',
      colours: ['sand', 'bone'], sizes: ['XS', 'S', 'M', 'L', 'XL', 'XXL'], images: [],
      short: 'Long-sleeve base layer with mapped circuit print and thumb loops.' },
    { id: 'glitch-compression-top-ss', name: 'Glitch Compression Top SS', category: 'tops', design: 'glitch', price: 42, compareAt: null, badge: null,
      colours: ['mocha', 'sand', 'onyx'], sizes: ['XS', 'S', 'M', 'L', 'XL', 'XXL'], images: [],
      short: 'Short-sleeve compression tee with flatlock seams and laser-cut vents.' },
    { id: 'grid-mock-neck-top', name: 'Grid Mock-Neck Top', category: 'tops', design: 'grid', price: 54, compareAt: 62, badge: 'Sale',
      colours: ['bone', 'onyx'], sizes: ['S', 'M', 'L', 'XL'], images: [],
      short: 'Mock neck, longline cut, wireframe grid across the shoulders.' },
    { id: 'stealth-compression-top', name: 'Stealth Compression Top', category: 'tops', design: 'stealth', price: 39, compareAt: null, badge: null,
      colours: ['onyx'], sizes: ['XS', 'S', 'M', 'L', 'XL', 'XXL'], images: [],
      short: 'The everyday layer. Matte black, second-skin fit.' },

    { id: 'circuit-leggings', name: 'Circuit Leggings', category: 'leggings', design: 'circuit', price: 59, compareAt: null, badge: 'Best seller',
      colours: ['sand', 'mocha', 'bone'], sizes: ['XS', 'S', 'M', 'L', 'XL', 'XXL'], images: [],
      short: 'High-rise, squat-proof, with a circuit trace running down each leg.' },
    { id: 'glitch-leggings', name: 'Glitch Leggings', category: 'leggings', design: 'glitch', price: 59, compareAt: null, badge: null,
      colours: ['mocha', 'bone'], sizes: ['XS', 'S', 'M', 'L', 'XL'], images: [],
      short: 'Signal-break panels at the calf and a hidden waistband pocket.' },
    { id: 'grid-7-8-leggings', name: 'Grid 7/8 Leggings', category: 'leggings', design: 'grid', price: 55, compareAt: null, badge: null,
      colours: ['sand', 'onyx'], sizes: ['XS', 'S', 'M', 'L', 'XL', 'XXL'], images: [],
      short: 'Ankle-length cut with a reflective grid for night runs.' },
    { id: 'stealth-run-tights', name: 'Stealth Run Tights', category: 'leggings', design: 'stealth', price: 52, compareAt: 60, badge: 'Sale',
      colours: ['onyx'], sizes: ['S', 'M', 'L', 'XL', 'XXL'], images: [],
      short: 'Unisex full-length tights with zip ankles and phone pocket.' }
  ],

  /* Shared product copy (shown on every product page; edit per product later). */
  productInfo: {
    details: [
      'Graduated compression from cuff to body',
      'Flatlock seams that will not rub under load',
      'Reflective print visible in headlights',
      'Designed in {city}'
    ],
    fabric: [
      '78% recycled polyamide, 22% elastane',
      '4-way stretch, 230 gsm',
      'Moisture-wicking, quick-dry finish',
      'UPF 50+ sun protection'
    ],
    care: [
      'Machine wash cold, inside out',
      'No fabric softener — it blocks the wicking finish',
      'Hang dry, do not tumble dry',
      'Do not iron the print'
    ]
  },

  sizeGuide: {
    note: 'Measurements are body measurements in cm. Between sizes? Size down for firmer compression, up for a relaxed fit.',
    apparel: {
      headers: ['Size', 'Chest', 'Waist', 'Hip'],
      rows: [
        ['XS', '80–86', '62–68', '84–90'],
        ['S', '86–92', '68–74', '90–96'],
        ['M', '92–98', '74–80', '96–102'],
        ['L', '98–104', '80–86', '102–108'],
        ['XL', '104–112', '86–94', '108–116'],
        ['XXL', '112–120', '94–102', '116–124']
      ]
    },
    sleeves: {
      headers: ['Size', 'Bicep (relaxed)', 'Forearm'],
      rows: [
        ['S', '24–28', '20–23'],
        ['M', '28–32', '23–26'],
        ['L', '32–36', '26–29'],
        ['XL', '36–40', '29–32']
      ]
    }
  },

  /* ---------- Page copy ---------- */
  copy: {
    home: {
      heroEyebrow: 'Drop 01 — Night Circuit',
      heroTitle: 'Wired for the night shift',
      heroText: 'Compression sleeves, tops and leggings that hold their shape when you push past midnight.',
      heroCta: 'Shop the drop',
      heroSecondary: 'View lookbook',
      collectionsTitle: 'Choose your layer',
      collections: {
        sleeves: 'Arm sleeves',
        tops: 'Compression tops',
        leggings: 'Leggings'
      },
      lookbookTitle: 'Seen after dark',
      lookbookCta: 'Full lookbook',
      techTitle: 'Built like hardware',
      techText: 'Every piece is cut from a recycled polyamide knit tuned for support, airflow and stretch.',
      tech: [
        { title: 'Compression', text: 'Graduated pressure that supports muscle and cuts vibration on impact.' },
        { title: 'Sweat-wicking', text: 'Moisture moves to the surface and dries fast, so the fabric never clings.' },
        { title: '4-way stretch', text: 'Moves with you in every direction and snaps back without bagging.' }
      ],
      reviewsTitle: 'From the crew',
      reviews: [
        { quote: '[CUSTOMER REVIEW — replace with a real, verified review]', name: '[CUSTOMER NAME]', product: '[PRODUCT]' },
        { quote: '[CUSTOMER REVIEW — replace with a real, verified review]', name: '[CUSTOMER NAME]', product: '[PRODUCT]' },
        { quote: '[CUSTOMER REVIEW — replace with a real, verified review]', name: '[CUSTOMER NAME]', product: '[PRODUCT]' }
      ],
      newsletterTitle: 'Get the next drop first',
      newsletterText: 'Early access, restock alerts and [OFFER, e.g. 10% off your first order]. No spam.'
    },
    shop: {
      title: 'Shop all',
      text: 'Sleeves, tops and leggings in four signal designs.',
      empty: 'Nothing matches those filters. Clear one and try again.'
    },
    lookbook: {
      title: 'Lookbook',
      text: 'Drop 01, shot after dark. Tap any look to shop the category.'
    },
    about: {
      title: 'Our story',
      lead: '[BRAND NAME] started in {city} in {founded} with one question: why does training gear look the same everywhere?',
      founderTitle: 'From one rack to a full drop',
      founderText: '[FOUNDER STORY — two or three sentences about who started the brand, why, and what they care about.]',
      makingTitle: 'How it is made',
      making: [
        { title: 'Design', text: 'Every print starts as a sketch, then gets tested for how it stretches over muscle.' },
        { title: 'Cut', text: 'Panels are cut to follow the body, so seams sit away from pressure points.' },
        { title: 'Pack', text: 'Orders are checked by hand and packed in recyclable boxes.' }
      ],
      valuesTitle: 'What we stand for',
      values: [
        'Gear that performs before it poses',
        'Recycled yarns wherever we can source them',
        'Small drops, made to last, no landfill restocks'
      ]
    },
    shippingPage: {
      title: 'Shipping, returns & FAQ',
      shippingTitle: 'Shipping',
      shipping: [
        'Orders ship in {processingDays} business days.',
        'Free shipping on orders over {freeShipping}. Below that, a flat {flatRate}.',
        'Tracking is emailed as soon as your parcel leaves us.',
        '[INTERNATIONAL SHIPPING POLICY]'
      ],
      returnsTitle: 'Returns & exchanges',
      returns: [
        '{returnDays}-day returns on unworn items with tags attached.',
        'Exchanges for a different size are free.',
        'For hygiene reasons, worn compression items cannot be returned.',
        'Start a return by emailing {email} with your order number.'
      ],
      faqTitle: 'FAQ'
    },
    contact: {
      title: 'Contact',
      text: 'Questions about sizing, an order or wholesale? Send a message and we reply within [RESPONSE TIME].',
      success: 'Message ready. This preview has no backend yet — connect a form service to receive it (see README).'
    },
    footer: {
      blurb: 'Cyberpunk compression wear. Designed for the night shift.',
      newsletterSuccess: 'You are on the list. (Preview mode — connect an email service in README.)'
    }
  },

  faq: [
    { q: 'How tight should compression wear feel?', a: 'Snug and supportive, like a firm handshake — never numb, tingly or restricting your breathing. If it does, go up a size.' },
    { q: 'Do I need one arm sleeve or a pair?', a: 'One is enough for a single sore arm or a sun-exposed side. Most people training both arms buy the pair.' },
    { q: 'Are the leggings squat-proof?', a: 'Yes. Every leggings fabric is tested opaque under deep stretch in bright light.' },
    { q: 'How do I wash the reflective print?', a: 'Cold wash, inside out, no softener, hang dry. Heat and softener wear the print and block wicking.' },
    { q: 'When will my order ship?', a: 'Within {processingDays} business days. You get a tracking link by email.' },
    { q: 'Can I return worn items?', a: 'Unworn items with tags can be returned within {returnDays} days. Worn compression items cannot, for hygiene reasons.' }
  ],

  /* Lookbook — images from images/on_model/. `shop` links each look to a category. */
  lookbook: [
    { src: 'images/on_model/model_black_bodysuit_neon_01.jpg', alt: 'Model in a black compression bodysuit under red neon', shop: 'tops' },
    { src: 'images/on_model/gym_woman_lifting_neon_smoke_01.jpg', alt: 'Woman lifting a barbell in cyan neon smoke', shop: 'leggings' },
    { src: 'images/on_model/athlete_man_compression_top_01.jpg', alt: 'Athlete in a black long-sleeve compression top', shop: 'tops' },
    { src: 'images/on_model/model_pink_neon_tracksuit_01.jpg', alt: 'Model in pink under magenta neon light', shop: 'leggings' },
    { src: 'images/on_model/gym_man_arms_dark_01.jpg', alt: 'Man training arms in a dark gym', shop: 'sleeves' },
    { src: 'images/on_model/model_cyberpunk_portrait_01.jpg', alt: 'Portrait lit in cyan and magenta neon', shop: 'tops' },
    { src: 'images/on_model/runner_night_silhouette_01.jpg', alt: 'Runner silhouetted at night', shop: 'leggings' },
    { src: 'images/on_model/model_uv_neon_fashion_01.jpg', alt: 'Model under UV and blue neon light', shop: 'sleeves' },
    { src: 'images/on_model/athlete_woman_black_leggings_run_01.jpg', alt: 'Woman running in black leggings', shop: 'leggings' },
    { src: 'images/on_model/gym_man_dark_moody_01.jpg', alt: 'Man on a rowing machine in a dark gym', shop: 'sleeves' },
    { src: 'images/on_model/model_cyberpunk_jacket_01.jpg', alt: 'Model in a cyberpunk jacket and visor beside neon racks', shop: 'tops' },
    { src: 'images/on_model/model_activewear_leggings_studio_01.jpg', alt: 'Model in neon yellow and navy leggings in a studio', shop: 'leggings' },
    { src: 'images/on_model/model_futuristic_neon_portrait_01.jpg', alt: 'Futuristic portrait with neon lines and visor', shop: 'sleeves' },
    { src: 'images/on_model/on_model_leggings_stretch_studio_01.jpg', alt: 'Woman stretching in pink leggings', shop: 'leggings' },
    { src: 'images/on_model/on_model_leggings_closeup_01.jpg', alt: 'Close-up of leggings with a rolled training mat', shop: 'leggings' },
    { src: 'images/on_model/on_model_woman_leggings_gym_machine_01.jpg', alt: 'Woman training on a gym machine in leggings', shop: 'leggings' }
  ]
};
