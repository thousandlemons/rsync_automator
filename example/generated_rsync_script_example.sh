##### Note that in reality this file would be named as output/rsync_my-awesome-project.sh
##### ========== EXAMPLE BEGINS ==========
#!/bin/bash

execute_rsync() {
  echo "Start Time: $(date -Iseconds)"
  echo "Source: /Users/myusername/Downloads/My Awesome Project/"
  echo "Destination: myusername@10.1.2.3:/home/myusername/Downloads/My Awesome Project/"
  printf "\n========== RSYNC BEGINS ==========\n\n"

  rsync \
    -e "ssh -p 22222" \
    --protect-args \
    --recursive \
    --delete \
    --times \
    --omit-dir-times \
    --itemize-changes \
    --verbose \
    --human-readable \
    --progress \
    --stats \
    --exclude "__rsync_logs__/" \
    --exclude ".DS_Store" \
    --exclude "._*" \
    --exclude "desktop.ini" \
    --exclude "Thumbs.db" \
    "/Users/myusername/Downloads/My Awesome Project/" \
    "myusername@10.1.2.3:/home/myusername/Downloads/My Awesome Project/"

  printf "\n========== RSYNC ENDS ==========\n\n"

  if true; then
    echo "Keeping 20 most recent log files only; log files to remove:"
    ls -dtp "/Users/myusername/Downloads/My Awesome Project/__rsync_logs__/"* | grep -v '/$' | tail -n +20 | while IFS= read -r f; do echo "$f"; done
    ls -dtp "/Users/myusername/Downloads/My Awesome Project/__rsync_logs__/"* | grep -v '/$' | tail -n +20 | xargs -I {} rm -- {}
  fi

  printf "\nEnd Time: $(date -Iseconds)"
  echo
}

if true; then
  mkdir -p "/Users/myusername/Downloads/My Awesome Project/__rsync_logs__/"
  LOG_FILE_PATH="/Users/myusername/Downloads/My Awesome Project/__rsync_logs__/$(date +"%Y-%m-%d %H-%M-%S").log"
  execute_rsync > >(tee "$LOG_FILE_PATH") 2>&1
else
  execute_rsync
fi
