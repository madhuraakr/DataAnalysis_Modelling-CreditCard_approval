# -*- coding: utf-8 -*-
"""KNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xuuMSlZ88JZhd8TiCmbDLJFfnfbjE7mJ
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
plt.style.use('ggplot')
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")
from sklearn.preprocessing import MinMaxScaler
from imblearn.over_sampling import SMOTE
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.metrics import plot_confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
from statsmodels.graphics.gofplots import qqplot
from sklearn.metrics import classification_report

from google.colab import drive
drive.mount('/content/drive')

#Collecting the data
application = pd.read_excel('/content/drive/My Drive/application_record.xlsx')
application.head()

credit = pd.read_excel('/content/drive/My Drive/credit_record.xlsx')
credit.head()

"""#### Data Understanding and Data Pre-processing

###### Application record
* ID: Unique Id of the row
* CODE_GENDER: Gender of the applicant. M is male and F is female.
* FLAG_OWN_CAR: Is an applicant with a car. Y is Yes and N is NO.
* FLAG_OWN_REALTY: Is an applicant with realty. Y is Yes and N is No.
* CNT_CHILDREN: Count of children.
* AMT_INCOME_TOTAL: the amount of the income.
* NAME_INCOME_TYPE: The type of income (5 types in total).
* NAME_EDUCATION_TYPE: The type of education (5 types in total).
* NAME_FAMILY_STATUS: The type of family status (6 types in total).
* DAYS_BIRTH: The number of the days from birth (Negative values).
* DAYS_EMPLOYED: The number of the days from employed (Negative values).
* FLAG_MOBIL: Is an applicant with a mobile. 1 is True and 0 is False.
* FLAG_WORK_PHONE: Is an applicant with a work phone. 1 is True and 0 is False.
* FLAG_PHONE: Is an applicant with a phone. 1 is True and 0 is False.
* FLAG_EMAIL: Is an applicant with a email. 1 is True and 0 is False.
* OCCUPATION_TYPE: The type of occupation (19 types in total). This column has missing values.
* CNT_FAM_MEMBERS: The count of family members.
"""

application.shape

#Finding missing values
application.isnull().sum()

del application['OCCUPATION_TYPE']

#Check for duplicate records
application['ID'].nunique() # the total rows are 438,557. This means it has duplicates

application = application.drop_duplicates('ID', keep='last') 
# we identified that there are some duplicates in this dataset
# we will be deleting those duplicates and will keep the last entry of the ID if its repeated.

"""##### Data Viz"""

#Count of children
fig = plt.figure(figsize=(7,4))
sns.countplot(x="CNT_CHILDREN",data=application,linewidth=2,edgecolor=sns.color_palette("dark", 1))
CNT_CHILDREN = application['CNT_CHILDREN'].value_counts()
for a,b in zip(range(len(CNT_CHILDREN)), CNT_CHILDREN):
    plt.text(a, b+50, '%.0f' % b, ha='center', va= 'bottom',fontsize=14)
plt.show()

#Count of family members
fig = plt.figure(figsize=(7,4))
sns.countplot(x="CNT_FAM_MEMBERS", data=application, palette="Greens_d")
CNT_FAM_MEMBERS = application.CNT_FAM_MEMBERS.apply(int).value_counts().sort_index()
for a,b in zip(range(len(CNT_FAM_MEMBERS)), CNT_FAM_MEMBERS):
    plt.text(a, b+50, '%.0f' % b, ha='center', va= 'bottom',fontsize=12)

plt.show()

#Distribution of Total income
fig = plt.figure(figsize=(5,4))
sns.distplot(application['AMT_INCOME_TOTAL'])
plt.title('Income Distribution')
plt.xlabel('Income')
plt.ylabel('Frequency')
plt.show()

fig = plt.figure(figsize=(5,4))
age = application.DAYS_BIRTH.apply(lambda x: int(-x / 365.25))
age_plot = pd.Series(age, name="age")
sns.distplot(age_plot)
plt.show()

