// Chords tab: a molecule's vibrational spectrum (or its bond graph's spring
// spectrum) played as a chord and an arpeggio, with the mode animated.
import { MolViewer } from './viewer.js';

const $ = (id) => document.getElementById(id);
const NS = 'http://www.w3.org/2000/svg';
const LIN = 0.25; // Hz per cm^-1 in "true ratios" mode: C–H stretch ~3000 cm^-1 -> 750 Hz

let index = [],
	mol = null,
	viewer = null,
	ctx = null,
	voices = [],
	playing = null; // {t0, notes, rate, kind}
const opt = { mode: 'vib', map: 'lin', shift: 0, ir: true, order: 'up', tempo: 6, timbre: 'soft' };

function audioCtx() {
	ctx ??= new (window.AudioContext || window.webkitAudioContext)();
	if (ctx.state === 'suspended') ctx.resume();
	return ctx;
}

function hz(nu) {
	const k = 2 ** opt.shift;
	if (opt.map === 'lin') return nu * LIN * k;
	// compressed: 100-4000 cm^-1 -> 110-880 Hz, log-linear
	return 110 * 2 ** ((3 * Math.log(Math.max(nu, 20) / 100)) / Math.log(40)) * k;
}

function notes() {
	if (!mol) return [];
	const src = opt.mode === 'vib' ? mol.vib : mol.graph;
	const irMax = Math.max(...mol.vib.map((m) => m.ir), 1e-9);
	return src
		.map((m, i) => ({
			i,
			nu: m.nu,
			f: hz(m.nu),
			w: opt.mode === 'vib' && opt.ir ? 0.12 + 0.88 * Math.sqrt(m.ir / irMax) : 1,
			ir: m.ir
		}))
		.filter((n) => n.f >= 25 && n.f <= 6000);
}

function wave(c) {
	if (opt.timbre === 'sine') return null;
	const real = new Float32Array([0, 1, 0.35, 0.16, 0.07, 0.03]);
	return c.createPeriodicWave(real, new Float32Array(real.length));
}

function stop() {
	for (const v of voices) {
		try {
			v.g.gain.cancelScheduledValues(ctx.currentTime);
			v.g.gain.setTargetAtTime(0, ctx.currentTime, 0.03);
			v.o.stop(ctx.currentTime + 0.2);
		} catch {}
	}
	voices = [];
	playing = null;
}

function tone(f, t, dur, amp, pw) {
	const c = audioCtx();
	const o = c.createOscillator(),
		g = c.createGain();
	if (pw) o.setPeriodicWave(pw);
	else o.type = 'sine';
	o.frequency.value = f;
	g.gain.setValueAtTime(0, t);
	g.gain.linearRampToValueAtTime(amp, t + 0.015);
	g.gain.setTargetAtTime(amp * 0.6, t + 0.05, 0.25);
	g.gain.setTargetAtTime(0, t + dur, 0.12);
	o.connect(g).connect(c.destination);
	o.start(t);
	o.stop(t + dur + 0.8);
	voices.push({ o, g });
}

function playChord() {
	stop();
	const c = audioCtx(),
		ns = notes(),
		pw = wave(c);
	const total = ns.reduce((s, n) => s + n.w, 0);
	const t = c.currentTime + 0.05;
	for (const n of ns) tone(n.f, t, 3.2, (0.5 * n.w) / Math.max(total, 1.5), pw);
	playing = { t0: t, notes: ns, kind: 'chord', dur: 3.2 };
}

function playArp() {
	stop();
	const c = audioCtx(),
		pw = wave(c);
	let ns = notes().slice().sort((a, b) => a.f - b.f);
	if (opt.order === 'down') ns.reverse();
	if (opt.order === 'updown') ns = ns.concat(ns.slice(0, -1).reverse().slice(0));
	if (opt.order === 'ir') ns = notes().slice().sort((a, b) => b.w - a.w);
	const dt = 1 / opt.tempo,
		t = c.currentTime + 0.05;
	ns.forEach((n, k) => tone(n.f, t + k * dt, dt * 0.9, 0.22 * (0.4 + 0.6 * n.w), pw));
	playing = { t0: t, notes: ns, kind: 'arp', dt, dur: ns.length * dt };
}

