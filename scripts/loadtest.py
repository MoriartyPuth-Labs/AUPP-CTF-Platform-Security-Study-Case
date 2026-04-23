#!/usr/bin/env python3
"""
loadtest.py — Web Application Load & Stress Testing Tool
─────────────────────────────────────────────────────────
Author : Eav Puthcambo (userCambo) — AUPP Cybersecurity Programme
Purpose: Authorized load testing for web applications. Measures response
         time degradation as concurrent users increase, identifies breaking
         points, and quantifies p50/p95/max latency under realistic load.

⚠  WARNING: Only run this against systems you are explicitly authorized to test.
   Unauthorized use constitutes a criminal offence in most jurisdictions.

Scenarios
─────────────────────────────────────────────────────────────────────────────
  T-01  Baseline          — single user, measure raw response times
  T-02  Unauthenticated   — ramp from 1 to 50 concurrent unauthenticated users
  T-03  Login Stress      — concurrent login attempts (rate limit detection)
  T-04  Auth Browse       — authenticated users hitting challenge/API endpoints
  T-05  Scoreboard Poll   — concurrent scoreboard polling
  T-06  Peak Load         — ramp to 100 concurrent users (breaking point)

Usage
─────
  # Unauthenticated tests only:
  python3 loadtest.py

  # With authentication (for T-04 / T-05):
  python3 loadtest.py --user <username> --pass <password>

  # Or set environment variables:
  export LT_USER=myuser LT_PASS=mypassword
  python3 loadtest.py

Results are printed to terminal. JSON summary saved to loadtest_results.json.
"""

import requests
import threading
import time
import statistics
import json
import sys
import argparse
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from collections import defaultdict

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── Configuration — edit these before running ─────────────────────────────────
TARGET     = 'https://example.com'   # ← set your authorized target here
VERIFY_SSL = False                    # set True if target has a valid cert
TIMEOUT    = 10                       # seconds per request

# ── Credentials — set via CLI args or environment variables ───────────────────
# DO NOT hardcode real credentials here — use --user / --pass or env vars
TEST_USER  = os.environ.get('LT_USER', '')
TEST_PASS  = os.environ.get('LT_PASS', '')

# ── Results storage ───────────────────────────────────────────────────────────
results      = defaultdict(list)
results_lock = threading.Lock()


def record(scenario, status_code, elapsed_ms, error=None):
    with results_lock:
        results[scenario].append((status_code, elapsed_ms, error))


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def get(url, session=None, timeout=None):
    s  = session or requests.Session()
    t0 = time.time()
    try:
        r = s.get(url, verify=VERIFY_SSL, timeout=timeout or TIMEOUT,
                  allow_redirects=True)
        return r.status_code, int((time.time() - t0) * 1000), None
    except requests.exceptions.Timeout:
        return 0, int((time.time() - t0) * 1000), 'TIMEOUT'
    except Exception as e:
        return 0, int((time.time() - t0) * 1000), str(e)[:80]


def post(url, data, session=None, timeout=None):
    s  = session or requests.Session()
    t0 = time.time()
    try:
        r = s.post(url, data=data, verify=VERIFY_SSL,
                   timeout=timeout or TIMEOUT, allow_redirects=True)
        return r.status_code, int((time.time() - t0) * 1000), None
    except requests.exceptions.Timeout:
        return 0, int((time.time() - t0) * 1000), 'TIMEOUT'
    except Exception as e:
        return 0, int((time.time() - t0) * 1000), str(e)[:80]


def get_nonce(session):
    """Extract CSRF nonce from the login page (CTFd-style)."""
    import re
    try:
        r = session.get(f'{TARGET}/login', verify=VERIFY_SSL, timeout=TIMEOUT)
        m = re.search(r"'nonce':\s*'([a-f0-9]+)'", r.text)
        if not m:
            m = re.search(r'name="nonce"[^>]+value="([a-f0-9]+)"', r.text)
        return m.group(1) if m else None
    except Exception:
        return None


def login(username, password):
    """Authenticate and return a session, or None on failure."""
    s     = requests.Session()
    nonce = get_nonce(s)
    if not nonce:
        return None
    sc, _, _ = post(f'{TARGET}/login',
                    {'name': username, 'password': password, 'nonce': nonce},
                    session=s)
    return s if sc in (200, 302) else None


