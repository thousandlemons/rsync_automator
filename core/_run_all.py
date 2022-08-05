import os

from _config import Paths
from _rsync import RsyncTask

RUN_ALL_SCRIPT_FILE = os.path.join(Paths.OUTPUT_DIR, 'run_all.sh')
RUN_ALL_SCRIPT_LINE_TEMPLATE = 'bash {absolute_path}'


class RunAllScriptGenerator(object):
    lines = None

    def __init__(self):
        self.lines = []

    def add_script(self, task: RsyncTask):
        self.lines.append(RUN_ALL_SCRIPT_LINE_TEMPLATE.format(
                absolute_path=task.get_absolute_generated_script_path()))

    def write_to_file(self):
        with open(RUN_ALL_SCRIPT_FILE, 'w+') as file:
            file.write('\n'.join(self.lines))
            file.write('\n')
