import { createContext, useState, useEffect, useContext } from "react";
import { getWeeklyTrends } from "../services/apiService";

// 1. Create the context
const DataContext = createContext(null);

// 2. Create a custom hook for easy access
export const useData = () => {
  return useContext(DataContext);
};

// 3. Create the Provider component that will manage the state
export const DataProvider = ({ children }) => {
  const [entities, setEntities] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // This effect runs only once to fetch and store the data globally
    getWeeklyTrends()
      .then((responseData) => {
        setEntities(responseData.data);
      })
      .catch((err) => {
        setError(err.message || "Failed to fetch data.");
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []); // Empty array ensures it runs only once

  const value = {
    entities,
    isLoading,
    error,
  };

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
};
