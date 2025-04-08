import subprocess

try:
    result = subprocess.run(
        "ls -l",  # replace with your command
        ,  # capture stdout and stderr
        text=True,  # decode bytes to str
        check=True,  # raise CalledProcessError if return code != 0
        shell=True,
    )
    print("Command succeeded.")
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)

except subprocess.CalledProcessError as e:
    print("Command failed with a non-zero exit status.")
    print("Return Code:", e.returncode)
    print("Command:", e.cmd)
    print("STDOUT:\n", e.stdout)
    print("STDERR:\n", e.stderr)

except FileNotFoundError as e:
    print("Command not found. Check the command name or path.")
    print("Error:", e)

except Exception as e:
    print("An unexpected error occurred.")
    print("Error:", e)
