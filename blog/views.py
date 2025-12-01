from django.views.generic import ListView
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import Post
from .forms import EmailPostForm, CommentForm
from taggit.models import Tag  # Django-taggit


# Create your views here.
class PostListView(ListView):
    queryset = (
        Post.published.all()
    )  # Custom QuerySet like model = Post, django would built the generic Post.obects.all() QuerSet
    context_object_name = "posts"  # if we don't specify special name with context_object_name for the query results, default will be object_list
    paginate_by = 3  # how much objects will be returned per Page
    template_name = "blog/post/list.html"  # using custom template to render, default django would search for blog/post_list.html


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    # Django-taggit: filter by tag if tag_slug is provided
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
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
    return render(request, "blog/post/list.html", {"posts": posts, "tag": tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )

    # List of active comments for this post
    comments = post.comments.filter(active=True)  # Queryset
    # Form for users to comment
    form = CommentForm()

    # List of similar psots
    post_tags_ids = post.tags.values_list("id", flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by(
        "-same_tags", "-publish"
    )[:4]

    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
            "similar_posts": similar_posts,
        },
    )


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    # Initiate variable to False
    sent = False
    if request.method == "POST":
        # Form was Submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            # ^ ... send mail Process
            # initiate the absolute path for the post we want to share
            post_url = request.build_absolute_uri(post.get_absolute_url())
            # create Subject Body
            subject = (
                f"{cd['name']} ({cd['email']}) " f"recommends you read {post.title}"
            )
            # create Message Body
            message = (
                f"Read {post.title} at {post_url} \n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )
            # send mail
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd["to"]],
            )
            sent = True
    else:
        form = EmailPostForm()
    return render(
        request, "blog/post/share.html", {"post": post, "form": form, "sent": sent}
    )


# Handle post comments
@require_POST
def post_comment(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    # Initialize comment as None
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create Comment object but don't save to database yet
        comment = form.save(commit=False)
        # Assign the current post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()

    # Render the comment form template
    return render(
        request,
        "blog/post/comment.html",
        {"post": post, "form": form, "comment": comment},
    )
