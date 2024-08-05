from hypo.resources import GlobalResources
from .experiment import Run

git_lock = GlobalResources()


def run_git_status():
    return Run(name="Git Version", command="git rev-parse HEAD", output=".", cwd=".")


def run_git_checkout(version: str):
    return Run(
        name="Git Checkout",
        command=f"sleep 5 && git checkout {version} && sleep 5",
        output=".",
        cwd=".",
        resource=git_lock,
    )
