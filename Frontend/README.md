# Fake Identity Screening — Frontend Prototype (SIH 2026)

A React frontend for a front-desk identity-document screening tool. An officer
uploads an ID document photo and captures a live photo via the device camera;
the app simulates five
automated checks (OCR extraction, face match, tamper detection, issuing-authority
cross-check, watchlist screening) and returns a trust score and a plain-language
verdict.

This is a **frontend-only prototype**. There is no backend — all "checks" are
simulated in the browser (see `src/utils/mockEngine.js`), and all data (users,
cases) is stored in `localStorage` so the app is fully interactive without any
server.

## Getting started

```bash
npm install
npm run dev
```

Then open the printed local URL (usually `http://localhost:5173`).

To create a production build:

```bash
npm run build
npm run preview
```

## Demo accounts

Two accounts are seeded automatically on first load:

| Role    | Email               | Password  |
|---------|---------------------|-----------|
| Officer | officer@fis.gov.in  | demo1234  |
| Admin   | admin@fis.gov.in    | demo1234  |

The admin account unlocks the **Analytics** page in the sidebar. Sign up with
any email containing "admin" to create additional admin accounts.

24 demo screening cases are seeded automatically so the dashboard, history,
and analytics pages have data to show right away. `resetDemoData()` in
`DataContext.jsx` can be wired up to a button if you want a reset control.

## Project structure

```
src/
  components/     Sidebar, app shell layout, status badges, landing hero widget
  context/        AuthContext (mock auth) and DataContext (mock case store)
  pages/          Landing, Login, Signup, Dashboard, NewScreening, Report,
                  History, Analytics, NotFound
  styles/         Design tokens (variables.css) and base/reset styles
  utils/          mockEngine.js (simulated screening logic), seedData.js,
                  format.js
```

## Where to plug in a real backend

Everything that would normally hit an API is isolated in two places:

- `src/context/AuthContext.jsx` — replace the `login`/`signup`/`logout`
  functions with real API calls; keep the same return shape (`{ name, email,
  role, department }`) and the rest of the app won't need to change.
- `src/context/DataContext.jsx` and `src/utils/mockEngine.js` — replace
  `runScreening()` with a call to your real OCR/face-match/fraud-detection
  service, and `addScreening`/`getById`/`updateResolution` with API calls.
  `Report.jsx` and `History.jsx` consume the same data shape either way.

## Tech stack

- React 19 + Vite
- React Router for navigation
- Recharts for the analytics charts
- Plain CSS (no framework), with a small design-token file (`src/styles/variables.css`)
