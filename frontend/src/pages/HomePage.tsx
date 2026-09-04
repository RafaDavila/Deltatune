import { Link } from "react-router";
import deltatuneLogo from "../assets/deltatune-logo.png";
import heartIcon from "../assets/heart.png";
import SiteFooter from "../components/SiteFooter";
import { useEffect, useState } from "react";

import AuthModal from "../components/AuthModal";
import { useAuth } from "../hooks/useAuth";
import DailyWeekCalendar from
  "../components/DailyWeekCalendar";

import {
  getDailyWeek,
  getInfiniteRecord,
} from "../services/deltatuneApi";

import type {
  DailyWeekDayResponse,
} from "../services/deltatuneApi";


function HomePage() {
  const [isAuthOpen, setIsAuthOpen] =
    useState(false);

  const [
    infiniteRecord,
    setInfiniteRecord,
  ] = useState<number | null>(null);

  const [
    isRecordLoading,
    setIsRecordLoading,
  ] = useState(false);

  const [recordError, setRecordError] =
    useState(false);
  const {
    user,
    isAuthenticated,
    isLoading,
    logout,
  } = useAuth();
  const [weekDays, setWeekDays] =
    useState<DailyWeekDayResponse[]>([]);

  const [
    isWeekLoading,
    setIsWeekLoading,
  ] = useState(false);

  const [weekError, setWeekError] =
    useState<string | null>(null);
  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    let cancelled = false;

    async function loadDailyWeek() {
      setIsWeekLoading(true);
      setWeekError(null);

      try {
        const dailyWeek =
          await getDailyWeek();

        if (!cancelled) {
          setWeekDays(dailyWeek.days);
        }
      } catch (error) {
        if (!cancelled) {
          setWeekError(
            error instanceof Error
              ? error.message
              : "Não foi possível carregar a semana.",
          );
        }
      } finally {
        if (!cancelled) {
          setIsWeekLoading(false);
        }
      }
    }

    void loadDailyWeek();

    return () => {
      cancelled = true;
    };
  }, [
    isAuthenticated,
    user?.id,
  ]);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    let cancelled = false;

    async function loadInfiniteRecord() {
      setIsRecordLoading(true);
      setRecordError(false);

      try {
        const record = await getInfiniteRecord();

        if (!cancelled) {
          setInfiniteRecord(record.bestStreak);
        }
      } catch {
        if (!cancelled) {
          setRecordError(true);
        }
      } finally {
        if (!cancelled) {
          setIsRecordLoading(false);
        }
      }
    }

    void loadInfiniteRecord();

    return () => {
      cancelled = true;
    };
  }, [
    isAuthenticated,
    user?.id,
  ]);
  return (
    <main className="home">
      <div className="home__account">
        {isLoading ? (
          <span className="home__account-status">
            Carregando conta...
          </span>
        ) : isAuthenticated && user !== null ? (
          <>
            <span className="home__account-name">
              {user.displayName}
            </span>

            <button
              className="home__account-button"
              type="button"
              onClick={logout}
            >
              Sair
            </button>
          </>
        ) : (
          <button
            className="home__account-button"
            type="button"
            onClick={() => {
              setIsAuthOpen(true);
            }}
          >
            Entrar
          </button>
        )}
      </div>
      <header className="home__header">
        <h1 className="home__title">
          <img
            className="home__logo"
            src={deltatuneLogo}
            alt="Deltatune"
          />
        </h1>

        <p>Escolha o seu desafio</p>
      </header>

      <section className="game-list">
        <Link
          className="game-card game-card--available"
          to="/musica"
        >
          <img
            className="game-card__heart"
            src={heartIcon}
            alt=""
            aria-hidden="true"
          />

          <div>
            <h2>Adivinhe a música</h2>
            <p>Reconheça a música ouvindo pequenos trechos.</p>
          </div>

          {isAuthenticated && (
            <div className="game-card__week">
              {isWeekLoading ? (
                <p className="game-card__week-message">
                  Carregando semana...
                </p>
              ) : weekError !== null ? (
                <p className="game-card__week-message">
                  Semana indisponível
                </p>
              ) : (
                <DailyWeekCalendar
                  days={weekDays}
                />
              )}
            </div>
          )}

          <span className="game-card__status">Jogar</span>
        </Link>

        <Link
          className="game-card game-card--available"
          to="/infinito"
        >
          <img
            className="game-card__heart"
            src={heartIcon}
            alt=""
            aria-hidden="true"
          />

          <div>
            <h2>MODO INFINITO</h2>
            <p>
              Adivinhe quantas músicas conseguir
              sem esperar o próximo desafio.
            </p>
          </div>

          {isAuthenticated && (
            <p className="game-card__record">
              Recorde:{" "}
              {isRecordLoading
                ? "..."
                : recordError
                  ? "indisponível"
                  : infiniteRecord ?? 0}
            </p>
          )}

          <span className="game-card__status">
            Jogar
          </span>
        </Link>
      </section>
      <SiteFooter />
      {isAuthOpen && (
        <AuthModal
          onClose={() => {
            setIsAuthOpen(false);
          }}
        />
      )}
    </main>
  );
}

export default HomePage;
