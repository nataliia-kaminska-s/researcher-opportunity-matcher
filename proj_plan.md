# Researcher Opportunity Matcher (ROM)

An intelligent system for personalized search of scientific grants and exchange programs based on the analysis of the researcher's profile.

> Primary focus: Ukrainian research community (expandable to international).

---

## Table of Contents

- Project Overview
- Roles & User Types
- Key Features
  - MVP
  - Phase 2+ (Nice-to-haves)
- Data Models
  - Researcher Profile
  - Opportunity
- System Architecture
  - Tech Stack
  - Frontend Architecture
  - Backend Architecture
  - API Endpoints
  - Database Schema (PostgreSQL)
- Matching Algorithm
  - Three-Layer Matching Approach
  - ML Pipeline
- Implementation Roadmap
  - Phase 0: Setup & Planning
  - Phase 1: MVP Core Features
  - Phase 2: Matching & Recommendations
  - Phase 3: Polish & Deployment
  - Phase 4+: Enhancements & Scaling
- Technology Decisions & Rationale
- Data Sources to Research
- Risk Mitigation
- Success Metrics
- Development Best Practices
- Next Steps

---

## Project Overview

**Name:** Researcher Opportunity Matcher (ROM)

**Purpose:** Intelligent system matching Ukrainian researchers with grant and exchange program opportunities based on comprehensive profile analysis.

**Primary Market:** Ukrainian research community (expandable to international).

**Languages:** Ukrainian, English.

**Platform:** Desktop web application.


## Roles & User Types

1. Researcher
   - Create and manage profile
   - Browse & search opportunities
   - Receive personalized recommendations
   - Save/favorite opportunities
   - Receive notifications and reminders
   - View match scores and explanations
   - Track application history

2. Administrator
   - Manage opportunities database (CRUD)
   - View researcher analytics
   - Generate reports
   - Manage content & translations

3. Data Manager (optional)
   - Import/update grant & program data from external sources
   - Data quality checks
   - Bulk operations


## Key Features

### MVP

- Researcher authentication & persistent profiles
- Multi-step profile builder capturing rich researcher attributes
- Opportunity search with advanced filters
- AI-powered ranking with match score and explainability
- Save/favorite/mark/apply flows and interaction tracking
- Admin panel for opportunity and user management

### Phase 2+ (Nice-to-haves)

- Email notifications and digests
- ML model refinement from user behavior
- Advanced analytics & reporting
- API integrations / web scraping for external data sources
- Mobile app (React Native or Flutter)
- ORCID / Google Scholar / LinkedIn profile linking


## Data Models

### Researcher Profile (high level)

- Identity: full name, email, institution, location
- Academic background: degrees, fields, years
- Research profile: primary/secondary areas, keywords
- Publications: count, h-index, recent publications
- Funding history: previous grants and total amount
- Projects: current/completed
- Languages: proficiencies
- Preferences: preferred countries, institutions, duration, amount
- System data: profile completion %, last updated


### Opportunity Attributes (high level)

- Basic info: title, type (grant/exchange/fellowship), description, source URL
- Eligibility: career stage, required fields, languages, citizenship restrictions
- Details: amount, duration, deadlines, start date
- Classification: research areas, topics, sectors
- Institution/funder info
- System data: created/updated dates, keywords


## System Architecture

### Tech Stack

Frontend:
- React 18+ with TypeScript
- Vite
- Redux Toolkit
- React Router v6
- Tailwind CSS (+ optional shadcn/ui)
- Recharts for data visualization
- Axios for HTTP
- i18n for localization (uk/en)

Backend:
- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL (primary DB)
- Redis (cache)
- Celery (async tasks)
- scikit-learn / XGBoost / LightGBM (ML)
- Pydantic for validation
- JWT for auth

Infrastructure:
- Docker + Docker Compose
- CI/CD via GitHub Actions
- Free tier hosting options: Vercel (frontend), Railway/Render/Neon (backend + Postgres)
- Redis Cloud (free tier)


### Frontend Architecture

