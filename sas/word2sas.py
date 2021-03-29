from docx import Document
import pandas as pd
import saspy as saspy


# https://stackoverflow.com/questions/58254609/python-docx-parse-a-table-to-panda-dataframe
def docx2sasdsets(file_path, lib_folder):
    document = Document(file_path)
    for table in document.tables:
        doctbls=[]
        tbllist=[]
        rowlist=[]
        for i, row in enumerate(table.rows):
            for j, cell in enumerate(row.cells):
                rowlist.append(cell.text)
            tbllist.append(rowlist)
            rowlist=[]
        doctbls=doctbls+tbllist

    finaltables=pd.DataFrame(doctbls)
    generate_sas_dataset(folder_path=lib_folder, df=finaltables)
    

def initialize_sas_session():
    global sas
    sas = saspy.SASsession()

def close_sas_session():
    sas.disconnect()

# https://www.sas.com/content/dam/SAS/support/en/sas-global-forum-proceedings/2019/3260-2019.pdf
def generate_sas_dataset(folder_path, df):
    libref = "local"
    # initialize sas session
    initialize_sas_session()
    # initialize sas lib
    sas.saslib(libref=libref, path=folder_path)
    # convert data frame to sas dataset
    sas.df2sd(df=df, table="word_tbl", libref=libref)
    # close sas session
    close_sas_session()
