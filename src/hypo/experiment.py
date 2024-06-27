from __future__ import annotations
from dataclasses import dataclass, asdict, field
import os
import shutil

import subprocess
import sys
import time
from pathlib import Path
import GPUtil
import json
import datetime
from axiom.utils import name as givename
import csv
import pprint
from loguru import logger
from .cudas import CUDAs


@dataclass
class Run:
    """A run is a task to run in a process. A run is a command to run.

    Args:
        name (str): The name of the run. nessary
        command (str): The command to run. nessary
        input (str): The input path. not nessary
        output (str): The output path. nessary

    If you want to init this dataclass for dict, use:

    Run(**run_dict) -> dataclass

    asdict(Run(**aa)) -> dict
    """

    name: str
    command: str
    # The cwd for process start.
    cwd: str = "."
    output: str = "."
    datetime: str = givename()  # as start time

    def __post_init__(self):
        self.output = Path(self.output)
        self.output.mkdir(parents=True, exist_ok=True)

    def _except_call_back(self, e: Exception):
        logger.exception(f"Error\n{self.command}")
        logger.exception(e)
        shutil.rmtree(self.output)
        logger.exception(f"removed the output: {self.output}")

    def __str__(self):
        s = pprint.pformat(asdict(self))
        return s


class BaseExperiment:
    """
    Is a container for Run class. Main function is "launch" the Runs.
    """
    

    # ===== For human =====
    # The title for this experiment.
    experiment: str
    # The preparation for this experiment.
    preparation: list

    # ===== For program =====
    # The env need to be registered.
    env: dict
    # The parameters settings for this experiment.
    parameters: any
    # The argparse args for experiments.
    args: list = None

    def __init__(self, queue, args: list = None) -> None:

        self.runs = queue
        if args is not None:
            self.args = args

        if hasattr(self, "env"):
            os.environ.update(self.env)

    def worker(self):
        """
        A threading safe method. The launch is not threading safe.
        Continuously fetches and processes tasks from the queue.
        """
        in_json = True
        in_csv = False

        while True:
            try:
                running: Run = self.runs.get()
                if running is None:  # Check for the end signal
                    self.runs.put(None)  # Propagate the end signal for other workers
                    break

                logger.info(f"LAUNCH:\n{pprint.pformat(asdict(running))}")
                start_time = time.time()

                # each thread should have its own copy of local variables.
                env = os.environ.copy()
                print("a")
                cuda_visible_devices = self.cudas.pop()
                env["CUDA_VISIBLE_DEVICES"] = str(cuda_visible_devices)

                # === launch ===

                try:
                    subprocess.run(
                        running.command,
                        shell=True,
                        cwd=running.cwd,
                        env=env if env is not None else os.environ,
                        stdout=sys.stdout,
                        stderr=sys.stderr,
                        check=True,
                    )
                except Exception as e:
                    running._except_call_back(e)

                # === /launch ===

                t = time.time() - start_time
                logger.info(f"{running.command} finished in {t:.1f}s.")
                running.time_consume = str(datetime.timedelta(seconds=t))

                summary = asdict(running)

                if in_json:
                    summary_path = running.output / "summary.json"
                elif in_csv:
                    summary_path = running.output / "summary.csv"

                with open(summary_path, "a") as f:
                    if in_csv:
                        c = csv.DictWriter(f, summary.keys())
                        c.writeheader()
                        c.writerow(summary)
                    if in_json:
                        json.dump(
                            summary,
                            f,
                            indent=4,
                            ensure_ascii=False,
                            default=json_encoder,
                        )

                    logger.info(f"Save the summary into {summary_path}")

                self.cudas.add(cuda_visible_devices)
            except Exception as e:
                logger.exception(f"Thread encountered an error: {e}")

    def launch(self, max_workers=None):
        """
        Run the experiments in parallel using processes.
        """
        from concurrent.futures import as_completed, ThreadPoolExecutor

        if max_workers is None:
            max_workers = len(GPUtil.getGPUs())

        logger.info(f"max workers: {max_workers}")
        start = time.time()
        self.cudas = CUDAs(max_workers=max_workers)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create a list of futures from the process executor
            futures = [executor.submit(self.worker) for _ in range(max_workers)]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.exception(f"Error processing a future: {e}")

        time_consume = time.time() - start
        logger.info(f"All tasks done, used {time_consume:.2f}s")
