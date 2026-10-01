// MD tab: explore trajectories with animation, blind failure test, molecule quiz.
import { MolViewer } from './viewer.js';

const $ = (id) => document.getElementById(id);
const NS = 'http://www.w3.org/2000/svg';
const cache = {};
async function getJSON(url) {
	return (cache[url] ??= fetch(url).then((r) => r.json()));
}

/* ------------------------------------------------ explore */
const TRAJS = [
	{ id: 'gly_stable_300K', label: 'stable, 300 K', group: 'Glyceraldehyde · ML force field' },
	{ id: 'gly_fail_400K', label: 'failing, 400 K', group: 'Glyceraldehyde · ML force field' },
	{ id: 'md17_ethanol', label: 'ethanol', group: 'MD17 · DFT, 500 K' },
	{ id: 'md17_malonaldehyde', label: 'malonaldehyde', group: 'MD17 · DFT, 500 K' },
	{ id: 'md17_benzene2017', label: 'benzene', group: 'MD17 · DFT, 500 K' },
	{ id: 'md17_toluene', label: 'toluene', group: 'MD17 · DFT, 500 K' },
	{ id: 'md17_naphthalene', label: 'naphthalene', group: 'MD17 · DFT, 500 K' },
	{ id: 'md17_salicylic', label: 'salicylic acid', group: 'MD17 · DFT, 500 K' },
	{ id: 'md17_aspirin', label: 'aspirin', group: 'MD17 · DFT, 500 K' },
	{ id: 'md17_uracil', label: 'uracil', group: 'MD17 · DFT, 500 K' }
];

let cur = null,
	viewer = null,
	forceVariant = false,
	plotGeom = null;
const audio = $('exAudio'),
	svg = $('exPlot');

function buildPicker() {
	const groups = [...new Set(TRAJS.map((t) => t.group))];
	$('trajPicker').innerHTML = groups
		.map(
			(g) =>
				`<div class="prow"><span class="muted small lab">${g}</span><div class="opts">${TRAJS.filter((t) => t.group === g)
					.map((t) => `<button data-traj="${t.id}" aria-pressed="false">${t.label}</button>`)
					.join('')}</div></div>`
		)
		.join('');
	$('trajPicker').querySelectorAll('[data-traj]').forEach((b) => (b.onclick = () => select(b.dataset.traj)));
}

async function select(id) {
	$('trajPicker').querySelectorAll('[data-traj]').forEach((b) => b.setAttribute('aria-pressed', b.dataset.traj === id));
	const t = await getJSON(`data/traj/${id}.json`);
	cur = t;
	$('forceRow').hidden = !t.audio_force;
	if (!t.audio_force) forceVariant = false;
	audio.src = forceVariant && t.audio_force ? t.audio_force : t.audio;
	$('exSource').textContent = `${t.name} · ${t.source} · ${t.frames} frames · ${(t.frames / t.fps).toFixed(0)} s`;
	$('voiceLegend').innerHTML = t.groups
		.map((g) => `<span><span class="sw" style="background:${g.color}"></span>${g.label.replace('H-O', 'O-H').replace('H-N', 'N-H')} · ${g.f0} Hz</span>`)
		.join('');
	viewer = new MolViewer($('exViewer'), { Z: t.Z, bonds: t.bonds, xyz: t.pos[0] });
	viewer.bondColor = t.bonds.map((b) => t.groups[b[2]].color);
	drawPlot();
	frameUpdate(0);
}

