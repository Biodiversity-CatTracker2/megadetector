# megadetector

## Setup

### Configure your environment (run only once)

```sh
cd /share/$GROUP/$USER
git clone https://github.com/Biodiversity-CatTracker2/megadetector-HPC.git megadetector
cd megadetector

mv lsf/configure.csh lsf/megadetector_job.csh .

chmod +x configure.csh
./configure.csh
```

### Connect to your cloud storage account (run only once)

- Here, we will use `Google Drive` as an example, but you can use any cloud storage listed [here](https://rclone.org/docs/).

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

## Download the data

```sh
set FULL_REMOTE_PATH="<PLACEHOLDER>"  # Full path to where the data is kept, including the remote entry name
set DATA_DIR="data"
./rclone copy "$FULL_REMOTE_PATH" "$DATA_DIR" --transfers 32 -P
```

## Submit the batch job

```sh
set CONF="0.3"  # confidence threshold
bsub -env "DATA_DIR=$DATA_DIR, CONF=$CONF" < megadetector_job.csh
```

## Upload the results when the job is complete

```sh
cp 'results.zip' 'failed.json' 'detections_per_conf_lvl.json' 'detections_per_conf_lvl_count.json' filtered_data
./rclone copy filtered_data "$FULL_REMOTE_PATH/results" -P
```
