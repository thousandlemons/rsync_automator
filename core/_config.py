import os


class Paths(object):
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config.json')
    TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'template')
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')


class ConfigKeys(object):
    """
    Keys in the config.json file
    """
    RSYNC = 'rsync'
    DIRECTION = 'direction'
    SOURCE_ROOT = 'source_root'
    DEST_ROOT = 'dest_root'
    SSH_PORT = 'ssh_port'
    SSH_KEY_FILE = 'ssh_key_file'
    LOG_DIR_NAME = 'log_dir_name'
    MAX_LOG_FILES = 'max_log_files'
    GENERATED_CRONTAB_COMMENT_MARK = 'generated_crontab_comment_mark'
    GLOBAL_EXCLUDE = 'global_exclude'
    GLOBAL_ARGS = 'global_args'
    TASKS = 'tasks'

    ALL_CONFIG_KEYS = {
        RSYNC,
        DIRECTION,
        SOURCE_ROOT,
        DEST_ROOT,
        SSH_PORT,
        SSH_KEY_FILE,
        LOG_DIR_NAME,
        MAX_LOG_FILES,
        GENERATED_CRONTAB_COMMENT_MARK,
        GLOBAL_EXCLUDE,
        GLOBAL_ARGS,
        TASKS,
    }

    REQUIRED_CONFIG_KEYS = {
        DIRECTION,
        SOURCE_ROOT,
        DEST_ROOT,
        GENERATED_CRONTAB_COMMENT_MARK,
        TASKS,
    }


class TaskKeys(object):
    """
    Keys in each of the config['task'] object
    """
    NAME = 'name'
    SOURCE_PATH = 'source_path'
    DEST_PATH = 'dest_path'
    EXCLUDE = 'exclude'
    ARGS = 'args'
    SCHEDULE = 'schedule'

    ALL_TASK_KEYS = {
        NAME,
        SOURCE_PATH,
        DEST_PATH,
        EXCLUDE,
        ARGS,
        SCHEDULE,
    }

    REQUIRED_TASK_KEYS = {
        NAME,
        SOURCE_PATH,
        DEST_PATH,
    }
