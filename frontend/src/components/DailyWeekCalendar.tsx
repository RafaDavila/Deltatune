import type {
  DailyWeekDayResponse,
} from "../services/deltatuneApi";

type DailyWeekCalendarProps = {
  days: DailyWeekDayResponse[];
};

const WEEKDAY_LABELS = [
  "dom.",
  "seg.",
  "ter.",
  "qua.",
  "qui.",
  "sex.",
  "sáb.",
];

function DailyWeekCalendar({
  days,
}: DailyWeekCalendarProps) {
  return (
    <div
      className="daily-week"
      aria-label="Desempenho da semana"
    >
      {days.map((day, index) => (
        <div
          className={
            "daily-week__day " +
            `daily-week__day--${day.status}`
          }
          data-status={day.status}
          key={day.challengeId}
        >
          <span className="daily-week__weekday">
            {WEEKDAY_LABELS[index]}
          </span>

          <strong className="daily-week__number">
            {Number(
              day.challengeId.slice(-2),
            )}
          </strong>
        </div>
      ))}
    </div>
  );
}

export default DailyWeekCalendar;