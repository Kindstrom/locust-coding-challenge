import time
import psutil
import requests
import argparse
from datetime import datetime, timedelta
import signal
import sys


class CPUMonitor:
    def __init__(
        self, api_url, username, password, measure_interval, display_interval, threshold
    ):
        self.api_url = api_url
        self.auth = (username, password)
        self.measure_interval = measure_interval
        self.display_interval = display_interval
        self.threshold = threshold
        self.test_run_id = None
        self.running = False
        self.start_time = None
        self.time_above_threshold = timedelta()
        self.last_display_time = None
        self.measurements = []

    def start_test_run(self):
        response = requests.post(
            f"{self.api_url}start-test-run",
            params={"name": f"CPU Monitor Run {datetime.now()}"},
            auth=(self.auth),
        )
        response.raise_for_status()
        self.test_run_id = response.json()["test_run_id"]
        print(f"Started new test run with ID: {self.test_run_id}")

    def record_cpu_usage(self):
        cpu_percent = psutil.cpu_percent(interval=1)
        measurement_timestamp = datetime.now()
        self.measurements.append((measurement_timestamp, cpu_percent))

        response = requests.post(
            f"{self.api_url}/record-cpu-usage/{self.test_run_id}",
            json={
                "cpu_percent": cpu_percent,
                "timestamp": measurement_timestamp.isoformat(),
            },
            auth=self.auth,
        )
        response.raise_for_status()

        if cpu_percent > self.threshold:
            print(
                f"\033[91mALERT: CPU usage {cpu_percent}% exceeds threshold of {self.threshold}%\033[0m"
            )
            self.time_above_threshold += timedelta(seconds=self.measure_interval)

        current_time = datetime.now()
        if (
            self.last_display_time is None
            or (current_time - self.last_display_time).total_seconds()
            >= self.display_interval
        ):
            print(f"Current CPU usage: {cpu_percent}% at {current_time}")
            self.last_display_time = current_time

    def run(self):
        self.start_test_run()
        self.running = True
        self.start_time = datetime.now()
        print("CPU monitoring started. Press Ctrl+C to stop.")
        print(f"Threshold set to {self.threshold}%")
        print(
            f"Measuring every {self.measure_interval} seconds, displaying every {self.display_interval} seconds"
        )

        while self.running:
            self.record_cpu_usage()
            time.sleep(self.measure_interval)

    def stop(self):
        self.running = False
        self.show_report()

    def show_report(self):
        total_time = datetime.now() - self.start_time

        print("\n--- CPU Usage Monitor Report ---")
        print(f"Total test duration: {total_time}")
        print(
            f"Time CPU usage was above {self.threshold}% threshold: {self.time_above_threshold}"
        )

        if self.measurements:
            avg_cpu = sum(m[1] for m in self.measurements) / len(self.measurements)
            max_cpu = max(m[1] for m in self.measurements)
            print(f"Average CPU usage: {avg_cpu:.2f}%")
            print(f"Maximum CPU usage: {max_cpu:.2f}%")

        print("--- End of Report ---")


def main():
    parser = argparse.ArgumentParser(
        description="Monitor CPU usage and send data to API"
    )
    # parser.add_argument("--api_url", required=True, help="Base URL of the API")
    parser.add_argument("--username", required=True, help="API username")
    parser.add_argument("--password", required=True, help="API password")
    parser.add_argument(
        "--measure_interval",
        type=int,
        default=5,
        help="Measurement interval in seconds",
    )
    parser.add_argument(
        "--display_interval", type=int, default=10, help="Display interval in seconds"
    )
    parser.add_argument(
        "--threshold", type=float, default=5, help="CPU usage threshold percentage"
    )

    args = parser.parse_args()

    monitor = CPUMonitor(
        api_url="http://localhost:8000/",
        username=args.username,
        password=args.password,
        measure_interval=args.measure_interval,
        display_interval=args.display_interval,
        threshold=args.threshold,
    )

    def _signal_handler(signum, frame):
        monitor.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    monitor.run()


if __name__ == "__main__":
    main()