function drawPlot() {
	const t = cur;
	svg.innerHTML = '';
	const hasChecks = !!t.drift_kcal;
	const W = 1000,
		L = 64,
		R = 16,
		H = hasChecks ? 470 : 250;
	svg.setAttribute('viewBox', `0 0 ${W} ${H + 20}`);
	const panels = hasChecks ? [{ y: 8, h: 220 }, { y: 250, h: 95 }, { y: 360, h: 95 }] : [{ y: 8, h: 230 }];
	const n = t.frames;
	const x = (i) => L + ((W - L - R) * i) / (n - 1);
	const el = (tag, a) => {
		const e = document.createElementNS(NS, tag);
		for (const k in a) e.setAttribute(k, a[k]);
		svg.appendChild(e);
		return e;
	};
	const path = (vals, y) => vals.map((v, i) => (i ? 'L' : 'M') + x(i).toFixed(1) + ',' + y(v).toFixed(1)).join('');
	const p = panels[0],
		yo = (v) => p.y + (p.h * (3 - v)) / 5;
	for (const g of [-2, -1, 0, 1, 2, 3]) {
		el('line', { x1: L, x2: W - R, y1: yo(g), y2: yo(g), stroke: 'var(--line)' });
		el('text', { x: L - 8, y: yo(g) + 4, 'text-anchor': 'end' }).textContent = (g > 0 ? '+' : '') + g;
	}
	el('text', { x: 14, y: p.y + p.h / 2, transform: `rotate(-90 14 ${p.y + p.h / 2})`, 'text-anchor': 'middle' }).textContent = 'octaves';
	t.octaves.forEach((o, i) => el('path', { d: path(o, yo), fill: 'none', stroke: t.groups[i].color, 'stroke-width': 1.1, opacity: 0.85 }));
	if (hasChecks) {
		[
			[t.drift_kcal, t.thresholds_kcal.energy, 'ΔE kcal/mol'],
			[t.fmax_kcal, t.thresholds_kcal.force, 'F kcal/mol/Å']
		].forEach(([vals, thr, label], k) => {
			const q = panels[k + 1],
				max = Math.max(thr * 2.2, ...vals);
			const lg = (v) => Math.log10(1 + v),
				y = (v) => q.y + q.h * (1 - lg(v) / lg(max));
			el('line', { x1: L, x2: W - R, y1: q.y + q.h, y2: q.y + q.h, stroke: 'var(--line)' });
			el('line', { x1: L, x2: W - R, y1: y(thr), y2: y(thr), stroke: 'var(--muted)', 'stroke-dasharray': '5 4' });
			el('text', { x: L - 8, y: y(thr) + 4, 'text-anchor': 'end' }).textContent = Math.round(thr);
			el('text', { x: 14, y: q.y + q.h / 2, transform: `rotate(-90 14 ${q.y + q.h / 2})`, 'text-anchor': 'middle', 'font-size': 11 }).textContent = label;
			el('path', { d: path(vals, y), fill: 'none', stroke: 'var(--fg)', 'stroke-width': 1.1 });
		});
	}
	const step = n > 1000 ? 250 : 100;
	for (let f = 0; f < n; f += step) el('text', { x: x(f), y: H + 16, 'text-anchor': 'middle' }).textContent = f;
	if (t.first_flag != null) {
		el('line', { x1: x(t.first_flag), x2: x(t.first_flag), y1: 4, y2: H, stroke: 'var(--warn)', 'stroke-width': 2 });
		const lbl = el('text', { x: x(t.first_flag) + 6, y: 20 });
		lbl.style.fill = 'var(--warn)';
		lbl.textContent = 'first automated flag · frame ' + t.first_flag;
	}
	const ph = el('line', { x1: L, x2: L, y1: 4, y2: H, stroke: 'var(--accent)', 'stroke-width': 2 });
	plotGeom = { x, n, ph };
	svg.onclick = (ev) => {
		const r = svg.getBoundingClientRect(),
			fx = ((ev.clientX - r.left) / r.width) * W;
		const f = Math.max(0, Math.min(n - 1, ((fx - L) / (W - L - R)) * (n - 1)));
		audio.currentTime = f / t.fps;
		frameUpdate(f);
	};
}

function frameUpdate(f) {
	if (!cur || !viewer) return;
	const t = cur,
		i = Math.max(0, Math.min(t.frames - 1, Math.floor(f)));
	viewer.setPositions(t.pos[i]);
	// bond stretch relative to the voice's spread: brighter and thicker when far from equilibrium
	const P = t.pos[i];
	t.bonds.forEach(([a, b, g], k) => {
		const d = Math.hypot(P[3 * a] - P[3 * b], P[3 * a + 1] - P[3 * b + 1], P[3 * a + 2] - P[3 * b + 2]);
		const z = Math.abs(d - t.bond_eq[k]) / t.groups[g].std;
		viewer.bondWidth[k] = 3 + 2.2 * Math.min(z, 4);
		viewer.bondAlpha[k] = 0.45 + 0.55 * Math.min(z / 3, 1);
	});
	viewer.render();
	if (plotGeom) {
		const xx = plotGeom.x(i);
		plotGeom.ph.setAttribute('x1', xx);
		plotGeom.ph.setAttribute('x2', xx);
	}
}

function loop() {
	if (cur && !audio.paused) frameUpdate(audio.currentTime * cur.fps);
	requestAnimationFrame(loop);
}
audio.addEventListener('seeked', () => cur && frameUpdate(audio.currentTime * cur.fps));

