import { HashRouter, Routes, Route } from "react-router-dom";
import { Home } from "../pages/Home";
import { AnalysisDetail } from "../pages/AnalysisDetail";

export const AppRoutes = () => {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/home" element={<Home />} />
        <Route path="/analysis" element={<AnalysisDetail />} />
        <Route path="/keyword" element={<Home />} />
      </Routes>
    </HashRouter>
  );
};
