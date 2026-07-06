import { useEffect, useMemo, useRef } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Sparkles } from '@react-three/drei';
import * as THREE from 'three';
import './House3D.css';

/*
  The model home at blue hour.
  A procedural house that arrives as blueprint line-work, then fills in
  as a dusk-lit building with lamplit windows. The camera walks around
  it as the visitor moves through the site's sections.
*/

// Per-section camera + mood. drawing = edge-line opacity, glow = window warmth.
const VIEWS = {
  landing:   { pos: [8.0, 2.9, 10.0], target: [-2.15, 1.0, 0], drawing: 0.55, glow: 1.0 },
  hero:      { pos: [-8.2, 2.6, 9.2], target: [0.6, 1.2, 0], drawing: 0.95, glow: 0.55 },
  services:  { pos: [-4.5, 7.5, 12.5], target: [0, 0.4, 0], drawing: 0.8, glow: 0.4 },
  rooms:     { pos: [9.5, 4.6, 11.5], target: [0, 0.9, 0], drawing: 0.15, glow: 0.5 },
  portfolio: { pos: [11.5, 2.2, 6.5], target: [-1.5, 1.1, 0], drawing: 0.3, glow: 0.7 },
  stories:   { pos: [-9.8, 3.4, 10.5], target: [0.4, 1.0, 0], drawing: 0.35, glow: 0.85 },
  gallery:   { pos: [10.0, 3.5, 13.0], target: [0, 0.9, 0], drawing: 0.2, glow: 0.45 },
  estimate:  { pos: [-6.0, 2.0, 12.5], target: [0.8, 1.0, 0], drawing: 0.45, glow: 1.1 },
  footer:    { pos: [0.5, 1.5, 16.0], target: [0, 0.9, 0], drawing: 0.1, glow: 1.5 },
};

const smoothstep = (a, b, t) => {
  const x = THREE.MathUtils.clamp((t - a) / (b - a), 0, 1);
  return x * x * (3 - 2 * x);
};

// Emissive window pane
function Pane({ size, position, rotation = [0, 0, 0], lit = true, mat, darkMat }) {
  return (
    <mesh position={position} rotation={rotation} material={lit ? mat : darkMat}>
      <planeGeometry args={size} />
    </mesh>
  );
}

// A run of panes separated by mullions, so glazing reads as architecture
function WindowBand({ width, height, panes, position, rotation = [0, 0, 0], lit = true, mat, darkMat }) {
  const gap = 0.06;
  const paneW = (width - gap * (panes - 1)) / panes;
  const start = -width / 2 + paneW / 2;
  return (
    <group position={position} rotation={rotation}>
      {Array.from({ length: panes }, (_, i) => (
        <mesh key={i} position={[start + i * (paneW + gap), 0, 0]} material={lit ? mat : darkMat}>
          <planeGeometry args={[paneW, height]} />
        </mesh>
      ))}
    </group>
  );
}

// A box volume that "builds" (rises from its base) and carries blueprint edges
function Volume({ size, position, mat, edgeMat, buildWindow, buildRef }) {
  const groupRef = useRef();
  const [w, h, d] = size;
  const edgesGeom = useMemo(() => new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, d)), [w, h, d]);

  useFrame(() => {
    if (!groupRef.current) return;
    const t = smoothstep(buildWindow[0], buildWindow[1], buildRef.current);
    groupRef.current.scale.y = Math.max(t, 0.0001);
    groupRef.current.visible = t > 0.001;
  });

  return (
    <group ref={groupRef} position={[position[0], position[1] - h / 2, position[2]]}>
      <mesh position={[0, h / 2, 0]} material={mat}>
        <boxGeometry args={[w, h, d]} />
      </mesh>
      <lineSegments position={[0, h / 2, 0]} geometry={edgesGeom} material={edgeMat} />
    </group>
  );
}

