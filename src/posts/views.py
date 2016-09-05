try:
    from urllib import quote_plus #python 2
except:
    pass

try:
    from urllib.parse import quote_plus #python 3
except: 
    pass

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from comments.forms import CommentForm
from comments.models import Comment
# from .forms import PostForm
from .models import Post

from formtools.wizard.views import SessionWizardView



def post_create(request):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
		
	form = PostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.user = request.user
		instance.save()
		# message success
		messages.success(request, "Successfully Created")
		return HttpResponseRedirect(instance.get_absolute_url())
	context = {
		"form": form,
	}
	return render(request, "post_form.html", context)

def post_detail(request, slug=None):
	instance = get_object_or_404(Post, slug=slug)
	if instance.publish > timezone.now().date() or instance.draft:
		if not request.user.is_staff or not request.user.is_superuser:
			raise Http404
	share_string = quote_plus(instance.title)

	initial_data = {
			"title_type": instance.get_title_type,
			"object_id": instance.id
	}
	form = CommentForm(request.POST or None, initial=initial_data)
	if form.is_valid() and request.user.is_authenticated():
		c_type = form.cleaned_data.get("title_type")
		title_type = ContentType.objects.get(model=c_type)
		obj_id = form.cleaned_data.get('object_id')
		title_data = form.cleaned_data.get("title")
		parent_obj = None
		try:
			parent_id = int(request.POST.get("parent_id"))
		except:
			parent_id = None

		if parent_id:
			parent_qs = Comment.objects.filter(id=parent_id)
			if parent_qs.exists() and parent_qs.count() == 1:
				parent_obj = parent_qs.first()


		new_comment, created = Comment.objects.get_or_create(
							user = request.user,
							title_type= title_type,
							object_id = obj_id,
							title = title_data,
							parent = parent_obj,
						)
		return HttpResponseRedirect(new_comment.title_object.get_absolute_url())


	comments = instance.comments
	context = {
		"title": instance.title,
		"instance": instance,
		"share_string": share_string,
		"comments": comments,
		"comment_form":form,
	}
	return render(request, "post_detail.html", context)

def post_list(request):
	today = timezone.now().date()
	queryset_list = Post.objects.active() #.order_by("-timestamp")
	if request.user.is_staff or request.user.is_superuser:
		queryset_list = Post.objects.all()
	
	query = request.GET.get("q")
	if query:
		queryset_list = queryset_list.filter(
				Q(title__icontains=query)|
				Q(title__icontains=query)|
				Q(user__first_name__icontains=query) |
				Q(user__last_name__icontains=query) |
				Q(tags__icontains=query)
				).distinct()
	paginator = Paginator(queryset_list, 8) # Show 25 contacts per page
	page_request_var = "page"
	page = request.GET.get(page_request_var)
	try:
		queryset = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		queryset = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		queryset = paginator.page(paginator.num_pages)


	context = {
		"object_list": queryset, 
		"title": "News Feed",
		"page_request_var": page_request_var,
		"today": today,
	}
	return render(request, "post_list.html", context)





def post_update(request, slug=None):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	instance = get_object_or_404(Post, slug=slug)
	form = PostForm(request.POST or None, request.FILES or None, instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "<a href='#'>Item</a> Saved", extra_tags='html_safe')
		return HttpResponseRedirect(instance.get_absolute_url())

	context = {
		"title": instance.title,
		"instance": instance,
		"form":form,
	}
	return render(request, "post_form.html", context)



def post_delete(request, slug=None):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	instance = get_object_or_404(Post, slug=slug)
	instance.delete()
	messages.success(request, "Successfully deleted")
	return redirect("posts:list")


def post_create(request):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
		
	form = PostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.user = request.user
		instance.save()
		# message success
		messages.success(request, "Successfully Created")
		return HttpResponseRedirect(instance.get_absolute_url())
	context = {
		"form": form,
	}
	return render(request, "post_form.html", context)


class ContactWizard(SessionWizardView):
	template_name = "contact_form.html"
	def done(self, form_list, **kwargs):
		form_data = process_form_data(form_list)

		return render_to_response('done.html', {'form_data' : form_data})

def process_form_data(form_list):
	form_data = [form.cleaned_data for form in form_list]
	return form_data

# def snt(request):
# 	today = timezone.now().date()
# 	queryset_list_snt = Post.objects.active_snt()#filter(title='Games') #.order_by("-timestamp")
	
