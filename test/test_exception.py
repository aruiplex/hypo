from hypo import runs, run, Run, run_git_status
from hypo.resources import GlobalResources


@run(max_workers=2)
def run_list():
    lock = GlobalResources()
    return [
        Run(
            command=f"exit 1",
            name="compute",
            cwd=".",
            output=".",
            resource=lock,
        ),
        Run(
            command=f"echo computing 2 && exit 1",
            name="compute",
            cwd=".",
            output=".",
            resource=lock,
        ),
    ]
