import { useRef, useEffect, useCallback, useMemo } from 'react';
import { gsap } from 'gsap';
import './DotGrid.css';

const throttle = (func, limit) => {
  let lastCall = 0;
  return function (...args) {
    const now = performance.now();
    if (now - lastCall >= limit) {
      lastCall = now;
      func.apply(this, args);
    }
  };
};

function hexToRgb(hex) {
  const m = hex.match(/^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i);
  if (!m) return { r: 51, g: 51, b: 51 };
  return {
    r: parseInt(m[1], 16),
    g: parseInt(m[2], 16),
    b: parseInt(m[3], 16)
  };
}

const DotGrid = ({
  dotSize = 4,
  gap = 35,
  baseColor = '#f4f3f3',
  activeColor = '#ff0000',
  proximity = 120,
  className = '',
}) => {
  const wrapperRef = useRef(null);
  const canvasRef = useRef(null);
  const dotsRef = useRef([]);
  const mouseRef = useRef({ x: -1000, y: -1000 });

  const baseRgb = useMemo(() => hexToRgb(baseColor), [baseColor]);
  const activeRgb = useMemo(() => hexToRgb(activeColor), [activeColor]);

  const buildGrid = useCallback(() => {
    const wrap = wrapperRef.current;
    const canvas = canvasRef.current;
    if (!wrap || !canvas) return;

    const { width, height } = wrap.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);

    const cols = Math.floor(width / gap);
    const rows = Math.floor(height / gap);
    
    const dots = [];
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        dots.push({
          x: x * gap + gap / 2,
          y: y * gap + gap / 2,
          currentX: x * gap + gap / 2,
          currentY: y * gap + gap / 2,
        });
      }
    }
    dotsRef.current = dots;
  }, [gap]);

  useEffect(() => {
    buildGrid();
    window.addEventListener('resize', buildGrid);
    return () => window.removeEventListener('resize', buildGrid);
  }, [buildGrid]);

  useEffect(() => {
    let rafId;
    const render = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      dotsRef.current.forEach(dot => {
        const dx = mouseRef.current.x - dot.x;
        const dy = mouseRef.current.y - dot.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        let color = baseColor;
        let finalX = dot.x;
        let finalY = dot.y;

        if (dist < proximity) {
          const angle = Math.atan2(dy, dx);
          const force = (proximity - dist) / proximity;
          finalX = dot.x - Math.cos(angle) * (force * 15);
          finalY = dot.y - Math.sin(angle) * (force * 15);

          const t = 1 - (dist / proximity);
          const r = Math.round(baseRgb.r + (activeRgb.r - baseRgb.r) * t);
          const g = Math.round(baseRgb.g + (activeRgb.g - baseRgb.g) * t);
          const b = Math.round(baseRgb.b + (activeRgb.b - baseRgb.b) * t);
          color = `rgb(${r},${g},${b})`;
        }

        dot.currentX += (finalX - dot.currentX) * 0.1;
        dot.currentY += (finalY - dot.currentY) * 0.1;

        ctx.beginPath();
        ctx.arc(dot.currentX, dot.currentY, dotSize / 2, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
      });
      rafId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(rafId);
  }, [baseColor, activeRgb, baseRgb, proximity, dotSize]);

  useEffect(() => {
    const handleMove = throttle((e) => {
      const rect = canvasRef.current?.getBoundingClientRect();
      if (!rect) return;
      mouseRef.current = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      };
    }, 10);

    window.addEventListener('mousemove', handleMove);
    return () => window.removeEventListener('mousemove', handleMove);
  }, []);

  return (
    <div ref={wrapperRef} className={`dot-grid-bg ${className}`} style={{ width: '100%', height: '100%' }}>
      <canvas ref={canvasRef} />
    </div>
  );
};

export default DotGrid;