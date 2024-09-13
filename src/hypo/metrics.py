import pandas as pd
import os
from filelock import Timeout, FileLock


def save(parameters, metrics, output):
    lock_file = output + ".lock"

    # Combine the parameters and metrics into a single dictionary
    new_data = {**parameters, **metrics}

    # Create a DataFrame from the new data
    new_df = pd.DataFrame([new_data])

    with FileLock(lock_file, timeout=60):
        # If the file exists, read it, otherwise create an empty DataFrame
        if os.path.isfile(output):
            existing_df = pd.read_csv(output)
        else:
            existing_df = pd.DataFrame()

        # Concatenate the new DataFrame with the existing one
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)

        # Save the DataFrame to a CSV file
        updated_df.to_csv(output, index=False)


if __name__ == "__main__":
    # Example usage
    parameters = {"param1": 1, "param2": 2, "param3": 3}
    metrics = {"accuracy": 0.95, "loss": 0.05, "precision": 0.9}
    save(parameters, metrics, "experiment_results.csv")

    parameters = {"param1": 13, "param2": 62, "param4": 55}
    metrics = {"accuracy": 0.95, "loss": 0.05, "precision": 0.9, "abc": 111}
    save(parameters, metrics, "experiment_results.csv")