#The number of the days from employed
fig = plt.figure(figsize=(5,4))
employed_year = application[application.DAYS_EMPLOYED<0].DAYS_EMPLOYED.apply(lambda x: int(-x // 365.25))
employed_plot = pd.Series(employed_year, name="employed_year")
sns.distplot(employed_plot)
plt.show()

#Gender proportion in applicants
gender_val = application.CODE_GENDER.value_counts(normalize = True)
gender_val
gender_val.plot.pie()
plt.show()

"""Around 67.14% of the applicants are female"""

#Applicants with cars
fig = plt.figure(figsize=(3,3))
x = application['FLAG_OWN_CAR'].value_counts()
sns.barplot(x.index,x)

#Applicant realty
fig = plt.figure(figsize=(3,3))
x = application['FLAG_OWN_REALTY'].value_counts()
sns.barplot(x.index,x)

#Type of income
fig = plt.figure(figsize=(9,3))
x = application['NAME_INCOME_TYPE'].value_counts()
sns.barplot(x.index,x)

#Level of education
fig = plt.figure(figsize=(12,3))
x = application['NAME_EDUCATION_TYPE'].value_counts()
sns.barplot(x.index,x)

#Education level and income relation
fig = plt.figure(figsize=(12,2))
application.groupby(["NAME_EDUCATION_TYPE"]).AMT_INCOME_TOTAL.mean().sort_values(ascending=False).plot.barh()
plt.show()

#Type of family status
fig = plt.figure(figsize=(12,2))
x = application['NAME_FAMILY_STATUS'].value_counts()
sns.barplot(x.index,x)

#Applicants' housing type
fig = plt.figure(figsize=(12,3))
x = application['NAME_HOUSING_TYPE'].value_counts()
sns.barplot(x.index,x)

#Outlier detection
d=application[['AMT_INCOME_TOTAL','DAYS_BIRTH','DAYS_EMPLOYED']]
d.plot(kind='box', subplots=True, sharex=False, sharey=False, figsize=(10,10), layout=(3,4))
plt.show()

#Outlier removal(not used,just checking)
print('original shape of dataset :',d.shape)
#criteria
Q1 = d.quantile(0.25)
Q3 = d.quantile(0.75)
IQR = Q3-Q1
max_ = Q3+1.5*IQR
min_ = Q1-1.5*IQR
#filter the outlier s
condition = (d <= max_) & (d >= min_)
condition = condition.all(axis=1)
df = d[condition]
print('filtered dataset shape : ',df.shape)
df.plot(kind='box', subplots=True, sharex=False, sharey=False, figsize=(10,10), layout=(3,4))
plt.show()

#Checking for normalization
fig = plt.figure(figsize=(6,3))
sns.distplot(application['AMT_INCOME_TOTAL'])
plt.title('Income Distribution')
plt.xlabel('Income')
plt.ylabel('Frequency')
plt.show()

fig = plt.figure(figsize=(6,1))
qqplot(application[['AMT_INCOME_TOTAL']], line='s')
plt.show()

#Outlier detection-Method2
Q1 = application[['AMT_INCOME_TOTAL','DAYS_EMPLOYED']].quantile(0.25)
Q3 = application[['AMT_INCOME_TOTAL','DAYS_EMPLOYED']] .quantile(0.75)
IQR = Q3-Q1
IQR

application['DAYS_EMPLOYED']=application[['DAYS_EMPLOYED']]*-1
application['DAYS_BIRTH']=application[['DAYS_BIRTH']]*-1
application.head()

"""Since the features are not normally distibuted, we cannot standardize the dataset, instead we normalize. The dataset will be normalised after after the 2 sub-datasets-'application' and 'credit'.

##### Credit record
This is a csv file with credit record for a part of ID in application record. We can treat it a file to generate labels for modeling. For the applicants who have a record more than 59 past due, they should be rejected

* ID: Unique Id of the row in application record.
* MONTHS_BALANCE: The number of months from record time.
* STATUS: Credit status for this month.


  X: No loan for the month
  C: paid off that month 
  0: 1-29 days past due 
  1: 30-59 days past due 
  2: 60-89 days overdue
  3: 90-119 days overdue 
  4: 120-149 days overdue 
  5: Overdue or bad debts, write-offs for more than 150 days
"""

credit.shape

#Checking for inconsistent data types
credit.info()

#Check for duplicate records
credit['ID'].nunique() 
# this has around 45,000 unique rows as there are repeating entries for different monthly values and status.

#Finding missing values
credit.isnull().sum()

#Checking for outliers
fig = plt.figure(figsize=(3,2))
credit['MONTHS_BALANCE'].plot(kind='box')

#records matching in two datasets
len(set(credit['ID']).intersection(set(application['ID'])))

fig = plt.figure(figsize=(7,4))
ax = fig.add_subplot()
ax.set_title('Correlation Plot', fontsize=18)
sns.heatmap(application[['CNT_CHILDREN', 'AMT_INCOME_TOTAL', 'DAYS_BIRTH', 'DAYS_EMPLOYED', 'FLAG_WORK_PHONE', 
                         'FLAG_PHONE', 'FLAG_EMAIL', 'CNT_FAM_MEMBERS']].corr(), ax=ax)

"""There's a strong correlation between DAYS_EMPLOYED and DAYS_BIRTH, CNT_FAM_MEMBERS and CNT_CHIDREN"""

#calculating months from today column to see how much old the month is 
credit['Months_from_today'] = credit['MONTHS_BALANCE']*-1
credit = credit.sort_values(['ID','Months_from_today'], ascending=True)
credit.head(3)

del credit['MONTHS_BALANCE']

application1=application.copy()

#LabelEncoding-transforming all the non numeric data columns into datacolumns of 0 and 1s
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
for x in application1:
    
    if application1[x].dtypes=='object':
        application1[x] = le.fit_transform(application1[x])

application1.head()

"""**Understanding the Response variable- 'Status':**

---






"""

credit['STATUS'].value_counts()

#Status will be the label/prediction result for our model
#Replacing the value C and X with 0 as it is the same type and 1,2,3,4,5 are classified as 1 because they are the same type
credit['STATUS'].replace({'C': 0, 'X' : 0}, inplace=True)
credit['STATUS'] = credit['STATUS'].astype('int')
credit['STATUS'] = credit['STATUS'].apply(lambda x:1 if x >= 2 else 0)

#Normalizing the Status counts
credit['STATUS'].value_counts(normalize=True)

"""It can be see that the data is oversampled for the labels since 
'0' are 99% '1' are only 1% in the whole dataset.This oversampling issue needs to be addressed in order to make sense of the further analysis.This problem will be dealt with after combining both datasets.
"""

#Grouping the data in 'credit' dataset by 'ID' so that we can join it with 'application' dataset
credit_grp = credit.groupby('ID').agg(max).reset_index()
credit_grp.head()

# Combining the datasets
df = application1.join(credit_grp.set_index('ID'), on='ID', how='inner')
df.head()

df.info()



#Splitting data
X = df.iloc[:,:] # All the variables except labels
X = X.drop('STATUS',  axis = 1)
X = X.drop('ID',  axis = 1)
y = df.iloc[:,-2] # Labels

#Creating the test train split first
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.3)

!pip install category_encoders

import category_encoders

#Fitting and transforming the data into a scaler for accurate result
mms = MinMaxScaler()
X_scaled = pd.DataFrame(mms.fit_transform(X_train), columns=X_train.columns)
X_test_scaled = pd.DataFrame(mms.transform(X_test), columns=X_test.columns)

from imblearn.over_sampling import SMOTE
oversample = SMOTE()
X_balanced, y_balanced = oversample.fit_resample(X_scaled, y_train)
X_test_balanced, y_test_balanced = oversample.fit_resample(X_test_scaled, y_test)
# we have addressed the issue of oversampling here

y_balanced=pd.DataFrame(y_balanced)
y_test_balanced=pd.DataFrame(y_test_balanced)
print(y_train.value_counts())
print(y_balanced.value_counts())
print(y_test.value_counts())
print(y_test_balanced.value_counts())

#### K-Nearest Neighbors (KNN)
####Generate a k-NN model using neighbors value.
model = KNeighborsClassifier(n_neighbors=7)
model.fit(X_balanced, y_balanced)
y_predict = model.predict(X_test_balanced)

print('Accuracy Score is {:.4}'.format(accuracy_score(y_test_balanced, y_predict)))
print(pd.DataFrame(confusion_matrix(y_test_balanced,y_predict)))
class_names = ['0','1']
titles_opt = [("Confusion matrix, without normalization", None),("Normalized confusion matrix", 'true')]
for title, normalize in titles_opt:
    disp = plot_confusion_matrix(model, X_test_balanced, y_test_balanced,display_labels=class_names,cmap=plt.cm.Blues,normalize=normalize)
    disp.ax_.set_title(title)

print(title)
print(disp.confusion_matrix)   
plt.show()
result1 = classification_report(y_test_balanced, y_predict)
print("Classification Report:",)
print (result1)

neighbors = np.arange(1, 9)
train_accuracy = np.empty(len(neighbors))
test_accuracy = np.empty(len(neighbors))
# Loop over K values
for i, k in enumerate(neighbors):
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_balanced, y_balanced)
      
    # Compute traning and test data accuracy
    train_accuracy[i] = knn.score(X_balanced, y_balanced)
    test_accuracy[i] = knn.score(X_test_balanced, y_test_balanced)
  
