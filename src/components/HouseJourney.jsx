import { Component, Suspense, useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { useGLTF, useTexture } from '@react-three/drei';
import * as THREE from 'three';
import home from '../data/premiumHome.json';
import { rooms, walkRooms } from '../data/rooms';
import { TOUR_PATHS, STOPS, JOURNEY_IDS, EXTERIOR_SECTIONS } from '../data/journey';
import { buildTourGraph, shortestRoute, measureRoute, sampleRoute } from '../lib/tourRoutes';
import './HouseJourney.css';

export { JOURNEY_IDS };

const SKY = '/sky/golden-sky.webp';

/*
  The landing opens on a Cycles render of the house at golden hour
  (blender/premium-home/render_hero.py), not on the live scene: at that
  framing the realtime exterior reads as a model. It fades into the live
  house over the About section. Portrait screens get their own framing.
*/
export const heroImageFor = (win) => {
  if (win.matchMedia('(max-aspect-ratio: 4/5)').matches) return '/hero/hero-mobile.webp';
  return win.innerWidth * (win.devicePixelRatio || 1) > 2100 ? '/hero/hero-desktop.webp' : '/hero/hero-desktop-1920.webp';
};
const EXTERIOR = '/models/exterior.glb';
const DOOR = '/models/door.glb';
// Where the walk stands before the living room's doors
const ENTRY_AT = JOURNEY_IDS.indexOf('entry');
// Baked door leaves are drawn unlit; this brings them to the level of the
// lightmapped walls around them (three divides lightmapped diffuse by pi)
const DOOR_GAIN = 0.72;
const SKY_MOBILE = '/sky/golden-sky-mobile.webp';
const graph = buildTourGraph(TOUR_PATHS);
const N = JOURNEY_IDS.length;

/*
  Overlay layers, weighted per section and blended continuously with scroll,
  so a wash never lingers after its section has gone (the old per-section
  switch left Services' white over the living room until its title reached
  the top of the screen).
*/
// Reading sections are now opaque sheets of their own (App.css); the paper
// wash only remains for the gallery page.
const PAPER_SECTIONS = new Set();
const WALK_IDS = new Set(walkRooms.map((r) => r.id));
const LAYERS = ['paper', 'room', 'landing', 'about'];
const WEIGHTS = JOURNEY_IDS.map((id) => ({
  paper: PAPER_SECTIONS.has(id) ? 1 : 0,
  room: WALK_IDS.has(id) ? 1 : 0,
  landing: id === 'landing' ? 1 : 0,
  about: id === 'hero' ? 1 : 0
}));


/*
  One route per pair of neighbouring sections, precomputed once. Scrolling
  from section i to i+1 walks LEGS[i] in exact proportion to how far you have
  scrolled, so the camera can never fall behind the page.
*/
const LEGS = JOURNEY_IDS.slice(0, -1).map((id, i) => {
  const a = STOPS[id];
  const b = STOPS[JOURNEY_IDS[i + 1]];
  try {
    return measureRoute(shortestRoute(graph, a.position, b.position));
  } catch {
    // Either end is off-graph: a straight run is safe between outdoor stops.
    return measureRoute([a.position, b.position]);
  }
});

const smoothstep = (a, b, x) => {
  const t = THREE.MathUtils.clamp((x - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
};

class SceneBoundary extends Component {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch(error) { this.props.onError(error); }
  render() { return this.state.failed ? null : this.props.children; }
}

/* ------------------------------------------------------------------ model */
function House({ mobile, onReady }) {
  const { scene } = useGLTF(home.model, '/draco/');
  const lightmap = useTexture(mobile ? home.mobileLightmap : home.lightmap);
  const { gl } = useThree();
  const maxAniso = gl.capabilities.getMaxAnisotropy();

  const prepared = useMemo(() => {
    const clone = scene.clone(true);
    lightmap.flipY = false;
    lightmap.colorSpace = THREE.SRGBColorSpace;
    lightmap.channel = 1;
    lightmap.anisotropy = maxAniso;
    lightmap.minFilter = THREE.LinearMipmapLinearFilter;
    lightmap.magFilter = THREE.LinearFilter;
    clone.traverse((o) => {
      if (!o.isMesh) return;
      const materials = Array.isArray(o.material) ? o.material : [o.material];
      const next = materials.map((original) => {
        const m = original.clone();
        // The atlas carries baked fixture and daylight irradiance. The sky
        // environment supplies view-dependent specular on top of it.
        if (o.geometry.attributes.uv1 && !/Glass|Water/.test(m.name)) {
          m.lightMap = lightmap;
          m.lightMapIntensity = 2.05;
        }
        m.envMapIntensity = 0.22;
        // Foliage carries no lightmap (it ships as its own mesh, see
        // export_web.py): the sky lights it, warmed to sit with the rooms
        if (o.name.includes('Foliage')) {
          m.envMapIntensity = 1.1;
          if (m.color) m.color.multiplyScalar(1.15);
        }
        if (/Glass/.test(m.name)) {
          m.transmission = 0;
          m.transparent = true;
          m.opacity = 0.1;
          m.depthWrite = false;
          m.roughness = 0.06;
          m.metalness = 0;
          m.side = THREE.DoubleSide;
          m.envMapIntensity = 1.1;
        }
        for (const tex of [m.map, m.normalMap, m.roughnessMap]) {
          if (tex) tex.anisotropy = maxAniso;
        }
        m.needsUpdate = true;
        return m;
      });
      o.material = Array.isArray(o.material) ? next : next[0];
    });
    return clone;
  }, [scene, lightmap, maxAniso]);

  useEffect(() => {
    onReady(true);
    return () => {
      prepared.traverse((o) => {
        if (!o.isMesh) return;
        (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => m.dispose());
      });
    };
  }, [prepared, onReady]);

  return <primitive object={prepared} />;
}

/* ------------------------------------------------------- exterior dressing */
/*
  The shipped model is interior-first, so the outside gets its roof, glazing
  frames, terrace, pool and landscape from a separate 37 KB file. Lit purely
  by the sky, no lightmap, so it costs almost nothing.
*/
function Exterior() {
  const { scene } = useGLTF(EXTERIOR, '/draco/');
  const { gl } = useThree();
  const maxAniso = gl.capabilities.getMaxAnisotropy();

  const prepared = useMemo(() => {
    const clone = scene.clone(true);
    clone.traverse((o) => {
      if (!o.isMesh) return;
      const m = Array.isArray(o.material) ? o.material[0] : o.material;
      if (!m) return;
      m.envMapIntensity = 1.0;
      if (/Water/i.test(m.name)) {
        // Still water is mostly a mirror of the sky at this hour
        m.roughness = 0.03;
        m.metalness = 0.25;
        m.envMapIntensity = 2.4;
      }
      if (/Lawn|Hedge|Canopy/i.test(m.name)) m.envMapIntensity = 0.7;
      for (const tex of [m.map, m.normalMap, m.roughnessMap]) {
        if (tex) tex.anisotropy = maxAniso;
      }
      m.needsUpdate = true;
    });
    return clone;
  }, [scene, maxAniso]);

  return <primitive object={prepared} />;
}

/* ------------------------------------------------------------------- rig */
function Rig({ progressRef, camProgressRef, visibleRef, invalidateRef, reducedMotion }) {
  const { camera, size, invalidate } = useThree();

  // The page asks for frames through this; the canvas renders on demand
  useEffect(() => {
    invalidateRef.current = invalidate;
    return () => { invalidateRef.current = null; };
  }, [invalidate, invalidateRef]);
  const scratch = useMemo(() => ({
    dummy: new THREE.PerspectiveCamera(),
    target: new THREE.Vector3(),
    a: new THREE.Vector3(),
    b: new THREE.Vector3(),
    ahead: new THREE.Vector3()
  }), []);

  const smoothed = useRef(0);
  const lastFrame = useRef(0);
  const settle = useRef(0);

  useFrame((_, delta) => {
    const dt = Math.min(delta, 0.08);

    /* ---------------------------------------------- scroll-bound travel */
    // A light damp only smooths wheel jitter; it still tracks scroll one to one.
    // After a spell unseen (under a sheet or the landing render) the canvas
    // drew nothing, so the damped value is stale: jump to the page rather
    // than sweep across the house to catch up
    const now = performance.now();
    const stale = now - lastFrame.current > 250;
    lastFrame.current = now;
    smoothed.current = reducedMotion || stale
      ? progressRef.current
      : THREE.MathUtils.damp(smoothed.current, progressRef.current, 11, dt);
    camProgressRef.current = smoothed.current;
    const p = THREE.MathUtils.clamp(smoothed.current, 0, N - 1);
    const i = Math.min(N - 2, Math.floor(p));
    const raw = p - i;
    // Arrive, rest while the copy is read, then move on. Through the door
    // the walk waits for the leaves to part before it steps forward.
    const t = i === ENTRY_AT ? smoothstep(0.34, 0.96, raw) : smoothstep(0.2, 0.9, raw);

    const leg = LEGS[i];
    const a = STOPS[JOURNEY_IDS[i]];
    const b = STOPS[JOURNEY_IDS[i + 1]];
    const d = leg.total * t;
    camera.position.fromArray(sampleRoute(leg, d).point);

    // Look where you are going while moving, at the room once you arrive
    // A leg that goes nowhere (Services and the hall share the door view)
    // has no "ahead" to look at: keep looking where the stops look
    const still = leg.total < 0.05;
    const atA = still ? 1 - t : 1 - smoothstep(0.0, 0.22, t);
    const atB = still ? t : smoothstep(0.72, 1.0, t);
    const travelling = Math.max(0, 1 - atA - atB);
    scratch.ahead.fromArray(sampleRoute(leg, Math.min(leg.total, d + 3)).point);
    scratch.target
      .set(0, 0, 0)
      .addScaledVector(scratch.a.fromArray(a.target), atA)
      .addScaledVector(scratch.b.fromArray(b.target), atB)
      .addScaledVector(scratch.ahead, travelling);

    scratch.dummy.position.copy(camera.position);
    scratch.dummy.lookAt(scratch.target);
    camera.quaternion.slerp(scratch.dummy.quaternion, reducedMotion || stale ? 1 : 1 - Math.exp(-dt * 6));

    const narrow = size.width / size.height < 0.85;
    camera.fov = THREE.MathUtils.lerp(a.fov, b.fov, t) + (narrow ? 12 : 0);
    camera.updateProjectionMatrix();

    // Keep drawing only while the camera is still settling onto the scroll
    // position (plus a short tail for the look-at slerp), and only while the
    // house is actually on screen
    if (Math.abs(smoothed.current - progressRef.current) > 1e-4) settle.current = 45;
    if (settle.current > 0) settle.current -= 1;
    if (visibleRef.current && settle.current > 0) invalidate();
  });

  return null;
}

/* ------------------------------------------------------------------- sky */
/*
  drei's Environment picks a loader by file extension and does not know
  .webp, so the sky is wired by hand. The raw equirect stays as the crisp
  background; a PMREM copy does the lighting, which is what gives roughness
  aware reflections on the glass and the stone.
*/
function Sky({ file }) {
  const texture = useTexture(file);
  const { scene, gl } = useThree();

  useEffect(() => {
    texture.mapping = THREE.EquirectangularReflectionMapping;
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = gl.capabilities.getMaxAnisotropy();

    const pmrem = new THREE.PMREMGenerator(gl);
    pmrem.compileEquirectangularShader();
    const env = pmrem.fromEquirectangular(texture).texture;

    const previousBg = scene.background;
    const previousEnv = scene.environment;
    scene.background = texture;
    scene.environment = env;

    return () => {
      scene.background = previousBg;
      scene.environment = previousEnv;
      env.dispose();
      pmrem.dispose();
    };
  }, [texture, scene, gl]);

  return null;
}

/* ----------------------------------------------------------------- world */
/* ---------------------------------------------------------- pocket doors */
/*
  The living room's two walnut leaves (build_door.py). They meet in the
  opening and slide apart into the wall as you scroll from the hall into the
  room, tied to the camera's own progress so door and step stay in time.
*/
/* Reeded glass: fine vertical ribs, drawn once to a small canvas */
function reededTexture() {
  const c = document.createElement('canvas');
  c.width = 512;
  c.height = 8;
  const g = c.getContext('2d');
  const ribs = 40;
  for (let x = 0; x < c.width; x++) {
    const u = (x / c.width) * ribs;
    const shade = 0.72 + 0.28 * Math.pow(Math.abs(Math.cos(Math.PI * u)), 0.6);
    const v = Math.round(255 * shade);
    g.fillStyle = `rgb(${v},${Math.round(v * 0.97)},${Math.round(v * 0.93)})`;
    g.fillRect(x, 0, 1, c.height);
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = THREE.RepeatWrapping;
  t.wrapT = THREE.RepeatWrapping;
  return t;
}

function Door({ camProgressRef }) {
  const { scene } = useGLTF(DOOR);
  const { gl } = useThree();
  const door = useMemo(() => {
    const clone = scene.clone(true);
    const leaves = {};
    const glass = new THREE.MeshStandardMaterial({
      color: '#f4ebdf',
      map: reededTexture(),
      transparent: true,
      opacity: 0.5,
      roughness: 0.18,
      metalness: 0,
      envMapIntensity: 0.9,
      depthWrite: false,
      side: THREE.DoubleSide
    });
    const bronze = new THREE.MeshStandardMaterial({ color: '#c49d6b', metalness: 1, roughness: 0.3, envMapIntensity: 1.3 });
    clone.traverse((o) => {
      if (o.isMesh) {
        const name = o.material?.name || '';
        if (name.includes('Glass')) o.material = glass;
        else if (name.includes('Pull')) o.material = bronze;
        else {
          // frames, panels and casing carry their light baked in
          const map = o.material.map;
          if (map) {
            map.colorSpace = THREE.SRGBColorSpace;
            map.anisotropy = gl.capabilities.getMaxAnisotropy();
          }
          o.material = new THREE.MeshBasicMaterial({ map, color: new THREE.Color(DOOR_GAIN, DOOR_GAIN, DOOR_GAIN) });
        }
      }
      if (o.name === 'DoorLeft' || o.name === 'DoorRight') leaves[o.name] = { node: o, x: o.position.x };
    });
    return { clone, leaves };
  }, [scene, gl]);

  useFrame(() => {
    const p = camProgressRef.current;
    const open = smoothstep(ENTRY_AT + 0.04, ENTRY_AT + 0.44, p);
    const travel = 1.42 * open;
    // DoorLeft is on your left from the hall (larger x) and slides that way
    const { DoorLeft: l, DoorRight: r } = door.leaves;
    if (l) l.node.position.x = l.x + travel;
    if (r) r.node.position.x = r.x - travel;
  });

  return <primitive object={door.clone} />;
}

function World({ mobile, onReady, ...rig }) {
  return (
    <>
      {/* The sky is both backdrop and reflection source, so the sunset reads
          through every window from inside the house. */}
      <Sky file={mobile ? SKY_MOBILE : SKY} />
      <ambientLight intensity={0.035} color="#efe7db" />
      <hemisphereLight args={['#ffd7a6', '#3d4632', 0.42]} />
      <House mobile={mobile} onReady={onReady} />
      <Exterior />
      <Door camProgressRef={rig.camProgressRef} />
      <Rig {...rig} />
    </>
  );
}

/* ---------------------------------------------------------------- public */
export default function HouseJourney({ activeSection }) {
  const [ready, setReady] = useState(false);
  const [error, setError] = useState(false);
  const progressRef = useRef(0);
  // The camera's damped progress, shared with the doors
  const camProgressRef = useRef(0);
  // Is any of the house visible? Under the landing render or a full-screen
  // paper sheet it is not, and the canvas stops drawing altogether.
  const visibleRef = useRef(false);
  const invalidateRef = useRef(null);
  const heroRef = useRef(null);
  const rootRef = useRef(null);
  const heroSrc = useMemo(() => heroImageFor(window), []);

  const mobile = useMemo(() => window.innerWidth < 900, []);
  const reducedMotion = useMemo(() => window.matchMedia('(prefers-reduced-motion: reduce)').matches, []);

  const inRoom = !EXTERIOR_SECTIONS.has(activeSection);
  const room = rooms.find((r) => r.id === activeSection) || rooms[0];

  /* Scroll position drives the camera directly. */
  useEffect(() => {
    let raf = 0;
    let tops = [];
    let height = -1;
    let lastCheck = 0;

    // Opaque paper sheets (App.css): Services on its own, and the run from
    // Portfolio to the footer
    let sheets = [];
    // Off the home page (the gallery) the sections are not in the document;
    // measuring then would read every top as 0 and park the journey at its
    // end, hiding the landing render for the way back
    let offHome = false;
    const measure = () => {
      offHome = !document.getElementById(JOURNEY_IDS[0]);
      if (offHome) return;
      tops = JOURNEY_IDS.map((id) => document.getElementById(id)?.offsetTop ?? 0);
      height = document.documentElement.scrollHeight;
      const s = document.getElementById('services');
      const tail = document.getElementById('portfolio');
      sheets = [
        s && [s.offsetTop, s.offsetTop + s.offsetHeight],
        tail && [tail.offsetTop, height]
      ].filter(Boolean);
    };

    const update = () => {
      raf = 0;
      if (offHome || !document.getElementById(JOURNEY_IDS[0])) {
        offHome = true;
        return;
      }
      const now = performance.now();
      if (tops.length !== N || tops[N - 1] === 0) measure();
      else if (now - lastCheck > 400) {
        lastCheck = now;
        if (document.documentElement.scrollHeight !== height) measure();
      }
      const y = window.scrollY || 0;
      let i = 0;
      while (i < N - 2 && y >= tops[i + 1]) i++;
      const span = Math.max(1, tops[i + 1] - tops[i]);
      progressRef.current = i + THREE.MathUtils.clamp((y - tops[i]) / span, 0, 1);

      const p = progressRef.current;
      const raw = p - i;

      // Draw the house only when some of it can be seen: not under the
      // opaque landing render, not behind a sheet that fills the screen.
      // Rounded sheet corners (28px) count as a gap.
      const vh = window.innerHeight;
      const covered = sheets.some(([top, bottom]) => y >= top + 28 && y + vh <= bottom - 28);
      const wasVisible = visibleRef.current;
      // Nothing of the house shows until the Services sheet lifts off the
      // doors: the landing render holds until the sheet covers the screen
      visibleRef.current = !covered && p >= 2;
      if (visibleRef.current || wasVisible) invalidateRef.current?.();

      // Hero render: a slow push-in while you read the landing and About.
      // It stays until the Services sheet covers the screen, then gives way
      // to the house, which Services lifts off at the living room doors.
      const hero = heroRef.current;
      if (hero) {
        hero.style.opacity = p < 2 ? '1' : '0';
        hero.style.transform = `scale(${1 + Math.min(p, 2) * 0.03})`;
        hero.style.visibility = p < 2 ? 'visible' : 'hidden';
      }

      // Overlay washes, blended across the middle of each hand-over
      const root = rootRef.current;
      if (root) {
        const e = smoothstep(0.28, 0.72, raw);
        const a = WEIGHTS[i];
        const b = WEIGHTS[Math.min(N - 1, i + 1)];
        for (const k of LAYERS) root.style.setProperty(`--w-${k}`, (a[k] * (1 - e) + b[k] * e).toFixed(3));
      }

    };

    const onScroll = () => { if (!raf) raf = requestAnimationFrame(update); };
    const onResize = () => { measure(); onScroll(); };

    measure();
    update();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onResize);
    // Coming back from the gallery the page is rebuilt at the top without a
    // scroll event: measure again once it has laid out
    let backTimers = [];
    const onRoute = () => {
      backTimers.forEach(clearTimeout);
      backTimers = [30, 250, 900].map((ms) => setTimeout(onResize, ms));
    };
    window.addEventListener('hashchange', onRoute);
    const settles = [300, 1200, 3000].map((ms) => setTimeout(onResize, ms));
    document.fonts?.ready?.then(onResize).catch(() => {});

    return () => {
      if (raf) cancelAnimationFrame(raf);
      settles.forEach(clearTimeout);
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onResize);
      window.removeEventListener('hashchange', onRoute);
      backTimers.forEach(clearTimeout);
    };
  }, []);

  return (
    <div
      ref={rootRef}
      className="journey-canvas"
      data-section={activeSection}
      data-room={inRoom}
      data-ready={ready && !error}
    >
      <img
        className="journey-poster"
        src={`/models/${inRoom ? room.id : 'exterior'}-preview.webp`}
        alt=""
      />
      <div className="hero-backdrop" ref={heroRef} aria-hidden="true">
        <img src={heroSrc} alt="" decoding="async" fetchpriority="high" />
      </div>
      <div className="scrim scrim-paper" aria-hidden="true" />
      <div className="scrim scrim-room" aria-hidden="true" />
      <div className="scrim scrim-landing" aria-hidden="true" />
      <div className="scrim scrim-about" aria-hidden="true" />
      {!error && (
        <SceneBoundary onError={() => setError(true)}>
          <Canvas
            // The walk is fill-rate bound: 1.25x keeps retina scrolling at 60fps
            // (2x held it near 30), and the scrims hide the difference
            dpr={[1, 1.25]}
            frameloop="demand"
            camera={{ position: STOPS.landing.position, fov: STOPS.landing.fov, near: 0.05, far: 600 }}
            gl={{ antialias: true, alpha: false, powerPreference: 'high-performance', stencil: false, logarithmicDepthBuffer: true }}
            onCreated={({ gl }) => {
              gl.toneMapping = THREE.ACESFilmicToneMapping;
              gl.toneMappingExposure = 1.0;
            }}
          >
            <Suspense fallback={null}>
              <World
                mobile={mobile}
                onReady={setReady}
                progressRef={progressRef}
                camProgressRef={camProgressRef}
                visibleRef={visibleRef}
                invalidateRef={invalidateRef}
                reducedMotion={reducedMotion}
              />
            </Suspense>
          </Canvas>
        </SceneBoundary>
      )}

    </div>
  );
}

useGLTF.preload(home.model, '/draco/');
useGLTF.preload(EXTERIOR, '/draco/');
useGLTF.preload(DOOR);
