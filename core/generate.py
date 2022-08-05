import json
import shutil
import os

from _rsync import RsyncProject
from _run_all import RunAllScriptGenerator
from _crontab import CrontabGenerator
from _config import Paths


def main():
    # Remove all previously generated files
    if os.path.exists(Paths.OUTPUT_DIR):
        shutil.rmtree(Paths.OUTPUT_DIR)
    os.makedirs(Paths.OUTPUT_DIR)

    # Read config
    with open(Paths.CONFIG_FILE, 'r') as file:
        config = json.load(file)

    # Initialize workers
    rsync_project = RsyncProject(config)
    run_all_script_generator = RunAllScriptGenerator()
    crontab_generator = CrontabGenerator(config)

    # Write generated scripts to files
    for task in rsync_project.tasks:
        task.write_to_file()
        run_all_script_generator.add_script(task)
        crontab_generator.add_script(task)
    run_all_script_generator.write_to_file()
    crontab_generator.write_to_file()


if __name__ == '__main__':
    main()
