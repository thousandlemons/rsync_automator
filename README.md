# Rsync Automator

A command line utility that can automatically

* Generate different rsync scripts for a list of tasks defined in a json config
* Generate crontab entries for the sync tasks
* Save the console output of scheduled rsync tasks to local log files
* Clean up old log files and only keep those from the latest N sync runs

## Getting Started

### Preparation

1. Make sure you have installed at least [Python](https://www.python.org/downloads/) 3.9
1. Clone this repository
2. `cd` into the repository

### Create a config file

The config file must be named as `config.json` and must be located in the repository root. It is
highly recommended to copy [`example/full_config_example.json`](example/full_config_example.json)
into `config.json` instead of creating it from scratch.

To copy the config file, simply run:

```bash
cp example/full_config_example.json config.json
```

A simplified config file may look like this:

```json
{
  "rsync": "/usr/bin/rsync",
  "direction": "push",
  "source_root": "/home/myname",
  "dest_root": "myname@10.1.2.3:/path/to/dest/folder/10.1.2.3/home/myname",
  "ssh_port": 22,
  "log_dir_name": "__rsync_logs__",
  "max_log_files": 10,
  "generated_crontab_comment_mark": "[Backup my home folders]",
  "global_exclude": [
    ".DS_Store",
    "._*",
    "desktop.ini",
    "Thumbs.db"
  ],
  "global_args": [
    "--protect-args",
    "-avi"
  ],
  "tasks": [
    {
      "name": "My Awesome Project",
      "source_path": "/Documents/My Awesome Project/",
      "dest_path": "/My Awesome Project/",
      "exclude": [
        "temp/",
        "output/"
      ],
      "args": [
        "--chmod=777"
      ],
      "schedule": "0 0 * * *"
    },
    {
      "name": "Favorite Songs",
      "source_path": "/Music/Favorite/",
      "dest_path": "/My Favorite Songs/"
    }
  ]
}
```

As shown in the example above, this tool takes care of one-way syncing between one pair of
source/destination devices, and multiple pairs of source/destination folders on them.

If you also need to sync folders to/from a different host, simply make another clone of this
repository, and create another config there. You can have as many clones of this repository as you
need on a single device. As long as you use a different `generated_crontab_comment_mark` for each
project, there won't be any conflict or side effect.

More information about the config file can be found at the [JSON Config Specs](#json-config-specs)
section below.

### Run the script

```bash
./main.sh
```

## Result of `main.sh`

### Generated rsync scripts

All the generated rsync scripts are located in the `output/` directory (relative to the repo's root
directory), and they are ignored by Git.

Upon each run of the `main.sh` script, all previously generated files in the `output/` directory are
first deleted. Then, one individual bash script is generated for each task defined in `tasks`. The
script names are in the format of `rsync_{name}.sh`, where `{name}` is the slugified task name.

Also, you can take a look at
an [example generated rsync script](example/generated_rsync_script_example.sh).

### Generated "run all" script

A "run all" script is generated at `output/run_all.sh`. Running this script will execute all other
generated rsync scripts (i.e. `output/rsync_*.sh`).

### Configured cron jobs

If the `schedule` field is provided in a task, a cron job is automatically added to the current
user's crontab. The automatically generated entries in crontab are commented
with `# {name} {generated_crontab_comment_mark}`, where `{name}` is the task name,
and `{generated_crontab_comment_mark}` is defined in the config file. Here is
an [example generated crontab entry](example/generated_crontab_example.txt).

Upon each run of `main.sh`, if there are existing crontab entries with exactly the
same `{generated_crontab_comment_mark}`, they will be deleted first. Then, new entries created from
the tasks in the current config file will be added to the bottom of crontab. Hence, it's highly
recommended to use different `{generated_crontab_comment_mark}` values for different clones of this
repository.

All other existing entries with other comments, or those without any comment, will be preserved
as-is.

Right before `main.sh` completes and exits, it automatically calls `crontab -l` to print the crontab
entries, so that you can visually verify whether the changes are correct.

### [Optional] Use `sudo` to configure the root user's crontab

If the rsync tasks are expected to be run with `sudo`, maybe because the rsync sources or
destinations are owned by root or other users, simply run `sudo ./main.sh` instead. Then,
run `sudo output/rsync_my-task.sh` if needed.

Also, when the `main.sh` script is run with `sudo`, it will also add the cron jobs into the root
user's crontab.

## Logging

This feature can be turned on by providing the `log_dir_name` field in the config. If the value is
not present, no log files will be saved.

With this feature on, when a generated rsync script (i.e. any of the `output/rsync_*.sh`) is run,
either manually or automatically by cron, a log file can be created inside the
task's `{local_dir}/{log_dir_name}/` directory.

The `{local_dir}` is the local (as opposed to "remote") location of either the source or destination
directory of a task, depending on whether the `direction` is a `push` or `pull`. If the task is
a `push`, the `{local_dir}` is absolute source directory. Otherwise, if it's a `pull`, then
the `{local_dir}` is the absolute destination directory.

Because this log directory will be automatically excluded by rsync, it's highly recommended to use a
unique name, such as `__rysnc_logs__`, so that rsync will not accidentally exclude any sub-folder
that should be synced.

Each log file is named with the start time of the run, in the format of `2022-07-06 09-57-48.log`.

Also, only `max_log_files` most recent log files will be kept. Older log files will be
automatically removed each time a generated rsync script is run. If `max_log_files` is not defined
but logging is enabled, the value will be set to 10 by default.

Each log file contains the following information:

* Start time
* SSH port
* Rsync source
* Rsync destination
* The complete console output of rsync
* List of older log files to remove
* End time

You can take a look at
the [example generated rsync script](example/generated_rsync_script_example.sh) to see what exactly
is saved into log files, and how older files are automatically removed at each run.

## JSON Config Specs

### The `Config` object

The `Config` object is the root object in `config.json`.

| Field                            | Required? | Type       | Explanation                                                                                                                                                                                                                                                                                                                           | 
|----------------------------------|-----------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `rsync`                          | Optional  | String     | The path to the rsync binary (e.g. /usr/bin/rsync or /usr/local/bin/rsync). If not set, the default value is just `"rsync"` without any absolute path.                                                                                                                                                                                |
| `direction`                      | Required  | String     | Either `"push"` or `"pull"`. If the source is on the local device and the destination is on a remote device, it's a `"push"`. Otherwise, it's a `"pull"`.                                                                                                                                                                             | 
| `source_root`                    | Required  | String     | An absolute path on the source device.                                                                                                                                                                                                                                                                                                | 
| `dest_root`                      | Required  | String     | An absolute path on the destination device.                                                                                                                                                                                                                                                                                           | 
| `ssh_port`                       | Optional  | Integer    | The SSH port of the remote device. Defining this field will add the `-e "ssh -p {port_number}"` argument to rsync. If the SSH port is 22, or if both the source and destination are local, you don't need to define this field.                                                                                                       |
| `log_dir_name`                   | Optional  | String     | The name of sub-directory inside of each task's local directory where the log files will be saved to. If this field is not defined, no logging files will be saved when the generated rsync scripts are run.                                                                                                                          | 
| `max_log_files`                  | Optional  | Integer    | The maximum number of historical log files to be kept. When this limit is reached, the oldest log file will be removed. The default value is 10, if this field is not present but logging is enabled.                                                                                                                                 | 
| `generated_crontab_comment_mark` | Optional  | String     | A tag used to distinguish which entries in the cron table were automatically generated by this script. Once defined, this value must not be changed later. Otherwise, previously configured crontab entries won't be automatically cleaned up anymore. If this value is not present, none of the tasks below may define a `schedule`. |
| `global_exclude`                 | Optional  | `String[]` | A list of string patterns to exclude with rsync's `--exclude` argument. This list will be appended to the start of each individual task's `exclude` list.                                                                                                                                                                             | 
| `global_args`                    | Optional  | `String[]` | A list of additional rsync arguments that will be included in each task.                                                                                                                                                                                                                                                              | 
| `tasks`                          | Required  | `Task[]`   | An array of `Task`s.                                                                                                                                                                                                                                                                                                                  |

### The `Task` object:

| Field         | Required? | Type       | Explanation                                                                                                                                                                                                                                                                                                                         | 
|---------------|-----------|------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `name`        | Required  | String     | The name of the task. The name after being slugified is used in the filename of the generated script, and the original name is a part of the comment of the generated crontab entry.                                                                                                                                                | 
| `source_path` | Required  | String     | Relative path from the `source_root` to the directory to sync. `source_root` and `source_path` will be literally concatenated before passing to rsync, so make sure they do not have redundant leading/trailing slashes. Also, see the section below [Source path with ending slash](#source-path-ending-with-slash) for more info. |
| `dest_path`   | Required  | String     | Relative path from the `dest_root` to the directory to sync. The ending slash is optional.                                                                                                                                                                                                                                          | 
| `exclude`     | Optional  | `String[]` | A list of string patterns to exclude with rsync's `--exclude` argument.                                                                                                                                                                                                                                                             |
| `args`        | Optional  | `String[]` | A list of rsync args to be added to this task.                                                                                                                                                                                                                                                                                      |
| `schedule`    | Optional  | String     | A valid [cron job schedule](https://cloud.google.com/scheduler/docs/configuring/cron-job-schedules) string. If not present, the `main.sh` script will not configure any crontab entry for this task. If this value is present, the `Config.generated_crontab_comment_mark` field above must also be present.                        | 

## Rsync Recommendations

### Arguments

* `--protect-args`: if the directories contain spaces or any other character that needs to be
  escaped, you must add this argument.
* A few arguments to help preserve more info in the log files:
    * `-i` or `--itemize-changes`
    * `--human-readable`
    * `--stats`
    * `--verbose`
* `--omit-dir-times` can be pretty useful to avoid unnecessary transfers

### Exclusions

This is a list of some basic OS files that should be generally excluded:

```json
{
  "global_exclude": [
    ".DS_Store",
    "._*",
    "desktop.ini",
    "Thumbs.db",
    "@eaDir"
  ]
}
```

### Source path ending with slash

Say if we want to sync the contents of these two directories:

```text
# The source directory at one location
my_source_dir
├── a.txt
├── b.txt
├── c.txt
└── some_subfolder
    └── more_file.txt

# The destination directory at another location
my_dest_dir
├── a.txt
├── b.txt
├── c.txt
└── some_subfolder
    └── more_file.txt
```

When using rsync, the source path must have an ending slash (`/`), and the destination path does not
necessarily end with slash. For example:

```bash
rsync -av /path/to/my_source_dir/ /path/to/my_dest_dir
```

However, if the source path does not end with a slash, `my_source_dir` will be placed inside
of `my_dest_dir`. The sync result will look like this:

```text
my_dest_dir
├── a.txt
├── b.txt
├── c.txt
├── my_source_dir
│   ├── a.txt
│   ├── b.txt
│   ├── c.txt
│   └── some_subfolder
│       └── more_file.txt
└── some_subfolder
    └── more_file.txt
```