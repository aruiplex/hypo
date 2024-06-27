from multiprocessing import Process, Queue
import time

from hypo.experiment import *

def task_producer(queue):
    """
    Produces tasks and puts them into the queue.
    """
    for i in range(6):  # Example: produce 5 tasks
        run = Run(
            name=f"Task {i}",
            command="python task_stub.py",
            cwd="/data/Hypothesis/hypo/tests/",
            output=f"/data/Hypothesis/hypo/tests/results/task_{i}"
        )
        queue.put(run)
        time.sleep(2)  # Simulate time delay between tasks
    queue.put(None)  # Signal that production is done

if __name__ == "__main__":
    queue = Queue()  # Create a managed Queue
    experiment = BaseExperiment(queue=queue)
    producer = Process(target=task_producer, args=(queue,))
    producer.start()

    experiment.launch(max_workers=5)  # Start the experiment which processes tasks

    producer.join()  # Wait for the producer to finish
