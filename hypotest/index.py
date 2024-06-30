from hypo import runs, run, Run, run_git_status
import time


@runs(max_workers=5)
def trials():
    for i in range(5):
        yield Run(
            command=f"echo computing {i} && sleep 5",
            name="compute",
            cwd=".",
            output=".",
        )
        print(f"yield {i}")
        time.sleep(2)  # preparing


@run(max_workers=2)
def run_list():
    return [
        [
            Run(
                command=f"echo computing && sleep 5",
                name="compute",
                cwd=".",
                output=".",
            ),
            Run(
                command=f"echo computing && sleep 5",
                name="compute",
                cwd=".",
                output=".",
            ),
        ],
        Run(
            command=f"echo aaa && sleep 5",
            name="compute",
            cwd=".",
            output=".",
        ),
        Run(
            command=f"echo aaa && sleep 5",
            name="compute",
            cwd=".",
            output=".",
        ),
    ]
