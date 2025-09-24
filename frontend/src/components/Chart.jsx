import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export const Chart = ({ chartData }) => {
  /**
   * A reusable line chart component for displaying time-series data.
   */
  if (!chartData || chartData.length === 0) {
    return <div className="text-center p-4">No interest data available.</div>;
  }

  // The data from the API is already in the correct array format.
  // We just need to rename the keys to match what the chart expects.
  const formattedData = chartData.map((item) => ({
    // Format the date for better display on the X-axis
    x: new Date(item.date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
    y: item.value,
  }));

  return (
    <div className="graph" style={{ width: "100%", height: 600 }}>
      {/* Use ResponsiveContainer to make the chart fit its parent */}
      <ResponsiveContainer>
        <LineChart
          data={formattedData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="x" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="y"
            stroke="#8884d8"
            strokeWidth={2}
            name="Search Interest"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
