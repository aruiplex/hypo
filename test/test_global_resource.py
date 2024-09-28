from hypo import runs, run, Run, run_git_status
from hypo.resources import GlobalResources
import time



@run(max_workers=2)
def run_list():
    lock = GlobalResources()
    return [
        [
            Run(
                command=f"echo computing 1 && sleep 5",
                name="compute",
                cwd=".",
                output=".",
                resource=lock
            ),
            Run(
                command=f"echo computing 2 && sleep 5",
                name="compute",
                cwd=".",
                output=".",
                resource=lock
            ),
        ],
        Run(
            command=f"echo aaa3  && sleep 5",
            name="compute",
            cwd=".",
            output=".",
            resource=lock
        ),
        Run(
            command=f"echo aaa4 && sleep 5",
            name="compute",
            cwd=".",
            output=".",
            resource=lock
        ),
        Run(
            command=f"echo aaa4 && sleep 5",
            name="compute",
            cwd=".",
            output=".",
            resource=lock
        ),
    ]
    
run_list()
