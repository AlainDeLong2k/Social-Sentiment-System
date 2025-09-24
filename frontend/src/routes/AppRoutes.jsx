import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Home } from "../pages/Home";
import { AnalysisDetail } from "../pages/AnalysisDetail";

export const AppRoutes = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/home" element={<Home />} />
        <Route path="/analysis/:entityId" element={<AnalysisDetail />} />
      </Routes>
    </BrowserRouter>
  );
};
