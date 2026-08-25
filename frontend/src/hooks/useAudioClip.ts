import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

type UseAudioClipOptions = {
  audioSource: string | undefined;
  clipDuration: number;
  disabled: boolean;
};

function loadSavedVolume(): number {
  const savedVolume = localStorage.getItem(
    "deltatune-volume",
  );

  if (savedVolume === null) {
    return 0.6;
  }

  const parsedVolume = Number(savedVolume);

  return Number.isFinite(parsedVolume)
    ? Math.min(1, Math.max(0, parsedVolume))
    : 0.6;
}

function useAudioClip({
  audioSource,
  clipDuration,
  disabled,
}: UseAudioClipOptions) {
  const audioRef = useRef<HTMLAudioElement>(null);

  const stopTimerRef = useRef<
    ReturnType<typeof setTimeout> | null
  >(null);

  const [volume, setVolume] = useState(
    loadSavedVolume,
  );

  const [isPlaying, setIsPlaying] =
    useState(false);

  const stopAudio = useCallback(() => {
    if (stopTimerRef.current) {
      clearTimeout(stopTimerRef.current);
      stopTimerRef.current = null;
    }

    const audio = audioRef.current;

    if (audio) {
      audio.pause();
      audio.currentTime = 0;
    }

    setIsPlaying(false);
  }, []);

  const playAudio = useCallback(async () => {
    const audio = audioRef.current;

    if (!audio || disabled) {
      return;
    }

    stopAudio();

    try {
      await audio.play();
      setIsPlaying(true);

      stopTimerRef.current = setTimeout(
        stopAudio,
        clipDuration * 1000,
      );
    } catch (error) {
      console.error(
        "Não foi possível reproduzir o áudio:",
        error,
      );

      stopAudio();
    }
  }, [
    clipDuration,
    disabled,
    stopAudio,
  ]);

  useEffect(() => {
    const audio = audioRef.current;

    if (audio) {
      audio.volume = volume;
    }

    localStorage.setItem(
      "deltatune-volume",
      volume.toString(),
    );
  }, [volume]);

  useEffect(() => {
    stopAudio();
  }, [
    audioSource,
    stopAudio,
  ]);

  useEffect(() => {
    const audio = audioRef.current;

    return () => {
      if (stopTimerRef.current) {
        clearTimeout(stopTimerRef.current);
      }

      audio?.pause();
    };
  }, []);

  return {
    audioRef,
    volume,
    setVolume,
    isPlaying,
    playAudio,
    stopAudio,
  };
}

export default useAudioClip;