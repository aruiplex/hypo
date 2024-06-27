from __future__ import annotations
from dataclasses import dataclass, asdict, field
import os
import shutil
from multiprocessing import Queue, queues, Process
import subprocess
import sys
import time
from pathlib import Path
import GPUtil
import json
import datetime
import csv
import pprint
from loguru import logger
from .cudas import CUDAs
from time import strftime, localtime


def givename(value=None):
    # zoneinfo is a standard library since python 3.9
    if value is None or value in ["", " "]:
        try:
            from zoneinfo import ZoneInfo

            return datetime.datetime.now(tz=ZoneInfo("Asia/Shanghai")).strftime(
                "%Y-%m-%d__%H-%M-%S"
            )
        except ImportError:
            return datetime.datetime.now().strftime("%Y-%m-%d__%H-%M-%S")


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
        self.output = Path(self.output).absolute()
        self.cwd = Path(self.cwd).absolute()
        self.output.mkdir(parents=True, exist_ok=True)

    def _except_call_back(self, e: Exception):
        logger.exception(f"Error\n{self.command}")
        logger.exception(e)
        shutil.rmtree(self.output)
        logger.exception(f"removed the output: {self.output}")

    def __str__(self):
        return pprint.pformat(asdict(self))


class Experiment:
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
    # a pipe to recv task from producer and consume the task to worker.
    runs: Queue
    # a record, to create summary.
    done_tasks = []

    def __init__(self, args: list = None) -> None:

        if args is not None:
            self.args = args

        if hasattr(self, "env"):
            os.environ.update(self.env)

    def worker(self):
        """
        A threading safe method. The launch is not threading safe.
        Continuously fetches and processes tasks from the queue.
        """

        while True:
            try:
                running: Run = self.runs.get()
                if running is None:  # Check for the end signal
                    self.runs.put(None)  # Propagate the end signal for other workers
                    break

                logger.info(f"LAUNCH:\n{pprint.pformat(asdict(running))}")
                start_time = time.time()

                # <resource-control> use env to control the using resouces & control the processing
                # each thread should have its own copy of local variables.
                env = os.environ.copy()
                cuda_visible_devices = self.cudas.pop()
                env["CUDA_VISIBLE_DEVICES"] = str(cuda_visible_devices)
                # </resource-control>

                # <launch>
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

                # </launch>

                # time consuming
                t = time.time() - start_time
                logger.info(f"{running.command} finished in {t:.1f}s.")
                running.time_consume = str(datetime.timedelta(seconds=t))
                running.finish_at = datetime.datetime.now().strftime(
                    "%Y-%m-%d__%H-%M-%S"
                )

                # return the resources
                self.cudas.add(cuda_visible_devices)
                # keep task to recording summary in experiment
                self.done_tasks.append(running)

            except Exception as e:
                logger.exception(f"Thread encountered an error: {e}")

    def launch(self, runs, max_workers=None):
        """
        Run the experiments in parallel using processes.
        """
        if isinstance(runs, queues.Queue):
            self.runs = runs
        else:
            self.runs = Queue()
            [self.runs.put(i) for i in runs]

        # control stop
        self.runs.put(None)

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

        time_consume = f"{time.time() - start:.2f}"
        logger.info(f"All tasks done, used {time_consume}s")

        # <summary>
        summary_path = "summary.json"
        summary = []

        # runs post-processing
        for idx, run in enumerate(self.done_tasks):
            run.output = str(run.output)
            run.cwd = str(run.cwd)
            run = asdict(run)
            self.done_tasks[idx] = run

        if os.path.exists(summary_path):
            summary = json.load(open(summary_path))

        summary.append(
            {
                "Experiment": givename(),
                "time": time_consume,
                "start": time.strftime("%Y-%m-%d__%H-%M-%S", time.localtime(start)),
                "end": time.strftime("%Y-%m-%d__%H-%M-%S", time.localtime(time.time())),
                "runs": self.done_tasks,
            }
        )

        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)
            logger.info(f"Save the summary into {summary_path}")


def _csv_summary(summary):
    summary_path = "summary.csv"
    c = csv.DictWriter(open(summary_path, "w"), summary.keys())
    c.writeheader()
    c.writerow(summary)


def run(max_workers=2):
    """Decorator. Run the experiments list"""

    def inner(func):
        exp = Experiment()

        def wrapper():
            result = func()
            exp.launch(result, max_workers)
            return result

        return wrapper

    return inner


def runs(max_workers=2):
    """Decorator. Run the experiments yield"""

    def inner(func):
        def wrapper():
            exp = Experiment()
            q = Queue()

            # run in seperate process
            def processing():
                gen = func()  # Get the generator
                for value in gen:
                    q.put(value)  # Put each value into the queue

            process = Process(target=processing)
            process.start()
            # need None to say stop
            q.put(None)
            process.join()

            exp.launch(q, max_workers)  # Process all items in the queue

        return wrapper

    return inner
