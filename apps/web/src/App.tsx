import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import type { HourPattern, Place } from "./types";
import { PlaceList } from "./components/PlaceList";
import { StatusCard } from "./components/StatusCard";
import { BestTime } from "./components/BestTime";
import { Reports } from "./components/Reports";
import { HowItWorks } from "./components/HowItWorks";
import { DemoPanel } from "./components/DemoPanel";
import { Logo } from "./components/Logo";

type View = "agora" | "como-funciona";
const viewFromHash = (): View => (location.hash === "#como-funciona" ? "como-funciona" : "agora");

export default function App() {
  const [view, setView] = useState<View>(viewFromHash);
  const [places, setPlaces] = useState<Place[]>([]);
  const [hours, setHours] = useState<HourPattern | null>(null);
  const [selected, setSelected] = useState<string>(() => localStorage.getItem("lugar") ?? "escola-jardim-primavera");
  const [offline, setOffline] = useState(false);

  const refresh = useCallback(async () => {
    try {
      setPlaces(await api.places());
      setOffline(false);
    } catch {
      setOffline(true);
    }
  }, []);

  useEffect(() => {
    refresh();
    api.hours().then(setHours).catch(() => undefined);
    const t = setInterval(refresh, 10000);
    const onHash = () => {
      setView(viewFromHash());
      scrollTo(0, 0);
    };
    addEventListener("hashchange", onHash);
    return () => {
      clearInterval(t);
      removeEventListener("hashchange", onHash);
    };
  }, [refresh]);

  const choose = (id: string) => {
    setSelected(id);
    try {
      localStorage.setItem("lugar", id);
    } catch {
      /* armazenamento indisponível: só não lembra a escolha */
    }
  };

  const place = places.find((p) => p.id === selected) ?? places[0];

  return (
    <div className="page">
      <header className="top">
        <a href="#" className="brand" aria-label="RespiraCidadão, início">
          <Logo />
          <span>RespiraCidadão</span>
        </a>
        <nav>
          <a href="#" aria-current={view === "agora" ? "page" : undefined}>Agora</a>
          <a href="#como-funciona" aria-current={view === "como-funciona" ? "page" : undefined}>Como funciona</a>
        </nav>
      </header>

      {offline && <p className="banner">Sem conexão com a central. Mostrando a última informação recebida.</p>}

      {view === "agora" ? (
        <main className="agora">
          <PlaceList places={places} selected={place?.id} onSelect={choose} />
          {place && <StatusCard place={place} />}
          <div className="grid-2">
            {hours && <BestTime pattern={hours} />}
            {place && <Reports place={place} onSent={refresh} />}
          </div>
        </main>
      ) : (
        <HowItWorks />
      )}

      <footer className="foot">
        <DemoPanel places={places} onDone={refresh} />
        <p>Os níveis seguem o monóxido de carbono medido em 6.941 horas de uma estação de referência.</p>
      </footer>
    </div>
  );
}
