import { createContext, useContext, useEffect, useState } from 'react';
import { buildSeedScreenings } from '../utils/seedData';

const DataContext = createContext(null);
const SCREENINGS_KEY = 'fis_screenings';

function loadScreenings() {
  try {
    const stored = JSON.parse(localStorage.getItem(SCREENINGS_KEY));
    if (stored && stored.length) return stored;
  } catch {
    // fall through to seed
  }
  const seeded = buildSeedScreenings();
  localStorage.setItem(SCREENINGS_KEY, JSON.stringify(seeded));
  return seeded;
}

export function DataProvider({ children }) {
  const [screenings, setScreenings] = useState([]);

  useEffect(() => {
    setScreenings(loadScreenings());
  }, []);

  function persist(next) {
    setScreenings(next);
    localStorage.setItem(SCREENINGS_KEY, JSON.stringify(next));
  }

  function addScreening(record) {
    const next = [record, ...screenings];
    persist(next);
    return record;
  }

  function updateResolution(id, resolution) {
    const next = screenings.map((s) => (s.id === id ? { ...s, resolution } : s));
    persist(next);
  }

  function getById(id) {
    return screenings.find((s) => s.id === id);
  }

  function resetDemoData() {
    const seeded = buildSeedScreenings();
    persist(seeded);
  }

  return (
    <DataContext.Provider
      value={{ screenings, addScreening, updateResolution, getById, resetDemoData }}
    >
      {children}
    </DataContext.Provider>
  );
}

export function useData() {
  return useContext(DataContext);
}
