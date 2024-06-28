from hypo import runs, run, Run, run_git_status
import time


@runs(max_workers=5)
def trials():
    for i in range(5):
        yield Run(command=f"echo computing {i} && sleep 5", name="compute", cwd=".", output=".")
        print(f"yield {i}")
        time.sleep(2)  # preparing
