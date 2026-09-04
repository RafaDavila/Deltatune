import {
  render,
  screen,
} from "@testing-library/react";

import {
  describe,
  expect,
  it,
} from "vitest";

import type {
  DailyWeekDayResponse,
  DailyWeekStatus,
} from "../services/deltatuneApi";

import DailyWeekCalendar from "./DailyWeekCalendar";

describe("DailyWeekCalendar", () => {
  it("renders seven days with their status classes", () => {
    const challengeIds = [
      "2026-08-30",
      "2026-08-31",
      "2026-09-01",
      "2026-09-02",
      "2026-09-03",
      "2026-09-04",
      "2026-09-05",
    ];

    const statuses: DailyWeekStatus[] = [
      "won",
      "lost",
      "not_played",
      "in_progress",
      "unavailable",
      "unavailable",
      "unavailable",
    ];

    const days: DailyWeekDayResponse[] =
      challengeIds.map(
        (challengeId, index) => ({
          challengeId,
          challengeNumber: index + 1,
          status: statuses[index],
          attemptsUsed: 0,
          sessionId: null,
        }),
      );

    const { container } = render(
      <DailyWeekCalendar days={days} />,
    );

    expect(
      container.querySelectorAll(
        ".daily-week__day",
      ),
    ).toHaveLength(7);

    expect(
      screen.getByText("dom."),
    ).toBeInTheDocument();

    expect(
      container.querySelector(
        '[data-status="won"]',
      ),
    ).toHaveClass(
      "daily-week__day--won",
    );

    expect(
      container.querySelector(
        '[data-status="lost"]',
      ),
    ).toHaveClass(
      "daily-week__day--lost",
    );

    expect(
      container.querySelector(
        '[data-status="not_played"]',
      ),
    ).toHaveClass(
      "daily-week__day--not_played",
    );
  });
});