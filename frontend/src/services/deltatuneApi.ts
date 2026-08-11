export type DailyChallengeResponse = {
    challengeId: string;
    challengeNumber: number;
    attemptDurations: number[];
    nextResetAt: string;
};

export type GuessResponse = {
    challengeId: string;
    correct: boolean;
    songTitle: string | null;
};

const API_BASE_URL = (
    import.meta.env.VITE_API_URL ??
    "http://127.0.0.1:8000"
).replace(/\/$/, "");

export async function getDailyChallenge(): Promise<DailyChallengeResponse>{
    const response = await fetch(
        `${API_BASE_URL}/challenges/daily`,
    );

    if (!response.ok) {
        throw new Error("Não foi possivel carregar o desafio diário");
    }
    return response.json();
}

export async function submitDailyGuess(
    challengeId: string,
    answer: string,
): Promise<GuessResponse> {
    const response = await fetch(
        `${API_BASE_URL}/challenges/daily/guess`,
        {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                challengeId,
                answer,
            }),
        },
    )

    if(!response.ok) {
        throw new Error ("Não foi possível validar o palpite.",);
    }
    return response.json();
}
