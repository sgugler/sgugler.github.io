// Minimal ball-and-stick viewer on a 2D canvas. Orthographic, depth-sorted,
// drag to rotate. No dependencies.
const CPK = { 1: '#e9e9e9', 6: '#606060', 7: '#3657f0', 8: '#e8352a', 9: '#90e050', 16: '#f0c020', 17: '#1ff01f' };
const RAD = { 1: 0.27, 6: 0.4, 7: 0.4, 8: 0.4 };

export class MolViewer {
	constructor(canvas, { Z, bonds, xyz }) {
		this.c = canvas;
		this.ctx = canvas.getContext('2d');
		this.Z = Z;
		this.bonds = bonds; // [[i, j, ...]]
		this.n = Z.length;
		this.rot = rotY(0.5).mul(rotX(-0.35));
		this.bondColor = bonds.map(() => '#9aa0aa');
		this.bondWidth = bonds.map(() => 3);
		this.bondAlpha = bonds.map(() => 0.9);
		this.atomScale = new Array(this.n).fill(1);
		this.atomTint = new Array(this.n).fill(null);
		this.setPositions(xyz);
		this.fit(xyz);
		this.spin = 0;
		this.#bindDrag();
		const ro = new ResizeObserver(() => this.render());
		ro.observe(canvas);
	}
	fit(xyz) {
		const pts = toPts(xyz, this.n);
		const c = centroid(pts);
		this.center = c;
		this.extent = Math.max(1.5, ...pts.map((p) => Math.hypot(p[0] - c[0], p[1] - c[1], p[2] - c[2]))) + 0.6;
	}
	setPositions(xyz) {
		this.pts = toPts(xyz, this.n);
	}
	render() {
		const c = this.c,
			dpr = window.devicePixelRatio || 1;
		const w = c.clientWidth,
			h = c.clientHeight;
		if (!w || !h) return;
		if (c.width !== Math.round(w * dpr)) c.width = Math.round(w * dpr);
		if (c.height !== Math.round(h * dpr)) c.height = Math.round(h * dpr);
		const ctx = this.ctx;
		ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
		ctx.clearRect(0, 0, w, h);
		if (this.spin) this.rot = rotY(this.spin).mul(this.rot);
		const s = (Math.min(w, h) / 2 / this.extent) * 0.95;
		const P = this.pts.map((p) => {
			const q = this.rot.apply([p[0] - this.center[0], p[1] - this.center[1], p[2] - this.center[2]]);
			return [w / 2 + q[0] * s, h / 2 - q[1] * s, q[2]];
		});
		const items = [];
		this.bonds.forEach((b, k) => {
			const [i, j] = b;
			items.push({ z: (P[i][2] + P[j][2]) / 2 - 0.01, k, bond: true });
		});
		for (let i = 0; i < this.n; i++) items.push({ z: P[i][2], i });
		items.sort((a, b) => a.z - b.z);
		const outline = getComputedStyle(c).getPropertyValue('--bg') || '#111';
		for (const it of items) {
			if (it.bond) {
				const [i, j] = this.bonds[it.k];
				ctx.globalAlpha = this.bondAlpha[it.k];
				ctx.strokeStyle = this.bondColor[it.k];
				ctx.lineWidth = this.bondWidth[it.k];
				ctx.lineCap = 'round';
				ctx.beginPath();
				ctx.moveTo(P[i][0], P[i][1]);
				ctx.lineTo(P[j][0], P[j][1]);
				ctx.stroke();
			} else {
				const i = it.i,
					z = this.Z[i];
				const r = (RAD[z] ?? 0.42) * s * 0.75 * this.atomScale[i];
				const depth = 0.75 + 0.25 * Math.tanh(P[i][2] / this.extent);
				ctx.globalAlpha = 1;
				const g = ctx.createRadialGradient(P[i][0] - r * 0.35, P[i][1] - r * 0.35, r * 0.1, P[i][0], P[i][1], r);
				const base = this.atomTint[i] ?? CPK[z] ?? '#c080c0';
				g.addColorStop(0, '#ffffff');
				g.addColorStop(0.25, base);
				g.addColorStop(1, shade(base, 0.55 * depth));
				ctx.fillStyle = g;
				ctx.beginPath();
				ctx.arc(P[i][0], P[i][1], Math.max(1.5, r), 0, 2 * Math.PI);
				ctx.fill();
				ctx.lineWidth = 1;
				ctx.strokeStyle = outline.trim() || '#111';
				ctx.stroke();
			}
		}
		ctx.globalAlpha = 1;
	}
	#bindDrag() {
		let last = null;
		this.c.style.touchAction = 'none';
		this.c.style.cursor = 'grab';
		this.c.addEventListener('pointerdown', (e) => {
			last = [e.clientX, e.clientY];
			this.c.setPointerCapture(e.pointerId);
		});
		this.c.addEventListener('pointermove', (e) => {
			if (!last) return;
			const dx = e.clientX - last[0],
				dy = e.clientY - last[1];
			last = [e.clientX, e.clientY];
			this.rot = rotY(dx * 0.01).mul(rotX(dy * 0.01)).mul(this.rot);
			this.render();
		});
		const end = () => (last = null);
		this.c.addEventListener('pointerup', end);
		this.c.addEventListener('pointercancel', end);
	}
}

function toPts(xyz, n) {
	if (Array.isArray(xyz[0])) return xyz.map((p) => [p[0], p[1], p[2]]);
	const out = [];
	for (let i = 0; i < n; i++) out.push([xyz[3 * i], xyz[3 * i + 1], xyz[3 * i + 2]]);
	return out;
}
function centroid(pts) {
	const c = [0, 0, 0];
	for (const p of pts) for (let k = 0; k < 3; k++) c[k] += p[k] / pts.length;
	return c;
}
function shade(hex, f) {
	const n = parseInt(hex.slice(1), 16);
	const r = ((n >> 16) & 255) * f,
		g = ((n >> 8) & 255) * f,
		b = (n & 255) * f;
	return `rgb(${r | 0},${g | 0},${b | 0})`;
}
class M3 {
	constructor(a) {
		this.a = a;
	}
	mul(o) {
		const a = this.a,
			b = o.a,
			r = new Array(9).fill(0);
		for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) for (let k = 0; k < 3; k++) r[3 * i + j] += a[3 * i + k] * b[3 * k + j];
		return new M3(r);
	}
	apply(v) {
		const a = this.a;
		return [a[0] * v[0] + a[1] * v[1] + a[2] * v[2], a[3] * v[0] + a[4] * v[1] + a[5] * v[2], a[6] * v[0] + a[7] * v[1] + a[8] * v[2]];
	}
}
function rotX(t) {
	const c = Math.cos(t),
		s = Math.sin(t);
	return new M3([1, 0, 0, 0, c, -s, 0, s, c]);
}
function rotY(t) {
	const c = Math.cos(t),
		s = Math.sin(t);
	return new M3([c, 0, s, 0, 1, 0, -s, 0, c]);
}
