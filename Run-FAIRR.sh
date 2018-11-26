#!/bin/sh

echo "Step-1:--------- add dcmqi and dcm2niix to path-------"
export PATH=$PATH:"$(pwd)/dcmqi/bin"
export PATH=$PATH:"$(pwd)/dcm2niix"

echo "Step-2:--------- Running FAIR-Radiomics main script-------"
python3 FAIR-Radiomics.py
