# Fake Identity Screening — Frontend Explained (Simple Language)

This document explains every part of the code in plain words, and lists
questions a teacher/judge is likely to ask — with simple answers you can say
out loud.

---

## 1. The Big Picture (say this first if asked "what is this project")

> "This is the frontend — the part people see and click — for a system that
> checks if someone's ID document is real or fake. An officer enters the
> applicant's details, uploads their ID photo, and the app runs 5 simulated
> checks (like face match, tamper detection, database check) and shows a
> trust score and a verdict: Verified, Flagged, or Manual Review."

**Important honesty point:** The checks are *simulated* right now (not real
AI/OCR). This is the frontend + workflow; a real backend/ML model would plug
in later. Say this upfront — it shows you understand the project, not just
copied code.

---

## 2. How the app is organized (folders)

```
src/
├── components/   → small reusable pieces (sidebar, badges, layout)
├── context/      → shared data that many pages need (login info, case list)
├── pages/        → one file per screen (Login, Dashboard, Report, etc.)
├── styles/       → CSS files (colors, fonts, spacing)
└── utils/        → helper functions (fake checking logic, date formatting)
```

**Simple analogy:** Think of `pages/` as rooms in a house, `components/` as
furniture used in multiple rooms, `context/` as the house's shared electricity
supply (everyone can use it), and `utils/` as a toolbox.

**Q: Why did you organize it into folders like this?**
A: "It keeps things easy to find. Anything about pages goes in `pages`,
anything reused everywhere goes in `components`, and shared data goes in
`context`. It's a common way to structure React projects."

---

## 3. `main.jsx` — the starting point

This is the very first file that runs. It just says: "take my `App`
component and put it inside the `<div id='root'>` in `index.html`."

**Q: What is `main.jsx` for?**
A: "It's the entry point — the first line of code that runs when the app
loads. It mounts the whole React app onto the webpage."

---

## 4. `App.jsx` — the map of all pages (Routing)

This file lists every URL/page in the app and which component to show:

```
/               → Landing page (public)
/login          → Login page
/signup         → Signup page
/app            → Dashboard (only if logged in)
/app/screen     → New Screening form
/app/history    → Case History
/app/analytics  → Analytics (admin only)
/app/report/:id → Report for one specific case
```

It uses a library called **React Router** to do this — so clicking a link
changes the page without actually reloading the browser (feels instant).

**Q: What is routing / React Router?**
A: "Routing means showing different content based on the URL. React Router
lets us do that inside a single-page app — so `/login` shows the login form
and `/app` shows the dashboard, without the browser doing a full page
reload."

**Q: What does `/app/report/:id` mean?**
A: "The `:id` is a placeholder — it means 'any case ID can go here', like
`/app/report/FIS-2026-000123`. The Report page reads that ID from the URL to
know which case to show."

**Q: Why is `/app` protected but `/` and `/login` are not?**
A: "Because anyone should be able to see the landing page and log in, but
only logged-in users should see the actual dashboard and case data. That's
handled by `AppLayout.jsx`."

---

## 5. `context/AuthContext.jsx` — Login system (fake/mock)

This file manages **who is logged in**. Since there's no real server, it
fakes login using the browser's built-in storage called **localStorage**
(like a small notebook the browser keeps).

What it does:
- `signup()` — creates a new fake account and saves it in localStorage
- `login()` — checks if email+password match a saved account
- `logout()` — clears the saved login
- Two demo accounts are automatically created the first time the app runs:
  `officer@fis.gov.in` and `admin@fis.gov.in` (password `demo1234` for both)

**Q: Is this a real login system?**
A: "No — it's a mock/fake login for demo purposes. It stores data in the
browser's localStorage instead of a real database. In a real product, this
would call a backend server with proper security (like password hashing)."

**Q: What is localStorage?**
A: "It's a small storage space built into every web browser. Websites can
save simple data there, and it stays even if you close and reopen the
browser — but it only exists on that one browser/computer, not on a server."

**Q: How do officer and admin get different access?**
A: "If the email contains the word 'admin', the account gets the 'admin'
role. The Sidebar checks this role and only shows the Analytics link to
admins."

**Q: Is storing passwords in localStorage safe?**
A: "No, it's not secure — it's plain text, fine only for a demo. A real
system would never do this; it would hash passwords and store them in a
secure database on a server."