$('forceToggle').onclick = () => {
	forceVariant = !forceVariant;
	$('forceToggle').setAttribute('aria-pressed', forceVariant);
	if (!cur?.audio_force) return;
	const t = audio.currentTime,
		playing = !audio.paused;
	audio.src = forceVariant ? cur.audio_force : cur.audio;
	audio.currentTime = t;
	if (playing) audio.play();
};

/* ------------------------------------------------ blind failure test */
async function initBlind() {
	const KEY = 'molsounds:test';
	const clips = (await getJSON('data/clips.json')).clips;
	const FPS = (await getJSON('data/clips.json')).fps;
	let state = null;
	try {
		state = JSON.parse(localStorage.getItem(KEY)) || null;
	} catch {}
	const save = () => {
		try {
			localStorage.setItem(KEY, JSON.stringify(state));
		} catch {}
	};
	const tAudio = $('testAudio');
	const show = (w) => {
		$('testIntro').hidden = w !== 'intro';
		$('testRun').hidden = w !== 'run';
		$('testDone').hidden = w !== 'done';
	};
	if (state && !state.done) $('resumeNote').textContent = `Saved progress: ${state.index} of ${clips.length} clips done. Start resumes.`;
	$('startTest').onclick = () => {
		if (!state || state.done) state = { started: new Date().toISOString(), index: 0, presses: {}, done: false };
		save();
		show('run');
		loadClip();
	};
	const clear = () => {
		state = null;
		try {
			localStorage.removeItem(KEY);
		} catch {}
	};
	$('resetTest').onclick = () => {
		clear();
		$('resumeNote').textContent = 'Cleared.';
	};
	$('againBtn').onclick = () => {
		clear();
		show('intro');
	};
	function loadClip() {
		const c = clips[state.index];
		$('clipTitle').textContent = 'Clip ' + c.id;
		$('clipCount').textContent = `${state.index + 1} of ${clips.length}`;
		tAudio.src = c.file;
		tAudio.currentTime = 0;
		tAudio.play().catch(() => {});
		renderPresses();
	}
	function renderPresses() {
		const p = state.presses[clips[state.index].id] || [];
		$('pressLog').textContent = p.length ? 'presses at ' + p.map((s) => s.toFixed(1) + ' s').join(', ') : 'no presses yet';
	}
	function press() {
		if ($('testRun').hidden || (tAudio.paused && tAudio.currentTime === 0)) return;
		const id = clips[state.index].id;
		(state.presses[id] = state.presses[id] || []).push(+tAudio.currentTime.toFixed(2));
		save();
		renderPresses();
		const b = $('pressBtn');
		b.classList.remove('press-flash');
		void b.offsetWidth;
		b.classList.add('press-flash');
	}
	$('pressBtn').onclick = press;
	document.addEventListener('keydown', (e) => {
		if (e.code === 'Space' && !$('testRun').hidden && !$('tab-md').hidden) {
			e.preventDefault();
			press();
		}
	});
	$('replayBtn').onclick = () => {
		tAudio.currentTime = 0;
		tAudio.play();
	};
	$('nextBtn').onclick = () => {
		tAudio.pause();
		state.index++;
		save();
		if (state.index >= clips.length) {
			state.done = true;
			state.finished = new Date().toISOString();
			save();
			finish();
		} else loadClip();
	};
	async function finish() {
		show('done');
		const key = await getJSON('data/key.json');
		let rows = '',
			delays = [],
			hits = 0,
			failing = 0,
			stable = 0,
			fa = 0;
		for (const c of clips) {
			const k = key[c.id],
				p = state.presses[c.id] || [],
				first = p.length ? p[0] : null;
			let verdict = '',
				cls = '';
			if (k.failing) {
				failing++;
				if (first == null) {
					verdict = 'missed';
					cls = 'bad';
				} else {
					hits++;
					const d = first - k.auto_seconds;
					delays.push(d);
					verdict = d <= 0 ? `${(-d).toFixed(1)} s before the checks` : `${d.toFixed(1)} s after the checks`;
					cls = d <= 0 ? 'good' : '';
				}
			} else {
				stable++;
				if (first != null) {
					fa++;
					verdict = 'false alarm';
					cls = 'bad';
				} else {
					verdict = 'correctly quiet';
					cls = 'good';
				}
			}
			rows += `<tr><td>${c.id}</td><td>${k.failing ? '<span class="tag bad">failing</span>' : '<span class="tag">stable</span>'} <span class="muted">${k.source}, frames ${k.start}–${k.stop}</span></td><td>${k.auto_seconds == null ? '—' : k.auto_seconds.toFixed(1) + ' s'}</td><td>${first == null ? '—' : first.toFixed(1) + ' s'}</td><td class="${cls}">${verdict}</td></tr>`;
		}
		$('resultTable').innerHTML = '<tr><th>Clip</th><th>Source</th><th>Checks fire at</th><th>Your first press</th><th>Result</th></tr>' + rows;
		const med = delays.length ? delays.slice().sort((a, b) => a - b)[Math.floor(delays.length / 2)] : null;
		$('summary').innerHTML = `<p style="font-size:1.1rem">You flagged <b>${hits} of ${failing}</b> failing clips${med == null ? '' : `, with a median of <b>${Math.abs(med).toFixed(1)} s ${med <= 0 ? 'before' : 'after'}</b> the automated checks (${Math.round(Math.abs(med) * FPS)} frames)`}, and raised <b>${fa} false alarm${fa === 1 ? '' : 's'}</b> on ${stable} stable clips.</p>`;
		state.results = clips.map((c) => ({ id: c.id, presses: state.presses[c.id] || [], ...key[c.id] }));
		save();
	}
	if (state && state.done) finish();
	$('downloadBtn').onclick = () => {
		const blob = new Blob([JSON.stringify({ page: 'mol-sounds', fps: FPS, ...state }, null, 1)], { type: 'application/json' });
		const a = document.createElement('a');
		a.href = URL.createObjectURL(blob);
		a.download = 'mol-sounds-result.json';
		a.click();
	};
}

