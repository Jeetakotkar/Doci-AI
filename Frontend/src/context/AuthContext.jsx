import { createContext, useContext, useEffect, useState } from 'react';

const AuthContext = createContext(null);
const SESSION_KEY = 'fis_session';
const USERS_KEY = 'fis_users';

const DEFAULT_USERS = [
  { name: 'Ravi Sharma', email: 'officer@fis.gov.in', password: 'demo1234', role: 'officer', department: 'District Screening Desk' },
  { name: 'Anita Desai', email: 'admin@fis.gov.in', password: 'demo1234', role: 'admin', department: 'State Verification Cell' },
];

function loadUsers() {
  try {
    const stored = JSON.parse(localStorage.getItem(USERS_KEY));
    if (stored && stored.length) return stored;
  } catch {
    // fall through to seed
  }
  localStorage.setItem(USERS_KEY, JSON.stringify(DEFAULT_USERS));
  return DEFAULT_USERS;
}

function saveUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    try {
      const stored = JSON.parse(localStorage.getItem(SESSION_KEY));
      if (stored) setUser(stored);
    } catch {
      // ignore corrupt session
    }
    setReady(true);
  }, []);

  function signup({ name, email, password, department }) {
    const users = loadUsers();
    if (users.some((u) => u.email === email)) {
      throw new Error('An account with this email already exists.');
    }
    const role = email.toLowerCase().includes('admin') ? 'admin' : 'officer';
    const newUser = { name, email, password, department: department || 'General Screening', role };
    saveUsers([...users, newUser]);
    const session = { name, email, role, department: newUser.department };
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    setUser(session);
    return session;
  }

  function login({ email, password }) {
    const users = loadUsers();
    const found = users.find((u) => u.email === email && u.password === password);
    if (!found) {
      throw new Error('Email or password is incorrect.');
    }
    const session = { name: found.name, email: found.email, role: found.role, department: found.department };
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    setUser(session);
    return session;
  }

  function logout() {
    localStorage.removeItem(SESSION_KEY);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, ready, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
