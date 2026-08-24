export type AttemptStatus =
    | "skipped"
    | "wrong"
    | "correct";

export type AttemptResult = {
    answer: string;
    status: AttemptStatus;
};