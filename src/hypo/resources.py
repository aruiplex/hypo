import GPUtil
import threading
from loguru import logger


class Resources:
    def __len__(self):
        pass

    def release(self, idx: int):
        pass

    def acquire(self) -> int:
        pass


class GlobalResources(Resources):
    # only one task could get the resource at the same time. Eg, git

    def __init__(self, name="global-lock-233") -> None:
        self.lock = threading.Lock()

    def __len__(self):
        if self.lock.locked():
            return 0
        else:
            return 1

    def acquire(self) -> int:
        return self.lock.acquire()

    def release(self, idx: int = 0):
        self.lock.release()


# class CUDAs:
#     """Dispatch tasks to different CUDA devices with load balancing.
#     1 task per cuda device by default.
#     """

#     def __init__(self, max_workers: int = 1) -> None:
#         self.lock = threading.Lock()
#         self.cuda_devices = {
#             x: 0 for x in range(len(GPUtil.getGPUs()))
#         }  # Track tasks per CUDA device

#         self.max_workers = max_workers

#         logger.info(f"Available GPUs: {list(self.cuda_devices.keys())}")

#     def __len__(self):
#         return sum(self.cuda_devices.values())

#     def pop(self) -> int:
#         with self.lock:
#             # Find the CUDA device with the least number of tasks, respecting the max_workers limit
#             available_devices = {
#                 k: v for k, v in self.cuda_devices.items() if v < self.max_workers
#             }
#             if not available_devices:
#                 raise Exception("No available CUDA devices under max_workers limit.")
#             cuda_id = min(available_devices, key=available_devices.get)
#             # Increment task count for the selected device
#             self.cuda_devices[cuda_id] += 1
#             return cuda_id

#     def add(self, idx: int):
#         with self.lock:
#             if self.cuda_devices[idx] > 0:
#                 self.cuda_devices[idx] -= 1  # Decrement task count for the device
#             else:
#                 logger.warning(
#                     f"Trying to remove a task from GPU {idx} which has no tasks."
#                 )


class CUDAs(Resources):
    """Dispatch the tasks to the different cudas."""

    def __init__(self, cuda_visible_devices=None, max_workers=1) -> None:
        self.lock = threading.Lock()
        if cuda_visible_devices is None:
            cudas = set(GPUtil.getAvailable(limit=8))
        else:
            assert isinstance(
                cuda_visible_devices, set
            ), "The visible devices should be set."
            cudas = cuda_visible_devices

        logger.info(f"Visible GPUs: {cuda_visible_devices}")
        self.cudas = [list(cudas)[i % len(cudas)] for i in range(max_workers)]

        if max_workers > len(cudas):
            logger.warning(
                f"Max workers is greater than the available GPUs. More than one task will be assigned to some GPUs."
            )
        logger.info(f"Available GPUs: {self.cudas}")

    def __len__(self):
        return len(self.cudas)

    def acquire(self) -> int:
        with self.lock:
            return self.cudas.pop()

    def release(self, idx):
        with self.lock:
            if isinstance(self.cudas, set):
                self.cudas.add(idx)
            elif isinstance(self.cudas, list):
                self.cudas.append(idx)
            else:
                raise Exception("The cudas should be set or list.")