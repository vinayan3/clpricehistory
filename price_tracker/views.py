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
        
        postList =  Post.objects.filter(title=prodName)
        postsWithPrice = filter(lambda x: x.price is not None, postList)
        avgPrice = sum(map(lambda x: x.price, postsWithPrice)) / len(postsWithPrice)
        context = Context ({
                'avgPrice': avgPrice,
                'numOfPosts': len(postsWithPrice),
                'prodName': prodName
                })
    else:
        context = Context ({})

    return HttpResponse(t.render(context))
