import { Children, cloneElement, isValidElement, useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion, useInView, useReducedMotion } from 'framer-motion';

/*
  The site's motion vocabulary, kept in one place so every section moves the
  same way.

  - <MaskReveal>: headings rise word by word out of a mask. Nested markup
    (a red <em> or .accent phrase) is split too and keeps its styling.
  - <ImageReveal>: a picture wipes up out of a clip and settles from a
    slight zoom.
  - <RotatingWord>: the landing's changing phrase.

  All of it respects prefers-reduced-motion: things simply appear.
*/
export const EASE = [0.16, 1, 0.3, 1];

/*
  A closing mark set as its own element (<span className="dot">.</span>)
  is folded into the mask of the word before it, so the two rise together
  and a line can never break between them.
*/
const isDot = (n) => isValidElement(n) && /\bdot\b/.test(n.props.className || '');

const flat = (nodes) => [nodes].flat(Infinity).filter((n) => n !== null && n !== undefined && n !== false);

function withSuffix(node, suffix) {
  if (typeof node === 'string') return { text: node, suffix };
  if (isValidElement(node)) {
    const kids = flat(node.props.children);
    kids[kids.length - 1] = withSuffix(kids[kids.length - 1], suffix);
    return cloneElement(node, { ...node.props, children: kids });
  }
  return node;
}

// Flattens children, gives elements stable keys, and folds each dot into the
// node before it. Marker objects ({ text, suffix }) never reach React: they
// are consumed by splitWords.
function foldDots(nodes) {
  const out = [];
  flat(nodes).forEach((n, i) => {
    if (isDot(n) && out.length) out[out.length - 1] = withSuffix(out[out.length - 1], n);
    else out.push(isValidElement(n) && n.key == null ? cloneElement(n, { key: `n${i}` }) : n);
  });
  return out;
}

/* Split every text node under `node` into masked words, keeping elements. */
function splitWords(node, state) {
  const suffixed = node && typeof node === 'object' && 'text' in node && 'suffix' in node;
  if (typeof node === 'string' || suffixed) {
    const text = suffixed ? node.text : node;
    const parts = text.split(/(\s+)/);
    let last = parts.length - 1;
    while (last > 0 && !parts[last].trim()) last--;
    return parts.map((part, i) => {
      if (!part) return null;
      if (/^\s+$/.test(part)) return part;
      const index = state.n++;
      return (
        <span className="mr-word" key={`${index}-${i}`}>
          <span className="mr-inner" style={{ '--i': index }}>
            {part}
            {suffixed && i === last ? node.suffix : null}
          </span>
        </span>
      );
    });
  }
  if (Array.isArray(node)) return foldDots(node).map((child) => splitWords(child, state));
  if (isValidElement(node)) {
    if (node.type === 'br' || isDot(node)) return node;
    return cloneElement(node, { ...node.props }, foldDots(node.props.children).map((c) => splitWords(c, state)));
  }
  return node;
}

export function MaskReveal({ as: Tag = 'h2', children, className = '', delay = 0, stagger = 0.055, amount = 0.5, show, ...rest }) {
  const ref = useRef(null);
  const seen = useInView(ref, { once: true, amount });
  const on = show === undefined ? seen : show;
  const state = { n: 0 };
  const words = splitWords(foldDots(children), state);
  // Once the last word has landed the masks open, so nothing (a text
  // shadow, an italic overhang) is ever seen clipped to a word's box
  const [done, setDone] = useState(false);
  useEffect(() => {
    if (!on) return undefined;
    const id = setTimeout(() => setDone(true), (delay + state.n * stagger + 1.15) * 1000);
    return () => clearTimeout(id);
  }, [on, delay, stagger, state.n]);
  return (
    <Tag
      ref={ref}
      className={`mask-reveal ${on ? 'is-in' : ''} ${done ? 'is-done' : ''} ${className}`}
      style={{ '--mr-delay': `${delay}s`, '--mr-stagger': `${stagger}s` }}
      {...rest}
    >
      {words}
    </Tag>
  );
}

/* Fade and lift, for paragraphs and small blocks */
export const rise = (delay = 0, distance = 22) => ({
  initial: { opacity: 0, y: distance },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.4 },
  transition: { duration: 1, delay, ease: EASE }
});

export function ImageReveal({ src, alt = '', className = '', delay = 0, ...rest }) {
  return (
    <motion.div
      className={`image-reveal ${className}`}
      initial={{ clipPath: 'inset(100% 0% 0% 0%)' }}
      whileInView={{ clipPath: 'inset(0% 0% 0% 0%)' }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 1.3, delay, ease: EASE }}
    >
      <motion.img
        src={src}
        alt={alt}
        initial={{ scale: 1.18 }}
        whileInView={{ scale: 1 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 1.8, delay, ease: EASE }}
        draggable={false}
        {...rest}
      />
    </motion.div>
  );
}

/*
  Cycles through `words`, one every `interval` ms. The current word lifts
  away, then the next rises letter by letter into its place. `suffix` (the
  red full stop) travels with the word so it always sits right after it.
*/
export function RotatingWord({ words, interval = 2600, className = '', paused = false, suffix = null }) {
  const reduce = useReducedMotion();
  const [i, setI] = useState(0);
  useEffect(() => {
    if (paused || reduce) return undefined;
    const id = setInterval(() => setI((n) => (n + 1) % words.length), interval);
    return () => clearInterval(id);
  }, [words.length, interval, paused, reduce]);
  const word = words[i];
  return (
    <span className={`rotating-word ${className}`}>
      <span className="sr-only" aria-live="polite">{word}</span>
      <AnimatePresence mode="wait" initial={false}>
        <motion.span className="rw-word" key={word} aria-hidden="true">
          {[...word].map((ch, k) => (
            <motion.span
              key={k}
              className="rw-char"
              initial={{ y: '100%', opacity: 0 }}
              animate={{ y: '0%', opacity: 1 }}
              exit={{ y: '-100%', opacity: 0, transition: { duration: 0.38, delay: k * 0.01, ease: [0.5, 0, 0.75, 0] } }}
              transition={{ duration: 0.75, delay: k * 0.024, ease: EASE }}
            >
              {ch === ' ' ? '\u00a0' : ch}
            </motion.span>
          ))}
          {suffix && (
            <motion.span
              className="rw-char"
              initial={{ y: '100%', opacity: 0 }}
              animate={{ y: '0%', opacity: 1 }}
              exit={{ y: '-100%', opacity: 0, transition: { duration: 0.38, ease: [0.5, 0, 0.75, 0] } }}
              transition={{ duration: 0.75, delay: word.length * 0.024, ease: EASE }}
            >
              {suffix}
            </motion.span>
          )}
        </motion.span>
      </AnimatePresence>
    </span>
  );
}
