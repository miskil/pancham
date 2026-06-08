const SHORT_MR = {
  basic: "मूलभूत", poverty: "गरिबी", water: "पाणी", agriculture: "शेती",
  infrastructure: "पायाभूत", education: "शिक्षण", health: "आरोग्य",
  governance: "स्वराज्य", community: "समुदाय", projects: "प्रकल्प",
  environment: "पर्यावरण", tribal: "आदिवासी",
};
const SHORT_EN = {
  basic: "Basics", poverty: "Poverty", water: "Water", agriculture: "Agri",
  infrastructure: "Infra", education: "Education", health: "Health",
  governance: "Governance", community: "Community", projects: "Projects",
  environment: "Environ.", tribal: "Tribal",
};
const ICONS = {
  basic: "🏘", poverty: "📊", water: "💧", agriculture: "🌾",
  infrastructure: "🛣", education: "📚", health: "🏥", governance: "🏛",
  community: "🤝", projects: "📋", environment: "🌿", tribal: "🌲",
};

const CX = 210, CY = 210, R = 108, LR = 162;
const LEVELS = [0.25, 0.5, 0.75, 1];
const N = 12;

function pt(r, i) {
  const rad = ((i * 360) / N - 90) * (Math.PI / 180);
  return { x: CX + r * Math.cos(rad), y: CY + r * Math.sin(rad) };
}

function polyPts(scores) {
  return scores
    .map((s, i) => { const p = pt(Math.max(s, 0.03) * R, i); return `${p.x},${p.y}`; })
    .join(" ");
}

function gridPoly(level) {
  return Array.from({ length: N }, (_, i) => { const p = pt(level * R, i); return `${p.x},${p.y}`; }).join(" ");
}

function anchor(i) {
  const deg = (i * 360) / N;
  if (deg < 15 || deg > 345) return "middle";
  if (deg <= 165) return "start";
  if (deg >= 195) return "end";
  return "middle";
}

function labelDy(i, line) {
  const deg = (i * 360) / N;
  const atBottom = deg > 75 && deg < 105;
  const atTop = deg < 15 || deg > 345;
  if (atTop) return line === 0 ? -13 : -2;
  if (atBottom) return line === 0 ? 5 : 16;
  return line === 0 ? -4 : 7;
}

export function VillageProfileCard({ profile = {}, sections = [], lang = "mr" }) {
  const scored = sections.map((s) => {
    const data = profile[s.key] || {};
    const filled = s.fields.filter((f) => data[f.key]).length;
    return { key: s.key, filled, total: s.fields.length, score: filled / s.fields.length };
  });

  const overall = Math.round(
    (scored.reduce((sum, s) => sum + s.score, 0) / scored.length) * 100
  );

  const scores = scored.map((s) => s.score);

  return (
    <div className="rounded-xl border bg-white overflow-hidden">
      <svg viewBox="0 0 420 420" className="w-full">
        {/* Grid polygons */}
        {LEVELS.map((lv) => (
          <polygon
            key={lv}
            points={gridPoly(lv)}
            fill={lv < 1 ? "none" : "none"}
            stroke={lv === 1 ? "#d1d5db" : "#f3f4f6"}
            strokeWidth={lv === 1 ? 1.5 : 1}
          />
        ))}

        {/* Axis spokes */}
        {Array.from({ length: N }, (_, i) => {
          const p = pt(R, i);
          return <line key={i} x1={CX} y1={CY} x2={p.x} y2={p.y} stroke="#e5e7eb" strokeWidth="1" />;
        })}

        {/* % level labels along top spoke */}
        {[0.25, 0.5, 0.75].map((lv) => {
          const p = pt(lv * R, 0);
          return (
            <text key={lv} x={p.x + 3} y={p.y} fontSize="7" fill="#9ca3af" dominantBaseline="middle">
              {Math.round(lv * 100)}%
            </text>
          );
        })}

        {/* Data fill */}
        <polygon
          points={polyPts(scores)}
          fill="rgba(22,101,52,0.12)"
          stroke="#166534"
          strokeWidth="2"
          strokeLinejoin="round"
        />

        {/* Data dots */}
        {scores.map((s, i) => {
          const p = pt(Math.max(s, 0.03) * R, i);
          return (
            <circle key={i} cx={p.x} cy={p.y} r="3.5" fill="#166534" stroke="white" strokeWidth="1.5" />
          );
        })}

        {/* Axis labels */}
        {scored.map((s, i) => {
          const p = pt(LR, i);
          const a = anchor(i);
          const short = lang === "mr" ? (SHORT_MR[s.key] || s.key) : (SHORT_EN[s.key] || s.key);
          const icon = ICONS[s.key] || "";
          return (
            <g key={s.key}>
              <text x={p.x} y={p.y + labelDy(i, 0)} textAnchor={a} fontSize="9" fill="#374151" fontWeight="600">
                {icon} {short}
              </text>
              <text x={p.x} y={p.y + labelDy(i, 1)} textAnchor={a} fontSize="8" fill="#6b7280">
                {s.filled}/{s.total}
              </text>
            </g>
          );
        })}

        {/* Centre: overall % */}
        <text x={CX} y={CY - 10} textAnchor="middle" fontSize="26" fontWeight="700" fill="#166534">
          {overall}%
        </text>
        <text x={CX} y={CY + 10} textAnchor="middle" fontSize="9" fill="#6b7280">
          {lang === "mr" ? "माहिती पूर्ण" : "profile filled"}
        </text>
      </svg>
    </div>
  );
}