# 	if request.user.is_staff or request.user.is_superuser:
# 		queryset_list_snt = Post.objects.active_snt()#filter(tags='SNT Council')#all()
	
# 	query = request.GET.get("q")
# 	if query:
# 		queryset_list_snt = queryset_list_snt.filter(
# 				Q(title__icontains=query)|
# 				Q(content__icontains=query)|
# 				Q(user__first_name__icontains=query) |
# 				Q(user__last_name__icontains=query) |
# 				Q(tags__icontains=query)
# 				).distinct()
# 	paginator = Paginator(queryset_list_snt, 10) # Show 25 contacts per page
# 	page_request_var = "page"
# 	page = request.GET.get(page_request_var)
# 	try:
# 		queryset = paginator.page(page)
# 	except PageNotAnInteger:
# 		# If page is not an integer, deliver first page.
# 		queryset = paginator.page(1)
# 	except EmptyPage:
# 		# If page is out of range (e.g. 9999), deliver last page of results.
# 		queryset = paginator.page(paginator.num_pages)


# 	context = {
# 		"object_list": queryset, 
# 		"title": "List",
# 		"page_request_var": page_request_var,
# 		"today": today,
# 	}
# 	return render(request, "snt.html", context)

# def game(request):
# 	today = timezone.now().date()
# 	queryset_list = Post.objects.filter(tags__icontains="u'Games and Sports'", publish__lte=timezone.now())#active_snt() #.order_by("-timestamp")
	
# 	if request.user.is_staff or request.user.is_superuser:
# 		queryset_list = Post.objects.filter(tags__icontains="u'Games and Sports'", publish__lte=timezone.now())#active_snt()
	
# 	query = request.GET.get("q")
# 	if query:
# 		queryset_list_snt = queryset_list_snt.filter(
# 				Q(title__icontains=query)|
# 				Q(content__icontains=query)|
# 				Q(user__first_name__icontains=query) |
# 				Q(user__last_name__icontains=query) |
# 				Q(tags__icontains=query)
# 				).distinct()
# 	paginator = Paginator(queryset_list, 8) # Show 25 contacts per page
# 	page_request_var = "page"
# 	page = request.GET.get(page_request_var)
# 	try:
# 		queryset = paginator.page(page)
# 	except PageNotAnInteger:
# 		# If page is not an integer, deliver first page.
# 		queryset = paginator.page(1)
# 	except EmptyPage:
# 		# If page is out of range (e.g. 9999), deliver last page of results.
# 		queryset = paginator.page(paginator.num_pages)


# 	context = {
# 		"object_list": queryset, 
# 		"title": "List",
# 		"page_request_var": page_request_var,
# 		"today": today,
# 	}
# 	return render(request, "game.html", context)


# def cultural(request):
# 	today = timezone.now().date()
# 	queryset_list = Post.objects.filter(tags__icontains="u'Cultural Council'", publish__lte=timezone.now())#active_snt() #.order_by("-timestamp")
	
# 	if request.user.is_staff or request.user.is_superuser:
# 		queryset_list = Post.objects.filter(tags__icontains="u'Cultutal Council'", publish__lte=timezone.now())#active_snt()
	
# 	query = request.GET.get("q")
# 	if query:
# 		queryset_list = queryset_list.filter(
# 				Q(title__icontains=query)|
# 				Q(content__icontains=query)|
# 				Q(user__first_name__icontains=query) |
# 				Q(user__last_name__icontains=query) |
# 				Q(tags__icontains=query)
# 				).distinct()
# 	paginator = Paginator(queryset_list, 8) # Show 25 contacts per page
# 	page_request_var = "page"
# 	page = request.GET.get(page_request_var)
# 	try:
# 		queryset = paginator.page(page)
# 	except PageNotAnInteger:
# 		# If page is not an integer, deliver first page.
# 		queryset = paginator.page(1)
# 	except EmptyPage:
# 		# If page is out of range (e.g. 9999), deliver last page of results.
# 		queryset = paginator.page(paginator.num_pages)


# 	context = {
# 		"object_list": queryset, 
# 		"title": "List",
# 		"page_request_var": page_request_var,
# 		"today": today,
# 	}
# 	return render(request, "cultural.html", context)	



