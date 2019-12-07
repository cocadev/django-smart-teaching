import random
import numpy as np
import pandas as pd


def makeDF(tuples, header):
    '''Assumes tuples as Python tuples both empty or non empty; header as a tuple with a convention
       as (RollNumber, Name, Exam-[name]-[max-marks], ..., Lab-[name]-[max-marks], ...,
       Asgn-[name]-[max-marks], ..., Oth-[name]-[max-marks],)

       Returns a Pandas DataFrame with all NULL values replaced by Cipher, and adds a fraud column
       for figuring out cheating factor for later functions.'''

    # make rows, column IDs and marks as a list for DataFrame initialization

    row_index = [int(i) for i in range(1, len(tuples) + 1)]
    col_index = list(header)
    values = list(tuples)

    # DataFrame initialisation

    df = pd.DataFrame(tuples, row_index, col_index)

    # Handling of NULLs

    for col in list(df.columns):
        df[col] = df[col].fillna(value=0)

    # Make a copy of last given exams marks

    df['fraud'] = 0
    df['fraud'] = df[df.columns[-2]]

    return df


def scaleMarks(df):
    '''Assumes df as a Pandas DataFrame.

       Returns a Pandas DataFrame with marks scaled up according to the max-marks defined in the
       column headings'''

    # iterate through all columns and scale marks using apply() attribute of DataFrames

    for exam in list(df.columns):
        if len(exam.split('-')) > 2:
            df[exam] = df[exam].apply(lambda x: x * 100 \
                                                / int(exam.split('-')[2]))

    return df


def createAvg(marks):
    '''Assumes marks as a Pandas DataFrame.

       Returns a DataFrame with added columns for overall weighted average, and individual exam,
       lab, assignments and other evaluations average'''

    # initilaize columns as zero

    marks['overall'] = 0
    marks['avgExam'] = 0
    marks['avgLab'] = 0
    marks['avgAsgn'] = 0
    marks['avgOth'] = 0

    # initialize count variables as zero

    exams = 0
    lab = 0
    asgn = 0
    oth = 0

    # iterate through the column list, filter and sum based on '-' as the additional columns do not have a '-'

    for exam in list(marks.columns):
        if exam.lower().startswith('exam'):
            marks['avgExam'] += marks[exam]
            exams += 1
        elif exam.lower().startswith('lab'):

            marks['avgLab'] += marks[exam]
            lab += 1
        elif exam.lower().startswith('asgn'):

            marks['avgAsgn'] += marks[exam]
            asgn += 1
        elif exam.lower().startswith('oth'):

            marks['avgOth'] += marks[exam]
            oth += 1
        else:

            continue

    # weight and scale marks and divide by total number of instances of similar type counted.
    # Weights based on the strictness  and students' interest in overall exam process

    marks['overall'] = 0.5 * marks['avgExam'] / exams + 0.3 \
                       * marks['avgLab'] / lab + 0.1 * marks['avgAsgn'] / asgn + 0.1 \
                       * marks['avgOth'] / oth

    marks['avgExam'] = marks['avgExam'].apply(lambda x: int(x / exams))
    marks['avgLab'] = marks['avgLab'].apply(lambda x: int(x / lab))
    marks['avgAsgn'] = marks['avgAsgn'].apply(lambda x: int(x / asgn))
    marks['avgOth'] = marks['avgOth'].apply(lambda x: int(x / oth))

    return marks


def createChMarks(marks):
    '''Assumes marks as a Pandas DataFrame.

       Returns a DataFrame with added column ChMarks which would be used further for overall cheating status'''

    # Not included marks for Assignments as they are done by students AT HOME

    marks['ChMarks'] = (marks['avgExam'] + marks['avgLab']
                        + marks['avgOth']) / 3
    return marks


def variance(df):
    '''Assumes df as a Pandas DataFrame.

       Returns the same DataFrame with added column for variance which has variance for all scores for a particular
       student'''

    # Figure out first the columns to be considered for variance calculation. Used '-' as an identifier again

    ls = list(df.columns)
    buffer = []
    for i in range(len(ls)):
        if len(ls[i].split('-')) > 2:
            buffer.append(ls[i])
        else:
            continue

    # initialise column var with iteration based indices so as to use the power of apply() attribute

    df['var'] = [int(i) for i in range(len(df[df.columns[0]]))]

    # make a dummy row index for slicing DataFrame for calculation

    row_index = [int(i) for i in range(1, 1 + len(df[df.columns[0]]))]

    # use the value in var as an indirect reference for the whole row and use the describe() attribute to get std

    df['var'] = df['var'].apply(lambda x: df.loc[row_index,
                                                 buffer].iloc[x].describe()['std'] ** 2)

    return df