/* ------------------------------------------------ which molecule? */
async function initQuiz() {
	const q = await getJSON('data/md17_quiz.json');
	const names = Object.fromEntries(q.molecules.map((m) => [m.id, m.name]));
	let order = q.clips.map((_, i) => i),
		pos = 0,
		score = 0,
		answered = 0,
		locked = false,
		qViewer = null;
	const qa = $('quizAudio');
	$('quizChoices').innerHTML = q.molecules.map((m) => `<button data-mol="${m.id}">${m.name}</button>`).join('');
	function load() {
		locked = false;
		const c = q.clips[order[pos]];
		qa.src = c.file;
		$('quizCount').textContent = `Clip ${pos + 1} of ${order.length}`;
		$('quizFeedback').textContent = 'Listen, then pick a molecule.';
		$('quizNext').hidden = true;
		$('quizReveal').hidden = true;
		$('quizChoices').querySelectorAll('button').forEach((b) => (b.className = ''));
	}
	$('quizChoices').querySelectorAll('button').forEach(
		(b) =>
			(b.onclick = async () => {
				if (locked) return;
				locked = true;
				answered++;
				const c = q.clips[order[pos]];
				const ok = b.dataset.mol === c.answer;
				if (ok) score++;
				b.className = ok ? 'right' : 'wrong';
				$('quizChoices').querySelector(`[data-mol="${c.answer}"]`).className = 'right';
				$('quizFeedback').innerHTML = `${ok ? 'Right' : 'No'}: it was <b>${names[c.answer]}</b>. Score ${score} / ${answered}.`;
				$('quizNext').hidden = pos >= order.length - 1;
				const t = await getJSON(`data/traj/${c.answer}.json`);
				$('quizReveal').hidden = false;
				qViewer = new MolViewer($('quizViewer'), { Z: t.Z, bonds: t.bonds, xyz: t.pos[0] });
				qViewer.bondColor = t.bonds.map((bd) => t.groups[bd[2]].color);
				qViewer.spin = 0.01;
				const spin = () => {
					if ($('quizReveal').hidden || !qViewer) return;
					qViewer.render();
					requestAnimationFrame(spin);
				};
				spin();
			})
	);
	$('quizNext').onclick = () => {
		pos++;
		load();
		qa.play().catch(() => {});
	};
	$('quizRestart').onclick = () => {
		order = order.sort(() => Math.random() - 0.5);
		pos = 0;
		score = 0;
		answered = 0;
		load();
	};
	order.sort(() => Math.random() - 0.5);
	load();
}

export function initMD() {
	buildPicker();
	select('gly_stable_300K');
	loop();
	initBlind();
	initQuiz();
}