# def fmc(request):
# 	today = timezone.now().date()
# 	queryset_list = Post.objects.filter(tags__icontains="u'FMC'", publish__lte=timezone.now())#active_snt() #.order_by("-timestamp")
	
# 	if request.user.is_staff or request.user.is_superuser:
# 		queryset_list = Post.objects.filter(tags__icontains="u'FMC'", publish__lte=timezone.now())#active_snt()
	
# 	query = request.GET.get("q")
# 	if query:
# 		queryset_list = queryset_list.filter(
# 				Q(title__icontains=query)|
# 				Q(content__icontains=query)|
# 				Q(user__first_name__icontains=query) |
# 				Q(user__last_name__icontains=query) |
# 				Q(tags__icontains=query)
# 				).distinct()
# 	paginator = Paginator(queryset_list, 8) # Show 25 contacts per page
# 	page_request_var = "page"
# 	page = request.GET.get(page_request_var)
# 	try:
# 		queryset = paginator.page(page)
# 	except PageNotAnInteger:
# 		# If page is not an integer, deliver first page.
# 		queryset = paginator.page(1)
# 	except EmptyPage:
# 		# If page is out of range (e.g. 9999), deliver last page of results.
# 		queryset = paginator.page(paginator.num_pages)


# 	context = {
# 		"object_list": queryset, 
# 		"title": "List",
# 		"page_request_var": page_request_var,
# 		"today": today,
# 	}
# 	return render(request, "fmc.html", context)		


# def vox(request):
# 	today = timezone.now().date()
# 	queryset_list = Post.objects.filter(tags__icontains="u'Vox Populi'", publish__lte=timezone.now())#active_snt() #.order_by("-timestamp")
	
# 	if request.user.is_staff or request.user.is_superuser:
# 		queryset_list = Post.objects.filter(tags__icontains="u'Vox Populi'", publish__lte=timezone.now())#active_snt()
	
# 	query = request.GET.get("q")
# 	if query:
# 		queryset_list = queryset_list.filter(
# 				Q(title__icontains=query)|
# 				Q(content__icontains=query)|
# 				Q(user__first_name__icontains=query) |
# 				Q(user__last_name__icontains=query) |
# 				Q(tags__icontains=query)
# 				).distinct()
# 	paginator = Paginator(queryset_list, 8) # Show 25 contacts per page
# 	page_request_var = "page"
# 	page = request.GET.get(page_request_var)
# 	try:
# 		queryset = paginator.page(page)
# 	except PageNotAnInteger:
# 		# If page is not an integer, deliver first page.
# 		queryset = paginator.page(1)
# 	except EmptyPage:
# 		# If page is out of range (e.g. 9999), deliver last page of results.
# 		queryset = paginator.page(paginator.num_pages)


# 	context = {
# 		"object_list": queryset, 
# 		"title": "List",
# 		"page_request_var": page_request_var,
# 		"today": today,
# 	}
# 	return render(request, "vox.html", context)	


# def senate(request):
# 	today = timezone.now().date()
# 	queryset_list = Post.objects.filter(tags__icontains="u'Senate'", publish__lte=timezone.now())#active_snt() #.order_by("-timestamp")
	
# 	if request.user.is_staff or request.user.is_superuser:
# 		queryset_list = Post.objects.filter(tags__icontains="u'Senate'", publish__lte=timezone.now())#active_snt()
	
# 	query = request.GET.get("q")
# 	if query:
# 		queryset_list = queryset_list.filter(
# 				Q(title__icontains=query)|
# 				Q(content__icontains=query)|
# 				Q(user__first_name__icontains=query) |
# 				Q(user__last_name__icontains=query) |
# 				Q(tags__icontains=query)
# 				).distinct()
# 	paginator = Paginator(queryset_list, 8) # Show 25 contacts per page
# 	page_request_var = "page"
# 	page = request.GET.get(page_request_var)
# 	try:
# 		queryset = paginator.page(page)
# 	except PageNotAnInteger:
# 		# If page is not an integer, deliver first page.
# 		queryset = paginator.page(1)
# 	except EmptyPage:
# 		# If page is out of range (e.g. 9999), deliver last page of results.
# 		queryset = paginator.page(paginator.num_pages)


# 	context = {
# 		"object_list": queryset, 
# 		"title": "List",
# 		"page_request_var": page_request_var,
# 		"today": today,
# 	}
# 	return render(request, "senate.html", context)	


