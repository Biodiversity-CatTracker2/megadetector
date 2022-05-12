#!/bin/bash

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

EOF

sleep 1
echo 'export PATH=$PATH:$WORK/.local/bin' >> $WORK/.bashrc

module unload python
module load tensorflow-gpu cuda/11.2 rclone

pip install --user -r requirements.txt

wget -O megadetector_v4_1_0.pb https://lilablobssc.blob.core.windows.net/models/camera_traps/megadetector/md_v4.1.0/md_v4.1.0.pb

git clone https://github.com/microsoft/CameraTraps
git clone https://github.com/microsoft/ai4eutils

cp CameraTraps/detection/run_tf_detector_batch.py .
cp CameraTraps/visualization/visualize_detector_output.py .
rm CameraTraps/detection/run_tf_detector.py

curl -o "run_tf_detector.py" "https://gist.githubusercontent.com/Alyetama/068054632e6ceacbf066664e2c18e920/raw/280b38acd47a3cddda4e411affb635a5e2d26701/run_tf_detector.py"
mv run_tf_detector.py CameraTraps/detection

mkdir -p logs
