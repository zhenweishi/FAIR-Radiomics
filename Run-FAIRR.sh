#!/bin/sh

echo "Step-1:--------- add dcmqi and dcm2niix to path-------"
export PATH=$PATH:/home/zhenwei/FAIR-Radiomics/dcmqi/bin
export PATH=$PATH:/home/zhenwei/FAIR-Radiomics/dcm2niix

echo "Step-2:--------- Running FAIR-Radiomics main script-------"
python3 FAIR-Radiomics.py
