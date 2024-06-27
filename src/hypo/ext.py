from .experiment import Run


def run_git_status():
    return Run(name="Git Version", command="git rev-parse HEAD", output=".", cwd=".")
