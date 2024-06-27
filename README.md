# Hypo, cli tool to run os command.

Run you complex prompt experiments in System level invoke.

```python
# In epoch/trial.py
from hypo import run, runs, Run


@run
def trial():
    return [Run(name="a", cwd=".", output=".", command="echo this_is_a_very_complex_prompt_to_start_your_experiment_in_bash")]

@runs
def trials():
    time.sleep(10) # computing
    yield Run(name="a", cwd=".", output=".", command="echo this_is_a_very_complex_prompt_to_start_your_experiment_in_bash_1")
    time.sleep(10) # computing
    yield Run(name="b", cwd=".", output=".", command="echo this_is_a_very_complex_prompt_to_start_your_experiment_in_bash_2")

```


Then you can start your task parallel.

```bash 
hypo epoch trial # to start method trial

hypo epoch trials # to start method trials, if your task producer need to prepare in another processing.
```

After run all experiments, you could check the task summary in the output folder named `summary.json`.

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

## Extension

You can use some pre-defined Run. for example, the `git version` using `run_git_status`.

```python
from hypo import runs, Run, run_git_status

@runs
def method():
    return [
        Run(name="a", cwd=".", output="./a", command="echo $cwd aaaaaa"),
        run_git_status(),
    ]

```


