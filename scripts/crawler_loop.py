#!/usr/bin/env python3
"""
Continuous crawler loop — runs multisite_crawler.py repeatedly.
Sleeps 30s between runs, writes each run's summary to a log file.
"""
import subprocess, time, sys, os, signal, datetime

LOOP_DELAY = 60  # seconds between runs
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crawler_loop.log')
CRAWLER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'multisite_crawler.py')

stopping = False

def sig_handler(sig, frame):
    global stopping
    stopping = True
    print(f"[{datetime.datetime.now():%H:%M:%S}] 🛑 Stopping crawler loop...")
    sys.stdout.flush()
signal.signal(signal.SIGTERM, sig_handler)
signal.signal(signal.SIGINT, sig_handler)

def run():
    print(f"[{datetime.datetime.now():%H:%M:%S}] Starting crawler...", flush=True)
    t0 = time.time()
    try:
        r = subprocess.run(
            ['python3.10', CRAWLER],
            capture_output=True, text=True, timeout=600
        )
        elapsed = time.time() - t0
        summary = f"[{datetime.datetime.now():%H:%M:%S}] Done in {elapsed:.0f}s — RC={r.returncode}"
        if r.stdout:
            for line in r.stdout.strip().split('\n')[-5:]:
                if line.strip():
                    summary += f" | {line.strip()}"
        print(summary, flush=True)
        with open(LOG_FILE, 'a') as f:
            f.write(summary + '\n')
    except subprocess.TimeoutExpired:
        print(f"[{datetime.datetime.now():%H:%M:%S}] ⏰ Crawler timed out (>600s), restarting...", flush=True)
    except Exception as e:
        print(f"[{datetime.datetime.now():%H:%M:%S}] ❌ Error: {e}", flush=True)

def main():
    print(f"🚀 Crawler loop started (delay={LOOP_DELAY}s, log={LOG_FILE})", flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(f"\n{'='*50}\n[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] LOOP START\n")
    
    while not stopping:
        run()
        if not stopping:
            time.sleep(LOOP_DELAY)
    
    print("✅ Crawler loop stopped gracefully.")

if __name__ == '__main__':
    main()
