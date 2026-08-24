import heartIcon from "../assets/heart.png";

type LivesDisplayProps = {
  remainingLives: number;
  maximumLives: number;
};

function LivesDisplay({
  remainingLives,
  maximumLives,
}: LivesDisplayProps) {
  return (
    <div className="lives">
      <div
        className="lives__hearts"
        aria-label={
          `${remainingLives} de ${maximumLives} ` +
          "tentativas restantes"
        }
      >
        {Array.from(
          { length: maximumLives },
          (_, index) => (
            <img
              key={index}
              className={
                index >= remainingLives
                  ? "lives__heart lives__heart--lost"
                  : "lives__heart"
              }
              src={heartIcon}
              alt=""
              aria-hidden="true"
            />
          ),
        )}
      </div>

      <p>
        {remainingLives} de {maximumLives} tentativas restantes
      </p>
    </div>
  );
}

export default LivesDisplay;