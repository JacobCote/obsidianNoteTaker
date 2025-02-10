
import shutil
from dataclasses import dataclass
from utils import Biblio, Article, Collection


if __name__ == "__main__" : 
    col = Collection(4,'1bc',[])
    col.path
    path = "/Users/jacobcote/Zotero/"
    destPath = "/Users/jacobcote/Desktop/maBiblio/Biblio"
    shutil.copyfile(path+"zotero.sqlite", path+"zotero.db")
    biblio  = Biblio(path,destPath)
    biblio.create_directory()
    biblio.populateAnnot()
    biblio.populateCollections()
    biblio.MakeMD()

    # aller chercher toutes les annotations 