# ── Worker functions ──────────────────────────────────────────────────────────

def worker_pages(scenario, endpoints, session=None):
    """One virtual user requesting each endpoint in the list once."""
    s = session or requests.Session()
    for url in endpoints:
        sc, ms, err = get(url, session=s)
        record(scenario, sc, ms, err)


def worker_login(scenario, username, password):
    """One login attempt — used to stress the login endpoint."""
    s     = requests.Session()
    nonce = get_nonce(s)
    if not nonce:
        record(scenario, 0, 0, 'no_nonce')
        return
    sc, ms, err = post(f'{TARGET}/login',
                       {'name': username, 'password': password, 'nonce': nonce},
                       session=s)
    record(scenario, sc, ms, err)


def worker_scoreboard(scenario, session=None):
    """One scoreboard API poll."""
    s = session or requests.Session()
    sc, ms, err = get(f'{TARGET}/api/v1/scoreboard', session=s)
    record(scenario, sc, ms, err)


# ── Runner helpers ─────────────────────────────────────────────────────────────

def run_concurrent(scenario, workers, fn, *args):
    """Submit `workers` concurrent tasks and wait for all to complete."""
    print(f'  >> {scenario} — {workers} concurrent', flush=True)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(fn, scenario, *args) for _ in range(workers)]
        for f in futures:
            try:
                f.result()
            except Exception:
                pass


# ── Stats ──────────────────────────────────────────────────────────────────────

def calc_stats(scenario):
    data = results.get(scenario, [])
    if not data:
        return None
    times = [d[1] for d in data]
    codes = [d[0] for d in data]
    errs  = [d[2] for d in data if d[2]]
    ok    = sum(1 for c in codes if 200 <= c < 400)
    fail  = len(codes) - ok
    return {
        'requests':    len(data),
        'ok':          ok,
        'fail':        fail,
        'error_rate':  f'{fail / len(data) * 100:.1f}%',
        'avg_ms':      int(statistics.mean(times)),
        'min_ms':      min(times),
        'max_ms':      max(times),
        'p50_ms':      int(statistics.median(times)),
        'p95_ms':      sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else times[0],
        'status_codes': dict(sorted({str(c): codes.count(c) for c in set(codes)}.items())),
        'errors':      list(set(errs))[:5],
    }


