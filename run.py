"""Jobwright entry point.

Usage:
  python run.py            # one full run (creates Gmail drafts)
  python run.py --dry-run  # discover + rank + print, no drafts written
  python run.py --serve    # run continuously every 3 hours (APScheduler)
"""
import argparse
import logging

from jobwright.pipeline import run

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")


def main():
    p = argparse.ArgumentParser(description="Jobwright — autonomous job-search agent")
    p.add_argument("--dry-run", action="store_true", help="don't create Gmail drafts")
    p.add_argument("--serve", action="store_true", help="run every 3 hours")
    args = p.parse_args()

    if args.serve:
        from apscheduler.schedulers.blocking import BlockingScheduler
        sched = BlockingScheduler()
        sched.add_job(lambda: run(dry_run=args.dry_run), "interval", hours=3, next_run_time=None)
        logging.info("Jobwright scheduled every 3 hours. Ctrl-C to stop.")
        run(dry_run=args.dry_run)  # run once immediately
        sched.start()
    else:
        run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
