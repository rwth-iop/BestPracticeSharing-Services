
import pandas as pd
import sqlite3


# read data from data mart
def readTransformedData(silent = True):
    if not silent:  print("- readTransformedData")

    conn = sqlite3.connect('BestPracticeSharing.sqlite')
    c = conn.cursor()
#    df1 = pd.DataFrame(conn.execute("SELECT xValue, yValue, Label FROM TransformedData").fetchall())
    df1 = pd.DataFrame(conn.execute("SELECT * FROM TransformedData").fetchall())
    conn.close()

    df1 = df1.drop(df1.columns[0], axis = 1)

    colnum = len(df1.columns)

    X = df1.iloc[:,0:colnum-1]
    y = df1.iloc[:, colnum-1]

    return X, y


# read clustering result from data mart
def readClusteredData(silent = True):
    if not silent:  print("- readClusteredData")

    conn = sqlite3.connect('BestPracticeSharing.sqlite')
    c = conn.cursor()
    df1 = pd.DataFrame(conn.execute("SELECT * FROM ClusteredData").fetchall())
    conn.close()

    df1 = df1.drop(df1.columns[0], axis = 1)

    colnum = len(df1.columns)

    X = df1.iloc[:,0:colnum-2]
    y = df1.iloc[:, colnum - 2].to_numpy().flatten()
    clustercore = df1.iloc[:, colnum - 1].to_numpy().flatten()

    if not silent:  print("+ readClusteredData")
    return X, y, clustercore


def readClusteredDataDF():
    print("- readClusteredDataDF")

    conn = sqlite3.connect('BestPracticeSharing.sqlite')
    c = conn.cursor()
    df1 = pd.DataFrame(conn.execute("SELECT * FROM ClusteredData").fetchall())
    conn.close()

    colnum = len(df1.columns)
    df1 = df1.rename(columns={df1.columns[colnum-1]: "Clustercore"})
    df1 = df1.rename(columns={df1.columns[colnum-2]: "Label"})

    print("+ readClusteredDataDF")
    return df1


def readClusteredDataDFWithID():
    print("- readClusteredDataWithDF")

    conn = sqlite3.connect('BestPracticeSharing.sqlite')
    c = conn.cursor()
    df1 = pd.DataFrame(conn.execute("SELECT * FROM ClusteredData").fetchall())
    conn.close()

    colnum = len(df1.columns)
    df1 = df1.rename(columns={df1.columns[colnum-1]: "Clustercore"})
    df1 = df1.rename(columns={df1.columns[colnum-2]: "Label"})

    print("+ readClusteredDataWithDF")
    return df1


def readFeedbackData(silent = True):
    if not silent:  print("- readFeedbackData")

    conn = sqlite3.connect('BestPracticeSharing.sqlite')
    c = conn.cursor()
    df1 = pd.DataFrame(conn.execute("SELECT id_punkt1, id_punkt2, feedback FROM Feedback").fetchall())
    conn.close()
    df1.columns = ['id_punkt1', 'id_punkt2', 'feedback']

    X = df1[['id_punkt1','id_punkt2']]
    y = df1[['feedback']].to_numpy().flatten()

    if not silent:  print("+ readFeedbackData")
    return X, y