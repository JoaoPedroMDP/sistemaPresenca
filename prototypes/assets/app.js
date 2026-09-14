/* ===========================================================
   Sistema de Presença — apoio compartilhado dos protótipos
   Dados falsos, QR Code desenhado à mão e as animações do app.
   =========================================================== */

/* ===========================================================
   Componente de membro — foto, nome completo e, na semana do
   aniversário, chapéu de festa.
   Mesma marcação em todo lugar: Phloating e lista do tablet.
   =========================================================== */
const PHOTO_PLACEHOLDER = 'assets/profileAzul.png';

/**
 * Marcação de um membro.
 * @param {object} member  { name, photo, birthday }
 * @param {object} [opts]  { size: px da foto, showName: bool }
 */
function memberHTML(member, opts = {}) {
  const size = opts.size ?? 80;
  const showName = opts.showName !== false;
  const perks = member.birthday
    ? `<img class="member-hat" src="assets/partyhat.png" alt="">`
    : '';

  return `
    <div class="member" style="--member-photo-size:${size}px">
      <div class="member-photo-wrap">
        ${perks}
        <img class="member-photo" src="${member.photo || PHOTO_PLACEHOLDER}" alt="${member.name}">
      </div>
      ${showName ? `<span class="member-name">${member.name}</span>` : ''}
    </div>`;
}

/** Mesma coisa, já como elemento do DOM. */
function memberEl(member, opts) {
  const wrap = document.createElement('div');
  wrap.innerHTML = memberHTML(member, opts).trim();
  return wrap.firstElementChild;
}

/* ---------- Membros falsos ---------- */
const MEMBER_NAMES = [
  'Ana Beatriz', 'Bruno Carvalho', 'Camila Rocha', 'Daniel Alves',
  'Eduarda Lima', 'Felipe Moraes', 'Gabriela Souza', 'Henrique Dias',
  'Isabela Freitas', 'João Pedro', 'Karina Mendes', 'Lucas Barbosa',
  'Mariana Teixeira', 'Nathan Ribeiro', 'Olívia Castro', 'Pedro Henrique',
  'Rafaela Nunes', 'Samuel Oliveira', 'Tatiane Gomes', 'Vitor Hugo',
];

// photo: null cai no placeholder, igual ao app (src || photoPlaceholder)
const MEMBERS = MEMBER_NAMES.map((name, i) => ({
  id: i + 1,
  name,
  photo: null,
  // Uma pessoa na semana do aniversário, para mostrar o chapéu
  birthday: name === 'Camila Rocha',
}));

const SCOREBOARD = [
  { name: 'Camila Rocha',    score: 480 },
  { name: 'João Pedro',      score: 450 },
  { name: 'Bruno Carvalho',  score: 420 },
  { name: 'Ana Beatriz',     score: 390 },
  { name: 'Felipe Moraes',   score: 360 },
];

/* ---------- QR Code falso ---------- */
/* O app usa @svelte-put/qr com módulos circulares, azul indigo-900 e
   âncoras verdes. Aqui desenhamos um padrão determinístico parecido. */
function renderFakeQr(el, seed, size = 300) {
  const N = 25;                     // módulos por lado
  const cell = size / N;
  const r = cell * 0.42;
  let h = 0;
  for (const ch of String(seed)) h = (h * 131 + ch.charCodeAt(0)) >>> 0;
  const rand = () => (h = (h * 1103515245 + 12345) >>> 0) / 4294967296;

  const isAnchor = (x, y) =>
    (x < 7 && y < 7) || (x >= N - 7 && y < 7) || (x < 7 && y >= N - 7);

  let dots = '';
  for (let y = 0; y < N; y++) {
    for (let x = 0; x < N; x++) {
      if (isAnchor(x, y)) continue;
      // Espaço reservado ao logo, no centro
      if (x > 9 && x < 15 && y > 9 && y < 15) continue;
      if (rand() > 0.52) {
        dots += `<circle cx="${(x + .5) * cell}" cy="${(y + .5) * cell}" r="${r}" fill="#312e81"/>`;
      }
    }
  }

  const anchor = (ax, ay) => {
    const p = ax * cell, q = ay * cell, s = 7 * cell;
    return `
      <rect x="${p}" y="${q}" width="${s}" height="${s}" rx="${s * .28}"
            fill="none" stroke="#34d399" stroke-width="${cell}"/>
      <rect x="${p + cell * 2}" y="${q + cell * 2}" width="${cell * 3}" height="${cell * 3}"
            rx="${cell}" fill="#312e81"/>`;
  };

  el.innerHTML = `
    <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}"
         style="border-radius:1rem;background:#fff">
      ${dots}
      ${anchor(0, 0)}${anchor(N - 7, 0)}${anchor(0, N - 7)}
      <image href="assets/jovensLogoVerde.png"
             x="${size * .38}" y="${size * .38}"
             width="${size * .24}" height="${size * .24}"/>
    </svg>`;
}

