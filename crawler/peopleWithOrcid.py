import time
import requests 
from bs4 import BeautifulSoup
import couchdb
from pyscopus import Scopus


count = 0

def findScopusIdByOrcid (orcid, firstName, lastName):
    try:
        search_df =scopus.search_author('ORCID('+orcid+')')
        authorId = list(search_df.author_id)
        print(authorId)
        if len(authorId) == 1:
            return authorId[0]

    except Exception as notfoundOrcid: 
        return findScopusIdByName(firstName, lastName)


def findScopusIdByName(firstName, lastName):
    #这个作者在scopus上没有orcid，用名字搜
    #2. School of Computing and Information Systems       60118847
    #3. University of Melbourne       60026553
    #1. Computing &amp; Information Systems      123209774

    try: 
        search_df =scopus.search_author("AUTHLASTNAME("+familyName+") and AUTHFIRST("+givenName+")")
        affiliationList = list(search_df.affiliation_id)
        personId = list(search_df.author_id)
        i = 0
        found = 0
        for affilId in affiliationList:
            if affilId == "123209774":
                found = 1
                break
            if affilId == "60118847":
                found = 1
                break
            if affilId == "60026553":
                found = 1
                break
            i = i+1
        if found == 1:
            scopusId = personId[i]
            return scopusId
        else: 
            raise Exception 

    except Exception as authorNotfound:
        
        print("really cannot find the person")
        return 0







key = '8088bb761a9b0680072b5eb79b89dff7'
scopus = Scopus(key)


#couch db
couch=couchdb.Server("http://jingjing:Jing1201@localhost:5984")
try:
    database=couch["staffinfo_scopus"]
except:
    database=couch.create("staffinfo_scopus")



#academic staff
staffUrlList = ['https://cis.unimelb.edu.au/people/#academic','https://cis.unimelb.edu.au/people/#research','https://cis.unimelb.edu.au/people/#professional']
#orcid url
orcidUrl = 'https://pub.orcid.org/v3.0/search/?q='
AND = '+AND+'
text = 'text:"University+of+Melbourne"'

for url in staffUrlList:
    staffResponse = requests.get(url)
    staffSoup = BeautifulSoup(staffResponse.text, 'html.parser')
    # find the div which contains academic staffs

    if 'academic' in url:
        staffType = 'academic'
    elif 'research' in url:
        staffType = 'research'
    elif 'professional' in url:
        staffType = 'professional'

    resultDiv = staffSoup.find(name = 'div', attrs = {'id' : staffType})
    # inside the div, find the table which contains the staff's info
    staffListTable = resultDiv.find(name = 'tbody')
    # inside the table, 
    staffList = staffListTable.find_all(name = 'tr')

    staffInfoList = []  

    for staff in staffList:
        staffInfo = staff.find_all(name = 'td')
    
        givenName = staffInfo[1].text
        familyName = staffInfo[2].text
        email = staffInfo[-1].text.split('"')[1] + '@unimelb.edu.au'
    
        #staffInfoDict = {'givenName' : givenName, 'familyName' : familyName, 'email' : email}
        firstAndLastName = 'family-name:' + familyName + AND + 'given-names:' + givenName
        # query
        unimelbResponse = requests.get(orcidUrl + firstAndLastName + AND + text)
        #print (unimelbResponse)
        # parser xml
        soup = BeautifulSoup(unimelbResponse.text, 'xml')
        orcid = soup.find(name = 'common:path')

        try: 
            if orcid:
                print(orcid.text)
                scopusId = findScopusIdByOrcid(orcid.text, givenName, familyName)
            
                if scopusId != 0 :
                    print("by orcid")
                    author_dict = scopus.retrieve_author(scopusId)
                    foundStaffDict = {'_id' : scopusId, 'orcid': orcid.text, 'familyName' : familyName, 'givenName' : givenName, 'fullName' : givenName+" "+familyName,'email' : email, 'staffType' : staffType,
                    'document_count' : author_dict['document-count'], 'cited_by_count': author_dict['cited-by-count']         
                    }
                    if foundStaffDict['_id'] not in database:
                        database.save(foundStaffDict)
                        print(foundStaffDict)
                        print('-------------------------------------------------------')
                        count +=1
            else:
                scopusId = findScopusIdByName(givenName, familyName)
                if scopusId != 0:
                    print("by name")
                    author_dict = scopus.retrieve_author(scopusId)
                    foundStaffDict = {'_id' : scopusId, 'orcid': 'none', 'familyName' : familyName, 'givenName' : givenName, 'fullName' : givenName+" "+familyName,'email' : email, 'staffType' : staffType,
                    'document_count' : author_dict['document-count'], 'cited_by_count': author_dict['cited-by-count']         
                    }
                    if foundStaffDict['_id'] not in database:
                        database.save(foundStaffDict)
                        print(foundStaffDict)
                        print('-------------------------------------------------------')
                        count +=1

        except BaseException as e:
            print(e)
            continue

        except couchdb.http.Resource:
            #handle duplicate tweet
            continue 
        except Exception as e1:
            print(e1)
            continue
        
print(count)
#'pub_range_end' : author_dict['publication-range'][1]

# todo: 
# 如果没有orcid就用名字和机构的id搜作者
    


# 0000-0002-2679-2275???

#'Tim Baldwin
