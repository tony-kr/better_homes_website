/*
  The client's actual site photography — every file in /assets, imported
  through Vite so the build fingerprints and optimises them.
  Categorised by what the photo actually shows.
*/
const files = import.meta.glob('../../assets/project-*.jpeg', {
  eager: true,
  import: 'default'
});

const CATEGORIES = {
  living: [3, 6, 14, 15, 31, 40, 44, 46, 57, 65],
  bedroom: [1, 8, 11, 37, 43, 45],
  wardrobe: [7, 9, 17, 19, 21, 23, 25, 27, 28, 32, 33, 36],
  kitchen: [10, 16, 18, 22, 34, 38, 41, 58],
  pooja: [2, 4, 13, 35],
  study: [30, 53]
};

const LABELS = {
  living: 'Living & TV units',
  bedroom: 'Bedroom',
  wardrobe: 'Wardrobes',
  kitchen: 'Kitchen',
  pooja: 'Pooja & partitions',
  study: 'Study & workspace'
};

const roomOf = (n) =>
  Object.keys(CATEGORIES).find((room) => CATEGORIES[room].includes(n)) || 'living';

export const projectPhotos = Object.keys(files)
  .map((path) => {
    const n = parseInt(path.match(/project-(\d+)\.jpeg$/)[1], 10);
    const room = roomOf(n);
    return { n, src: files[path], room, label: LABELS[room] };
  })
  .sort((a, b) => a.n - b.n);

/*
  The gallery is organised into three tabs. Room categories are kept, but only
  as a deep link: a room stop on the home page can open the gallery already
  narrowed to its own photos. There is no longer a row of room buttons.
*/
export const galleryTabs = [
  {
    id: 'works',
    label: 'Our Works',
    blurb:
      'No renders, no stock photography — every frame below was shot on site in a home we delivered.'
  },
  {
    id: 'plans',
    label: '2D & 3D',
    blurb:
      'The drawings behind the build: floor plans, elevations, and the 3D views clients approve before a single panel is cut.'
  },
  {
    id: 'transform',
    label: 'Before & After',
    blurb:
      'The same room, the day we measured it and the day we handed it back. Drag the divider to see the change.'
  }
];

/* Room deep links, e.g. '#/gallery?room=kitchen' */
export const roomFilters = Object.keys(LABELS).map((id) => ({ id, label: LABELS[id] }));

export const roomLabel = (id) => LABELS[id];

/*
  Drawings and 3D views. Drop files into /public/plans and list them here —
  the tab renders itself from this array.
*/
export const planShots = [];

/*
  Before / after pairs. Each entry needs both frames shot from the same spot:
  { id, room, label, before: '/before-after/x-before.jpg', after: '…-after.jpg' }
*/
export const beforeAfterPairs = [];

// Hand-picked hero shots for the featured-projects list
export const featuredPhoto = (n) => projectPhotos.find((p) => p.n === n)?.src;
