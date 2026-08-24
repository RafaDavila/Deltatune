import type { AttemptResult } from "../types/game";

type AttemptListProps = {
  attemptDurations: number[];
  attemptResults: AttemptResult[];
};

function AttemptList({
  attemptDurations,
  attemptResults,
}: AttemptListProps) {
  return (
    <div className="attempt-list">
      {attemptDurations.map((duration, index) => {
        const result = attemptResults[index];
        const status = result?.status ?? "empty";

        return (
          <div
            className={
              `attempt-slot attempt-slot--${status}`
            }
            key={duration}
          >
            <span className="attempt-slot__number">
              {index + 1}
            </span>

            <span
              className={
                `attempt-slot__result ` +
                `attempt-slot__result--${status}`
              }
            >
              {result?.answer ?? ""}
            </span>

            <span className="attempt-slot__duration">
              {duration
                .toString()
                .replace(".", ",")}
              s
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default AttemptList;