def CI(marks, column):
    '''Assumes marks as a Pandas DataFrame and column and a string.

       Returns the 95% confidence interval for the given data as a tuple with entries as (low, high)'''

    column = str(column)

    # CI = mean +- 2*std_error; std_error = std_deviation/sqrt(total observations)

    std_error = marks[column].describe()['std'] / len(marks['avgExam']) \
                ** 0.5
    mean = marks[column].describe()['mean']

    return (mean - 2 * std_error, mean + 2 * std_error)


def width(tup):
    '''Assumes tup as tuple.

       Returns an integer as the difference of 2nd and 1st values of tuple'''

    return tup[1] - tup[0]


def CourseStats(marks):
    '''Assumes marks as a Pandas DataFrame.

       Returns a tuple with values as : (course_difficulty, cheat_risk, list(cheat_flagged),
                                         avg_marks, quartile1, quartile2, quartile3,)

       course_difficulty (str) : HIGH/MODERATE/EASY based on the weighted average and cut-off marks
       cheat_risk (str) : HIGH/MODERATE/LOW based on the spread of Assignment and Other Exam marks
       cheat_flagged (list) : A list of 5 RollNumbers who we believe with some confidence are
                              indulged in academic malpractices in the class as a whole.
       avg_marks (str) : A range of marks where the most of students lie in between.
       quartile1, quartile2, quartile3 (int) : The stastical quartile scores for the overall analysis.'''

    # Calculate course difficulty based on 3rd Quartile scores of students.

    marker = marks['overall'].describe()['75%']
    if marker > 0 and marker < 40:
        course_difficulty = 'HIGH'
    elif marker > 40 and marker < 75:
        course_difficulty = 'MODERATE'
    else:
        course_difficulty = 'EASY'

    # Calculate the probability of cheating based on the width of assignment scores and other marks combined

    cheatProb = 1 - width(CI(marks, 'avgAsgn')) / width(CI(marks,
                                                           'ChMarks'))
    if cheatProb > 0.7 and cheatProb < 1:
        cheat_risk = 'HIGH'
    elif cheatProb > 0.4 and cheatProb < 0.7:
        cheat_risk = 'MODERATE'
    else:
        cheat_risk = 'LOW'

    # Flag out top 5 students whose overall scores and assignment socres tell two different stories

    marks['cheatflagged'] = 0

    marks['cheatflagged'] = marks['avgAsgn'] - marks['ChMarks']
    cheat_flagged = marks.sort_values('cheatflagged', ascending=False)['RollNumber'].iloc[1:6]

    # Calculate the range of marks for most students
    avg_marks = str(round(CI(marks, 'overall')[0], 2)) + '-' + str(round(CI(marks, 'overall')[1], 2))

    # Calculate quartile scores for weighted marks

    quartile1 = round(marks['overall'].describe()['25%'], 2)
    quartile2 = round(marks['overall'].describe()['50%'], 2)
    quartile3 = round(marks['overall'].describe()['75%'], 2)

    return (
        course_difficulty,
        cheat_risk,
        list(cheat_flagged),
        avg_marks,
        [quartile1,
         quartile2,
         quartile3]
    )


def ExamStats(marks):
    '''Assumes marks as a Pandas DataFrame.

       Returns a tuple with values as : (exam_difficulty, cheat_risk, list(cheat_flagged),
                                         avg_marks, quartile1, quartile2, quartile3,)

       exam_difficulty (str) : HIGH/MODERATE/EASY based on the exam performance
       cheat_risk (str) : HIGH/MODERATE/LOW based on the unevenness in marks
       cheat_flagged (list) : A list of 5 RollNumbers who we believe with some confidence should
                              be re-evaluated
       avg_marks (str) : A range of marks where the most of students lie in between.
       quartile1, quartile2, quartile3 (int) : The stastical quartile scores for the overall analysis.'''

    # Figure out the name of last exam and store it in location

    temp = list(marks.columns)
    count = 1
    for i in range(len(temp)):
        if len(temp[i].split('-')) > 2:
            count += 1
    location = temp[count]

    # Calculate the difficulty based on 2nd quartile cut-offs

    marker = marks[location].describe()['50%']
    if marker > 0 and marker < 40:
        exam_difficulty = 'HIGH'
    elif marker > 40 and marker < 75:
        exam_difficulty = 'MODERATE'
    else:
        exam_difficulty = 'EASY'

    # Build the frequency table for digit occurences, add the numbers not present in DataFrame with zero occurence

    freq_df = marks['fraud'].apply(lambda x: int(x % 10)).value_counts()

    for i in range(10):
        try:
            if freq_df.loc[i] >= 0:
                continue
        except:
            freq_df.loc[i] = 0

    # Calculate the variance of the same Dataframe and figure out cheating risk

    cheat_var = freq_df.describe()['std'] ** 2
    if cheat_var < 15:
        cheat_risk = 'LOW'
    if cheat_var > 15 and cheat_var < 80:
        cheat_risk = 'MODERATE'
    else:
        cheat_risk = 'HIGH'

    # Find the number with most occurences, sample 5 random roll numbers with that number for re-evaluation

    max_repeat = freq_df.index[0]
    marks['fraud'] = marks['fraud'].apply(lambda x: int(x % 10))
    suspicious = marks[marks['fraud'] == max_repeat]['fraud']
    if len(suspicious) > 5:
        check_sheets_index = random.sample(list(range(0, len(suspicious))), 5)
        cheat_flagged = []
        for index in check_sheets_index:
            cheat_flagged.append(marks['RollNumber'].iloc[index])
    else:
        cheat_flagged = []

    # Calculate the range of marks for most students

    avg_marks = str(round(CI(marks, location)[0], 2)) + '-' + str(round(CI(marks, location)[1], 2))

    # Calculate quartile scores for exam marks

    quartile1 = round(marks[location].describe()['25%'], 2)
    quartile2 = round(marks[location].describe()['50%'], 2)
    quartile3 = round(marks[location].describe()['75%'], 2)

    return (
        exam_difficulty,
        cheat_risk,
        cheat_flagged,
        avg_marks,
        [quartile1,
         quartile2,
         quartile3],
    )


