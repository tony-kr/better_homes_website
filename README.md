# 🏛️ Architectural Excellence Portfolio

A heavily animated, cinematic architecture portfolio website built with React, Vite, and Framer Motion. Features smooth scroll animations, line-drawing effects, and immersive room transitions.

## ✨ Features

- **Animated Line Drawing**: Landing page with SVG path animation of a house sketch
- **Smooth Scrolling**: Buttery smooth scroll experience with Lenis
- **Parallax Effects**: Depth and movement throughout the site
- **Room Transitions**: Seamless transitions between different architectural spaces
- **Dark Luxury Theme**: Deep black background with gold accents
- **Fully Responsive**: Works beautifully on all devices
- **Performance Optimized**: Efficient animations using Framer Motion

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ installed
- npm or yarn package manager

### Installation

1. **Navigate to project directory**:
```bash
cd architecture-portfolio
```

2. **Install dependencies**:
```bash
npm install
```

3. **Start development server**:
```bash
npm run dev
```

4. **Open in browser**:
Visit `http://localhost:5173`

### Build for Production

```bash
npm run build
npm run preview  # Preview production build
```

## 📁 Project Structure

```
architecture-portfolio/
├── src/
│   ├── components/
│   │   └── sections/
│   │       ├── LandingSection.jsx        # Line drawing animation
│   │       ├── LandingSection.css
│   │       ├── HeroSection.jsx           # Company showcase
│   │       ├── HeroSection.css
│   │       ├── RoomSection.jsx           # Individual room displays
│   │       ├── RoomSection.css
│   │       ├── Footer.jsx
│   │       └── Footer.css
│   ├── App.jsx                           # Main app component
│   ├── App.css                           # Global styles
│   └── main.jsx                          # Entry point
├── package.json
└── README.md
```

## 🎨 Customization Guide

### 1. **Replace Placeholder Visuals with Real Images**

Current code uses CSS-based placeholder designs. To use real images:

**In RoomSection.jsx**, replace the `RoomVisual` component:

```jsx
// Replace this:
<RoomVisual type={image} />

// With this:
<img 
  src={`/images/rooms/${image}.jpg`} 
  alt={title}
  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
/>
```

**Image Requirements**:
- Living Room: 800x600px minimum
- Kitchen: 800x600px minimum
- Bedroom: 800x600px minimum
- Patio: 800x600px minimum
- Format: JPG, PNG, or WebP
- Place in `/public/images/rooms/` directory

### 2. **Customize Colors**

Edit the CSS variables in `App.css`:

```css
:root {
  --color-bg-primary: #0a0a0a;        /* Main background */
  --color-accent-gold: #d4af37;       /* Primary accent */
  --color-accent-bronze: #cd7f32;     /* Secondary accent */
  --color-text-primary: #f5f5f5;      /* Main text */
}
```

### 3. **Modify Typography**

Change fonts in `App.css`:

```css
@import url('YOUR_GOOGLE_FONTS_URL');

:root {
  --font-display: 'Your Display Font', serif;
  --font-body: 'Your Body Font', serif;
}
```

**Recommended Font Pairings**:
- **Luxury**: Bodoni Moda + Crimson Text
- **Modern**: Montserrat + Open Sans
- **Editorial**: Libre Baskerville + Source Sans Pro

### 4. **Add More Rooms**

In `App.jsx`, add to the `rooms` array:

```jsx
const rooms = [
  // ... existing rooms
  {
    id: 'bathroom',
    title: 'Bathroom',
    description: 'Spa-like sanctuaries...',
    image: 'bathroom',
    projects: 10
  }
];
```

Create a corresponding visual in `RoomSection.jsx`:

```jsx
const visuals = {
  // ... existing visuals
  'bathroom': (
    <div className="visual-bathroom">
      {/* Your bathroom design */}
    </div>
  )
};
```

### 5. **Adjust Animation Timing**

Modify delays and durations in component files:

```jsx
// Faster animations
transition={{ duration: 0.5, delay: 0.1 }}

// Slower animations
transition={{ duration: 2, delay: 1 }}
```

### 6. **Change Company Information**

**Edit LandingSection.jsx**:
```jsx
<h1 className="landing-title">Your Company Name</h1>
<p className="landing-subtitle">Your Tagline</p>
```

**Edit HeroSection.jsx**:
```jsx
<h2 className="tagline-main">
  Your Main
  <br />
  <span className="tagline-highlight">Message</span>
</h2>
```

**Edit Footer.jsx** for contact details and social links.

## 🎬 Animation Details

### Landing Section
- **SVG Path Animation**: 5-second sequence drawing a house
- **Fade-in Title**: Appears after sketch completes
- **Scroll Indicator**: Animated mouse with scroll prompt

### Hero Section
- **Parallax Background**: Moves slower than foreground
- **Scale Transform**: Image scales on scroll
- **Staggered Text**: Title, description, and stats appear in sequence

### Room Sections
- **Alternating Layouts**: Even/odd sections flip layout
- **Scroll-triggered**: Animations activate when section enters viewport
- **Parallax Images**: Room visuals move at different speeds
- **Intersection Observer**: Efficient animation triggering

## 🔧 Advanced Customization

### Adding GSAP ScrollTrigger

For more complex scroll animations:

```bash
npm install gsap
```

```jsx
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);
```

### Adding 3D House Model

For a realistic 3D house:

```bash
npm install three @react-three/fiber @react-three/drei
```

Replace the SVG sketch with a Three.js scene.

### Creating Project Galleries

Create a new `GallerySection.jsx` for project showcases:
- Lightbox image viewer
- Filterable grid
- Lazy loading
- Image zoom effects

## 📱 Responsive Breakpoints

- **Desktop**: 1024px+
- **Tablet**: 768px - 1023px
- **Mobile**: < 768px

## ⚡ Performance Tips

1. **Optimize Images**: Use WebP format, lazy load below fold
2. **Code Splitting**: Implement React.lazy() for galleries
3. **Reduce Motion**: Add `prefers-reduced-motion` media query
4. **Compress Assets**: Run build through image optimizer

## 🎯 Next Steps

1. **Add Project Galleries**: Create detailed project pages
2. **Contact Form**: Integrate with backend/email service
3. **CMS Integration**: Connect to Contentful, Sanity, or Strapi
4. **SEO Optimization**: Add meta tags, sitemap, schema markup
5. **Analytics**: Add Google Analytics or Plausible
6. **Blog Section**: Share architectural insights
7. **Client Testimonials**: Add social proof

## 🐛 Troubleshooting

### Animations Not Working
- Check that Framer Motion is installed: `npm list framer-motion`
- Verify React version is 18+
- Clear browser cache

### Scroll Not Smooth
- Ensure Lenis is properly initialized in `App.jsx`
- Check for conflicting CSS: `overflow: hidden` on body

### Images Not Loading
- Verify images are in `/public` directory
- Check file paths are correct
- Use browser dev tools to inspect network requests

## 📚 Resources

- [Framer Motion Docs](https://www.framer.com/motion/)
- [Lenis Smooth Scroll](https://github.com/studio-freight/lenis)
- [React + Vite Guide](https://vitejs.dev/guide/)
- [CSS Tricks - SVG Line Animation](https://css-tricks.com/svg-line-animation-works/)

## 🤝 Contributing

Feel free to fork this project and customize it for your needs!

## 📄 License

MIT License - feel free to use for personal or commercial projects.

---

**Built with passion for architectural excellence** ✨