function playOne(i) {
	stop();
	const c = audioCtx(),
		n = notes().find((x) => x.i === i);
	if (!n) return;
	const t = c.currentTime + 0.02;
	tone(n.f, t, 1.6, 0.25, wave(c));
	playing = { t0: t, notes: [n], kind: 'one', dur: 1.6 };
}

/* --------------------------------------------- spectrum plot */
function drawSpectrum(active) {
	const svg = $('chSpec');
	svg.innerHTML = '';
	const ns = notes();
	const W = 1000,
		H = 170,
		L = 40,
		R = 16;
	const f0 = 20,
		f1 = 2000;
	const x = (f) => L + ((W - L - R) * Math.log(f / f0)) / Math.log(f1 / f0);
	const el = (tag, a) => {
		const e = document.createElementNS(NS, tag);
		for (const k in a) e.setAttribute(k, a[k]);
		svg.appendChild(e);
		return e;
	};
	for (const f of [25, 50, 100, 200, 400, 800, 1600]) {
		el('line', { x1: x(f), x2: x(f), y1: 8, y2: H, stroke: 'var(--line)' });
		el('text', { x: x(f), y: H + 16, 'text-anchor': 'middle' }).textContent = f + ' Hz';
	}
	const maxw = Math.max(...ns.map((n) => n.w), 1e-9);
	for (const n of ns) {
		const xx = Math.min(x(Math.min(Math.max(n.f, f0), f1)), W - R);
		const on = active && active.has(n.i);
		const ln = el('line', {
			x1: xx,
			x2: xx,
			y1: H,
			y2: H - (H - 14) * (n.w / maxw),
			stroke: on ? 'var(--warn)' : 'var(--accent)',
			'stroke-width': on ? 5 : 3,
			'stroke-linecap': 'round',
			cursor: 'pointer'
		});
		const tt = document.createElementNS(NS, 'title');
		tt.textContent = `${n.nu.toFixed(0)} cm⁻¹ → ${n.f.toFixed(0)} Hz${opt.mode === 'vib' ? ` · IR ${n.ir.toFixed(1)} km/mol` : ''}`;
		ln.appendChild(tt);
		ln.addEventListener('click', () => playOne(n.i));
	}
}

/* --------------------------------------------- animation */
function animate() {
	requestAnimationFrame(animate);
	if (!viewer || !mol) return;
	const now = ctx ? ctx.currentTime : 0;
	let active = null,
		modeIdx = null;
	if (playing) {
		const el = now - playing.t0;
		if (el > playing.dur + 0.3) {
			playing = null;
		} else if (playing.kind === 'arp') {
			const k = Math.min(playing.notes.length - 1, Math.max(0, Math.floor(el / playing.dt)));
			modeIdx = playing.notes[k].i;
			active = new Set([modeIdx]);
		} else if (playing.kind === 'one') {
			modeIdx = playing.notes[0].i;
			active = new Set([modeIdx]);
		} else active = new Set(playing.notes.map((n) => n.i));
	}
	const key = active ? [...active].join(',') : '';
	if (key !== animate.last) {
		drawSpectrum(active);
		animate.last = key;
		$('chNow').textContent =
			modeIdx != null
				? describe(modeIdx)
				: playing?.kind === 'chord'
					? `all ${playing.notes.length} ${opt.mode === 'vib' ? 'vibrational modes' : 'spring modes'} at once`
					: '';
	}
	const t = performance.now() / 1000;
	const xyz = mol.xyz;
	viewer.atomScale.fill(1);
	viewer.atomTint.fill(null);
	if (modeIdx != null && opt.mode === 'vib') {
		const d = mol.vib[modeIdx].d;
		const m = Math.max(...d.map((v) => Math.hypot(...v)), 1e-6);
		const a = (0.45 / m) * Math.sin(2 * Math.PI * 1.6 * t);
		viewer.setPositions(xyz.map((p, i) => [p[0] + a * d[i][0], p[1] + a * d[i][1], p[2] + a * d[i][2]]));
	} else {
		viewer.setPositions(xyz);
		if (modeIdx != null && opt.mode === 'graph') {
			const v = mol.graph[modeIdx].v,
				m = Math.max(...v.map(Math.abs), 1e-6),
				s = Math.sin(2 * Math.PI * 1.6 * t);
			v.forEach((c, i) => {
				viewer.atomScale[i] = 1 + 0.75 * (c / m) * s;
				viewer.atomTint[i] = c * s > 0 ? '#ff9f1c' : c * s < 0 ? '#3fa7d6' : null;
			});
		}
	}
	viewer.spin = playing ? 0 : 0.004;
	viewer.render();
}
function describe(i) {
	if (opt.mode === 'vib') {
		const m = mol.vib[i];
		return `mode ${i + 1}: ${m.nu.toFixed(0)} cm⁻¹ → ${hz(m.nu).toFixed(0)} Hz, IR intensity ${m.ir.toFixed(1)} km/mol`;
	}
	const m = mol.graph[i];
	return `spring mode ${i + 1}: ${m.nu.toFixed(0)} cm⁻¹ equivalent → ${hz(m.nu).toFixed(0)} Hz (atom size and colour show the amplitude)`;
}