function Scene({ activeSection, reducedMotion }) {
  const houseRef = useRef();
  const buildRef = useRef(0);
  const startRef = useRef(null);
  const pointer = useRef({ x: 0, y: 0 });
  const targetRef = useRef(new THREE.Vector3(-1.15, 1.05, 0));
  const { camera } = useThree();

  // Shared materials — animated once, applied everywhere
  const mats = useMemo(() => {
    const edge = new THREE.LineBasicMaterial({
      color: '#c3d0dd',
      transparent: true,
      opacity: 0,
    });
    const wall = new THREE.MeshStandardMaterial({
      color: '#1f2a37',
      roughness: 0.92,
      transparent: true,
      opacity: 0,
    });
    const wood = new THREE.MeshStandardMaterial({
      color: '#413325',
      roughness: 0.85,
      transparent: true,
      opacity: 0,
    });
    const slab = new THREE.MeshStandardMaterial({
      color: '#0d141c',
      roughness: 0.95,
      transparent: true,
      opacity: 0,
    });
    const glow = new THREE.MeshStandardMaterial({
      color: '#120d06',
      emissive: '#ffb35f',
      emissiveIntensity: 0,
      transparent: true,
      opacity: 0,
    });
    const darkGlass = new THREE.MeshStandardMaterial({
      color: '#0e1622',
      roughness: 0.25,
      metalness: 0.4,
      transparent: true,
      opacity: 0,
    });
    const ground = new THREE.MeshStandardMaterial({ color: '#0b1119', roughness: 1 });
    return { edge, wall, wood, slab, glow, darkGlass, ground };
  }, []);

  const lampA = useRef();
  const lampB = useRef();

  useEffect(() => {
    const onMove = (e) => {
      pointer.current.x = (e.clientX / window.innerWidth) * 2 - 1;
      pointer.current.y = (e.clientY / window.innerHeight) * 2 - 1;
    };
    window.addEventListener('pointermove', onMove);
    return () => window.removeEventListener('pointermove', onMove);
  }, []);

  useFrame((state, delta) => {
    const view = VIEWS[activeSection] || VIEWS.landing;
    const t = state.clock.elapsedTime;

    // Build-in: 0 → 1 over ~2.4s after mount
    if (startRef.current === null) startRef.current = t;
    const elapsed = t - startRef.current;
    buildRef.current = reducedMotion ? 1 : Math.min(elapsed / 2.4, 1);
    const build = buildRef.current;

    // Blueprint lines lead, fills follow
    const d = 1 - Math.pow(0.0025, delta); // frame-rate independent damp factor
    const edgeTarget = Math.max(view.drawing, (1 - build) * 0.9) * smoothstep(0, 0.12, build);
    mats.edge.opacity += (edgeTarget - mats.edge.opacity) * d;

    const fill = smoothstep(0.35, 0.95, build);
    mats.wall.opacity = fill;
    mats.wood.opacity = fill;
    mats.slab.opacity = fill;

    // Windows come on last, with a gentle lamplight flicker
    const windows = smoothstep(0.78, 1, build);
    const flicker = 1 + Math.sin(t * 1.7) * 0.035 + Math.sin(t * 4.3) * 0.02;
    mats.glow.opacity = windows;
    mats.darkGlass.opacity = windows;
    mats.glow.emissiveIntensity += (view.glow * 1.15 * windows * flicker - mats.glow.emissiveIntensity) * d;
    const lampIntensity = view.glow * 2.4 * windows;
    if (lampA.current) lampA.current.intensity += (lampIntensity - lampA.current.intensity) * d;
    if (lampB.current) lampB.current.intensity += (lampIntensity * 0.7 - lampB.current.intensity) * d;

    // Camera drift toward the section's viewpoint, with light mouse parallax.
    // Narrow viewports get a wider shot so the house doesn't swallow the type.
    const aspect = state.size.width / state.size.height;
    const wide = aspect < 0.8 ? 1.6 : aspect < 1.2 ? 1.3 : 1;
    const px = reducedMotion ? 0 : pointer.current.x;
    const py = reducedMotion ? 0 : pointer.current.y;
    const lambda = 1.6;
    camera.position.x = THREE.MathUtils.damp(camera.position.x, view.pos[0] * wide + px * 0.45, lambda, delta);
    camera.position.y = THREE.MathUtils.damp(camera.position.y, view.pos[1] * wide - py * 0.3, lambda, delta);
    camera.position.z = THREE.MathUtils.damp(camera.position.z, view.pos[2] * wide, lambda, delta);
    targetRef.current.x = THREE.MathUtils.damp(targetRef.current.x, view.target[0], lambda, delta);
    targetRef.current.y = THREE.MathUtils.damp(targetRef.current.y, view.target[1], lambda, delta);
    targetRef.current.z = THREE.MathUtils.damp(targetRef.current.z, view.target[2], lambda, delta);
    camera.lookAt(targetRef.current);

    // Very slow yaw drift — the model turntable
    if (houseRef.current && !reducedMotion) {
      houseRef.current.rotation.y = Math.sin(t * 0.07) * 0.05;
    }
  });

  const groundGeom = useMemo(() => new THREE.CircleGeometry(34, 48), []);

  return (
    <>
      <fog attach="fog" args={['#0b1118', 9, 36]} />
      <ambientLight color="#3d4d66" intensity={0.55} />
      <directionalLight color="#8fa8c8" intensity={0.7} position={[-6, 9, -4]} />
      {/* Faint warm fill from the street side so facades read against the sky */}
      <directionalLight color="#c9a06a" intensity={0.22} position={[5, 3, 10]} />

      {/* First evening stars */}
      <Sparkles count={60} scale={[30, 12, 20]} position={[0, 8, -6]} size={1.6} speed={reducedMotion ? 0 : 0.25} opacity={0.5} color="#dbe6f2" />

      {/* Ground plane */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, 0]} geometry={groundGeom} material={mats.ground} />

      <group ref={houseRef}>
        {/* Terrace slab */}
        <Volume size={[7, 0.12, 4.6]} position={[0, 0.06, 0]} mat={mats.slab} edgeMat={mats.edge} buildWindow={[0.02, 0.22]} buildRef={buildRef} />
        {/* Ground floor volume */}
        <Volume size={[4.4, 1.35, 3]} position={[-0.4, 0.795, 0]} mat={mats.wall} edgeMat={mats.edge} buildWindow={[0.14, 0.45]} buildRef={buildRef} />
        {/* Canopy over the entry side */}
        <Volume size={[2.7, 0.08, 3.25]} position={[-1.45, 1.52, 0]} mat={mats.slab} edgeMat={mats.edge} buildWindow={[0.38, 0.6]} buildRef={buildRef} />
        {/* Cantilevered upper volume, wood-clad */}
        <Volume size={[3.2, 1.15, 2.5]} position={[0.9, 2.045, -0.15]} mat={mats.wood} edgeMat={mats.edge} buildWindow={[0.5, 0.78]} buildRef={buildRef} />
        {/* Roof slab */}
        <Volume size={[3.5, 0.1, 2.7]} position={[0.9, 2.67, -0.15]} mat={mats.slab} edgeMat={mats.edge} buildWindow={[0.72, 0.92]} buildRef={buildRef} />
        {/* Chimney / service core */}
        <Volume size={[0.5, 3.1, 0.5]} position={[-1.7, 1.67, -0.85]} mat={mats.wall} edgeMat={mats.edge} buildWindow={[0.6, 0.88]} buildRef={buildRef} />

        {/* Windows — the lamplight */}
        <WindowBand width={2.3} height={0.95} panes={4} position={[-0.85, 0.82, 1.511]} mat={mats.glow} darkMat={mats.darkGlass} />
        <Pane size={[0.5, 1.12]} position={[1.35, 0.71, 1.511]} mat={mats.glow} darkMat={mats.darkGlass} />
        <WindowBand width={2.5} height={0.58} panes={3} position={[0.9, 2.06, 1.111]} mat={mats.glow} darkMat={mats.darkGlass} />
        <Pane size={[1.1, 0.5]} position={[2.511, 2.05, -0.15]} rotation={[0, Math.PI / 2, 0]} lit={false} mat={mats.glow} darkMat={mats.darkGlass} />
        <Pane size={[0.9, 0.6]} position={[-2.611, 0.85, 0.3]} rotation={[0, -Math.PI / 2, 0]} lit={false} mat={mats.glow} darkMat={mats.darkGlass} />

        {/* Interior lamplight spilling onto the terrace */}
        <pointLight ref={lampA} color="#ffaf5e" position={[-0.85, 0.9, 1.9]} distance={6} decay={2} intensity={0} />
        <pointLight ref={lampB} color="#ffaf5e" position={[0.9, 2.1, 1.5]} distance={5} decay={2} intensity={0} />

        {/* Path leading toward the viewer */}
        <mesh rotation={[-Math.PI / 2, 0, 0.18]} position={[-0.85, 0.005, 3.6]} material={mats.slab}>
          <planeGeometry args={[0.9, 4.4]} />
        </mesh>
      </group>
    </>
  );
}

const House3D = ({ activeSection }) => {
  const reducedMotion = useMemo(
    () => window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    []
  );

  return (
    <div className="house3d-container" data-section={activeSection} aria-hidden="true">
      <div className="house3d-sky" />
      <div className="house3d-horizon" />
      <Canvas
        dpr={[1, 1.75]}
        gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
        camera={{ fov: 33, near: 0.1, far: 60, position: [7.4, 2.7, 8.6] }}
      >
        <Scene activeSection={activeSection} reducedMotion={reducedMotion} />
      </Canvas>
    </div>
  );
};

export default House3D;
