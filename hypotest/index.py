from hypo import runs, Run, run_git_status


@runs
def method():
    return [
        Run(name="a", cwd=".", output="./a", command="echo $cwd aaaaaa"),
        run_git_status(),
    ]


@runs
def methods():
    yield Run(name="a", cwd=".", output="./a", command="echo $cwd aaaaaa")
    yield Run(name="b", cwd=".", output="./b", command="echo $cwd bbbbb")
