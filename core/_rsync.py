import re
import os
import unicodedata

from _config import Paths, ConfigKeys, TaskKeys

# Values
_DIRECTION_PUSH = 'push'
_DIRECTION_PULL = 'pull'
_VALID_DIRECTIONS = {_DIRECTION_PUSH, _DIRECTION_PULL}
_DEFAULT_MAX_LOG_FILES = 10
_PYTHON_BOOLEAN_TO_BASH_MAP = {
    True: 'true',
    False: 'false'
}

# Templates
_RSYNC_SCRIPT_TEMPLATE_FILE = os.path.join(Paths.TEMPLATE_DIR, 'rsync.sh.template')
_RSYNC_SSH_ARG_TEMPLATE = '-e "ssh -p {port}"'
_RSYNC_EXCLUDE_ARG_TEMPLATE = '--exclude "{pattern}"'
_RSYNC_ARG_LINE_TEMPLATE = '    {arg} \\'
_RSYNC_SCRIPT_NAME_TEMPLATE = 'rsync_{name}.sh'


class RsyncProject(object):
    direction: str = None
    source_root: str = None
    dest_root: str = None
    ssh_port: int = None
    log_dir_name: str = None,
    max_log_files: int = None
    global_excludes: list[str] = None
    global_args: list[str] = None
    tasks: list['RsyncTask'] = None

    is_logging_enabled: bool = None
    is_ssh_enabled: bool = None

    def __init__(self, config: dict):
        RsyncProject._validate_config_dict(config)
        self.direction = config[ConfigKeys.DIRECTION]
        self.source_root = config[ConfigKeys.SOURCE_ROOT]
        self.dest_root = config[ConfigKeys.DEST_ROOT]

        if ConfigKeys.SSH_PORT in config:
            self.is_ssh_enabled = True
            self.ssh_port = config[ConfigKeys.SSH_PORT]
        else:
            self.is_ssh_enabled = False

        if ConfigKeys.LOG_DIR_NAME in config:
            self.is_logging_enabled = True
        else:
            self.is_logging_enabled = False
        self.log_dir_name = config.get(ConfigKeys.LOG_DIR_NAME, '')
        self.max_log_files = config.get(ConfigKeys.MAX_LOG_FILES, _DEFAULT_MAX_LOG_FILES)

        self.global_excludes = config.get(ConfigKeys.GLOBAL_EXCLUDE, [])
        self.global_args = config.get(ConfigKeys.GLOBAL_ARGS, [])

        self.tasks = []
        for task_dict in config[ConfigKeys.TASKS]:
            self.tasks.append(RsyncTask(self, task_dict))

    @staticmethod
    def _validate_config_dict(config: dict) -> None:
        for key in config:
            if key not in ConfigKeys.ALL_CONFIG_KEYS:
                raise ValueError('Unrecognized project config key: {}'.format(key))

        for key in ConfigKeys.REQUIRED_CONFIG_KEYS:
            if key not in config:
                raise ValueError('Required key not present in project config: {}'.format(key))

        direction = config[ConfigKeys.DIRECTION]
        if direction not in _VALID_DIRECTIONS:
            raise ValueError('Unrecognized direction: {}'.format(direction))

        if ConfigKeys.SSH_PORT in config:
            ssh_port = config[ConfigKeys.SSH_PORT]
            if ssh_port < 1 or ssh_port > 65535:
                raise ValueError('Invalid SSH port: {}'.format(ssh_port))

        if ConfigKeys.MAX_LOG_FILES in config:
            max_log_files = config[ConfigKeys.MAX_LOG_FILES]
            if max_log_files <= 0:
                raise ValueError(
                        '`max_log_files` must be greater than 0; however, now it is {}.'.format(
                                max_log_files))

        if len(config[ConfigKeys.TASKS]) == 0:
            raise ValueError('No task defined in the project.')


