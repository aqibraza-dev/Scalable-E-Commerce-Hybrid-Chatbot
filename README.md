# Shopcart: Enterprise Scalable E-Commerce Search & Hybrid Chatbot Platform (1M+ Users)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-Agent%20Development%20Kit-4285F4.svg?style=flat&logo=google&logoColor=white)](https://github.com/google/adk)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6.4+-646CFF.svg?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-FTS5%20B--Tree-003B57.svg?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Redis](https://img.shields.io/badge/Redis-Multi--Tier%20L2-DC382D.svg?style=flat&logo=redis&logoColor=white)](https://redis.io/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4+-38B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/Pytest-88%2F88%20Passed-brightgreen.svg?style=flat&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat)](LICENSE)


A high-performance, production-grade e-commerce search and hybrid chatbot platform designed for high-concurrency workloads (~1,000,000 monthly active users). Modeled after the **Shopcart** reference design, the application combines a **sub-millisecond B-Tree & FTS5 search engine**, a **Google ADK multi-agent architecture**, and a **5-tier hybrid routing pipeline achieving 99.14% LLM token savings** with **full shopping cart integration**.

---

## Table of Contents

- [Executive Summary & Business Impact (1M Users)](#executive-summary)
- [1. Project Goal & Strategic Vision](#goal)
- [2. Google ADK Multi-Agent Teamwork Architecture](#teamwork)
- [3. Engineering Learnings & Architectural Principles](#learn)
- [4. Performance Boost & Optimization Benchmarks ](#boost)
- [5. System Architecture: The 5-Tier Hybrid Engine](#system-architecture)
- [6. Deep Chatbot Issue Resolutions & Research](#chatbot-resolutions)
- [7. Database Schema, Datatypes & Secure Database Agent](#database-schema)
  - [7.1 Smartphones Table Schema (`smartphones`)](#smartphones-schema)
  - [7.2 Full-Text Search Virtual Table (`smartphones_fts`)](#fts-schema)
  - [7.3 Secure Database Agent (`DatabaseAgent`)](#database-agent)
- [8. Enhanced Chat Features (Modern E-Commerce Experience)](#enhanced-features)
- [9. Enterprise Security & Database Hardening (Anti-Hacking)](#enterprise-security)
- [10. Visual Benchmark Reports & Architecture Charts](#benchmark-reports)
- [11. Repository Structure](#repository-structure)
- [12. Quick Start (Local Development)](#quick-start)
  - [12.1 Prerequisites](#prerequisites)
  - [12.2 Backend Setup](#backend-setup)
  - [12.3 Frontend Setup](#frontend-setup)
- [13. Running Automated Tests](#running-tests)
- [14. License](#license)

---

<a id="executive-summary"></a>
## Executive Summary & Business Impact (1M User Projection)

Based on comprehensive synthetic workload benchmarks (simulating 500 multi-parameter e-commerce queries with realistic natural language, Hinglish phrasing, and multi-turn context):

| Metric | Pure LLM Pipeline | Enterprise Hybrid Architecture | Business Impact / Improvement |
| :--- | :--- | :--- | :--- |
| **P95 Latency** | `22.70 ms` (virtual) / `1,520 ms` (live) | **`2.58 ms`** | **8.79x (virtual) to 580x (live) Faster Response** |
| **LLM Token Reduction** | `0%` (135.4k tokens / 500 reqs) | **`99.14%`** (only 1,291 tokens consumed) | **99.14% Cost & Token Reduction** |
| **Search Engine Throughput** | N/A | **`6,745 QPS`** | Sub-millisecond B-Tree & FTS5 search with slot extraction |
| **Search Engine P95 Latency** | N/A | **`0.166 ms`** | Real-time faceted catalog filtering |
| **1M User Monthly Spend** | **`$1,692.80`** | **`$16.20`** | **`$1,676.60 / month saved`** |
| **Annualized Cost Savings** | Baseline | **`₹1,740,311 / year ($20,119)`** | **99% Cloud Inference ROI** |

---

<a id="goal"></a>
## 1. Project Goal & Strategic Vision 
The primary objective of **Shopcart** is to solve the retail e-commerce dilemma: providing a high-intelligence conversational shopping assistant while maintaining sub-millisecond query performance, bulletproof security, and a 99%+ token reduction for **1,000,000+ monthly active users**.

- **Sub-Millisecond Catalog Exploration**: Real-time faceted filtering over 3,260 smartphone models across 21 hardware columns in $< 0.2\text{ ms}$ via B-Tree & FTS5 BM25 search.
- **99.14% Inference Cost Reduction**: Slashes monthly LLM spend from **$1,692.80 to $16.20**, saving over **₹1,740,311 / year** through deterministic routing and two-tier caching.
- **Physical Driver-Level Security**: Blocks 100% of SQL injections, stacked commands, prompt injections, and PII leaks, enforcing `PRAGMA query_only = ON`.
- **Zero-Reasoning Leakage**: Guarantees zero chain-of-thought monologue leaks (`<AnswerToUser>...`) with automatic fallback to grounded catalog responses.

---

<a id="teamwork"></a>
## 2. Google ADK Multi-Agent Teamwork Architecture 

Shopcart integrates the **Google Agent Development Kit (ADK)** to build an enterprise hierarchical multi-agent teamwork architecture. The root supervisor coordinates four autonomous sub-agents with strictly typed tools:

```
                            [ Incoming User Query ]
                                       │
                                       ▼
                   ┌───────────────────────────────────────┐
                   │   Google ADK Multi-Agent Supervisor   │
                   │     (`shopcart_supervisor` Agent)     │
                   │   - Session Memory & State Delta      │
                   │   - Intent Classification & Routing   │
                   └───────────────────┬───────────────────┘
                                       │
     ┌───────────────────┬─────────────┴───────┬───────────────────┐
     │                   │                     │                   │
     ▼                   ▼                     ▼                   ▼
┌──────────────────┐┌──────────────────┐┌──────────────────┐┌──────────────────┐
│ Catalog Search   ││ Database Schema  ││ Store Policy     ││ Shopping Advisor │
│ Specialist Agent ││ Specialist Agent ││ Specialist Agent ││ & Bag Specialist │
│                  ││                  ││                  ││                  │
│ • search_catalog ││ • query_database ││ • check_store_   ││ • manage_cart    │
│ • get_phone_specs││ • get_database_  ││   policy_tool    ││ • get_phone_specs│
│ • compare_phones ││   schema_tool    ││ (Return, Warranty││ • search_catalog │
│ • find_catalog_  ││ (AST check +     ││  Shipping, EMI)  ││ (Lifestyle RAG   │
│   extremes       ││  PRAGMA read-only││                  ││  & Bag checkout) │
└──────────────────┘└──────────────────┘└──────────────────┘└──────────────────┘
```

1. **`shopcart_supervisor` (Supervisor Agent)**: Manages multi-turn conversation sessions using ADK's `InMemorySessionService`, routes tasks to specialized child agents, and emits interactive context action chips.
2. **`catalog_search_specialist` (Catalog Search Specialist)**: Executes faceted multi-attribute catalog queries, hardware spec lookups, and side-by-side comparison tables with category winners.
3. **`database_schema_specialist` (Database & Schema Specialist)**: Grounded in the explicit 21-column schema, executes verified read-only SQL SELECT queries with `PRAGMA query_only = ON` isolation.
4. **`store_policy_specialist` (Store Policy Specialist)**: Answers return conditions (7-day replacement), 1-year brand warranty, express shipping, and EMI financing plans.
5. **`shopping_advisor_specialist` (Shopping Advisor & Bag Specialist)**: Delivers lifestyle recommendations (gaming, students, vlogging, night photography) and handles instant "Add to Shopping Bag" cart mutations with discount code `NIKEAIR`.

---

<a id="learn"></a>
## 3. Engineering Learnings & Architectural Principles

1. **The Latency Cliff**: Pure LLMs take 1,500ms to 3,000ms per turn. Under retail traffic, every 100ms delay degrades cart conversions by 7%. Our hybrid architecture delivers a **2.58 ms P95 response**.
2. **Slot-Aware Semantic Caching**: Generic vector caches suffer false-positive hits (e.g. matching "phone under 15k" with "phone under 50k"). Our slot-aware cache extracts brand and price ceilings, guaranteeing that cached answers never violate commercial constraints.
3. **Physical Driver Isolation (`PRAGMA query_only = ON`)**: String sanitization alone is insufficient against SQL injection. By locking the SQLite C driver into read-only mode, any mutation attempt physically errors out at the database engine level.
4. **Zero-Reasoning Leakage**: Free open-weights models frequently emit chain-of-thought chatter. Strict `<AnswerToUser>` tagging and multi-pass scrubbers eliminate draft reasoning before content reaches the user.
5. **Google ADK Model Agnosticism**: Through ADK's `LLMRegistry`, the system operates seamlessly across Gemini 2.5 Flash, OpenRouter free models, and a high-speed deterministic virtual provider for offline CI/CD unit testing.

---

<a id="boost"></a>
## 4. Performance Boost & Optimization Benchmarks (/boost)

Synthetic benchmark runs over **500 multi-parameter e-commerce queries** show substantial throughput and cost boosts:

- **Latency Boost**: Median (P50) latency boosted from `21.20 ms` to **`1.42 ms`** (14.9x virtual / 901x live speedup). P95 latency boosted to **`2.58 ms`** (8.8x virtual / 589x live speedup).
- **Token Reduction Boost**: 135,400 tokens reduced to **1,291 tokens** (**`99.14% token savings`**).
- **Zero-Token Query Rate**: **`98.60%`** of all retail user requests are resolved without consuming any LLM tokens.
- **Search Engine Throughput Boost**: **`6,745 QPS`** at **`0.166 ms P95 latency`**.
- **Financial Boost**: Monthly spend for 1,000,000 active users drops from **`$1,692.80 to $16.20`**, yielding **`$1,676.60 / month in pure cloud savings`** (**`₹1,740,311 / year`**).

---

<a id="system-architecture"></a>
## System Architecture: The 5-Tier Hybrid Engine

```
                             [ Incoming User Query ]
                                        │
                                        ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │ TIER 0: Enterprise Security Guardrails & PII Sanitizer                 │
    │  - Prompt Injection, Jailbreak, & DAN Mode Blocker                     │
    │  - PII Detection & Anonymization (Emails, Credit Cards, Phones, IDs)   │
    │  - Length Capping & DoS Buffer Overflow Protection                     │
    └───────────────────────────────────┬────────────────────────────────────┘
                                        │ (Sanitized Safe Query)
                                        ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │ TIER 1: Exact Hash Query Cache (L1 Memory LRU + L2 Redis)              │
    │  - SHA-256 Normalized Query Hash Lookup                                │
    │  - Latency: < 0.1 ms | Token Consumption: 0 (100% Token Savings)       │
    └───────────────────────────────────┬────────────────────────────────────┘
                                        │ (Cache Miss)
                                        ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │ TIER 2: Slot-Aware Semantic Cache (TF-IDF Cosine Similarity >= 0.62)   │
    │  - Catches paraphrased / duplicate intents ("under 20k" vs "20000")    │
    │  - Strict slot verification guarantees brand & price constraints match │
    │  - Latency: 1 - 3 ms | Token Consumption: 0 (100% Token Savings)       │
    └───────────────────────────────────┬────────────────────────────────────┘
                                        │ (Cache Miss)
                                        ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │ TIER 3: Typical Deterministic Bot (Rules, Slot Parser & SQL Engine)    │
    │  - Deterministic Intent Routing (Comparison, Policy FAQs, Search)      │
    │  - Resolves fuzzy budgets ("mid budget" -> ₹15k–₹30k) & Hinglish       │
    │  - SQLite B-Tree Composite Indexes & FTS5 BM25 Engine                  │
    │  - Latency: 2 - 5 ms | Token Consumption: 0 (100% Token Savings)       │
    └───────────────────────────────────┬────────────────────────────────────┘
                                        │ (Subjective / Advisory / Open-Ended)
                                        ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │ TIER 4: LLM-Augmented RAG Engine (OpenRouter API Free Models)          │
    │  - Models: google/gemma, liquid/lfm, nvidia/nemotron with auto-failover│
    │  - Grounded RAG Catalog Context Injection (Guaranteed Product Cards)   │
    │  - Leaky-Bucket Rate Limiter (20 RPM / 1000 RPD) + Virtual Backpressure│
    │  - Attaches structured product cards with "Add to Cart" readiness      │
    │  - Automatically populates Tier 1 & Tier 2 caches for future queries   │
    └────────────────────────────────────────────────────────────────────────┘
```

---

<a id="chatbot-resolutions"></a>
## Deep Chatbot Issue Resolutions & Research

We resolved the critical e-commerce failure modes common in modern conversational AI bots:

| Issue / Failure Mode | Before (Broken Behavior) | After (Shopcart Resolution) | Routing Tier |
|---|---|---|---|
| **1. "Who are you / who built you"** | Generic fallback or hallucinated identity. | Introduces itself as **Shopcart AI**, specialized smartphone advisor built for fast, grounded shopping. | `TIER_3_TYPICAL_BOT` (0 tokens) |
| **2. "Best camera phone under mid budget"** | Output plain text with no product cards. | Resolves *"mid budget"* to ₹15,000–₹30,000, ranks by `camera DESC`, and returns **Motorola Edge 30 Ultra (200MP)** and **Realme 11 Pro+ (200MP)** with interactive cards and **Add to Cart** buttons. | `TIER_3_TYPICAL_BOT` (0 tokens) |
| **3. "Sabse sasta aur mahanga phone dikhao"** | Replied in plain text without running queries. | Handled as `EXTREMES_COMPARISON`: queries both minimum (₹2,500) and maximum (₹200,999) phones, returning both with side-by-side cards. | `TIER_3_TYPICAL_BOT` (0 tokens) |
| **4. "Best camera phone under 10k rupees"** | Returned *"Sorry, no smartphones matched"* or listed obsolete 10-year-old Zopo/Panasonic 5MP phones. | Currency regex normalizes `"10k"` / `"10000"`, relevance ranking prioritizes modern phones with $\ge 4\text{GB RAM}$ and high MP cameras, returning **Realme C53 (108MP)** with product cards. | `TIER_3_TYPICAL_BOT` (0 tokens) |
| **5. Products missing in Tier 4 LLM stage** | LLM answered in text with no way to add to cart. | Structured catalog parsing extracts recommended products and attaches interactive product cards with **Add to Cart** buttons directly in chat. | `TIER_4_LLM_RAG` (Attached Cards) |
| **6. "benefits of moto edgee 50" (LLM reasoning leaks)** | Emitted internal chain-of-thought, draft notes (*"The user previously asked... Let me craft:"*), and unrequired chatter. | Strict `<AnswerToUser>...</AnswerToUser>` prompt framing and aggressive output parser scrubs all internal reasoning. Phonetic typo (`"edgee"` $\rightarrow$ `"edge"`) resolves to **Motorola Edge 50 Fusion (₹20,299)** with concise benefits & Add to Cart. | `TIER_3_TYPICAL_BOT` / `TIER_4_LLM_RAG` |
| **7. "compare cheapest and priminum phones"** | Failed with *"Could not find exact matches for both 'cheapest' and 'priminum phones'"*. | Resolves typo (`"priminum"` $\rightarrow$ `"premium"`), maps concepts to catalog extremes, and outputs side-by-side comparison table between lowest price phone (₹2,500) and ultra-flagship (₹200,999) with active cart cards. | `TIER_3_TYPICAL_BOT` (0 tokens) |
| **8. "weather i can give back if is used the phone for more than 7 days"** | Misclassified typo `"weather"` as general out-of-domain trivia. | Prioritizes policy FAQs, resolves `"weather"` $\rightarrow$ `"whether"`, and provides exact clarification on the 7-day return expiration and continued coverage under the **1-Year Manufacturer Warranty**. | `TIER_3_TYPICAL_BOT` (0 tokens) |
| **9. Database Schema & Datatypes Grounding** | LLM previously lacked explicit database column definitions and types. | Implemented dedicated `schema_context.py` and `db_agent.py` injecting all 21 columns, exact datatypes, bounds, units, and constraints directly into the prompt. | `TIER_3` & `TIER_4` Grounding |
| **10. Zero Reasoning Leakage Enforcement** | Free models like liquid/nemotron outputting CoT monologue when hitting limits. | Enforced strict `<AnswerToUser>` boundaries, multi-pass reasoning scrubber, and intelligent fallback to grounded virtual response generator if a model emits only chain-of-thought. | Zero Reasoning Guarantee |

---

<a id="database-schema"></a>
## 🗄️ Database Schema, Datatypes & Secure Database Agent

The platform operates over a high-performance relational database with composite B-Tree indexes and an FTS5 full-text search index. The complete schema and datatypes context is explicitly exposed to the agent and LLM pipeline (`src/data/schema_context.py` and `src/chatbot/db_agent.py`):

<a id="smartphones-schema"></a>
### 1. Smartphones Table Schema (`smartphones`)

| Column Name | SQLite Data Type | Python Type | Unit / Range | Constraints & Nullability | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `int` | `1 .. N` | `PRIMARY KEY AUTOINCREMENT` | Unique product identifier |
| `brand` | `TEXT` | `str` | Canonical lowercase | `NOT NULL`, Indexed | Manufacturer brand (`samsung`, `apple`, `oneplus`, etc.) |
| `name` | `TEXT` | `str` | String title | `NOT NULL`, Indexed | Full commercial product name |
| `price` | `INTEGER` | `int` | `₹2,500 .. ₹200,999` | `NOT NULL`, Indexed | Retail price in Indian Rupees (INR ₹) |
| `ram` | `REAL` | `float` | `0.25 .. 24.0 GB` | `NOT NULL`, Indexed | Random Access Memory in Gigabytes |
| `os` | `TEXT` | `str` | `android` / `ios` | `NOT NULL` | Mobile operating system |
| `storage` | `REAL` | `float` | `4.0 .. 1024.0 GB` | `NOT NULL` | Internal storage / ROM capacity |
| `battery_cap` | `INTEGER` | `int` | `1100 .. 7000 mAh` | `NOT NULL`, Indexed | Battery capacity in milliampere-hours |
| `has_fast_charging` | `TEXT` | `str` | `'Yes'` / `'No'` | `NOT NULL` | Quick charging support |
| `has_fingerprints` | `TEXT` | `str` | `'Yes'` / `'No'` | `NOT NULL` | Biometric fingerprint scanner |
| `has_nfc` | `TEXT` | `str` | `'Yes'` / `'No'` | `NOT NULL` | NFC contactless support |
| `has_5g` | `TEXT` | `str` | `'Yes'` / `'No'` | `NOT NULL`, Indexed | 5G cellular network support |
| `processor_brand` | `TEXT` | `str` | SoC name | `NOT NULL` | Processor manufacturer (`snapdragon`, `bionic`, etc.) |
| `num_core` | `REAL` | `float` | `4.0 .. 10.0 cores` | `NOT NULL` | CPU processor core count |
| `primary_rear_camera` | `REAL` | `float` | `0.3 .. 200.0 MP` | `NOT NULL` | Main rear camera sensor resolution |
| `num_rear_cameras` | `INTEGER` | `int` | `1 .. 4` | `NOT NULL` | Total count of rear camera lenses |
| `primary_front_camera`| `REAL` | `float` | `5.0 .. 50.0 MP` | `NOT NULL` | Front selfie camera resolution |
| `num_front_camera` | `INTEGER` | `int` | `1 .. 2` | `NOT NULL` | Total count of selfie camera lenses |
| `display_size` | `REAL` | `float` | `4.0 .. 6.9 inches` | `NOT NULL` | Screen diagonal size in inches |
| `refresh_rate` | `REAL` | `float` | `60.0 .. 165.0 Hz` | `NOT NULL` | Screen refresh rate in Hertz |
| `display_type` | `TEXT` | `str` | Category string | `NOT NULL` | Panel tech (`amoled display`, `oled display`, etc.) |

<a id="fts-schema"></a>
### 2. Full-Text Search Virtual Table (`smartphones_fts`)
- **Engine**: SQLite FTS5 with BM25 relevance scoring.
- **Indexed Columns**: `brand`, `name`, `processor_brand`, `display_type`.
- **Row Mapping**: `content='smartphones', content_rowid='id'`.

<a id="database-agent"></a>
### 3. Secure Database Agent (`DatabaseAgent`)
- **Query Validation**: Strict AST and token analysis guarantees ONLY `SELECT` statements are executed, strictly targeting `smartphones` or `smartphones_fts`.
- **Driver-Level Isolation**: All agent queries execute on connections with `PRAGMA query_only = ON`. Mutations physically fail at the C-driver level.
- **Bound Limit Enforcement**: All queries are capped at a maximum of 50 rows (default 3 to 10).
- **Dynamic Action Chips**: Generates context-aware follow-up suggestion pills (`action_chips`) returned with every response.
- **Zero Reasoning Leakage**: Outputs strictly enclosed within `<AnswerToUser>...</AnswerToUser>` tags with all internal thoughts scrubbed.

---

<a id="enhanced-features"></a>
## ⚡ Enhanced Chat Features (Modern E-Commerce Experience)

1. **Dynamic Quick-Action Chips**:
   - The chatbot generates context-aware follow-up suggestion chips (e.g., *"Under ₹20,000"*, *"5G Smartphones Only"*, *"Compare with Galaxy S25"*, *"Add to Shopping Bag"*).
   - Tapping any chip immediately triggers the inquiry with smooth, zero-latency feedback.
2. **Interactive Side-by-Side Comparison Charts**:
   - When 2 or more devices are returned or compared, an interactive Recharts comparison bar chart dynamically renders directly inside the chat window.
3. **Spec Badges & One-Click Cart Addition**:
   - Product cards inside chat include visual spec badges (`5G`, `Fast Charge`, screen size, AMOLED display) with direct "Add to Cart" and "Specs" buttons.
4. **Intelligent Filter Relaxation**:
   - When strict multi-parameter filters yield zero matches, the agent automatically identifies overly narrow constraints, suggests relaxation options, and displays the closest matching devices.

---

<a id="enterprise-security"></a>
## 🛡️ Enterprise Security & Database Hardening (Anti-Hacking & 100k+ Scale)

To protect the platform against adversarial attacks, prompt hacking, and database corruption, Shopcart implements an in-depth defensive security perimeter:

```
[ User Request ]
       │
       ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Layer 1: Token & Regex AST SQL Injection Defense                       │
│ - Blocks Destructive Tokens: DROP, DELETE, TRUNCATE, ALTER, INSERT     │
│ - Blocks Stacked Commands: Semicolon injection (; DROP TABLE...)       │
│ - Blocks Filter Evasion: Comments (-- , /* */, ;--)                    │
│ - Blocks Exfiltration: UNION SELECT, UNION ALL SELECT                  │
│ - Blocks Boolean Tautologies: ' OR 1=1, ' OR '1'='1, ' OR ''='         │
│ - Blocks Schema Recon: sqlite_master, sqlite_schema, information_schema│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Passed)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Layer 2: Prompt Injection & System Extraction Defense                  │
│ - Blocks "system prompt", "hidden instructions", "database password"   │
│ - Blocks "DAN mode", "jailbreak", "unrestricted mode" attempts         │
│ - PII Redaction: Anonymizes Emails, Phone Numbers, Credit Cards, IDs   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Passed)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Layer 3: Driver-Level Physical Read-Only Enforcement                   │
│ - SQLite PRAGMA query_only = ON set on all query & search connections  │
│ - Mutation queries (DROP/DELETE/UPDATE) physically fail at C/driver    │
│   level with OperationalError: attempt to write a readonly database    │
│ - Isolated, parameterized write connection only for admin endpoints    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Execution)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Layer 4: Output Guardrail & Sensitive Information Scrubber             │
│ - Strips all internal reasoning via <AnswerToUser> delimiters          │
│ - Redacts leaked API keys (Bearer tokens, sk- keys)                    │
│ - Redacts server paths (/home/ubml/..., C:\...) and DB connection strings│
│ - Blocks hallucinated or impossible smartphone prices (<₹1k or >₹300k) │
└────────────────────────────────────────────────────────────────────────┘
```

---

<a id="benchmark-reports"></a>
## Visual Benchmark Reports & Architecture Charts

All figures are automatically generated from real benchmark runs in `reports/figures/`:

| P95 Latency Comparison | 1M User Token & Cost Savings |
| :---: | :---: |
| ![Latency Comparison](reports/figures/latency_p95_comparison.png) | ![Token & Cost Savings](reports/figures/token_and_cost_savings.png) |

| Traffic Routing by Tier | Cache Efficiency Curve |
| :---: | :---: |
| ![Traffic Routing](reports/figures/query_routing_breakdown.png) | ![Cache Curve](reports/figures/cache_efficiency_curve.png) |

| Price Distribution | Brand Market Share |
| :---: | :---: |
| ![Price Distribution](reports/figures/price_distribution.png) | ![Brand Share](reports/figures/brand_market_share.png) |

---

<a id="repository-structure"></a>
## 📁 Repository Structure

```
├── data/
│   ├── smartphones_data.csv.csv    # Raw dataset (3,260 smartphone models)
│   └── smartphones.db              # SQLite relational + FTS5 database
├── docs/                           # Architecture & Engineering Specifications
│   ├── GOAL.md                     # Project Goal & Strategic Vision (/goal)
│   ├── TEAMWORK.md                 # Google ADK Multi-Agent Teamwork (/teamwork)
│   ├── LEARN.md                    # Core Learnings & Architectural Principles (/learn)
│   ├── BOOST.md                    # Performance Boost & Benchmark Metrics (/boost)
│   └── DEPLOYMENT.md               # Production deployment runbook
├── frontend/                       # React 18 + Vite + Tailwind CSS SPA
│   ├── src/
│   │   ├── components/
│   │   │   ├── Admin/              # AdminPanel with telemetry & cache eviction
│   │   │   ├── Auth/               # Dedicated AuthPage & AuthModal
│   │   │   ├── Benchmarks/         # BenchmarksPage with Recharts & 500-input pool
│   │   │   ├── Cart/               # CartDrawer with promo codes & checkout
│   │   │   ├── Catalog/            # ProductGrid, filter pills, ProductDetailModal
│   │   │   ├── Chatbot/            # ChatWidget, context memory, ChatSpecChart
│   │   │   ├── Home/               # ArchitectureSimulator with animated pipeline
│   │   │   ├── Layout/             # Navbar with pill dropdowns, Hero banner
│   │   │   └── PhoneRenderer.jsx   # Procedural SVG phone generator (12+ brands)
│   │   ├── context/                # AuthContext (5-chart limit) & CartContext
│   │   ├── App.jsx                 # Multi-page routing & layout
│   │   └── index.css               # Tailwind & custom CSS variables
│   ├── package.json
│   ├── tailwind.config.js
│   └── vercel.json                 # Vercel SPA rewrites configuration
├── reports/
│   ├── analysis_report.json        # Dataset statistical analysis report
│   ├── benchmark_results.json      # P50/P90/P95/P99 latency & token benchmarks
│   └── figures/                    # 8 publication-ready charts (PNG)
├── src/
│   ├── config.py                   # Pydantic Settings & environment config
│   ├── agents/                     # Google ADK (Agent Development Kit) Multi-Agent System
│   │   ├── orchestrator.py         # Supervisor Agent coordinating sub-agents & ADK Runner
│   │   ├── catalog_agent.py        # Catalog Search & Comparison Specialist
│   │   ├── db_agent.py             # Schema & Read-Only SQL Database Specialist
│   │   ├── policy_agent.py         # Store Policy & Customer Care Specialist
│   │   ├── advisor_agent.py        # Lifestyle Recommendations & Cart Specialist
│   │   ├── tools.py                # Typed Google ADK tool definitions
│   │   ├── models.py               # Custom ADK LLM provider (Gemini / OpenRouter / Virtual)
│   │   └── guardrails.py           # ADK Agent lifecycle security callbacks
│   ├── data/                       # Ingestion, cleaning, SQLite indexes & schema context
│   ├── search/                     # Two-tier L1/L2 Redis caching & search engine
│   ├── guardrails/                 # Security, injection defense, PII masking, rate limiting
│   ├── chatbot/                    # Typical bot, semantic cache, LLM bot, hybrid orchestrator
│   └── api/                        # FastAPI app, schemas, ADK endpoints, timing middleware
├── supabase/
│   └── schema.sql                  # PostgreSQL schema with Row-Level Security
├── tests/                          # 88 automated pytest test cases (including test_adk_agents.py)
├── .github/workflows/
│   └── ci.yml                      # GitHub Actions CI pipeline (backend + frontend)                
├── Dockerfile                      # Production container definition
├── render.yaml                     # Render web service blueprint
├── vercel.json                     # Root Vercel configuration
└── pytest.ini                      # Pytest configuration
```

---

<a id="quick-start"></a>
## 🚀 Quick Start (Local Development)

<a id="prerequisites"></a>
### 1. Prerequisites
- Python 3.12+ (or `uv`)
- Node.js 18+ and `npm`

<a id="backend-setup"></a>
### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/your-username/Optimized-chat-bot.git
cd Optimized-chat-bot

# Set up Python virtual environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start FastAPI backend
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be live at: `http://localhost:8000/docs`  
Documentation routes: `/goal`, `/teamwork`, `/learn`, `/boost`

<a id="frontend-setup"></a>
### 3. Frontend Setup
```bash
# In a new terminal
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser. All `/api` requests will proxy automatically to the FastAPI backend.

---

<a id="running-tests"></a>
## 🧪 Running Automated Tests

Run the full automated test suite (88 test cases covering Google ADK multi-agent teamwork, tool execution, multi-turn pronoun resolution, natural language cart mutations, search, Hinglish queries, fuzzy mid-budgets, dual extremes, context memory, guardrails, schema validation, safe SQL execution, and API endpoints):
```bash
pytest -v tests/
```
Output:
```
============================== 88 passed in 1.47s ==============================
```

To run frontend build checks:
```bash
cd frontend && npm run build
```

<a id="license"></a>
## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
