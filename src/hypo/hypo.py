import os
import sys

# if do not have this line, Python will not add the cwd path to the Python Path.
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

def main():
    import importlib
    from .experiment import Experiment
    from .cfg import args, subargs

    load_module = args.expName + "index"
    # load the index file of the theorm. The index file contains the Experiment class.
    module = importlib.import_module(load_module)
    # experiment: BaseExperiment = module.Experiment(subargs)

    # the method function in the Experiment class.
    method = getattr(module, args.method)

    method(*subargs)


if __name__ == "__main__":
    main()
