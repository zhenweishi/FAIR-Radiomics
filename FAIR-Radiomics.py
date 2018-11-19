"""
###############################
@author: zhenwei.shi, Maastro##
###############################
Usage:

"""
from __future__ import print_function

import pydicom,os
import pandas as pd
import numpy as np
import re
import glob
import yaml
import shutil
from DicomDatabase import DicomDatabase
from subprocess import call
from pathlib import Path
import FAIR_Radiomics_batch

def dcmImageToNRRD(inputImageDir,ptid,exportDir,):
    image = os.path.join(exportDir,ptid + '_image.nrrd')
    try:
        call(['plastimatch', 'convert','--input',inputImageDir,'--output-img',image])
    except:
        print("Error: plastimatch failed to convert image to image.nrrd")
    return image

def dcmRtToNRRD(inputRtDir,inputImageDir,exportDir,ROIname):
    try:
        call(['plastimatch', 'convert','--input',inputRtDir,'--output-prefix',exportDir, '--prefix-format', 'nrrd',\
        '--referenced-ct',inputImageDir])
    except:
        print("Error: plastimatch failed to convert RT to mask.nrrd")
    for label in os.listdir(exportDir):
        if not re.search(ROIname,label):
            os.remove(os.path.join(exportDir,label))
def SEGJsoner(JsontemplateDir,jsonexportDir):
    # In this study, we are using one json template for all patients, which means that it is in cohort level
    shutil.copy2(os.path.join(JsontemplateDir,'metadata.json'),jsonexportDir)

# convert SEG.dcm to nrrd file
def dcmSEGToNRRDs(inputSEG, workingDir,patientid):
    segmentsDir = os.path.join(workingDir,'Segments')
    if not os.path.exists(segmentsDir):
        os.mkdir(segmentsDir)
    try:
        call(['segimage2itkimage', '--inputDICOM', inputSEG, '--outputDirectory', segmentsDir,'-p', patientid])
    except:
        print('Error: Failed to pack SEG to nrrd image')
    return glob.glob(os.path.join(segmentsDir,"*nrrd"))

# export result to Dicom-SR
def ExportDicomSR(pyradiomicsdcmfile,inputImageDir,inputSEG,exportDir,featureDict,paramsyaml):
    try:
        call(['python3',pyradiomicsdcmfile,'--input-image',inputImageDir,'--input-seg-file',inputSEG,'--output-dir',\
        exportDir,'--features-dict',featureDict,'--parameters',paramsyaml])
    except:
        print('Error: Failed to convert Dicom-SR')

# convert nrrd to SEG.dcm
def dcmNRRDsToSEG(inputImageList,inputDICOMDirectory,inputMetadata,outputDICOM,workingDir):
    SEGDir = os.path.join(workingDir,'SEG')
    if not os.path.exists(SEGDir):
        os.mkdir(SEGDir)
    try:
        call(['itkimage2segimage', '--inputImageList', inputImageList,'--inputDICOMDirectory',inputDICOMDirectory,\
              '--inputMetadata',inputMetadata, '--outputDICOM', outputDICOM])
    except:
        print('Error: failed to pack dcm image to SEG.dcm')
    
