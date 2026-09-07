import { Route, Routes } from "react-router";
import "./App.css";
import HomePage from "./pages/HomePage";
import MusicGamePage from "./pages/MusicGamePage";
import InfiniteGamePage from "./pages/InfiniteGamePage";
import ResetPasswordPage from "./pages/ResetPasswordPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/musica" element={<MusicGamePage />} />
      <Route path="/infinito" element={<InfiniteGamePage/>}/>
      <Route path="/redefinir-senha" element={<ResetPasswordPage />} />
    </Routes>
  );
}

export default App;