def PersistentLabels(df):
    '''Assumes df as a Pandas DataFrame.

       Returns a tuple with values as (consistent, moderately_varying, highly_varying,)

       consistent (list) : RollNumbers have almost no variation in their marks obtained so far.
       moderately_varying (list) : RollNumbers have some variation in their marks obtained so far.
       highly_varying (list) : RollNumbers have a high variation in their marks obtained so far.'''

    # calculate and filter the roll number list

    consistent = list(df[df['var'] < 30]['RollNumber'])
    moderately_varying = list(df[(df['var'] > 30) & (df['var']
                                                     < 150)]['RollNumber'])
    highly_varying = list(df[df['var'] > 150]['RollNumber'])

    return (consistent, moderately_varying, highly_varying)


def PerformanceLabels(df):
    '''Assumes df as a Pandas DataFrame.

       Returns a tuple with values as (exceptional, promising, average, needy,)

       exceptional (list) : RollNumbers with really good performance overall.
       promising (list) : RollNumbers who can be pushed to top with a little efforts.
       average (list) : RollNumbers who are just a few steps from failing marks and need some attention.
       needy (list) : RollNumbers who are in an immediate need of attention.'''

    # Calculate and filter the roll number list

    exceptional = list(df[df['overall'] > 85]['RollNumber'])
    promising = list(df[(df['overall'] < 85) & (df['overall']
                                                > 50)]['RollNumber'])
    average = list(df[(df['overall'] < 50) & (df['overall']
                                              > 30)]['RollNumber'])
    needy = list(df[df['overall'] < 30]['RollNumber'])

    return (exceptional, promising, average, needy)


def mainFunc(df):
    '''Assumes df as a Pandas DataFrame.

       Returns the top needy students based on algo as a list.'''

    # initialise an empty column to save scores

    df['temp'] = 1 / df['overall'] + df['var']
    return list((df.sort_values('temp', ascending=False)['RollNumber'])[0:5])

def initialse(tuples, headers):
    df = makeDF(tuples, headers)
    df = scaleMarks(df)
    df = createAvg(df)
    df = createChMarks(df)
    df = variance(df)
    return df

def OverallMarks(df):
    '''Assumes df as a Pamdas DataFrame.

       Returns overall weighted marks of students as a list.'''

    return list(df['overall'])

def BoxPlot(df):
    '''Assumes df as a Pandas DataFrame.

       Returns the scaled marks for visualization as a tuple.'''

    box = df[['avgExam', 'avgLab', 'avgAsgn', 'avgOth']]
    #box.to_csv('boxplot.csv', index = False)
    return tuple([tuple(x) for x in box.to_records(index=False)])




def getRank(df, exam):
    '''Assumes df as a Pandas dataframe, amd exam as a string.
    
       Returns a dataframe with ranks according to roll number.'''

    # Sort values according to the particular exam on Roll number column.
    examRank = df.sort_values(exam, ascending=False)['RollNumber']

    # initialise a dummy column later to be used as the rank.
    temp = [int(i) + 1 for i in range(len(df['RollNumber']))]

    # join the two columns in a dataframe and sort according to Roll number.
    df1 = pd.DataFrame({exam: temp, 'RollNumber': examRank})
    df1.sort_values('RollNumber', inplace=True)

    return df1


