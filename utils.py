
import sqlite3
import os
from dataclasses import dataclass
import json
import re
from collections import defaultdict


@dataclass
class Collection:
    num: int
    path: str
    itemList: list
    def makeMD(self):
        for i in self.itemList:
            i.makeMD(self.path)
            
   

class Article:
    def __init__(self,title,metaData,itemID,parentID,isPDF,isAnott = False):
         self.title = title
         self.itemID = itemID
         self.parentID = parentID
         self.isPDF = isPDF
         self.isAnot = isAnott
         self.metaData = metaData
         self.annotations = []
         self.tags = []
         self.dictCollectionItems = dict()
         self.typePrefixDict = defaultdict(lambda: "")
         self.typePrefixDict["#ffd400" ] = ""
         self.typePrefixDict["#ff6666" ] = "## "
         self.typePrefixDict["#5fb236" ] = "### "
         
        
         
    def addAnnotation(self, annotation):
        self.annotations.append(annotation)
    def makeMD(self,path):
        def classer(annotation):
            classe1,classe2, classe3, = annotation[8].split("|")
            classe4 = json.loads(annotation[9])["rects"][0][0] 
            return(int(classe1),int(classe2),int(classe3),classe4)
       

        sort = sorted(self.annotations,key= lambda  x: classer(x))
   
        with open(path+"/"+self.title+".md","w") as f:
            f.write(self.metaData + "\n\n")
            f.write("Tags : ")
            for tag in self.tags:
                f.write("#"+ "_".join(tag.split())+" ")
            
            f.write("\n\n")
            
            for i in range(len(sort)):
                if sort[i][2] == 1:
                    annot = sort[i][4]
                    pattern = r'(?<!\n)( [0-9]{1,2}\. )'
                    annot = re.sub(pattern, r'\n\1', annot)
                    #print(annot)
                    f.write(self.typePrefixDict[sort[i][6]]+ annot)
                    if i < len(sort)-1  :
                        if json.loads(sort[i+1][9])["pageIndex"] != json.loads(sort[i][9])["pageIndex"] :
                            f.write(f"<center>{json.loads(sort[i][9])["pageIndex"]}</center>")
                    else :
                        f.write(f"<center>{json.loads(sort[i][9])["pageIndex"]}</center>")
                    
                        
                ## check si le prochain higlight est proche, si oui, pas mettre de newline
                    
                    newline = "\n\n"
  
                    f.write(newline)
                    
                    
                elif sort[i][2] == 6 :
                    f.write(f"<u>TextBox Note: {sort[i][5]} </u> \n")
                    
                    
                elif sort[i][2] == 2:
                    f.write(f"Post-it Note: {sort[i][5]} \n")
                    


class Biblio:
    def __init__(self,sourcePath,destpath):
        self.traduction = dict()
        self.sourcePath = sourcePath
        self.destPath = destpath
        self.initBiblio()
        self.collectionList = dict()
        
        
        
        articles = dict()
        for i in self.itemAttachements:
            metaData = i[5].rstrip(".pdf").lstrip('storage:').split(" - ")
            name = metaData[-1]
            if len(metaData) >1 :
                metaData = ', '.join(metaData[0:-1])
            else :
                metaData = ""
                
            
            articles[i[0]] = Article(name,metaData,i[0],i[1],i[3]=="application/pdf")
            self.traduction[i[1]] = i[0]
        self.articles = articles
        
        
        
    def initBiblio(self,):
        try:
            # Connect to DB and create a cursor
            sqliteConnection = sqlite3.connect(self.sourcePath+"zotero.db")
            cursor = sqliteConnection.cursor()
            print('DB Init')

            # Write a query and execute it with cursor
            query = 'SELECT * FROM items'
            cursor.execute(query)

            # Fetch and output result
            items  = cursor.fetchall()
            
            
            query = 'SELECT * FROM itemAnnotations'
            cursor.execute(query)


            # Fetch and output result
            itemAnnotations  = cursor.fetchall()
        
            self.itemAttachements = cursor.execute("SELECT * FROM itemAttachments").fetchall()
            self.collectionItems = cursor.execute("SELECT * FROM collectionItems").fetchall()
            self.collections = cursor.execute("SELECT * FROM collections").fetchall()
            self.tags = cursor.execute("SELECT * FROM tags").fetchall()
            self.itemTags = cursor.execute("SELECT * FROM itemTags").fetchall()
            self.itemData = cursor.execute("SELECT * FROM itemData").fetchall()
            self.itemAnnotation = cursor.execute("SELECT * FROM itemAnnotations").fetchall()
            self.deletedCollections = { i[0] for i in cursor.execute("SELECT collectionID FROM deletedCollections").fetchall()}
            print(self.deletedCollections)
            
            
            

            # Close the cursor
            cursor.close()

        # Handle errors
        except sqlite3.Error as error:
            print('Error occurred - ', error)

        # Close DB Connection irrespective of success
        # or failure
        finally:

            if sqliteConnection:
                sqliteConnection.close()
                print('SQLite Connection closed')
        
        
        
    def populateAnnot(self,):
        # create tag dictionnary with tags 
        self.tags = {x[0]: x[1] for x in self.tags }
    
        for annotation in self.itemAnnotation:
            
            self.articles[annotation[1]].addAnnotation(annotation)
        for tag in self.itemTags:
            self.articles[self.traduction[tag[0]]].tags.append(self.tags[tag[1]])
           
            
            

    def create_directory(self):
        
        
        for idx,i in enumerate(self.collections):
            
            if i[2] == None :
                if i[0] not in self.deletedCollections:
                    self.collectionList[idx+1] = Collection(path=self.destPath+"/"+ i[1],itemList=[], num=idx+1)
                
            else :
                if i[0] not in self.deletedCollections:
            
                    self.collectionList[idx+1] = Collection(path=self.collectionList[i[2]].path + "/" + i[1],itemList=[],num = idx+1)
        self.collectionList[0] = Collection(0,self.destPath+"/+Autres",[])
        for i in self.collectionList.values():
            if not os.path.exists(i.path):
                os.makedirs(i.path)
       
       
                
    def populateCollections(self,):
        self.dictCollectionItems = defaultdict(lambda:[])
        for i in self.collectionItems :
            self.dictCollectionItems[i[1]].append(i[0])
           
       

        
        for articleNum,listCollections in self.dictCollectionItems.items():
            #print(articleNum,listCollections)
            #print(self.articles.keys())
            for collection in listCollections:
                try: 
                    self.collectionList[collection].itemList.append(self.articles[self.traduction[articleNum]])
                except:
                    pass
                    #self.collectionList[0].itemList.append(self.articles[self.traduction[articleNum]])
                    
                
                
    def MakeMD(self,):
        for i in self.collectionList.values():
            i.makeMD()
            
        
                
        
                
        
        

                
     
     