# Generate plot
plt.plot(neighbors, test_accuracy, label = 'Testing dataset Accuracy')
plt.plot(neighbors, train_accuracy, label = 'Training dataset Accuracy')
  
plt.legend()
plt.xlabel('n_neighbors')
plt.ylabel('Accuracy')
plt.show()#the graph isn't intersecting

"""If there are three categories, a, b and c and if we assigned them the value 1, 2 and 3 you would implicitly be assuming that category a is closer to category b than c in our feature space (distance 1 compared to distance 2).If we enumerated the categorical variable then you would introduce a bias about which categories are “closer”. One hot encoding can be used for the categorical data.

## **Differentiating the features as Binary, Numerical and Categorical**
"""

#filtering the columns that have non numeric values
obj = pd.DataFrame(application.dtypes =='object').reset_index()
object_type = obj[obj[0] == True]['index']
object_type

object_type=pd.DataFrame(object_type)
object_type
object_type.iloc[4,0]

binary=[]
cat=[]
num=[]

#Deciding if features are Binary or Categorical
for i in range(len(object_type)):
  col=object_type.iloc[i,0]
  if application[col].value_counts().count()<3:
    binary.append(col)
  else:
    cat.append(col)

"""Using the number of levels under non-numerical features, we decide if they are Binary or Categorical features."""

