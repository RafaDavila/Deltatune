import { useEffect, useState } from "react";

import {
  getInfiniteAudioBlob,
} from "../services/deltatuneApi";

type AudioResult = {
  key: string;
  signal: AbortSignal;
  url: string | undefined;
  error: string | null;
};

type UseInfiniteAudioOptions = {
  runId: string | undefined;
  roundId: string | undefined;
  accountKey: string;
  enabled: boolean;
};

function useInfiniteAudio({
  runId,
  roundId,
  accountKey,
  enabled,
}: UseInfiniteAudioOptions) {
  const [result, setResult] =
    useState<AudioResult | null>(null);

  const key = JSON.stringify([
    accountKey,
    runId,
    roundId,
  ]);

  useEffect(() => {
    if (!enabled || !runId || !roundId) {
      return;
    }

    const controller = new AbortController();
    let objectUrl: string | undefined;

    async function loadAudio() {
      try {
        const blob = await getInfiniteAudioBlob(
          runId!,
          roundId!,
          controller.signal,
        );

        if (controller.signal.aborted) {
          return;
        }

        objectUrl = URL.createObjectURL(blob);

        setResult({
          key,
          signal: controller.signal,
          url: objectUrl,
          error: null,
        });
      } catch (error) {
        if (controller.signal.aborted) {
          return;
        }

        setResult({
          key,
          signal: controller.signal,
          url: undefined,
          error: error instanceof Error
            ? error.message
            : "Não foi possível carregar o áudio.",
        });
      }
    }

    void loadAudio();

    return () => {
      controller.abort();

      if (objectUrl !== undefined) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [enabled, runId, roundId, key]);

  const currentResult = (
    enabled &&
    result?.key === key &&
    !result.signal.aborted
  ) ? result : null;

  return {
    audioUrl: currentResult?.url,
    audioError: currentResult?.error ?? null,
  };
}

export default useInfiniteAudio;