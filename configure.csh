#!/bin/tcsh

cat <<'EOF'

                                                           .
                  .                                    .::'
                  `::.          CONFIGURATION        .`  :
                   :  '.            SCRIPT         .`o    :
                  :    o'.                        ~~}     :
                  :     {~~                        `:     `:.
                .:`     :'                          :    .:   `.
             .`   :.    :                           :   :       `.
           .`       :   :                           `.   `.       :
          :       .'   .'                            `.    `..    :
          :    ..'    .'   MOHAMMAD ALYETAMA          `:.. '.````:
          :''''.' ..:'     malyeta@ncsu.edu              ::`::`:   :.      .
        .:   :'::'::        ..........................:"``````'"`:   `:""": :
.:"""""""""""`''''''""""""""                     ...........""""""`:   `:"`,'
:                            ..........""""""""""                   ':   `:
`............."""""""""""""""                                         `..:'
  `:..'

'EOF'

sleep 1
echo 'set path=($path /share/$GROUP/$USER/.local/bin)' >> /home/$USER/.tcshrc

module load cuda tensorflow
pip install --user loguru humanfriendly jsonpickle GPUtil python-dotenv tqdm pandas matplotlib numpy

wget -O megadetector_v4_1_0.pb https://lilablobssc.blob.core.windows.net/models/camera_traps/megadetector/md_v4.1.0/md_v4.1.0.pb

git clone https://github.com/microsoft/CameraTraps
git clone https://github.com/microsoft/ai4eutils

cp CameraTraps/detection/run_tf_detector_batch.py .
cp CameraTraps/visualization/visualize_detector_output.py .
rm CameraTraps/detection/run_tf_detector.py

curl -o "run_tf_detector.py" "https://gist.githubusercontent.com/Alyetama/068054632e6ceacbf066664e2c18e920/raw/280b38acd47a3cddda4e411affb635a5e2d26701/run_tf_detector.py"
mv run_tf_detector.py CameraTraps/detection

curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip
unzip rclone-current-linux-amd64.zip
cd rclone-*-linux-amd64
chmod 755 rclone
cp rclone ..
cd ..
rm rclone-current-linux-amd64.zip
rm -rf rclone-*-linux-amd64

mkdir -p logs

mv submit.csh submit
chmod +x submit
mv upload.csh upload
chmod +x upload

wget "https://d.aibird.me/a6f58f88" -O detox
chmod +x detox
