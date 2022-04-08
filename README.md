# megadetector

## Setup

### Configure your environment (run only once)

```sh
cd /share/$GROUP/$USER
git clone https://github.com/Biodiversity-CatTracker2/megadetector-Henry2.git megadetector
cd megadetector

chmod +x configure.csh
./configure.csh
```

### Connect to your Google Drive account (run only once)

```sh
./rclone config
# >>>> Prompt responses:
# n/s/q> n
# name> gdrive
# Storage> drive
# client_id> leave empty
# client_secret> leave empty
# scope> 1
# root_folder_id> leave empty
# service_account_file> leave empty
# y/n> n
# y/n> n
# COPY THE URL IN THE OUTPUT, AND OPEN IT IN YOUR BROWSER TO LOG IN...
#     ...THEN COPY THE CODE THAT WILL SHOW UP
# config_verification_code> PASTE THE CODE YOU COPIED HERE
# y/n> n
# y/e/d> y
# e/n/d/r/c/s/q> q
```

## Submit jobs

```sh
set FULL_REMOTE_PATH="<PLACEHOLDER>"  # for example: gdrive:cameratrap/deployments
# if you're not the original owner of the remote folder, add `--drive-shared-with-me` to `rclone` commands
./batch_submit.csh $FULL_REMOTE_PATH
```

## Upload the results to Google Drive when all job are complete

```sh
set FULL_REMOTE_PATH="<PLACEHOLDER>"
set DATA_FOLDER=`basename $FULL_REMOTE_PATH`
tar -czf "results.tgz" `find $DATA_FOLDER -name "*.json"`
./rclone copy "results.tgz" "$FULL_REMOTE_PATH" -P --stats-one-line
```

## Filter the results

- First, move the results file (`results.tgz`) to the same parent directory where the images data folder is on your local drive (e.g., `./parent/labels_folder_path`, `./parent/images`), then extract the folder and filter the data

```sh
tar -zxf "results.tgz"
filter_megadetector_output.py --results-dir "$DATA_FOLDER" --max-detection-conf 0.3  # accepted values: 0.1-0.9
```
