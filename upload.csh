#!/bin/tcsh

cat <<'EOF'


                     _.--.
                 .-"`_.--.\   .-.___________
               ."_-"`     \\ (  0;------/\"'`
             ,."=___      =)) \ \      /  \
              `~` .=`~'~)  ( _/ /     /    \
      =`---====""~`\          _/     /      \
                    `-------"`      /  DATA  \
                                   /  UPLOAD  \
                                  (   SCRIPT   )
MOHAMMAD ALYETAMA                  '._      _.'
malyeta@ncsu.edu                      '----'

'EOF'


printf "ENTER THE FULL GOOGLE DRIVE FOLDER PATH (DO NOT INCLUDE 'SHARED WITH ME' OR 'MY DRIVE' IN THE PATH!): "
set GOOGLE_DRIVE_FOLDER_FULL_PATH="$<"
set IMAGES_DIR=`basename "${GOOGLE_DRIVE_FOLDER_FULL_PATH}"`

printf "ARE YOU THE ORIGINAL OWNER OF THE FOLDER (Y/N)? "
set RCLONE_ANS=$<

cat <<'EOF'
     _   _ ___ _    ___   _   ___ ___ _  _  ___   ___   _ _____ _         
    | | | | _ | |  / _ \ /_\ |   |_ _| \| |/ __| |   \ /_|_   _/_\        
    | |_| |  _| |_| (_) / _ \| |) | || .` | (_ | | |) / _ \| |/ _ \ _ _ _ 
     \___/|_| |____\___/_/ \_|___|___|_|\_|\___| |___/_/ \_|_/_/ \_(_(_(_)
                                                                          
'EOF'

if ( $RCLONE_ANS == y | $RCLONE_ANS == Y ) ./rclone copy "$IMAGES_DIR/output" gdrive:"$GOOGLE_DRIVE_FOLDER_FULL_PATH/output" --transfers 32 -P --stats-one-line
if ( $RCLONE_ANS == n | $RCLONE_ANS == N ) ./rclone --drive-shared-with-me copy "$IMAGES_DIR/output" gdrive:"$GOOGLE_DRIVE_FOLDER_FULL_PATH/output" --transfers 32 -P --stats-one-line

echo "\nFinished uploading!\n"
