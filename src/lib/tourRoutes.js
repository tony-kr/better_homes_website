// Paths come from the Blender wall / furniture clearance audit. Never smooth
// positions across corners: an unconstrained spline can cut through a wall.
export function buildTourGraph(paths) {
  const nodes = new Map();
  const key = (p) => p.map((n) => n.toFixed(3)).join(',');
  for (const points of Object.values(paths)) {
    points.forEach((point, i) => {
      const id = key(point);
      if (!nodes.has(id)) nodes.set(id, { point, edges: new Map() });
      if (!i) return;
      const before = key(points[i - 1]);
      const distance = Math.hypot(...point.map((v, j) => v - points[i - 1][j]));
      nodes.get(id).edges.set(before, distance);
      nodes.get(before).edges.set(id, distance);
    });
  }
  return { nodes, key };
}

export function shortestRoute(graph, start, finish) {
  const source = graph.key(start), target = graph.key(finish);
  if (!graph.nodes.has(source) || !graph.nodes.has(target)) throw new Error('Unknown tour waypoint');
  const distance = new Map([[source, 0]]), previous = new Map(), open = new Set([source]);
  while (open.size) {
    const current = [...open].reduce((a, b) => distance.get(a) < distance.get(b) ? a : b);
    open.delete(current);
    if (current === target) {
      const ids = [current];
      while (ids[0] !== source) ids.unshift(previous.get(ids[0]));
      return ids.map((id) => graph.nodes.get(id).point);
    }
    for (const [next, length] of graph.nodes.get(current).edges) {
      const candidate = distance.get(current) + length;
      if (candidate < (distance.get(next) ?? Infinity)) {
        distance.set(next, candidate); previous.set(next, current); open.add(next);
      }
    }
  }
  throw new Error('Disconnected tour route');
}

export function measureRoute(points) {
  const lengths = [0];
  for (let i = 1; i < points.length; i++) {
    lengths.push(lengths[i - 1] + Math.hypot(...points[i].map((v, j) => v - points[i - 1][j])));
  }
  return { points, lengths, total: lengths.at(-1) };
}

export function sampleRoute(route, distance) {
  const d = Math.max(0, Math.min(distance, route.total));
  let i = 0;
  while (i < route.points.length - 2 && route.lengths[i + 1] < d) i++;
  const a = route.points[i], b = route.points[i + 1] || a;
  const span = (route.lengths[i + 1] ?? 0) - route.lengths[i];
  const t = span > 0 ? (d - route.lengths[i]) / span : 0;
  return { point: a.map((v, j) => v + (b[j] - v) * t), segment: i, t };
}

// Interrupt travel by going to an endpoint of the CURRENT edge, then following
// the graph. A nearest-global-point lookup could select the other side of a wall.
export function redirectRoute(graph, route, distance, finish) {
  const sample = sampleRoute(route, distance);
  const adjacent = [route.points[sample.segment], route.points[sample.segment + 1]].filter((p) => p && graph.nodes.has(graph.key(p)));
  const endpoint = adjacent.reduce((a, b) => Math.hypot(...a.map((v, i) => v - sample.point[i])) < Math.hypot(...b.map((v, i) => v - sample.point[i])) ? a : b);
  return measureRoute([sample.point, ...shortestRoute(graph, endpoint, finish)]);
}