---

## 6. `context/DataContext.jsx` — Case data storage (fake/mock)

This manages the **list of all screening cases** (the "database" of this
demo). Again, no real server — it's saved in localStorage.

What it does:
- Loads existing cases when the app starts (or creates 24 fake demo cases if
  none exist yet — see `utils/seedData.js`)
- `addScreening()` — adds a new case after someone runs a screening
- `getById()` — finds one case by its ID (used on the Report page)
- `updateResolution()` — updates a case's status (Approved/Rejected/etc.)

**Q: Where does the "case history" data actually live?**
A: "In the browser's localStorage, under a key called `fis_screenings`. It's
not a real database — it's just enough to make the demo fully interactive
without needing a server."

**Q: What are "seed" cases?**
A: "24 fake example cases that get created automatically the first time you
open the app, so the Dashboard, History, and Analytics pages aren't empty."

---

## 7. `components/AppLayout.jsx` — the protected area guard

This wraps every page under `/app/...`. Its only job:
- If nobody is logged in → send them to `/login`
- If someone is logged in → show the Sidebar + whichever page they clicked

**Q: How does the app know if someone is logged in?**
A: "It checks the `AuthContext` — if there's no user saved there, it
redirects to the login page using React Router's `<Navigate>`."

---

## 8. `components/Sidebar.jsx` — left-side navigation

Shows the app logo, navigation links (Overview, New Screening, Case
History, Analytics), the logged-in user's name, and a Sign Out button.

**Q: Why does the Analytics link only show for some users?**
A: "The code checks `user.role === 'admin'` and only renders that link if
true. This is called role-based access — different users see different
menu options."

---

## 9. `components/StatusBadge.jsx` — the colored pill (Verified/Flagged/etc.)

A small reusable component that shows a colored label:
- Green = Verified / Pass
- Red = Flagged / Fail
- Yellow/amber = Manual review / Warning

It's reused in the Dashboard table, History table, and Report page so the
colors stay consistent everywhere.

**Q: Why make this a separate component instead of writing it everywhere?**
A: "So the styling and logic for a status badge exists in one place. If I
want to change how 'Flagged' looks, I only edit one file instead of five."

---

## 10. `components/ScanConsole.jsx` — the animated box on the landing page

This is just a visual/decorative component — it shows a fake "document
being scanned" animation with a moving highlight bar and a checklist that
appears one item at a time, on a loop. It's built using CSS animations
(`@keyframes`), not JavaScript logic.

**Q: Does this scan console actually do anything?**
A: "No, it's purely decorative — it's there to make the landing page look
like the product in action, using CSS animation, not real functionality."

---

## 11. `pages/Landing.jsx` — the homepage

Public marketing/pitch page: headline, the ScanConsole animation, three
"why it's needed" stat cards, a 3-step "how it works" section, and a list
explaining what each of the 5 checks does. Ends with a call-to-action button
to sign up.

**Q: Why have a landing page at all?**
A: "It explains the problem and the product before asking someone to log in
— useful for a hackathon demo/pitch, and standard practice for any real
product."

---

## 12. `pages/Login.jsx` and `pages/Signup.jsx`

Simple forms. Login asks for email + password and calls `login()` from
AuthContext. Signup asks for name, email, department, password and calls
`signup()`. Both redirect to `/app` (the dashboard) on success, and show an
error message if something's wrong (e.g., wrong password, duplicate email).

**Q: What happens if I enter a wrong password?**
A: "The `login()` function in AuthContext throws an error, this page
catches it with `try/catch`, and displays the error message under the form."

---

## 13. `pages/Dashboard.jsx` — the overview page after login

Shows:
- 5 stat cards: total cases, verified count, review count, flagged count,
  average trust score (all calculated live from the case list)
- A table of the 6 most recent cases, with a link to view the full history

**Q: Where do the stat numbers come from?**
A: "They're calculated in JavaScript by looping through the `screenings`
array from DataContext and counting how many have each verdict — it's not
hardcoded, it updates automatically as new cases are added."

---

## 14. `pages/NewScreening.jsx` — the core "run a check" page

This is the most important page to understand well. It has two parts:

**Part A — the form** (shown first):
- Applicant details: full name, date of birth, document type (dropdown),
  document number
