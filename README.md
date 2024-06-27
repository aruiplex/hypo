# Hypo, cli tool to run os command.

Run you complex prompt experiments in System level invoke.

```python
# In epoch/trial.py
from hypo import run, runs, Run


@run
def trial():
    return [Run(command="echo this_is_a_very_complex_prompt_to_start_your_experiment_in_bash", name="echo", cwd=".", output=".")]

@runs
def trials():
    for i in range(10):
        yield Run(command="sleep 5", name="compute", cwd=".", output=".")
        time.sleep(2) # preparing 
```


Then you can start your task parallel.

```bash 
hypo epoch trial # to start method trial. Create tasks, then run.

hypo epoch trials # to start method trials. Parallel create tasks and run.
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