# def DirConstruction(datasetDir,ROIname):
def main():
    #-----------------create the data structure-----------
    df_combine = pd.DataFrame()

    # -----------------------------------------------------------
    # initialize dicom DB
    dicomDb = DicomDatabase()
    # walk over all files in folder, and index in the database
    dicomDb.parseFolder(datasetDir)
    excludeStructRegex = "(Patient.*|BODY.*|Body.*|NS.*|Couch.*)"
    # ----------------------------------------------------
    # loop over patients
    for ptid in dicomDb.getPatientIds():
        print("staring with Patient %s" % (ptid))
        # get patient by ID
        myPatient = dicomDb.getPatient(ptid)
        # loop over RTStructs of this patient
        for myStructUID in myPatient.getRTStructs():
            print("Starting with RTStruct %s" % myStructUID)
            # Get RTSTRUCT by SOP Instance UID
            myStruct = myPatient.getRTStruct(myStructUID)
            # Get CT which is referenced by this RTStruct, and is linked to the same patient
            # mind that this can be None, as only a struct, without corresponding CT scan is found
            myCT = myPatient.getCTForRTStruct(myStruct)
            structfile = myStruct.getFileLocation()
            struct = pydicom.dcmread(structfile)
            SOPInstanceUID = struct.SOPInstanceUID
            patient = 'FAIRR_'+ ptid + '_'+SOPInstanceUID
            # patient = 'FAIRR_'+ ptid
            if not os.path.exists(os.path.join(datasetDir,patient)):
                os.makedirs(os.path.join(datasetDir,patient),0o755)
            if not os.path.exists(os.path.join(datasetDir,patient,'dicom','Image')):
                os.makedirs(os.path.join(datasetDir,patient,'dicom','Image'))
            if not os.path.exists(os.path.join(datasetDir,patient,'dicom','STRUCT')):
                os.makedirs(os.path.join(datasetDir,patient,'dicom','STRUCT'))
            if not os.path.exists(os.path.join(datasetDir,patient,'SEG')):
                os.makedirs(os.path.join(datasetDir,patient,'SEG'))
            if not os.path.exists(os.path.join(datasetDir,patient,'Mask_Nrrd')):
                os.makedirs(os.path.join(datasetDir,patient,'Mask_Nrrd'))
            if not os.path.exists(os.path.join(datasetDir,patient,'Volume_Nrrd')):
                os.makedirs(os.path.join(datasetDir,patient,'Volume_Nrrd'))            
            if not os.path.exists(os.path.join(datasetDir,patient,'Json')):
                os.makedirs(os.path.join(datasetDir,patient,'Json'))
            if not os.path.exists(os.path.join(datasetDir,patient,'DicomSR')):
                os.makedirs(os.path.join(datasetDir,patient,'DicomSR'))
            #---------------------------------       
            #only show if we have both RTStruct and CT
            if myCT is not None:
                # copy RTSTRUCT file to tmp folder as 'struct.dcm'
                shutil.copy2(myStruct.getFileLocation(),os.path.join(datasetDir,patient,'dicom','STRUCT','struct.dcm'))
                # copy DICOM slices to tmp folder as 'struct.dcm'
                slices = myCT.getSlices()
                for i in range(len(slices)):
                    shutil.copy2(slices[i],os.path.join(datasetDir,patient,'dicom','Image',str(i)+".dcm"))
           
                # catch directories
                inputImageDir = os.path.join(datasetDir,patient,'dicom','Image') 
                inputRtDir = os.path.join(datasetDir,patient,'dicom','STRUCT')
                MaskDir = os.path.join(datasetDir,patient,'Mask_Nrrd')
                VolumeDir = os.path.join(datasetDir,patient,'Volume_Nrrd')
                JsontemplateDir = os.path.join(datasetDir)
                JsonexportDir = os.path.join(datasetDir,patient,'Json')
                DicomSRDir = os.path.join(datasetDir,patient,'DicomSR')
                # catch files
                Jsonfile = os.path.join(JsonexportDir,'metadata.json')
                # convert RT to Nrrd labels
                dcmRtToNRRD(inputRtDir,inputImageDir,MaskDir,ROIname)
                mask_list = glob.glob(os.path.join(MaskDir,'*'))
                # # ---------------------------------------------------
                # update Json file based on the Json template
                SEGJsoner(JsontemplateDir,JsonexportDir)
                workingDir = os.path.join(datasetDir,patient)
                # pack itk image to SEG dcm
                SEGfile = os.path.join(datasetDir,patient,'SEG',('%s_SEG.dcm' %patient)) 
                label_list = ','.join(map(str,mask_list))
               
                dcmNRRDsToSEG(label_list,inputImageDir,Jsonfile,SEGfile,workingDir)

                # convert image to nrrd
                image = dcmImageToNRRD(inputImageDir,patient,VolumeDir)
                # convert result to dicom-SR
                pyradiomicsdcmfile = '../pyradiomics/labs/pyradiomics-dcm/pyradiomics-dcm.py'
                featureDict = '../pyradiomics/labs/pyradiomics-dcm/resources/featuresDict_IBSIv7.tsv'
                paramsyaml = '../pyradiomics/labs/pyradiomics-dcm/Pyradiomics_Params.yaml'
                try:
                    ExportDicomSR(pyradiomicsdcmfile,inputImageDir,SEGfile,DicomSRDir,featureDict,paramsyaml)
                except:
                    print('Error: failed to export DICOM-SR')
                #---------------------------------------
                # unpack SEG dcm to itk image
                # dcmSEGToNRRDs(SEGfile, workingDir,ptid)
                labellist = glob.glob(os.path.join(MaskDir,'*.nrrd'))
                for label in labellist:
                    df_NRRD = pd.DataFrame({'ID':[patient+'_'+ROIname],'Image':[image],'Mask':[label]})
                    df_combine = pd.concat([df_combine,df_NRRD],axis=0)
    return df_combine

if __name__ == '__main__':
  # set parameters
  ROIname = '[Gg][Tt][Vv][-][1]'
  walk_dir = 'Test'
  # ----------------------------
  dataset_list = glob.glob(os.path.join(os.getcwd(),walk_dir,'*'))
  df = pd.DataFrame()
  for datasetDir in dataset_list:
    df_tmp = main()
    df = pd.concat([df,df_tmp],axis= 0)
  df.to_csv(os.path.join(os.getcwd(),walk_dir,'FAIRR_casetable.csv'),index = False)
  FAIR_Radiomics_batch.main()

