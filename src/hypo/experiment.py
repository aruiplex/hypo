from __future__ import annotations
from dataclasses import dataclass, asdict, field
import os
import shutil
from multiprocessing import Process, Queue, queues
from concurrent.futures import as_completed, ThreadPoolExecutor
import subprocess
import sys
import threading
import time
from pathlib import Path
import GPUtil
import json
import datetime
import csv
import pprint
from loguru import logger
from .resources import CUDAs, Resources, GlobalResources
from time import strftime, localtime
from alive_progress import alive_bar


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
    resource: Resources = None  # do not represent in asdict
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
        # logger.exception(e)

    def __str__(self):
        return pprint.pformat(self.asdict())

    def asdict(self):
        d = {
            "name": self.name,
            "command": self.command,
            "cwd": str(self.cwd),
            "output": str(self.output),
            "datetime": self.datetime,
        }
        if hasattr(self, "time_consume"):
            d["time_consume"] = self.time_consume
        if hasattr(self, "finish_at"):
            d["finish_at"] = self.finish_at
        if hasattr(self, "start_at"):
            d["start_at"] = self.start_at
        if hasattr(self, "resource"):
            d["resource"] = self.resource.__class__.__name__
        if hasattr(self, "input"):
            d["input"] = str(self.input)

        return d


class Experiment:
    """
    Is a container for Run class. Main function is "launch" the Runs.
    """

    summary_lock = threading.Lock()  # Use this to synchronize summary file writing

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
    runs: list

    def __init__(self, args: list = None) -> None:

        if args is not None:
            self.args = args

        if hasattr(self, "env"):
            os.environ.update(self.env)

    def worker(self):
        """
        A threading safe method. The launch is not threading safe.
        Continuously fetches and processes tasks from the list.
        """

        while True:
            running_candidate: Run = self.runs.pop(0)
            if running_candidate is None:  # Check for the end signal
                self.runs.append(None)  # Propagate the end signal for other workers
                break

            if isinstance(running_candidate, list):
                s = "\n".join([pprint.pformat(x.asdict()) for x in running_candidate])
                logger.info(f"[LAUNCH Sequence]\n{s}")

            elif isinstance(running_candidate, Run):
                logger.info(f"[LAUNCH]\n{pprint.pformat(running_candidate.asdict())}")
                running_candidate = [running_candidate]
            else:
                raise Exception("Running should be list[Run] or Run.")

            # <resource-control> use env to control the using resouces & control the processing
            env = os.environ.copy()
            cuda_cuda_visible_devices = self.cudas.acquire()
            env["CUDA_VISIBLE_DEVICES"] = str(cuda_cuda_visible_devices)

            # <launch>
            for running in running_candidate:
                running: Run
                start_time = time.time()
                running.start_at = datetime.datetime.now().strftime(
                    "%Y-%m-%d__%H-%M-%S"
                )
                if running.resource is not None:
                    running.resource.acquire()
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
                    print(e)

                if running.resource is not None:
                    running.resource.release()
                # </launch>

                t = time.time() - start_time
                logger.info(f"[FINISH {t:.1f}s] {running.command}")
                running.time_consume = str(datetime.timedelta(seconds=t))
                running.finish_at = datetime.datetime.now().strftime(
                    "%Y-%m-%d__%H-%M-%S"
                )
                self.cudas.release(cuda_cuda_visible_devices)

            # Update the summary after every task
            self.update_summary(running_candidate)
            self.bar()

    def update_summary(self, run):
        """Updates the summary file with the latest run information."""
        summary_path = "summary.json"

        # Make sure to synchronize access to the summary file across threads
        with self.summary_lock:
            summary = []
            if os.path.exists(summary_path):
                with open(summary_path, "r") as f:
                    summary = json.load(f)

            # Check if `run` is a list of runs or a single run instance
            if isinstance(run, list):
                sub_summary = []
                for single_run in run:
                    sub_summary.append(single_run.asdict())
                summary.append(sub_summary)

            else:
                # If it's a single Run object
                summary.append(run.asdict())

            # Write the updated summary back to the file
            with open(summary_path, "w") as f:
                json.dump(summary, f, indent=4, ensure_ascii=False)
                logger.info(
                    f"Updated the summary with {run if isinstance(run, list) else run.name} into {summary_path}"
                )

    def launch(self, runs: list, cuda_visible_devices=None, max_workers=None):
        """
        Run the experiments in parallel using processes.
        """
        self.runs = runs

        assert isinstance(self.runs, list), "The runs should be list."

        if max_workers is None:
            max_workers = len(GPUtil.getGPUs())

        logger.info(f"max workers: {max_workers}")
        start = time.time()
        self.cudas = CUDAs(cuda_visible_devices=cuda_visible_devices, max_workers=max_workers)
        num = len(self.runs) - 1
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            with alive_bar(num, title="Hypo Progress") as bar:
                self.bar = bar
                futures = [executor.submit(self.worker) for _ in range(max_workers)]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.exception(e)

        time_consume = f"{time.time() - start:.2f}"
        logger.info(f"All tasks done, used {time_consume}s")



def run(cuda_visible_devices=None, max_workers=None):
    """Decorator. Run the experiments list"""

    def inner(func):
        exp = Experiment()

        def wrapper(*args, **kwargs):
            result: list = func(*args, **kwargs)
            assert isinstance(result, list), "The result should be list."
            # assert all([isinstance(x, Run) for x in result]), "The result should be list of Run."
            result.append(None)
            exp.launch(result, cuda_visible_devices=cuda_visible_devices, max_workers=max_workers)
            return result

        return wrapper

    return inner


def runs(cuda_visible_devices=None, max_workers=None):
    """Decorator. Run the experiments yield"""

    def inner(func):
        def wrapper(*args, **kwargs):
            exp = Experiment()
            q = []  # maybe a queue

            # run in seperate process
            def processing():
                gen = func(*args, **kwargs)  # Get the generator
                for value in gen:
                    # logger.info(f"Put into queue: {value}")
                    q.append(value)  # Put each value into the queue

                # need None to say stop
                q.append(None)

            process = Process(target=processing)
            process.start()
            # process.join()  # donot join here, no need for waiting for the processing() done

            # Process all items in the queue
            exp.launch(q, cuda_visible_devices=cuda_visible_devices, max_workers=max_workers)

        return wrapper

    return inner
