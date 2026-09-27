import home from './premiumHome.json';
import { rooms, walkRooms } from './rooms';

/*
  The scroll journey.

  Two ideas here that the previous build did not have.

  First, the camera is bound to scroll position, not to a clock. Every section
  owns a stop; scrolling between two sections moves the camera along the route
  between their stops in exact proportion to how far you have scrolled. The
  house answers the wheel immediately instead of walking at its own pace.

  Second, the sections that are not rooms get proper exterior framing rather
  than resolving to one far aerial. APPROACH and DEPARTURE are hand-placed
  polylines that pass outside the building, and they terminate on the shared
  entry node so the wall-aware graph can route straight through them.
*/

// The entry waypoint every room path in premiumHome.json begins from.
// The first APPROACH point must match it exactly or the graph will not join.
const ENTRY = home.paths.living[0];

/*
  Arrival. A descent from high outside the compound, over the courtyard wall,
  down into the side yard and in through the door. The wall tops out at 2.8 m,
  so the path stays above 3.2 m until it is past z = 8.
*/
const APPROACH = [
  [34.0, 6.5, 34.0],
  [28.0, 5.6, 27.5],
  [22.0, 4.9, 21.0],
  [15.0, 4.3, 15.0],
  [7.0, 3.9, 11.5],
  [-2.0, 3.7, 10.0],
  [-5.5, 3.4, 5.5],
  [-6.2, 2.3, 1.0],
  [-5.6, 1.72, -3.5],
  [-3.0, 1.6, -6.6],
  [-1.2, 1.6, -7.02],
  ENTRY
];

/* Departure: out of the patio, back over the wall, and up to a closing wide. */
const DEPARTURE = [
  home.paths.patio.at(-1),
  [0.5, 2.6, 6.0],
  [-1.0, 4.0, 10.5],
  [3.0, 4.6, 16.0],
  [10.0, 5.2, 22.0],
  [20.0, 5.9, 28.0],
  [31.0, 6.6, 35.0]
];

/*
  Dining is framed from the living-room end of the table, looking at the
  sideboard wall, rather than from the audited endpoint beside the kitchen
  door. Two short links join that spot to the graph across open floor: one
  straight from the living stop (the rooms share one space), one to the
  dining doorway node. Both were checked against the furniture in Blender.
*/
const DINING_AT = [7.6, 1.6, -4.8];
const DINING_LINKS = {
  livingToDining: [home.views.living.position, DINING_AT],
  diningToDoor: [DINING_AT, [9.75, 1.6, -6.0]]
};

/*
  The way in (client round 5). After Services the walk no longer flies in
  from outside: it stands in the gallery facing the living room's pocket
  doors (blender/premium-home/build_door.py), the doors slide apart, and it
  walks straight through, joining the audited living path just inside the
  doorway at (3.6, -5.55). Three.js space: the partition is z = -6, the
  gallery is z < -6.
*/
// Wide enough to hold the whole door, its casing and threshold
export const DOOR_VIEW = { position: [3.7, 1.6, -7.72], target: [3.7, 1.52, -3.0], fov: 70 };
const ENTRY_LINK = { entryToLiving: [DOOR_VIEW.position, [3.7, 1.6, -6.6], [3.6, 1.6, -5.55]] };

/* Everything the tour graph should know about, rooms plus the outdoor runs. */
export const TOUR_PATHS = { ...home.paths, ...DINING_LINKS, ...ENTRY_LINK, approach: APPROACH, departure: DEPARTURE };

const HOUSE = [9.0, 2.2, -4.0];

const exteriorStop = (position, target = HOUSE, fov = 40) => ({ position, target, fov });

/*
  Room views come from the Blender manifest framed dead centre. The page puts
  its copy down the left, so each interior is yawed a little to the left,
  which slides the subject of the room clear of the text.
*/
const ROOM_YAW = (-11 * Math.PI) / 180;

const roomStop = (id) => {
  const view = home.views[id];
  const [px, py, pz] = view.position;
  const [tx, ty, tz] = view.target;
  const dx = tx - px;
  const dz = tz - pz;
  const cos = Math.cos(ROOM_YAW);
  const sin = Math.sin(ROOM_YAW);
  return {
    position: view.position,
    target: [px + dx * cos - dz * sin, ty, pz + dx * sin + dz * cos],
    fov: view.fov
  };
};

/*
  The five walk rooms, framed by hand in the browser against the baked scene
  (after the September 2026 wall dressing): the room's best wall right of
  centre, the copy's side of the frame left for the dark falloff.
*/
const WALK_VIEWS = {
  living: { position: home.views.living.position, target: [0.4, 1.3, -3.2], fov: 48 },
  dining: { position: DINING_AT, target: [11.9, 1.25, -1.7], fov: 50 },
  kitchen: { position: home.views.kitchen.position, target: [16.0, 1.2, -1.8], fov: 52 },
  bedroom: { position: home.views.bedroom.position, target: [15.2, 1.0, -12.8], fov: 52 },
  patio: { position: home.views.patio.position, target: [9.0, 1.1, 1.2], fov: 48 }
};

/*
  One stop per page section. Room stops come straight from the Blender view
  manifest; exterior stops sit on the approach and departure polylines so the
  route between any two of them stays outside the walls.
*/
export const STOPS = {
  landing: exteriorStop(APPROACH[0], [10.0, 4.7, -6.0], 38),
  hero: exteriorStop(APPROACH[2], [10.0, 3.9, -6.0], 42),
  // Services is a full-screen sheet; behind it the camera is already at the
  // doors, so the sheet lifts straight off them
  services: DOOR_VIEW,
  entry: DOOR_VIEW,
  portfolio: exteriorStop(DEPARTURE[3], [9.0, 3.2, -6.0], 44),
  stories: exteriorStop(DEPARTURE[4], [10.0, 3.6, -6.0], 42),
  estimate: exteriorStop(DEPARTURE[5], [10.0, 4.2, -6.0], 40),
  footer: exteriorStop(DEPARTURE[6], [10.0, 4.7, -6.0], 38),
  ...Object.fromEntries(rooms.map((r) => [r.id, WALK_VIEWS[r.id] || roomStop(r.id)]))
};

export const JOURNEY_IDS = [
  'landing',
  'hero',
  'services',
  'entry',
  ...walkRooms.map((r) => r.id),
  'portfolio',
  'stories',
  'estimate',
  'footer'
];

/* Sections whose stop is outside the house; the page dims the scene less for these. */
export const EXTERIOR_SECTIONS = new Set([
  'landing',
  'hero',
  'services',
  'entry',
  'portfolio',
  'stories',
  'estimate',
  'footer'
]);

/* "04 / 12" style counters for section eyebrows, derived so they never drift */
export const sheetNumber = (id) => ({
  n: String(JOURNEY_IDS.indexOf(id) + 1).padStart(2, '0'),
  total: String(JOURNEY_IDS.length).padStart(2, '0')
});