- An upload box for the ID document photo (shows a preview once picked)
- A grey placeholder box for "Live camera face capture" (this used to be a
  selfie upload box, but was removed because the plan is to replace it with
  real-time camera recognition later)
- A "Run screening" button

**Part B — the processing screen** (shown after clicking submit):
- A step-by-step checklist that "ticks off" one item every ~0.65 seconds,
  using `setTimeout()`, to simulate the checks running
- After all steps finish, it calls `runScreening()` (the fake-checking
  logic), creates a new case record, saves it via `addScreening()`, and
  navigates to that case's Report page

**Q: Is the upload box actually reading the image / doing OCR?**
A: "No. It just uses `FileReader` to show a preview of the image you picked
— it doesn't analyze the image at all. The actual 'checking' is faked in a
separate function."

**Q: Why does it take a few seconds to show a result?**
A: "That's an artificial delay using `setTimeout` — just to make the demo
feel like real processing is happening. There's no real computation
happening during that wait."

**Q: Why was the selfie upload removed?**
A: "The plan is to replace file upload with a live camera face-recognition
feature instead, so it was removed and a placeholder was added to show
where that feature will go."

**Q: What is `setTimeout` doing here exactly?**
A: "It's a JavaScript function that runs some code after a delay. Here it's
used 5 times with increasing delays, so each processing step lights up one
after another instead of all at once."

---

## 15. `pages/Report.jsx` — the detailed result page

Shows one case in full detail:
- Trust score (a number out of 100) and the verdict badge (Verified /
  Flagged / Manual review)
- All 5 individual checks, each with its own status badge, a colored
  confidence bar, and a plain-language explanation
- The applicant's details (name, DOB, document number, case ID)
- Three action buttons: Approve, Escalate, Reject — clicking one updates
  the case's `resolution` and shows it immediately

**Q: How does this page know which case to show?**
A: "It reads the case ID from the URL (`useParams()` from React Router) and
looks it up using `getById()` from DataContext."

**Q: Does approving/rejecting a case actually do anything real, like send
an email or notify someone?**
A: "No — it just updates a status field in localStorage and updates the
screen. In a real system, this would call a backend API."

**Q: How is the confidence bar's width and color decided?**
A: "Each check has a `confidence` number (0–100) — that number becomes the
bar's width in percent, and the bar's color depends on whether the check
`status` is pass, fail, or warning."

---

## 16. `pages/History.jsx` — searchable list of all cases

A table of every case, with:
- A search box (matches name, case ID, or document number as you type)
- Filter buttons: All / Verified / Manual review / Flagged

**Q: How does the search work — does it call a server?**
A: "No, it's all done in the browser. It just filters the existing
`screenings` array in JavaScript using `.filter()` based on what you typed
and which filter button is active — no server request needed since all
the data is already loaded."

---

## 17. `pages/Analytics.jsx` — charts (admin only)

Shows 4 charts, built using a charting library called **Recharts**:
1. **Line chart** — number of screenings per day
2. **Donut/pie chart** — how many cases are Verified vs Flagged vs Review
3. **Horizontal bar chart** — which of the 5 checks fails most often
4. **Vertical bar chart** — how many cases per document type

All the numbers are calculated live from the same case list using
JavaScript's `.reduce()` and `.map()` — nothing is hardcoded.

**Q: Why can only admins see this page?**
A: "Analytics usually contains sensitive, aggregated information meant for
supervisors, not every officer — so access is restricted by role, same
idea as in a real organization."

**Q: What library did you use for the charts and why?**
A: "Recharts — a popular, free React charting library. It was chosen
because it's easy to use with React and produces clean, responsive charts
without much custom code."

---

## 18. `utils/mockEngine.js` — the "fake brain" (most asked-about file)

This is the file that decides whether a case is Verified, Flagged, or needs
Manual review. It simulates 5 checks:

1. **Document data extraction (OCR)** — pretends to read the ID's text
2. **Face match** — pretends to compare the selfie/live photo to the ID photo
3. **Tamper detection** — pretends to check for signs of editing
4. **Authority cross-check** — pretends to validate against a government database
5. **Watchlist screening** — pretends to check against a fraud watchlist

Each check gets a random-ish confidence score (0–100). If the applicant's
name or ID number contains a "suspicious" word (like "test" or "fake"), the
scores are deliberately made lower — this is a trick built in so the demo
can reliably show a "Flagged" result when you want to prove that case works.

