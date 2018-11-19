import xnat
import os
import subprocess
import zipfile

# Download data from XNAT in .zip format
def xnat_collection(myWorkingDirectory,collectionURL,myProjectID):
    os.chdir(myWorkingDirectory)
    #connections to public collections do not require passwords
    with xnat.connect(collectionURL) as mySession:
        myProject= mySession.projects[myProjectID]
        mySubjectsList = myProject.subjects.values()
        for s in mySubjectsList:
            mySubjectID = s.label
            print('\nEntering subject ...' + mySubjectID)
            mySubject = myProject.subjects[mySubjectID]
            myExperimentsList = mySubject.experiments.values()
            for e in myExperimentsList:
                myExperimentID = e.label
                #print('\nEntering experiment ...' + myExperimentID)
                myExperiment = mySubject.experiments[myExperimentID]
                #the next line downloads each subject, experiment pair one-by-one into separate zip files
                myExperiment.download(os.path.join(myWorkingDirectory,myExperimentID+'.zip'))
#
#
def main():
    for i in range(len(ProjectIDs)):
        Dataset_dir = os.path.join(WorkingDir,Dataset_name[i])
        xnat_collection(Dataset_dir,collectionURL,ProjectIDs[i])
        # Unzip zip files download from XNAT
        # archives = [fn for fn in os.listdir('.') if fn.endswith('CT.zip') or fn.endswith('TEST.zip')]
        archives = [fn for fn in os.listdir('.') if (fn.endswith('.zip') and not fn.endswith('PET.zip'))]
        for zip_name in archives:
            zip_ref = zipfile.ZipFile(zip_name,'r')
            zip_ref.extractall()
            zip_ref.close()
        #remove all zip file
        Dir = os.curdir
        zip_files=os.listdir(Dir)
        for item in zip_files:
            if item.endswith(".zip"):
                os.remove(os.path.join(Dir, item))

if __name__ == '__main__':
    #edit this for the collection you want to download
    # ProjectIDs = ['stwstrategymmd','stwstrategyrdr','stwstrategyln1','stwstrategyhn1']
    # Dataset_name = ['MMD','RIDER','Lung1','HN1'] # data director
    # --------------------------
    # ProjectIDs = ['stwstrategyrdr']
    # Dataset_name = ['RIDER'] # data directory

    # ProjectIDs = ['stwstrategymmd']
    # Dataset_name = ['MMD'] # data 

    # ProjectIDs = ['stwstrategyln1']
    # Dataset_name = ['Lung1'] # data directory
    
    ProjectIDs = ['stwstrategyhn1']
    Dataset_name = ['HN1'] # data directory
    # Working directory. ./Data in FAIR-Radiomics
    WorkingDir = os.path.join(os.getcwd(),'DataTest')
    collectionURL = 'https://xnat.bmia.nl' #edit this if you are using a different XNAT repo
    main()
