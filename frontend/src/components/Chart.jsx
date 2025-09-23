import React from "react";
// import { json } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

export const Chart = ({ jsonData }) => {
  if (!jsonData) {
    return null;
  }

  const data = JSON.parse(jsonData);

  const entries = Object.entries(data);
  console.log(entries);
  const keys = entries.map(([key, value]) => key);
  keys.sort();
  console.log(keys);
  const chartdata = keys.map((key, i) => ({ x: key, y: parseInt(data[key]) }));

  return (
    <div className="graph">
      <LineChart width={1600} height={600} data={chartdata}>
        <XAxis dataKey="x" />
        <YAxis />
        <CartesianGrid strokeDasharray="4 4" />
        <Tooltip />
        <Line type="monotone" dataKey="y" stroke="#8884d8" />
      </LineChart>
    </div>
  );
};