The final verdict logic:
- Any check **fails** → verdict = "flagged"
- No fails, but some checks show a **warning** → verdict = "review"
- All checks **pass** → verdict = "verified"

**Q: Is this real fraud detection / AI?**
A: "No — this is simulated logic using semi-random numbers, built only to
make the demo interactive and show what a real result screen would look
like. A real system would replace this with actual OCR software, face
recognition AI, and real database/API connections."

**Q: How do you make a flagged result appear for the demo?**
A: "Type a word like 'test' or 'fake' into the name or ID number field —
the code checks for these words and deliberately lowers the scores so you
can reliably demonstrate a flagged case."

**Q: What is a 'trust score'?**
A: "It's the average of all 5 checks' confidence scores, shown as a single
number out of 100, so the officer gets one quick number to look at instead
of five separate ones."

---

## 19. `utils/seedData.js` — demo case generator

Generates 24 realistic-looking fake cases (names, document types, dates,
verdicts) so the app isn't empty when you first open it. Runs once, only if
no cases already exist in localStorage.

**Q: Why 24 cases specifically?**
A: "No special reason — just enough to make the charts and tables look
populated and realistic without being excessive."

---

## 20. `utils/format.js` — small helper functions

Two tiny functions:
- `generateCaseId()` — makes IDs like `FIS-2026-000123`
- `formatDate()` / `formatDateShort()` — turns a raw date into a readable
  format like "08 Sep 2026"

**Q: Why separate these into their own file?**
A: "So they can be reused anywhere in the app without repeating code — it's
called the 'DRY' principle: Don't Repeat Yourself."

---

## 21. `styles/variables.css` and `styles/base.css`

- `variables.css` — defines all the colors, fonts, and spacing values once
  (as CSS variables, e.g. `--verified: #1b7a5a;`), so the whole app uses a
  consistent look
- `base.css` — resets default browser styling and defines shared classes
  like `.btn`, `.field`, `.container` used across every page

**Q: Why use CSS variables instead of typing colors everywhere?**
A: "If I want to change the 'flagged' red color, I only change it in one
place instead of hunting through every file."

**Q: Did you use a CSS framework like Bootstrap or Tailwind?**
A: "No — plain custom CSS, organized with CSS variables for consistency."

---

## 22. Likely "why did you choose X" questions

**Q: Why React and not plain HTML/JS?**
A: "React lets you build reusable components (like the StatusBadge or
Sidebar) and automatically updates the screen when data changes — much
easier to manage for an app with many pages and shared data like this one."

**Q: Why Vite instead of Create React App?**
A: "Vite is faster to start up and rebuild during development — it's the
current recommended tool for new React projects."

**Q: Why is there no backend?**
A: "This is a hackathon prototype focused on proving out the frontend
workflow and user experience first. The backend (real OCR, face
recognition, database checks) is a separate piece meant to be built next
and connected through a few specific functions I kept isolated for that
purpose."

**Q: How would you connect a real backend later?**
A: "Two files would change: `AuthContext.jsx` (replace fake login with real
API calls) and `DataContext.jsx` / `mockEngine.js` (replace the fake
checking logic with a real API call to a backend that does actual OCR and
face matching). Every other page already just displays whatever data comes
back from those two places, so they wouldn't need to change."

**Q: What would you improve if you had more time?**
A: "Real OCR and face-matching using something like Tesseract.js or
face-api.js (which can even run in the browser), a real backend with a
proper database, secure password handling, and a live camera feature
instead of file uploads."

---

## 23. Quick one-line answers cheat sheet

| Question | One-line answer |
|---|---|
| What is this? | Frontend prototype for a fake-ID screening tool |
| What's the frontend framework? | React, built with Vite |
| Is the checking real? | No, simulated — proves the UI/workflow |
| Where's the data stored? | Browser's localStorage (no server yet) |
| How do pages change? | React Router, based on the URL |
| How do officer/admin differ? | Role stored in login data controls menu access |
| What are the 5 checks? | OCR extraction, face match, tamper detection, database cross-check, watchlist screening |
| What decides Verified/Flagged/Review? | Whether any check fails or just warns |
| What are the charts made with? | Recharts library |
| What's missing for production? | Real backend, real AI checks, secure auth, live camera |
