from django.http import HttpResponse
from django.template import RequestContext, Context, loader

from models import Post

def index(request):
    
    t = loader.get_template('price_tracker/index.html')
    c = RequestContext (request, {})

    return HttpResponse(t.render(c))


def results(request):
    context = None
    t = loader.get_template('price_tracker/results.html')

    if 'prod_name' in request.POST:
        prodName = request.POST['prod_name']
        mungedProdName = prodName.lower().strip()
        
        exactMatches = []
        avgPriceExact = None

        possibleMatches = []
        
        for i in Post.objects.all():
            titleMunged = i.title.strip()
            #handle spcaing between words; people sometimes add extra
            titleMunged = ' '.join(titleMunged.split())
            #case insensitive search
            titleMunged = titleMunged.lower()
            if titleMunged == mungedProdName:                
                exactMatches.append(i)
            else:
                if titleMunged.find(mungedProdName) >= 0:
                    possibleMatches.append(i)

        if len(exactMatches) > 0 : 
            exactMatches = filter(lambda x: x.price is not None, exactMatches)
            avgPriceExact = sum(map(lambda x: x.price, exactMatches)) / len(exactMatches)
        

        context = Context ({
                'numExactMatches': len(exactMatches),
                'avgPriceExact': avgPriceExact,
                'possibleMatches': possibleMatches,
                'prodName': prodName
                })
    else:
        context = Context ({})

    return HttpResponse(t.render(context))
