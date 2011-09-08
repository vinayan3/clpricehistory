from django.core.management import setup_environ
import settings
setup_environ(settings)
from price_tracker import models

import re
import time
import datetime


def parseToc(pageSoup):
    posts = []

    bodyToc = pageSoup.find('body', {'class': 'toc'})

    headerDiv = bodyToc.find('div', {'class': 'bchead'})
    firstSpanHeader = headerDiv.find('span')

    #Cookie crumbes is like sub craigslist > [sub section > ]* section
    cookieCrumbs = firstSpanHeader.findNextSiblings('a')

    subCraigsList = cookieCrumbs[0].string
    subCraigsList = subCraigsList.strip('craigslist')

    section = cookieCrumbs[-1].string

    reParagraphHeading = re.compile('p|(h4)')
    reClass = re.compile('((ban)|(row))')

    post = bodyToc.find('h4', {'class': 'ban'})
    curDate = None
    
    while post is not None:
        if post.name == 'h4' and \
                (post.has_key('class') and post['class'] == 'ban'):
            #Adding the year to the year to the date str
            dateStr = "%s %s" % (post.string , time.strftime("%Y", time.gmtime()))
            curDate = datetime.date.fromtimestamp(
                time.mktime(time.strptime(dateStr, "%a %b %d %Y")))

        elif post.name == 'p' and \
                (post.has_key('class') and post['class'] == 'row'):
            assert curDate is not None
            #deal with post
            curTag = post.find('a')

            title = curTag.string

            curTag = curTag.nextSibling
            
            #the price looks like this - $3900
            price = curTag.string
            price = price.strip()
            if price == "-":
                price = None
            else:
                price = price.split()[1]
                price = price.strip('$')
                price = int(price)

            curTag = post.find('font')

            #String is like ' (san jose south)'
            neighborhood = None
            if curTag is not None:
                neighborhood = curTag.string.strip()
                neighborhood = neighborhood[1:] #Exclude (
                neighborhood = neighborhood[:-1] #Exclude )
                
            posts.append(models.Post(
                title=title,
                price=price,
                neighborhood=neighborhood,
                subCraigsList=subCraigsList,
                section=section,
                date=curDate))
        else:
            #Impossible.... Famous last words?
            assert False

        nextPosts = post.findNextSiblings(reParagraphHeading,
                                          {'class': reClass },
                                          limit=1)
        if len(nextPosts) == 1:
            post = nextPosts[0]
        elif len(nextPosts) == 0:
            post = None
        else:
            assert False

    return posts


def parseListing(pageSoup):

    bodyPosting = pageSoup.find('body', {'class': 'posting'})
    if not bodyPosting:
        return None #some other page

    pageHead = bodyPosting.find('div', {'class': 'bchead'})
    #There is a risk that findAll does not perserve the order of the '<a>' tags.
    #The code using the list generated depends on the order to find 
    #which CL city and sub section.
    subLinks = pageHead.findAll('a')
    clCity = subLinks[1].string.strip()
    clCity = clCity.strip('craigslist')
    subSection = subLinks[-1].string.strip()

    #The title is in the format of
    #[Some Title] - $[Some Price] ([Some city or area])
    title =  pageSoup.find('h2').string
    dashIndex = title.rfind('-')
    postDash = title[dashIndex + 1:].strip()
    titleStr = title[:dashIndex].strip()

    price = None
    priceMatch = re.match('\s*\$(\d+)', postDash)
    if priceMatch is not None:
        price = int(priceMatch.groups()[0].strip())

    neighborhood = postDash[postDash.rfind("(") + 1:]
    neighborhood = neighborhood[:neighborhood.rfind(")")]

    dateStr = pageSoup.find(text=re.compile("Date.*")).string
    dateStr = dateStr[dateStr.find(':') + 1:].strip()
    
    dateStr = dateStr[:dateStr.rfind(' ')]
    postDateTime = datetime.date.fromtimestamp(
        time.mktime(time.strptime(dateStr, "%Y-%m-%d, %I:%M%p")))
    
    return models.Post(
        title=titleStr,
        price=price,
        neighborhood=neighborhood,
        subCraigsList=clCity,
        section=subSection,
        date=postDateTime)

def parse(pageSoup):
    if pageSoup.find('body', {'class': 'posting'}):
        return [parseListing(pageSoup)]
    elif pageSoup.find('body', {'class': 'toc'}):
        return parseToc(pageSoup)
    else:
        return []
