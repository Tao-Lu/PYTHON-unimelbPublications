
from pyscopus import Scopus
import couchdb

key = '8088bb761a9b0680072b5eb79b89dff7'
# key = '3f2462d7e1fabbb399a54d937b0bcfbf'
scopus = Scopus(key)


def searchDocsByOrcid_Scopus (authorId, CISauthorName):
    
    author_pub_df = scopus.search_author_publication(authorId)
    scopusId = list (author_pub_df.scopus_id)

    for paperid in scopusId:
        try:  
            doc = {}
            doc['_id'] = paperid
            pub_info = scopus.retrieve_abstract(paperid)

            if doc['_id'] in dbPaper:
                # if the current cisAuthor not in cisAuthor list, add the authorid
                # update the cited count
                print('this paper already exist')

                paperInfo = dbPaper.get(doc['_id'])
                currentCISAuthors = paperInfo['CISAuthors']
                if paperInfo['cite_count'] != pub_info['citedby-count']:
                    paperInfo['cite_count'] = pub_info['citedby-count']
               
                if authorId not in currentCISAuthors:
                    paperInfo['CISAuthors'] = currentCISAuthors + "," + authorId
                    print(paperInfo['_id'])
                    dbPaper.save(paperInfo)
                    print('update paper')
                    print('-----------------------------------------------------')

            else:

                doc['title'] = pub_info['title']
                doc['abstract'] = pub_info['abstract']
                doc['coverDate'] = pub_info['prism:coverDate']
                doc['coverDateYear'] = doc['coverDate'].split(',')[0]
                doc['cite_count'] = pub_info['citedby-count']
                doc['paper_type'] = pub_info['subtypeDescription']
                doc['CISAuthors'] = authorId


                if (pub_info['prism:doi'] != 'none'):
                    # use doi to find author id list 
                    searchpaper_df = scopus.search('DOI('+pub_info['prism:doi']+')', count=1)
                else:
                    searchpaper_df = scopus.search('TITLE('+doc['title']+')', count=1)

                authorList = list(searchpaper_df.authors) #list of scopus author id 
                
                doc['co_author'] = authorList[0]

                putOtherAuthorInDB(authorList[0])

                dbPaper.save(doc)
                print('insert new paper')
                print('-----------------------------------------------------')
        except BaseException as e:
            print(e)
            continue

        except couchdb.http.Resource:
            print("couchdb exception")
            continue 
        except Exception as e1:
            print(e1)
            continue 
        
def putOtherAuthorInDB (authorList):
    #如果authorid在CISStaff库中不存在，则是otherAuthor
    #如果是otherAuthor， 并且id不在otherAuthor库里，insert data
    for authorid in authorList:
        try:
            if authorid in dbOtherAuthor or authorid in dbPeople:
                print('this co author already exist')
                continue
            else:
                author_dict = scopus.retrieve_author(authorid)
                doc = {}
                doc['_id'] = authorid
                doc['name'] = author_dict['name']
                doc['affiliation'] = author_dict['affiliation-current']['name']
                affiliationId = author_dict['affiliation-current']['id']
                affil_dict = scopus.retrieve_affiliation(affiliationId)
                doc['affiliation_city'] = affil_dict['city']
                doc['affiliation_country'] = affil_dict['country']
                if(doc['affiliation_country'].lower() == 'australia'):
                    doc['is_Aus'] = 'Y'
                else:
                    doc['is_Aus'] = 'N'
                dbOtherAuthor.save(doc)
                print('insert new co author')
                print('-----------------------------------------------------')

        except BaseException as e:
            print(e)
            continue

        except couchdb.http.Resource:
            print("couchdb exception")
            continue 
        except Exception as e1:
            print(e1)
            continue 

        


#couch db connection
couch=couchdb.Server("http://admin:password@localhost:5984")

try:
    database=couch.create("paperinfo_scopus")

except:
    database=couch["paperinfo_scopus"]

try: 
    database1 = couch.create("coauthorinfo_scopus")

except:
    database1 = couch["coauthorinfo_scopus"]

try:
    database3=couch["staffinfo_scopus"]
except:
    database3=couch.create("staffinfo_scopus")

dbPeople = couch['staffinfo_scopus']
dbPaper = couch['paperinfo_scopus']
dbOtherAuthor = couch['coauthorinfo_scopus']

for doc in dbPeople.view('_all_docs'):
    if '_design' not in doc.id:
        docDetail = dbPeople.get(doc['id'])
        CISauthorId = doc['id']
        CISauthorName = docDetail['fullName']
        searchDocsByOrcid_Scopus(CISauthorId, CISauthorName)