def print_stats(scenario):
    s = calc_stats(scenario)
    if not s:
        print(f'  [STATS] {scenario} — no data')
        return
    print(f'\n  [STATS] {scenario}')
    print(f'     Requests : {s["requests"]}')
    print(f'     OK/Fail  : {s["ok"]} / {s["fail"]}  ({s["error_rate"]} error rate)')
    print(f'     Avg/p50  : {s["avg_ms"]}ms / {s["p50_ms"]}ms')
    print(f'     p95/Max  : {s["p95_ms"]}ms / {s["max_ms"]}ms')
    print(f'     Status   : {s["status_codes"]}')
    if s['errors']:
        print(f'     Errors   : {s["errors"]}')


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    # CLI argument parsing
    parser = argparse.ArgumentParser(
        description='Web application load testing tool (authorized use only)')
    parser.add_argument('--user', default=TEST_USER,
                        help='Username for authenticated tests')
    parser.add_argument('--pass', dest='password', default=TEST_PASS,
                        help='Password for authenticated tests')
    parser.add_argument('--target', default=TARGET,
                        help='Target base URL (e.g. https://example.com)')
    args = parser.parse_args()

    global TARGET
    TARGET = args.target.rstrip('/')

    if TARGET == 'https://example.com':
        print('[!] TARGET is still the placeholder. Set --target or edit the script.')
        sys.exit(1)

    print('=' * 60)
    print('  Web Application Load Test')
    print(f'  Target : {TARGET}')
    print(f'  Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 60)

    public_pages = [
        f'{TARGET}/',
        f'{TARGET}/scoreboard',
        f'{TARGET}/challenges',
        f'{TARGET}/login',
    ]

    # ── T-01 Single-user baseline ──────────────────────────────────
    print('\n[T-01] Baseline — single user response times')
    for label, url in [
        ('homepage',   f'{TARGET}/'),
        ('login_page', f'{TARGET}/login'),
        ('challenges', f'{TARGET}/challenges'),
        ('scoreboard', f'{TARGET}/scoreboard'),
        ('api_challs', f'{TARGET}/api/v1/challenges'),
    ]:
        sc, ms, err = get(url)
        icon = 'OK' if 200 <= sc < 400 else 'FAIL'
        print(f'  {icon}  {label:<14} {sc}  {ms}ms  {err or ""}')

    # ── T-02 Unauthenticated ramp ──────────────────────────────────
    print('\n[T-02] Unauthenticated page load ramp (1 → 50 users)')
    for w in [1, 5, 10, 25, 50]:
        run_concurrent('T02_unauth', w, worker_pages, public_pages)
        time.sleep(2)
    print_stats('T02_unauth')

    # ── T-03 Login stress ──────────────────────────────────────────
    if args.user and args.password:
        print('\n[T-03] Login endpoint stress (10 → 30 concurrent logins)')
        for w in [10, 20, 30]:
            run_concurrent('T03_login', w, worker_login, args.user, args.password)
            time.sleep(3)
        print_stats('T03_login')
    else:
        print('\n[T-03] Skipped — no credentials provided (use --user / --pass)')

    # ── T-04 Authenticated browsing ────────────────────────────────
    auth = None
    if args.user and args.password:
        print('\n[T-04] Authenticated challenge API browsing (10 → 40 users)')
        auth = login(args.user, args.password)
        if auth:
            print('  Auth session established')
            auth_pages = [
                f'{TARGET}/api/v1/challenges',
                f'{TARGET}/challenges',
            ]
            for w in [10, 20, 40]:
                run_concurrent('T04_auth_browse', w, worker_pages, auth_pages, auth)
                time.sleep(3)
            print_stats('T04_auth_browse')
        else:
            print('  Could not authenticate — check credentials')
    else:
        print('\n[T-04] Skipped — no credentials provided')

    # ── T-05 Scoreboard polling ────────────────────────────────────
    print('\n[T-05] Scoreboard polling (20 → 60 concurrent users)')
    for w in [20, 40, 60]:
        run_concurrent('T05_scoreboard', w, worker_scoreboard, auth)
        time.sleep(3)
    print_stats('T05_scoreboard')

    # ── T-06 Peak load ─────────────────────────────────────────────
    print('\n[T-06] Peak load — ramp to 100 concurrent users')
    for w in [60, 80, 100]:
        run_concurrent('T06_peak', w, worker_pages,
                       [f'{TARGET}/', f'{TARGET}/scoreboard'])
        s = calc_stats('T06_peak')
        if s:
            print(f'  @ {w:3d} users — avg: {s["avg_ms"]}ms  '
                  f'p95: {s["p95_ms"]}ms  err: {s["error_rate"]}  '
                  f'codes: {s["status_codes"]}')
        time.sleep(5)
    print_stats('T06_peak')

    # ── Summary ────────────────────────────────────────────────────
    print('\n' + '=' * 60)
    print('  SUMMARY')
    print('=' * 60)
    all_stats = {}
    for scenario in ['T02_unauth', 'T03_login', 'T04_auth_browse',
                     'T05_scoreboard', 'T06_peak']:
        s = calc_stats(scenario)
        if s:
            all_stats[scenario] = s
            print(f'  {scenario:<22} {s["requests"]:>4} reqs  '
                  f'avg {s["avg_ms"]:>5}ms  p95 {s["p95_ms"]:>5}ms  '
                  f'err {s["error_rate"]:>6}')

    # Save JSON results
    try:
        with open('loadtest_results.json', 'w') as f:
            json.dump({
                'target':    TARGET,
                'timestamp': datetime.now().isoformat(),
                'results':   all_stats,
            }, f, indent=2)
        print('\n  Results saved to loadtest_results.json')
    except Exception as e:
        print(f'\n  [!] Could not save JSON: {e}')

    print(f'  Finished: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 60)


if __name__ == '__main__':
    main()
