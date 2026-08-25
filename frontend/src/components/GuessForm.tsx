import {
  useState,
  type ChangeEvent,
  type KeyboardEvent,
  type SubmitEvent,
} from "react";

type GuessFormProps = {
  guess: string;
  songTitles: string[];
  guessError: string | null;
  songCatalogError: string | null;
  disabled: boolean;
  isSubmitting: boolean;
  onGuessChange: (value: string) => void;
  onSkip: () => void | Promise<void>;
  onSubmit: (
    event: SubmitEvent<HTMLFormElement>,
  ) => void | Promise<void>;
};

function GuessForm({
  guess,
  songTitles,
  guessError,
  songCatalogError,
  disabled,
  isSubmitting,
  onGuessChange,
  onSkip,
  onSubmit,
}: GuessFormProps) {
  const [
    isSuggestionsOpen,
    setIsSuggestionsOpen,
  ] = useState(false);

  const [
    activeSuggestionIndex,
    setActiveSuggestionIndex,
  ] = useState(-1);

  const normalizedGuess = guess
    .trim()
    .toLocaleLowerCase();

  const filteredSongs = normalizedGuess
    ? songTitles
        .filter((songTitle) =>
          songTitle
            .toLocaleLowerCase()
            .includes(normalizedGuess),
        )
        .slice(0, 5)
    : [];

  const showSuggestions =
    isSuggestionsOpen &&
    normalizedGuess.length > 0 &&
    !disabled;

  function closeSuggestions() {
    setIsSuggestionsOpen(false);
    setActiveSuggestionIndex(-1);
  }

  function handleGuessChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    onGuessChange(event.target.value);
    setIsSuggestionsOpen(true);
    setActiveSuggestionIndex(-1);
  }

  function handleSelectSong(songTitle: string) {
    onGuessChange(songTitle);
    closeSuggestions();
  }

  function handleGuessKeyDown(
    event: KeyboardEvent<HTMLInputElement>,
  ) {
    if (event.key === "Escape") {
      closeSuggestions();
      return;
    }

    if (filteredSongs.length === 0) {
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setIsSuggestionsOpen(true);

      setActiveSuggestionIndex(
        (previousIndex) =>
          previousIndex >=
          filteredSongs.length - 1
            ? 0
            : previousIndex + 1,
      );

      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      setIsSuggestionsOpen(true);

      setActiveSuggestionIndex(
        (previousIndex) =>
          previousIndex <= 0
            ? filteredSongs.length - 1
            : previousIndex - 1,
      );

      return;
    }

    if (
      event.key === "Enter" &&
      isSuggestionsOpen &&
      activeSuggestionIndex >= 0
    ) {
      const selectedSong =
        filteredSongs[activeSuggestionIndex];

      if (selectedSong) {
        event.preventDefault();
        handleSelectSong(selectedSong);
      }
    }
  }

  function handleSubmit(
    event: SubmitEvent<HTMLFormElement>,
  ) {
    closeSuggestions();
    onSubmit(event);
  }

  return (
    <form
      className="guess-form"
      onSubmit={handleSubmit}
    >
      <label
        className="guess-form__label"
        htmlFor="song-guess"
      >
        Qual é a música?
      </label>

      {guessError && (
        <p
          className="guess-form__error"
          role="alert"
        >
          {guessError}
        </p>
      )}

      {songCatalogError && (
        <p
          className="guess-form__error"
          role="alert"
        >
          {songCatalogError}
        </p>
      )}

      <div className="guess-form__autocomplete">
        <input
          id="song-guess"
          name="song-guess"
          type="text"
          role="combobox"
          placeholder="Digite o nome da música..."
          autoComplete="off"
          value={guess}
          disabled={disabled}
          aria-autocomplete="list"
          aria-expanded={showSuggestions}
          aria-controls="song-suggestions"
          aria-activedescendant={
            activeSuggestionIndex >= 0
              ? (
                `song-suggestion-` +
                `${activeSuggestionIndex}`
              )
              : undefined
          }
          onChange={handleGuessChange}
          onKeyDown={handleGuessKeyDown}
          onFocus={() => {
            if (guess.trim()) {
              setIsSuggestionsOpen(true);
            }
          }}
          onBlur={closeSuggestions}
        />

        {showSuggestions && (
          <ul
            className="song-suggestions"
            id="song-suggestions"
            role="listbox"
          >
            {filteredSongs.length > 0 ? (
              filteredSongs.map(
                (songTitle, index) => (
                  <li
                    id={
                      `song-suggestion-${index}`
                    }
                    key={songTitle}
                    role="option"
                    aria-selected={
                      index ===
                      activeSuggestionIndex
                    }
                  >
                    <button
                      className={
                        "song-suggestions__option " +
                        (
                          index ===
                          activeSuggestionIndex
                            ? (
                              "song-suggestions__" +
                              "option--active"
                            )
                            : ""
                        )
                      }
                      type="button"
                      onPointerDown={(event) => {
                        event.preventDefault();
                        handleSelectSong(songTitle);
                      }}
                      onClick={() =>
                        handleSelectSong(songTitle)
                      }
                    >
                      {songTitle}
                    </button>
                  </li>
                ),
              )
            ) : (
              <li className="song-suggestions__empty">
                Nenhuma música encontrada
              </li>
            )}
          </ul>
        )}

        <button
          className={
            "guess-button guess-button--skip"
          }
          type="button"
          onClick={onSkip}
          disabled={disabled}
        >
          Pular
        </button>

        <button
          className={
            "guess-button guess-button--confirm"
          }
          type="submit"
          disabled={disabled}
        >
          {isSubmitting
            ? "Validando..."
            : "Confirmar"}
        </button>
      </div>
    </form>
  );
}

export default GuessForm;