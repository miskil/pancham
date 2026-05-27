const STAGES = ["PROPOSAL", "PLAN", "ACTIVE", "COMPLETED"];
const LABELS = { PROPOSAL: "Proposal", PLAN: "Plan", ACTIVE: "Active", COMPLETED: "Completed" };

export function VillageStageTracker({ stage, subStatus }) {
  const currentIdx = STAGES.indexOf(stage);

  return (
    <div className="flex items-start gap-0 mb-6 overflow-x-auto pb-1">
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
                  className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold
                    ${done ? "bg-primary-700 text-white" : ""}
                    ${current ? "bg-primary-600 text-white ring-2 ring-primary-300" : ""}
                    ${upcoming ? "bg-gray-200 text-gray-400" : ""}
                  `}
                >
                  {done ? "✓" : i + 1}
                </div>
                {!isLast && (
                  <div
                    className={`h-0.5 flex-1 mx-1
                      ${done ? "bg-primary-700" : ""}
                      ${current ? "bg-gray-300" : ""}
                      ${upcoming ? "border-t-2 border-dashed border-gray-300 bg-transparent" : ""}
                    `}
                  />
                )}
              </div>
              <div className="mt-1 text-center px-1">
                <span
                  className={`text-xs font-medium leading-tight block
                    ${current ? "text-primary-700" : done ? "text-gray-600" : "text-gray-400"}
                  `}
                >
                  {LABELS[s]}
                </span>
                {current && subStatus && (
                  <span className="text-xs text-gray-500 block leading-tight mt-0.5">{subStatus}</span>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
