#!/bin/sh

echo "Step-1:"
echo "-------- initial update-------"
sudo apt-get update

echo "Step-2:"
echo "-------- install Anaconda3----- (optional)" 
cd /tmp
wget https://repo.anaconda.com/archive/Anaconda3-5.2.0-Linux-x86_64.sh
bash Anaconda3-5.2.0-Linux-x86_64.sh
sudo rm Anaconda3-5.2.0-Linux-x86_64.sh 

echo "Step-3:"
echo "-------- install pip3---------"
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
sudo rm get-pip.py

echo "Step-4:"
echo "--------- install latest pyradiomics-------"
cd ~
git clone https://github.com/Radiomics/pyradiomics.git
cd ~/pyradiomics
sudo python3 -m pip install -r requirements.txt
sudo python3 setup.py install

echo "Step-5:"
echo "--------- install FAIR-Radiomics package-------"
cd ~
git clone https://github.com/zhenweishi/FAIR-Radiomics.git
cd ./FAIR-Radiomics
sudo python3 -m pip install -r FAIRR_requirements.txt

echo "Step-6:--------- install plastimatch package-------"
sudo apt-get install plastimatch
cd ~

echo "Step-7:--------- change exe files mode-------"
# cd ~/FAIR-Radiomics/dcmqi/bin
# sudo chmod u+x itkimage2segimage
# sudo chmod u+x segimage2itkimage
# sudo chmod u+x tid1500writer
# cd ~/FAIR-Radiomics/dcm2niix
# sudo chmod u+x dcm2niibatch
# sudo chmod u+x dcm2niix
# cd ~

# echo "Step-:--------- download data from XNAT-------"
# cd ./FAIR-Radiomics
# python3 FAIR_Radiomics_XNAT.py


