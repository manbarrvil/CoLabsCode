import pandas as pd

def meas_acq(cursor,list_of_tags):
    df = pd.DataFrame()
    for Tag in list_of_tags:
        # Query to fetch data from TagArray_W table
        cursor.execute("SELECT "+Tag+"_Name,"+Tag+"_Value,"+Tag+"_DT,"+Tag+"_Type FROM TagArray_W")  # Change this to get specific data
        tmp = cursor.fetchone()
        data = {'Tag_Name' : tmp[0], 'Value' : tmp[1], 'DT' : tmp[2], 'Type' : tmp[3]}
        df = pd.concat([df,pd.DataFrame([data])])
    df['Tag_Name'] = df['Tag_Name'].str.replace('_','')
    return df


