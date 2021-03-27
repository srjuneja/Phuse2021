from docx import Document
import pandas as pd
import saspy as saspy


# https://stackoverflow.com/questions/58254609/python-docx-parse-a-table-to-panda-dataframe
# document = Document('c:\\temp\\BPI Change from Baseline Report Specification.docx')

def read_docx_tables(file_path):
    document = Document(file_path)
    tables = []
    for table in document.tables:
        df = [['' for i in range(len(table.columns))] for j in range(len(table.rows))]
        for i, row in enumerate(table.rows):
            for j, cell in enumerate(row.cells):
                if cell.text:
                    df[i][j] = cell.text

    tables.append(pd.DataFrame(df))
    print(tables)

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
    print(finaltables)

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


if __name__ == '__main__':
    docx2sasdsets(file_path='c:\\temp\\BPI Change from Baseline Report Specification.docx', lib_folder="C:\\temp\\")