##filtering the columns that have numeric values
num_type = pd.DataFrame(application.dtypes != 'object').reset_index()
num_type = num_type[num_type[0] ==True]['index']
num_type

##Deciding if features are Binary or Categorical
num_type=pd.DataFrame(num_type)
for i in range(len(num_type)):
  col=num_type.iloc[i,0]
  if application[col].value_counts().count()<3:
    binary.append(col)
  else:
    num.append(col)

"""Using the number of levels under numerical features, we decide if they are Binary or Categorical features, as features with 1 and 0 are also named numerical."""

#BINARY FEATURES

for i in binary:
  print(i)  #Feature names
application[binary].head()  #Binary Features

# CATEGORICAL FEATURES
for i in cat:
  print(i)
application[cat].head()#Categorical features

#NUMERICAL FEATURES

for i in num:
  print(i)
application[num].head()#Numerical features

# Combining the datasets
df1 = application.join(credit_grp.set_index('ID'), on='ID', how='inner')
df1.head()

"""### One Hot Encoding (Categorical variables)
Despite the different names, the basic strategy is to convert each category value into a new column and assigns a 1 or 0 (True/False) value to the column. This has the benefit of not weighting a value improperly but does have the downside of adding more columns to the data set.
"""

for i in cat:
  print(i)

#get_dummies() function is named this way because it creates dummy/indicator variables (aka 1 or 0).
df1=pd.get_dummies(df1, columns=df1[cat].columns,prefix=["Income_type","Edu_type","Fam_stat","House_type"])

df1.head()

"""### Label Encoding(Binary features)"""

for i in binary:
  print(i)

#LabelEncoding-transforming all the non numeric data columns into datacolumns of 0 and 1s
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
for x in binary:
        df1[x] = le.fit_transform(df1[x])

df1.head()

"""### KNN Classifier"""

'''#Normalizing
import sklearn as sk
df1_norm=sk.preprocessing.normalize(df1, norm='l2', axis=0, copy=False, return_norm=False)
df1_norm=pd.DataFrame(df1_norm)
df1_norm.head()'''

#dataf=((df1-df1.min())/(df1.max()-df1.min()))*1
#dataf

X = df1.iloc[:,:] # All the variables except labels
X = X.drop('STATUS',  axis = 1)
X = X.drop('ID',  axis = 1)
y = df1.loc[:,'STATUS'] # Labels

#Creating the test train split first
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.3)

#Fitting and transforming the data into a scaler for accurate result
mms = MinMaxScaler()
X_scaled = pd.DataFrame(mms.fit_transform(X_train), columns=X_train.columns)
X_test_scaled = pd.DataFrame(mms.transform(X_test), columns=X_test.columns)

