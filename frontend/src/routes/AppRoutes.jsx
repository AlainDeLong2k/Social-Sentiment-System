import React from "react";
import { HashRouter, Routes, Route } from "react-router-dom";
import { Home } from "../pages/Home";

export const AppRoutes = () => {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    </HashRouter>
  );
};