Directory layout (recommended):

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── common/
│   │   ├── features/
│   │   └── layout/
│   ├── pages/
│   ├── store/
│   ├── services/
│   ├── hooks/
│   ├── utils/
│   ├── types/
│   ├── i18n/
│   ├── styles/
│   ├── App.tsx
│   └── main.tsx
├── tailwind.config.js
├── vite.config.ts
└── package.json
```

Key components:
- Auth forms (Login/Register)
- ProfileBuilder (multi-step)
- SearchFilters
- OpportunityCard & OpportunityDetail
- Recommendation widgets & MatchScoreBreakdown
- Admin dashboard components

State management with Redux Toolkit for auth, profile, opportunities, recommendations, ui, notifications.


### Backend Architecture

Directory layout (recommended):

```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   └── routes/ (auth, profile, opportunities, matching, admin, analytics)
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── ml/
│   ├── core/
│   ├── database/
│   ├── tasks/
│   └── utils/
├── tests/
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```


### API Endpoints (overview)

Authentication:
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- POST /api/v1/auth/logout

Researcher Profile:
- GET /api/v1/profile
- PUT /api/v1/profile
- POST /api/v1/profile/validate
- POST /api/v1/profile/picture

Opportunities:
- GET /api/v1/opportunities
- GET /api/v1/opportunities/:id
- POST /api/v1/opportunities (admin)
- PUT /api/v1/opportunities/:id (admin)
- DELETE /api/v1/opportunities/:id (admin)

Matching & Recommendations:
- GET /api/v1/matching/recommendations
- GET /api/v1/matching/:id/explain
- POST /api/v1/matching/search
- GET /api/v1/matching/similar/:id

Interactions:
- POST /api/v1/interactions/click
- POST /api/v1/interactions/favorite
- POST /api/v1/interactions/applied
- GET /api/v1/interactions/history

Admin:
- GET /api/v1/admin/users
- GET /api/v1/admin/analytics
- POST /api/v1/admin/opportunities/bulk

Notifications:
- GET /api/v1/notifications
- PUT /api/v1/notifications/:id/read
- PUT /api/v1/notifications/preferences


### Database Schema (PostgreSQL) - high-level

Main tables include (summaries):
- researchers (id, email, password_hash, name, institution, location, career_stage, profile_completion, timestamps)
- researcher_degrees
- researcher_research_areas
- researcher_keywords
- researcher_publications
- researcher_funding_history
- researcher_languages
- researcher_preferences
- opportunities (id, title, type, description, eligibility, amount, duration, deadlines, keywords, funder)
- researcher_interactions (click/favorite/applied)
- researcher_favorites
- researcher_applications
- match_scores (cache table)
- notifications
- admin_users

(Refer to detailed plan for full field lists.)


## Matching Algorithm

### Three-Layer Matching Approach

1. Rule-based filtering (hard constraints):
   - Eligibility checks: career stage, citizenship, language, required fields.
   - If a hard constraint fails -> match_score = 0.

2. Keyword & semantic matching:
   - TF-IDF / exact keyword matching.
   - Semantic similarity (FastText / Word2Vec / Transformer embeddings for Ukrainian where available).
   - Normalize to 0-100.

3. Behavioral & collaborative filtering (ML-based):
   - Use user interactions (clicks, favorites, applications) and similar users' behavior.
   - Candidate algorithms: collaborative filtering, XGBoost/LightGBM ranking models, or neural ranking models.

Final score composition (example):
```
match_score = rule_pass * (0.4 * keyword_score + 0.3 * behavioral_score + 0.2 * interaction_score + 0.1 * institutional_alignment)
```

Explainability:
- Return component-wise breakdown, top matching factors, top non-matching factors, and suggestions for improving match.


### ML Model Training Pipeline (outline)

- Data collection: researcher profiles, interactions, opportunity metadata, application outcomes.
- Feature engineering: vectorize textual fields, encode categorical fields, normalize numeric ones.
- Model choices: start with XGBoost ranking (LambdaMART) or LightGBM; iterate to neural models if needed.
- Evaluation: NDCG, MAP, precision@K.
- Retraining cadence: weekly/monthly depending on data volume.


## Implementation Roadmap

### Phase 0: Setup & Planning (1 week)

Deliverables:
- Repo scaffold (monorepo: frontend/ & backend/)
- Docker Compose local dev environment
- DB schema & Alembic migrations
- Basic FastAPI skeleton + React + Vite scaffold
- i18n setup (uk/en)
- Wireframes for key pages

Tasks:
- Initialize Git repo
- Setup Docker Compose (Postgres, Redis, backend, frontend)
- Setup CI (GitHub Actions basic)


### Phase 1: MVP Core Features (4-5 weeks)

Sprint 1.1 (Auth):
- Registration, Login, JWT refresh.

Sprint 1.2 (Profile):
- Multi-step profile builder
- Profile CRUD
- Profile completion calculation

Sprint 1.3 (Opportunity & Search):
- Opportunity list and detail
- Basic search & filters
- Seed DB with sample opportunities

Sprint 1.4 (Admin):
- Admin CRUD, bulk import, basic analytics


### Phase 2: Matching & Recommendations (3-4 weeks)

Sprint 2.1 (Keyword Matching):
- TF-IDF & semantic similarity
- Rule-based eligibility
- Caching scores

Sprint 2.2 (Interaction Tracking):
- Log clicks/favorites/applies
- Store for ML training

Sprint 2.3 (ML Model):
- Feature extraction, training scripts, model serialization
- Start with XGBoost / LightGBM

Sprint 2.4 (Explainability & UI):
- Recommendation page, match breakdown UI
- Explainability API endpoints


### Phase 3: Polish & Deployment (2-3 weeks)

- Testing (unit, integration, E2E)
- Performance optimization & caching
- Deploy to free-tier providers (Vercel, Railway/Render)
- Production-ready docs & monitoring


### Phase 4+: Enhancements & Scaling (ongoing)

- Email notifications (SendGrid)
- Advanced analytics dashboards
- More data sources and scaling up to thousands of opportunities
- Mobile app and social features


## Technology Decisions & Rationale

- React + TypeScript: robust frontend ecosystem and type safety.
- Vite: fast dev server and build.
- Tailwind CSS: highly customizable styling.
- FastAPI: high performance, modern Python web framework with automatic docs.
- PostgreSQL: reliable relational DB, JSON support for flexible fields.
- Redis: caching and fast lookup for recommendations.
- Celery: background jobs for notifications and heavy tasks.
- XGBoost / LightGBM: strong baseline for tabular ranking tasks.


## Data Sources to Research (priority)

- Ukrainian government & national research agencies (NRFU, Ministry of Education & Science of Ukraine)
- Ukrainian university research offices
- European sources: Horizon Europe, Erasmus+, EURAXESS
- International: Fulbright (Ukraine), DAAD, British Council
- Aggregators: ResearchGate, funding portals


## Risk Mitigation

- Limited grant data: start with mock/seeding, build scrapers and import pipeline.
- ML model quality: start rule-based, iterate with real interactions, validate with metrics.
- Ukrainian NLP complexity: test and validate Ukrainian models (spaCy / transformers supporting Ukrainian).
- Data privacy: implement encryption at rest/in transit, GDPR-like controls, delete policies.


## Success Metrics (sample)

- 50+ registered researchers by Phase 2
- 80% profile completion
- 5+ interactions per user per week
- 70%+ recommendation CTR
- API p95 response < 500ms
- ML NDCG@10 > 0.7 (target)


## Development Best Practices

- Strict TypeScript for frontend; ESLint + Prettier
- Black + Flake8 + isort for backend; type hints
- Unit + integration + E2E tests; target reasonable coverage
- Git branching with protected main; PR reviews
- CI/CD with tests and linting


## Next Steps

1. Review this plan and adjust priorities
2. Initialize repository and scaffolding
3. Create wireframes for key pages
4. Begin Phase 0: environment and DB schema
5. Start Phase 1: auth & profile flows


---

*File created automatically from the design & planning session.*
