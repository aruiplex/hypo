from hypo import runs, Run


@runs
def method():
    return [Run(name="a", cwd=".", output="./a", command="echo $cwd aaaaaa")]

@runs
def methods():
    yield Run(name="a", cwd=".", output="./a", command="echo $cwd aaaaaa")
    yield Run(name="b", cwd=".", output="./b", command="echo $cwd bbbbb")
