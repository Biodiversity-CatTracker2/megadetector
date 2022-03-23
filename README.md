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

## Submit a job

```sh
./submit
```

## Upload the data to Google Drive when the job is complete

```sh
./upload
```
