# megadetector

## Setup

### Configure your environment (run only once)

```sh
cd $WORK
git clone https://github.com/Biodiversity-CatTracker2/megadetector-HPC.git megadetector
cd megadetector

mv slurm/track_progress_job.sh slurm/configure.sh slurm/megadetector_job.sh .

chmod +x configure.sh
./configure.sh
```

### Connect to your cloud storage account (run only once)

- Here, we will use `Google Drive` as an example, but you can use any cloud storage listed [here](https://rclone.org/docs/).

```sh
module load rclone
rclone config
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
FULL_REMOTE_PATH="<PLACEHOLDER>"  # Full path to where the data is kept, including the remote entry name
DATA_DIR="data"
rclone copy "$FULL_REMOTE_PATH" "$DATA_DIR" --transfers 32 -P
```

## Submit the batch job

1. Edit the main batch job file: `megadetector_job.sh`.
2. Edit the progress tracking job file: `track_progress_job.sh`.
3. Submit the jobs

```sh
sbatch megadetector_job.sh
sbatch track_progress_job.sh
```

## Upload the results when the job is complete

```sh
cp 'results.zip' 'failed.json' filtered_data
rclone copy filtered_data "$FULL_REMOTE_PATH/results" -P
```
