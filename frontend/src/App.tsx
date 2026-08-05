import { Route, Routes } from "react-router";
import "./App.css";
import HomePage from "./pages/HomePage";
import MusicGamePage from "./pages/MusicGamePage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/musica" element={<MusicGamePage />} />
    </Routes>
  );
}

export default App;