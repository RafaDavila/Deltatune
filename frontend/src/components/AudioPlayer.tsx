import type { RefObject } from "react";
import {
  FaVolumeHigh,
  FaVolumeXmark,
} from "react-icons/fa6";

import heartIcon from "../assets/heart.png";

type AudioPlayerProps = {
  audioRef: RefObject<HTMLAudioElement | null>;
  audioUrl: string | undefined;
  attemptDurations: number[];
  currentAttempt: number;
  unlockedDuration: number;
  gameFinished: boolean;
  isPlaying: boolean;
  volume: number;
  challengeError: string | null;
  onPlay: () => void | Promise<void>;
  onStop: () => void;
  onVolumeChange: (volume: number) => void;
};

function AudioPlayer({
  audioRef,
  audioUrl,
  attemptDurations,
  currentAttempt,
  unlockedDuration,
  gameFinished,
  isPlaying,
  volume,
  challengeError,
  onPlay,
  onStop,
  onVolumeChange,
}: AudioPlayerProps) {
  const formattedDuration = unlockedDuration
    .toString()
    .replace(".", ",");

  return (
    <section className="audio-player">
      <audio
        ref={audioRef}
        src={audioUrl}
        preload="auto"
        onEnded={onStop}
      />

      <div className="audio-player__info">
        <span>Trecho liberado</span>

        <strong>
          {formattedDuration}{" "}
          {unlockedDuration <= 1
            ? "segundo"
            : "segundos"}
        </strong>
      </div>

      <div
        className="audio-timeline"
        aria-label={
          `Trecho de ${formattedDuration} ` +
          `${unlockedDuration <= 1
            ? "segundo"
            : "segundos"} liberado`
        }
      >
        {attemptDurations.map((duration, index) => (
          <span
            key={duration}
            className={
              gameFinished ||
              index <= currentAttempt
                ? (
                  "audio-timeline__segment " +
                  "audio-timeline__segment--active"
                )
                : "audio-timeline__segment"
            }
          />
        ))}
      </div>

      {challengeError && (
        <p className="challenge-error">
          {challengeError}
        </p>
      )}

      <button
        className="play-button"
        type="button"
        aria-label="Reproduzir trecho da música"
        onClick={onPlay}
      >
        <img
          src={heartIcon}
          alt=""
          aria-hidden="true"
        />

        <span>
          {isPlaying ? "Tocando..." : "Reproduzir"}
        </span>
      </button>

      <label className="volume-control">
        <span
          className="volume-control__icon"
          aria-hidden="true"
        >
          {volume === 0
            ? <FaVolumeXmark />
            : <FaVolumeHigh />}
        </span>

        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={volume}
          aria-label="Volume do áudio"
          aria-valuetext={
            `${Math.round(volume * 100)}%`
          }
          onChange={(event) =>
            onVolumeChange(
              Number(event.target.value),
            )
          }
        />

        <strong>
          {Math.round(volume * 100)}%
        </strong>
      </label>
    </section>
  );
}

export default AudioPlayer;