oversample = SMOTE()
X_balanced, y_balanced = oversample.fit_resample(X_scaled, y_train)
X_test_balanced, y_test_balanced = oversample.fit_resample(X_test_scaled, y_test)
# we have addressed the issue of oversampling here

y_balanced=pd.DataFrame(y_balanced)
y_test_balanced=pd.DataFrame(y_test_balanced)
print(y_train.value_counts())
print(y_balanced.value_counts())
print(y_test.value_counts())
print(y_test_balanced.value_counts())

#### K-Nearest Neighbors (KNN)
####Generate a k-NN model using neighbors value.

model = KNeighborsClassifier(n_neighbors=7)
model.fit(X_balanced, y_balanced)
y_predict = model.predict(X_test_balanced)

print('Accuracy Score is {:.4}'.format(accuracy_score(y_test_balanced, y_predict)))
print(pd.DataFrame(confusion_matrix(y_test_balanced,y_predict)))
class_names = ['0','1']
titles_opt = [("Confusion matrix, without normalization", None),("Normalized confusion matrix", 'true')]
for title, normalize in titles_opt:
    disp = plot_confusion_matrix(model, X_test_balanced, y_test_balanced,display_labels=class_names,cmap=plt.cm.Blues,normalize=normalize)
    disp.ax_.set_title(title)

print(title)
print(disp.confusion_matrix)   
plt.show()
result1 = classification_report(y_test_balanced, y_predict)
print("Classification Report:",)
print (result1)

#### K-Nearest Neighbors (KNN)
####Generate a k-NN model using neighbors value.

model = KNeighborsClassifier(n_neighbors=7,metric='manhattan')
model.fit(X_balanced, y_balanced)
y_predict = model.predict(X_test_balanced)

print('Accuracy Score is {:.4}'.format(accuracy_score(y_test_balanced, y_predict)))
print(pd.DataFrame(confusion_matrix(y_test_balanced,y_predict)))
class_names = ['0','1']
titles_opt = [("Confusion matrix, without normalization", None),("Normalized confusion matrix", 'true')]
for title, normalize in titles_opt:
    disp = plot_confusion_matrix(model, X_test_balanced, y_test_balanced,display_labels=class_names,cmap=plt.cm.Blues,normalize=normalize)
    disp.ax_.set_title(title)

print(title)
print(disp.confusion_matrix)   
plt.show()
result1 = classification_report(y_test_balanced, y_predict)
print("Classification Report:",)
print (result1)

neighbors = np.arange(1, 9)
train_accuracy = np.empty(len(neighbors))
test_accuracy = np.empty(len(neighbors))
# Loop over K values
for i, k in enumerate(neighbors):
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_balanced, y_balanced)
      
    # Compute traning and test data accuracy
    train_accuracy[i] = knn.score(X_balanced, y_balanced)
    test_accuracy[i] = knn.score(X_test_balanced, y_test_balanced)
  
# Generate plot
plt.plot(neighbors, test_accuracy, label = 'Testing dataset Accuracy')
plt.plot(neighbors, train_accuracy, label = 'Training dataset Accuracy')
  
plt.legend()
plt.xlabel('n_neighbors')
plt.ylabel('Accuracy')
plt.show()#the graph isn't intersecting

neighbors = np.arange(1, 9)
train_accuracy = np.empty(len(neighbors))
test_accuracy = np.empty(len(neighbors))
# Loop over K values
for i, k in enumerate(neighbors):
    knn = KNeighborsClassifier(n_neighbors=k,metric='manhattan')
    knn.fit(X_balanced, y_balanced)
      
    # Compute traning and test data accuracy
    train_accuracy[i] = knn.score(X_balanced, y_balanced)
    test_accuracy[i] = knn.score(X_test_balanced, y_test_balanced)
  
# Generate plot
plt.plot(neighbors, test_accuracy, label = 'Testing dataset Accuracy')
plt.plot(neighbors, train_accuracy, label = 'Training dataset Accuracy')
  
plt.legend()
plt.xlabel('n_neighbors')
plt.ylabel('Accuracy')
plt.show()#the graph isn't intersecting