/* Caminho quadrado-arredondado do anel de contagem regressiva (QrCode.svelte) */
function ringPath(inset, radius) {
  const a = inset, b = 100 - inset, r = radius;
  return [
    `M 50 ${a}`,
    `H ${b - r}`, `A ${r} ${r} 0 0 1 ${b} ${a + r}`,
    `V ${b - r}`, `A ${r} ${r} 0 0 1 ${b - r} ${b}`,
    `H ${a + r}`, `A ${r} ${r} 0 0 1 ${a} ${b - r}`,
    `V ${a + r}`, `A ${r} ${r} 0 0 1 ${a + r} ${a}`,
    `H 50`,
  ].join(' ');
}

/* ---------- Phloating: fotos flutuantes com colisão nas bordas ---------- */
const PHOTO_SIZE = 80;
const MIN_SPEED = 2;
const MAX_SPEED = 5;
const DECELERATION = 0.997;

function createPhloating(container) {
  const items = [];
  let W = container.clientWidth || 800;
  let H = container.clientHeight || 600;

  const between = (a, b) => a + Math.random() * (b - a);
  const sign = () => (Math.random() > 0.5 ? 1 : -1);

  function addPhoto(member) {
    // Mesmo componente da lista do tablet, só que flutuando
    const el = memberEl(member, { size: PHOTO_SIZE });
    el.classList.add('floating-item');
    container.appendChild(el);

    items.push({
      el,
      w: el.offsetWidth || PHOTO_SIZE,
      h: el.offsetHeight || PHOTO_SIZE,
      x: between(PHOTO_SIZE, Math.max(PHOTO_SIZE + 1, W - PHOTO_SIZE * 2)),
      y: between(PHOTO_SIZE, Math.max(PHOTO_SIZE + 1, H - PHOTO_SIZE * 2)),
      vx: between(MIN_SPEED, MAX_SPEED) * sign(),
      vy: between(MIN_SPEED, MAX_SPEED) * sign(),
    });
  }

  function decel(v) {
    const nv = v * DECELERATION;
    return Math.abs(nv) < MIN_SPEED ? v : nv;
  }

  function tick() {
    for (const it of items) {
      // O nome deixa o item mais largo que a foto; mede depois de pintar
      if (it.el.offsetWidth) { it.w = it.el.offsetWidth; it.h = it.el.offsetHeight; }

      it.x += it.vx;
      it.y += it.vy;
      if (it.x <= 0)          { it.x = 0;          it.vx = Math.abs(it.vx); }
      if (it.x >= W - it.w)   { it.x = W - it.w;   it.vx = -Math.abs(it.vx); }
      if (it.y <= 0)          { it.y = 0;          it.vy = Math.abs(it.vy); }
      if (it.y >= H - it.h)   { it.y = H - it.h;   it.vy = -Math.abs(it.vy); }
      it.vx = decel(it.vx);
      it.vy = decel(it.vy);
      it.el.style.transform = `translate(${it.x}px, ${it.y}px)`;
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);

  window.addEventListener('resize', () => {
    W = container.clientWidth;
    H = container.clientHeight;
  });

  return { addPhoto, count: () => items.length };
}

/* ---------- Versão exibida no canto ---------- */
function stampVersion(v = '1.1.0') {
  const s = document.createElement('span');
  s.className = 'version';
  s.textContent = 'v' + v;
  document.body.appendChild(s);
}

/* ---------- Credencial do dispositivo ----------
 * O aparelho é liberado escaneando um QR gerado no admin. O código vem na
 * URL (/checkin/device/<code>), é resgatado uma única vez e fica guardado
 * aqui. Daí em diante ele entra no path de toda chamada do dispositivo
 * (/api/checkin/device/<code>/...) — é o que prova que quem chama é um
 * aparelho liberado, e não alguém que abriu a URL no próprio celular.
 * Fica no localStorage (não no sessionStorage): reabrir o app ou o navegador
 * não pede ativação de novo. */
const DEVICE_CODE_KEY = 'device_code';

function getDeviceCode() {
  return localStorage.getItem(DEVICE_CODE_KEY);
}

function setDeviceCode(code, eventName) {
  localStorage.setItem(DEVICE_CODE_KEY, code);
  localStorage.setItem('device_event', eventName);
}
