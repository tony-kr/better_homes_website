/*
  Every space in the Blender-built residence. All eleven stay in the model;
  only `walkRooms` below, the five the client asked for, are scroll stops on
  the home page.

  Each id must match a camera view in premiumHome.json, or the camera and
  the copy will drift apart.

  A `chapter` marks a room where the walk enters a new part of the home. The
  stop then renders a chapter card above its own title, which gives the walk
  a shape instead of a row of identical slides.

  `galleryFilter` points at a category in projectPhotos.js. `concepts` are the
  inspiration boards in /public; rooms without either simply omit those links.
*/
export const rooms = [
  {
    id: "living",
    chapter: { label: "Part one", title: "Where everyone gathers" },
    label: "Living room",
    kicker: "The gathering room",
    description: "The room the evening belongs to. Low light, deep seating, and sightlines that pull everyone toward the same corner.",
    note: "Walnut slats washed in warm light, a book-matched marble wall, an olive by the glass.",
    galleryFilter: "living",
    still: "/living_room_broll.jpeg",
    accent: "#c4b1cf",
    ink: "#2e2139",
    concepts: [
      "/living_room/living-01.webp",
      "/living_room/living-02.jpg",
      "/living_room/living-03.webp",
      "/living_room/living-04.avif",
      "/living_room/living-05.jpg",
      "/living_room/living-06.jpg"
    ]
  },
  {
    id: "dining",
    label: "Dining",
    kicker: "The long table",
    description: "One long table, light centred above it, and room enough for the conversation to run late.",
    note: "A travertine table on a single plinth, stone dome pendants, jute underfoot.",
    galleryFilter: "living",
    still: "/dining_broll.jpg",
    accent: "#d4937a",
    ink: "#3d1a0e",
    concepts: [
      "/dining_space/dining-01.avif",
      "/dining_space/dining-02.jpg",
      "/dining_space/dining-03.jpeg",
      "/dining_space/dining-04.jpg",
      "/dining_space/dining-05.jpg",
      "/dining_space/dining-06.jpg"
    ]
  },
  {
    id: "kitchen",
    label: "Kitchen",
    kicker: "The working heart",
    description: "Where the home actually lives. Working surfaces, honest materials, and a lamp left on over the island.",
    note: "Walnut joinery floor to ceiling, a marble waterfall island, a lit open shelf.",
    galleryFilter: "kitchen",
    still: "/kitchen_broll.jpg",
    accent: "#e8e6e3",
    ink: "#2b2825",
    concepts: [
      "/kitchen/kitchen-01.jpg",
      "/kitchen/kitchen-02.jpg",
      "/kitchen/kitchen-03.webp",
      "/kitchen/kitchen-04.jpg",
      "/kitchen/kitchen-05.jpeg",
      "/kitchen/kitchen-06.jpg"
    ]
  },
  {
    id: "bedroom",
    chapter: { label: "Part two", title: "Where the day ends" },
    label: "Bedroom",
    kicker: "The quiet end",
    description: "The quietest room in the home. We shape bedrooms around morning light and evening stillness, in that order.",
    note: "A sand channel headboard, a limewash wall between walnut slats, mushroom lamps.",
    galleryFilter: "bedroom",
    still: "/bedroon_brol.jpg",
    accent: "#c2cdb8",
    ink: "#28331e",
    concepts: [
      "/bedroom/bedroom-01.jpg",
      "/bedroom/bedroom-02.jpg",
      "/bedroom/bedroom-03.avif",
      "/bedroom/bedroom-04.jpeg",
      "/bedroom/bedroom-05.jpeg",
      "/bedroom/bedroom-06.webp",
      "/bedroom/bedroom-07.webp"
    ]
  },
  {
    id: "guest",
    label: "Guest bedroom",
    kicker: "A warm welcome",
    description: "A restful retreat for guests, with soft textiles and carefully framed daylight.",
    note: "Layered linen, warm timber, and a quiet reading corner.",
    galleryFilter: "all",
    still: "/models/guest-preview.webp",
    accent: "#d8cec0",
    ink: "#302b25",
    concepts: []
  },
  {
    id: "study",
    label: "Study",
    kicker: "Room to think",
    description: "A dedicated space for focused work, surrounded by natural materials.",
    note: "A generous desk, open shelving, and an upholstered task chair.",
    galleryFilter: "all",
    still: "/models/study-preview.webp",
    accent: "#d8cec0",
    ink: "#302b25",
    concepts: []
  },
  {
    id: "bathroom",
    chapter: { label: "Part three", title: "Where the day begins" },
    label: "Bathroom",
    kicker: "Everyday ritual",
    description: "A calm bathroom with room to move and a walk-in shower.",
    note: "Stone surfaces, brushed metal, and warm lighting.",
    galleryFilter: "all",
    still: "/models/bathroom-preview.webp",
    accent: "#d8cec0",
    ink: "#302b25",
    concepts: []
  },
  {
    id: "ensuite",
    label: "En suite",
    kicker: "A private sanctuary",
    description: "A private bathing space connected to the primary suite.",
    note: "A sculptural bath, floating vanity, and glass shower.",
    galleryFilter: "all",
    still: "/models/ensuite-preview.webp",
    accent: "#d8cec0",
    ink: "#302b25",
    concepts: []
  },
  {
    id: "dressing",
    label: "Dressing room",
    kicker: "Everything in its place",
    description: "Tailored storage brings a sense of order to the morning routine.",
    note: "Walnut wardrobes, open rails, and integrated lighting.",
    galleryFilter: "all",
    still: "/models/dressing-preview.webp",
    accent: "#d8cec0",
    ink: "#302b25",
    concepts: []
  },
  {
    id: "utility",
    chapter: { label: "Part four", title: "The rooms that do the work" },
    label: "Utility",
    kicker: "Thoughtfully practical",
    description: "The working spaces receive the same care as the rest of the home.",
    note: "Full-height storage, laundry appliances, and durable worktops.",
    galleryFilter: "all",
    still: "/models/utility-preview.webp",
    accent: "#d8cec0",
    ink: "#302b25",
    concepts: []
  },
  {
    id: "patio",
    chapter: { label: "Part three", title: "Where the evening goes on" },
    label: "Patio",
    kicker: "The room without a roof",
    description: "We treat outdoor space as floor plan, not leftover garden. Deep seating, greenery, and somewhere to stay past midnight.",
    note: "A travertine table, olive trees in stone planters, walnut slats on the facade.",
    galleryFilter: "all",
    still: "/patio_broll.jpg",
    accent: "#d9c88e",
    ink: "#3a2f10",
    concepts: [
      "/patio/patio-01.webp",
      "/patio/patio-02.jpeg",
      "/patio/patio-03.jpg",
      "/patio/patio-04.jpg",
      "/patio/patio-05.jpg",
      "/patio/patio-06.avif"
    ]
  }
];

/* The scroll walk: the five rooms the client wants on the home page, in order. */
const WALK = ["living", "dining", "kitchen", "bedroom", "patio"];
export const walkRooms = WALK.map((id) => rooms.find((r) => r.id === id));

export const roomIds = rooms.map((r) => r.id);

export const roomById = (id) => rooms.find((r) => r.id === id);

/* The chapter a given room belongs to, for progress labelling. */
export const chapterOf = (id) => {
  let current = null;
  for (const r of rooms) {
    if (r.chapter) current = r.chapter;
    if (r.id === id) return current;
  }
  return null;
};
