from django.views.generic import ListView
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render, get_object_or_404
from .models import Post


# Create your views here.
class PostListView(ListView):
    """_summary_

    Args:
        ListView (_type_): _description_
    """

    queryset = (
        Post.published.all()
    )  # Custom QuerySet like model = Post, django would built the generic Post.obects.all() QuerSet
    context_object_name = "post"  # if we don't specify special name with context_object_name for the query results, default will be object_list
    paginate_by = 3  # how much objects will be returned per Page
    template_name = "blog/post/list.html"  # using custom template to render, default django would search for blog/post_list.html


def post_list(request):
    post_list = Post.published.all()
    # Pagination with 3 post per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        # If page_number is out of range get last page of results
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        # If page_number is not an Integer get the first page
        posts = paginator.page(1)

    # Render Post List
    return render(request, "blog/post/list.html", {"posts": posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    return render(request, "blog/post/detail.html", {"post": post})