/* --------------------------------------------- UI */
async function load(id) {
	stop();
	mol = await (await fetch(`data/chords/${id}.json`)).json();
	$('chPicker').querySelectorAll('[data-mol]').forEach((b) => b.setAttribute('aria-pressed', b.dataset.mol === id));
	viewer = new MolViewer($('chViewer'), { Z: mol.Z, bonds: mol.bonds, xyz: mol.xyz });
	viewer.bondWidth = mol.bonds.map((b) => (b[2] >= 2 ? 6 : b[2] > 1 ? 5 : 3.5));
	$('chInfo').innerHTML = `<b>${mol.name}</b> · ${fmtFormula(mol.formula)} · ${mol.Z.length} atoms · ${mol.vib.length} vibrational modes · <span class="muted">${mol.smiles}</span>`;
	animate.last = null;
	drawSpectrum(null);
}
function fmtFormula(f) {
	return f.replace(/(\d+)/g, '<sub>$1</sub>');
}

export async function initChords() {
	index = await (await fetch('data/chords/index.json')).json();
	const groups = [
		['small', 'Small molecules'],
		['MD17', 'MD17'],
		['rMD17', 'MD17'],
		['this page', 'MD17'],
		['classic', 'Classics']
	];
	const order = ['Small molecules', 'MD17', 'Classics'];
	const byGroup = {};
	for (const m of index) {
		const g = groups.find((x) => x[0] === m.group)?.[1] ?? 'Other';
		(byGroup[g] ??= []).push(m);
	}
	$('chPicker').innerHTML = order
		.map((g) => `<div class="prow"><span class="muted small lab">${g}</span><div class="opts">${(byGroup[g] || []).map((m) => `<button data-mol="${m.id}" aria-pressed="false">${m.name}</button>`).join('')}</div></div>`)
		.join('');
	$('chPicker').querySelectorAll('[data-mol]').forEach((b) => (b.onclick = () => load(b.dataset.mol)));
	const bindGroup = (attr, key, after) =>
		document.querySelectorAll(`[${attr}]`).forEach(
			(b) =>
				(b.onclick = () => {
					opt[key] = b.getAttribute(attr);
					document.querySelectorAll(`[${attr}]`).forEach((x) => x.setAttribute('aria-pressed', x === b));
					after?.();
				})
		);
	bindGroup('data-mode', 'mode', () => {
		$('irRow').style.visibility = opt.mode === 'vib' ? 'visible' : 'hidden';
		stop();
		animate.last = null;
	});
	bindGroup('data-map', 'map', () => (animate.last = null));
	bindGroup('data-order', 'order');
	bindGroup('data-timbre', 'timbre');
	$('irToggle').onclick = () => {
		opt.ir = !opt.ir;
		$('irToggle').setAttribute('aria-pressed', opt.ir);
		animate.last = null;
	};
	$('shift').oninput = (e) => {
		opt.shift = +e.target.value;
		$('shiftVal').textContent = (opt.shift > 0 ? '+' : '') + opt.shift + ' oct';
		animate.last = null;
	};
	$('tempo').oninput = (e) => {
		opt.tempo = +e.target.value;
		$('tempoVal').textContent = opt.tempo + ' notes/s';
	};
	$('chChord').onclick = playChord;
	$('chArp').onclick = playArp;
	$('chStop').onclick = stop;
	await load('aspirin');
	animate();
}
