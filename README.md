# Hypo is a CLI tool to run OS commands.

Run your complex prompt experiments in System-level invoke.

```python
# In the file epoch/index.py
from hypo import run, runs, Run


# Use one thread to collect the tasks.
@run
def trial():
    return [Run(command="echo this_is_a_very_complex_prompt_to_start_your_experiment_in_bash", name="echo", cwd=".", output=".")]


# Use multiprocessing to collect the tasks.
@runs
def trials():
    for i in range(10):
        yield Run(command="sleep 5", name="compute", cwd=".", output=".")
        time.sleep(2) # preparing
```

Then you can start your task parallel.

```bash
# hypo <dir_name> <function_name>

hypo epoch trial # to start method trial. Create tasks, then run.

hypo epoch trials # to start method trials. Parallel create tasks and run.
```

Or, directly call the function you need.

```python
trial()
```

After running all experiments, you can check the task summary in the output folder named `summary.json`.

```json
[
  {
    "Experiment": "2024-06-27__18-35-21",
    "time": "0.00",
    "start": "2024-06-27__18-35-21",
    "end": "2024-06-27__18-35-21",
    "runs": [
      {
        "name": "a",
        "command": "echo $cwd aaaaaa",
        "cwd": "/data/Hypothesis/hypo",
        "output": "/data/Hypothesis/hypo/a",
        "datetime": "2024-06-27__18-35-21"
      },
      {
        "name": "Git Version",
        "command": "git rev-parse HEAD",
        "cwd": "/data/Hypothesis/hypo",
        "output": "/data/Hypothesis/hypo",
        "datetime": "2024-06-27__18-35-21"
      }
    ]
  }
]
```

## Extensions

You can use some pre-defined Run. for example, the `git version` using `run_git_status`.

```python
from hypo import runs, Run, run_git_status

@runs
def method():
    return [
        Run(name="a", cwd=".", output="./a", command="echo $cwd"),
        run_git_status(),
    ]

```

If you want to run the command in a specific git version, you can use `run_git_checkout`.

```python

from hypo import run, run_git_checkout, Run


@run()
def test_run_git_checkout():
    return [
        [
            run_git_checkout("a6bb0c3"),
            Run(command="python main.py", output=".", cwd=".", name="run1"),
        ],
        [
            run_git_checkout("483a83f"),
            Run(command="python main.py", output=".", cwd=".", name="run2"),
        ],
    ]

```