def getRankMatrix(df):
    '''Assumes df as a Pandas DataFrame.
    
        Returns a tuple of tuples with individual type of exam ranks.'''

    # find individual ranks for classes of exams
    df1 = getRank(df, 'avgExam')
    df2 = getRank(df, 'avgLab')
    df3 = getRank(df, 'avgAsgn')
    df4 = getRank(df, 'avgOth')
    df5 = getRank(df, 'overall')

    # make the combines dataframe
    temp = df['RollNumber']
    dfRank = pd.DataFrame(
        {'RollNumber': temp, 'ClassRank': df5['overall'], 'ExamRank': df1['avgExam'], 'LabRank': df2['avgLab'],
         'AsgnRank': df3['avgAsgn'], 'OthRank': df4['avgOth']})

    return tuple([tuple(x) for x in dfRank.to_records(index=False)])


def ExamDetails(df):
    '''Assumes df as a Pandas DataFrame.
    
    Returns a listof lists with individual exam analysis'''

    details = []

    # for all the exams entered, find CI, max marks and exam name.
    for exam in df.columns:
        if len(exam.split('-')) > 2:
            avgCI = str(round(CI(df, exam)[0], 2)) + '-' + str(round(CI(df, exam)[1], 2))
            examName = exam
            maxMarks = round(max(df[exam]), 2)
            details.append([examName, avgCI, maxMarks])

    return details


def findBestExam(i):
    '''Assumes i as an int.
    
       Returns a string with the value as the exam with maximum marks in any Dataframe record'''

    # find exams
    evals = []
    for exam in df.columns:
        if len(exam.split('-')) > 2:
            evals.append(exam)

    # Boolean Series with True at the desired location
    check = df[evals].iloc[i] == df.iloc[i]['best']

    # list of all conducted exam columns
    temp = df[evals].columns

    # find the name of exam, as per the faculty
    for seek in range(len(temp)):
        if check[seek] == True:
            exam = temp[seek].split('-')[1]
    return exam


def findWorstExam(i):
    '''Assumes i as an int.
    
       Returns a string with the value as the exam with minimum marks in any Dataframe record'''

    # find exams
    evals = []
    for exam in df.columns:
        if len(exam.split('-')) > 2:
            evals.append(exam)

    # Boolean Series with True at the desired location
    check = df[evals].iloc[i] == df.iloc[i]['worst']

    # list of all conducted exam columns
    temp = df[evals].columns

    # find the name of exam, as per the faculty
    for seek in range(len(temp)):
        if check[seek] == True:
            exam = temp[seek].split('-')[1]

    return exam


def studentMarks(dfArg):
    '''Assumes dfArg as a Pandas DataFrame.

       Returns a tuple of tuples, with best exam and worst exam performances.'''

    # find all the exam names
    global df
    df = dfArg
    evals = []
    for exam in dfArg.columns:
        if len(exam.split('-')) > 2:
            evals.append(exam)
    # initialise new attributes with their iterative location index to use the power of lambda functions.
    dfArg['best'] = [i for i in range(len(dfArg['RollNumber']))]
    dfArg['worst'] = [i for i in range(len(dfArg['RollNumber']))]
    dfArg['bestExam'] = [i for i in range(len(dfArg['RollNumber']))]
    dfArg['worstExam'] = [i for i in range(len(dfArg['RollNumber']))]

    # Find the max or min oerformance of the record.
    dfArg['best'] = dfArg['best'].apply(lambda x: max(dfArg[evals].iloc[x]))
    dfArg['worst'] = dfArg['worst'].apply(lambda x: min(dfArg[evals].iloc[x]))

    # Find the best or worst exam name.
    dfArg['bestExam'] = dfArg['bestExam'].apply(findBestExam)
    dfArg['worstExam'] = dfArg['worstExam'].apply(findWorstExam)

    # rounding off
    dfArg['best'] = dfArg['best'].apply(lambda x: round(x, 2))
    dfArg['worst'] = dfArg['worst'].apply(lambda x: round(x, 2))

    # Make new dataframe
    dfArg1 = dfArg[['RollNumber', 'best', 'worst', 'bestExam', 'worstExam']]

    # Coercion
    ret = tuple([tuple(x) for x in dfArg1.to_records(index=False)])

    return ret


def BoxPlot(df):
    '''Assumes df as a Pandas DataFrame.

       Returns the scaled marks for visualization as a tuple
       as a list of columns of ['avgExam', 'avgLab', 'avgAsgn', 'avgOth']'''

    box = df[['avgExam', 'avgLab', 'avgAsgn', 'avgOth']]

    return tuple([tuple(x) for x in box.to_records(index=False)])



