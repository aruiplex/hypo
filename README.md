# Hypo is a CLI tool to run OS commands concurrently.

You are tired of running commands one by one manually when the previous command is finished. A lot of commands (maybe experiments) need to run in your project (maybe paper). You want to run them concurrently, without leaving the Free time. 

Hypo is a tool to help you run commands concurrently.  You can use Hypo to run them concurrently without wasting time. It run your complex commands in System-level. You can easily manipulate the commands in the way you like.

You can install it by `pip install hypo-run`.

```python
# In the file folder_a/index.py
from hypo import run, Run

@run()
def trial():
    return [Run(command="echo this_is_a_very_complex_prompt_to_start_your_experiment_in_bash", name="indicate your task")]

@run(max_workers=10) # run 10 tasks concurrently
def trial():
    return [Run(command="echo this_is_a_very_complex_prompt_to_start_your_experiment_in_bash", name="indicate your task")]

```

Then you can start your task parallel.

```bash
# hypo <dir_name> <function_name>

hypo folder_a index.trial # to start method trial. Create tasks, then run.

# if the file named `index.py`, then you can ignore the file name.
hypo folder_a trial # to start method trial. Create tasks, then run.

# if you are already in the folder_a
hypo trial # to start method trial. Create tasks, then run.

```

Or, directly call the function you need.

```python
trial()
# Then, `python folder_a/index.py`
```

After running all experiments, you can check the task summary in the output folder named `summary.json`.

```json
[
  {
    "name": "A very complex task",
    "command": "echo this_is_a_very_complex_prompt_to_start_your_experiment_in_bash",
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
```

## CUDA CMD Friendly

You may have a lot of cuda tasks to do. Run them concurrently! Assume your GPU could have 2 task to run at the same time. `cuda_visible_devices` will be the environment variable `CUDA_VISIBLE_DEVICES` pass to processing.

```python
from hypo import run, Run, run_git_checkout
from itertools import product

@run(cuda_visible_devices={0, 1, 6, 7}, max_workers=8) 
def compare():
    cmd_templete = "python main.py --category {clz}"

    clzs = [
        "table",
        "sofa",
        "bench",
        "watercraft",
        # ... a really long list
    ]
    tasks = []
    for clz, method in product(clzs, ["my_method", "baseline", "sota"]): # the method you want to compare
        task = [
            run_git_checkout(method),  # branch name. git checkout to the branch you want to run. 
            Run(
                command=cmd_templete.format(clz=clz),
                name=f"{method}-{clz}",
                cwd="/path/to/your/project",
                out="/summary.json/will/be/generated/here",
            ),
        ]
        tasks.append(task)
    return tasks

```

You do not need to worry about the `run_git_checkout`. Python will load all file in memory at the start. Your code will not go wrong.


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
            run_git_checkout("a6bb0c3"), # commit name
            Run(command="python main.py", output=".", cwd=".", name="run1"),
        ],
        [
            run_git_checkout("main"), # branch name
            Run(command="python main.py", output=".", cwd=".", name="run2"),
        ],
    ]

```
