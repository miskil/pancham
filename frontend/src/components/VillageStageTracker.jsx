const STAGES = ["PROPOSAL", "PLAN", "ACTIVE", "COMPLETED"];
const LABELS = { PROPOSAL: "Proposal", PLAN: "Plan", ACTIVE: "Active", COMPLETED: "Completed" };

export function VillageStageTracker({ stage, subStatus }) {
  const currentIdx = STAGES.indexOf(stage);

  return (
    <div className="surface-muted mb-6 overflow-x-auto px-3 py-4 md:px-4">
      <div className="flex items-start gap-0 min-w-[560px] md:min-w-0 pb-1">
      {STAGES.map((s, i) => {
        const done = i < currentIdx;
        const current = i === currentIdx;
        const upcoming = i > currentIdx;
        const isLast = i === STAGES.length - 1;

        return (
          <div key={s} className="flex items-start flex-1 min-w-0">
            <div className="flex flex-col items-center flex-1 min-w-0">
              <div className="flex items-center w-full">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold border transition-all
                    ${done ? "bg-accent-600 border-accent-600 text-white shadow-soft" : ""}
                    ${current ? "bg-primary-600 border-primary-600 text-white ring-4 ring-primary-100 shadow-soft" : ""}
                    ${upcoming ? "bg-white/90 border-primary-100 text-ink-300" : ""}
                  `}
                >
                  {done ? "✓" : i + 1}
                </div>
                {!isLast && (
                  <div
                    className={`h-0.5 flex-1 mx-2
                      ${done ? "bg-accent-600" : ""}
                      ${current ? "bg-primary-200" : ""}
                      ${upcoming ? "border-t-2 border-dashed border-primary-100 bg-transparent" : ""}
                    `}
                  />
                )}
              </div>
              <div className="mt-1 text-center px-1">
                <span
                  className={`text-xs font-medium leading-tight block tracking-[0.08em] uppercase
                    ${current ? "text-primary-700" : done ? "text-ink-600" : "text-ink-300"}
                  `}
                >
                  {LABELS[s]}
                </span>
                {current && subStatus && (
                  <span className="text-xs text-ink-500 block leading-tight mt-1">{subStatus}</span>
                )}
              </div>
            </div>
          </div>
        );
      })}
      </div>
    </div>
  );
}