neighbors = np.arange(1, 9)
train_accuracy = np.empty(len(neighbors))
test_accuracy = np.empty(len(neighbors))
# Loop over K values
for i, k in enumerate(neighbors):
    knn = KNeighborsClassifier(n_neighbors=k,metric='jaccard')
    knn.fit(X_balanced, y_balanced)
      
    # Compute traning and test data accuracy
    train_accuracy[i] = knn.score(X_balanced, y_balanced)
    test_accuracy[i] = knn.score(X_test_balanced, y_test_balanced)
  
# Generate plot
plt.plot(neighbors, test_accuracy, label = 'Testing dataset Accuracy')
plt.plot(neighbors, train_accuracy, label = 'Training dataset Accuracy')
  
plt.legend()
plt.xlabel('n_neighbors')
plt.ylabel('Accuracy')
plt.show()#the graph isn't intersecting

neighbors = np.arange(1, 9)
train_accuracy = np.empty(len(neighbors))
test_accuracy = np.empty(len(neighbors))
# Loop over K values
for i, k in enumerate(neighbors):
    knn = KNeighborsClassifier(n_neighbors=k,metric='hamming')
    knn.fit(X_balanced, y_balanced)
      
    # Compute traning and test data accuracy
    train_accuracy[i] = knn.score(X_balanced, y_balanced)
    test_accuracy[i] = knn.score(X_test_balanced, y_test_balanced)
  
# Generate plot
plt.plot(neighbors, test_accuracy, label = 'Testing dataset Accuracy')
plt.plot(neighbors, train_accuracy, label = 'Training dataset Accuracy')
  
plt.legend()
plt.xlabel('n_neighbors')
plt.ylabel('Accuracy')
plt.show()#the graph isn't intersecting



"""Input features-Binary"""

X = df1[binary].iloc[:,:] # All the variables except labels
y = df1.loc[:,'STATUS'] # Labels

#Creating the test train split first
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.3)

#Fitting and transforming the data into a scaler for accurate result
mms = MinMaxScaler()
X_scaled = pd.DataFrame(mms.fit_transform(X_train), columns=X_train.columns)
X_test_scaled = pd.DataFrame(mms.transform(X_test), columns=X_test.columns)

from imblearn.over_sampling import SMOTE
oversample = SMOTE()
X_balanced, y_balanced = oversample.fit_resample(X_scaled, y_train)
X_test_balanced, y_test_balanced = oversample.fit_resample(X_test_scaled, y_test)
# we have addressed the issue of oversampling here

#### K-Nearest Neighbors (KNN)
####Generate a k-NN model using neighbors value.
model = KNeighborsClassifier(n_neighbors=7)
model.fit(X_balanced, y_balanced)
y_predict = model.predict(X_test_balanced)

print('Accuracy Score is {:.4}'.format(accuracy_score(y_test_balanced, y_predict)))
print(pd.DataFrame(confusion_matrix(y_test_balanced,y_predict)))
class_names = ['0','1']
titles_opt = [("Confusion matrix, without normalization", None),("Normalized confusion matrix", 'true')]
for title, normalize in titles_opt:
    disp = plot_confusion_matrix(model, X_test_balanced, y_test_balanced,display_labels=class_names,cmap=plt.cm.Blues,normalize=normalize)
    disp.ax_.set_title(title)

print(title)
print(disp.confusion_matrix)   
plt.show()
result1 = classification_report(y_test_balanced, y_predict)
print("Classification Report:",)
print (result1)

#### K-Nearest Neighbors (KNN)
####Generate a k-NN model using neighbors value.

model = KNeighborsClassifier(n_neighbors=7,metric='jaccard')#or euclidean
model.fit(X_balanced, y_balanced)
y_predict = model.predict(X_test_balanced)

print('Accuracy Score is {:.4}'.format(accuracy_score(y_test_balanced, y_predict)))
print(pd.DataFrame(confusion_matrix(y_test_balanced,y_predict)))
class_names = ['0','1']
titles_opt = [("Confusion matrix, without normalization", None),("Normalized confusion matrix", 'true')]
for title, normalize in titles_opt:
    disp = plot_confusion_matrix(model, X_test_balanced, y_test_balanced,display_labels=class_names,cmap=plt.cm.Blues,normalize=normalize)
    disp.ax_.set_title(title)

print(title)
print(disp.confusion_matrix)   
plt.show()
result1 = classification_report(y_test_balanced, y_predict)
print("Classification Report:",)
print (result1)

"""Considering only binary features will not tell about the performance of KNN with binary in this case, as number of features considered also matters. As in the numerical features are more, and for the same reason, the accuracy may bet higher."""