class RsyncTask(object):
    name: str = None
    source_path: str = None
    dest_path: str = None
    exclude: list[str] = None
    args: list[str] = None
    schedule: str = None

    _rsync_project: RsyncProject = None
    _absolute_local_source_dest_path: str = None
    _absolute_generated_script_path: str = None

    def __init__(self, rsync_project: RsyncProject, task: dict):
        RsyncTask._validate_task_dict(task)
        self.name = task[TaskKeys.NAME]
        self.source_path = task[TaskKeys.SOURCE_PATH]
        self.dest_path = task[TaskKeys.DEST_PATH]
        self.exclude = task.get(TaskKeys.EXCLUDE, [])
        self.args = task.get(TaskKeys.ARGS, [])
        self.schedule = task.get(TaskKeys.SCHEDULE, None)
        self._rsync_project = rsync_project

    def get_absolute_generated_script_path(self) -> str:
        if self._absolute_generated_script_path is None:
            filename = _RSYNC_SCRIPT_NAME_TEMPLATE.format(name=_slugify(self.name))
            self._absolute_generated_script_path = os.path.abspath(
                    os.path.join(Paths.OUTPUT_DIR, filename))
        return self._absolute_generated_script_path

    def write_to_file(self) -> None:
        """ Example template variables:
            {
                'rsync_source': '/home/myname/Documents/Example Project/',
                'rsync_dest': 'username@1.2.3.4:/path/to/dest/folder/1.2.3.4/home/myname/Example Project/',
                'multiline_args': '-av \\\n--chmod=777'
                'enable_logging': 'true',
                'log_dir': '/home/myname/Documents/Example Project/__rsync_logs__/',
                'max_log_files': 10,
            }
        """
        rsync_source = self._rsync_project.source_root + self.source_path
        rsync_dest = self._rsync_project.dest_root + self.dest_path
        if self._rsync_project.is_logging_enabled:
            absolute_log_dir = str(os.path.join(self._get_absolute_local_path(),
                                                self._rsync_project.log_dir_name))
            if not absolute_log_dir.endswith('/'):
                absolute_log_dir += '/'
        else:
            absolute_log_dir = ''

        with open(_RSYNC_SCRIPT_TEMPLATE_FILE, 'r') as file:
            script_template = file.read()
        kwargs = {
            _RsyncTemplateKeys.RSYNC_SOURCE: rsync_source,
            _RsyncTemplateKeys.RSYNC_DEST: rsync_dest,
            _RsyncTemplateKeys.MULTILINE_ARGS: self._generate_multiline_rsync_args(),
            _RsyncTemplateKeys.ENABLE_LOGGING: _PYTHON_BOOLEAN_TO_BASH_MAP[
                self._rsync_project.is_logging_enabled],
            _RsyncTemplateKeys.LOG_DIR: absolute_log_dir,
            _RsyncTemplateKeys.MAX_LOG_FILES: self._rsync_project.max_log_files,
        }
        content = script_template.format(**kwargs)

        with open(self.get_absolute_generated_script_path(), 'w+') as file:
            file.write(content)

    @staticmethod
    def _validate_task_dict(task: dict) -> None:
        for key in task:
            if key not in TaskKeys.ALL_TASK_KEYS:
                raise ValueError('Unrecognized task key: {}'.format(key))

        for key in TaskKeys.REQUIRED_TASK_KEYS:
            if key not in task:
                raise ValueError('Required key not present in task: {}'.format(key))

    def _get_absolute_local_path(self) -> str:
        if self._absolute_local_source_dest_path is None:
            direction = self._rsync_project.direction
            if direction == _DIRECTION_PUSH:
                self._absolute_local_source_dest_path = self._rsync_project.source_root + self.source_path
            elif direction == _DIRECTION_PULL:
                self._absolute_local_source_dest_path = self._rsync_project.dest_root + self.dest_path
            else:
                raise ValueError('Unrecognized direction: {}'.format(direction))
        return self._absolute_local_source_dest_path

    def _generate_rsync_exclude_arg_list(self) -> list[str]:
        patterns = []
        # If logging is enabled, we must exclude that directory
        if self._rsync_project.is_logging_enabled:
            patterns.append(self._rsync_project.log_dir_name + '/')
        patterns.extend(self._rsync_project.global_excludes)
        patterns.extend(self.exclude)
        return [_RSYNC_EXCLUDE_ARG_TEMPLATE.format(pattern=pattern) for pattern in patterns]

    def _generate_multiline_rsync_args(self) -> str:
        args = []
        if self._rsync_project.is_ssh_enabled:
            args.append(_RSYNC_SSH_ARG_TEMPLATE.format(port=self._rsync_project.ssh_port))
        args.extend(self._rsync_project.global_args)
        args.extend(self.args)
        args.extend(self._generate_rsync_exclude_arg_list())

        if len(args) == 0:
            args.append('')

        args_with_ending_backslash = [_RSYNC_ARG_LINE_TEMPLATE.format(arg=arg) for arg in args]
        return '\n'.join(args_with_ending_backslash)


class _RsyncTemplateKeys(object):
    RSYNC_SOURCE = 'rsync_source'
    RSYNC_DEST = 'rsync_dest'
    MULTILINE_ARGS = 'multiline_args'
    ENABLE_LOGGING = 'enable_logging'
    LOG_DIR = 'log_dir'
    MAX_LOG_FILES = 'max_log_files'


def _slugify(value):
    value = str(value)
    value = unicodedata.normalize('NFKC', value)
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')
