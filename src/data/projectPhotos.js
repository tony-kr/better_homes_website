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

export const galleryFilters = [
  { id: 'all', label: 'All work' },
  ...Object.keys(LABELS).map((id) => ({ id, label: LABELS[id] }))
];

// Hand-picked hero shots for the featured-projects list
export const featuredPhoto = (n) => projectPhotos.find((p) => p.n === n)?.src;
