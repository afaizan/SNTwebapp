from urllib import quote_plus
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm

from .models import Post

# Create your views here.
def post_create(request):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
		
	form=PostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance=form.save(commit=False)
		instance.user=request.user
		instance.save()
		messages.success(request,"Successfully created")
		return HttpResponseRedirect(instance.get_absolute_url())
	
	context={
		"form":form,
	}
	return render(request,"post_form.html",context)

def post_detail(request, id=None):
	#instance=Post.object.get(id=1)
	instance=get_object_or_404(Post,id=id)
	share_string=quote_plus(instance.content)
	context={
		"title":instance.title,
		"instance":instance,
		"share_string":share_string,
	}
	return render(request,"post_detail.html",context)


def post_list(request):
		#	today=timezone.now().date()	
		queryset_list=Post.objects.all()#.order_by('-timestamp')
		
		query=request.GET.get("q")
		if  query:
			queryset_list = queryset_list.filter(title__icontains=query)
		paginator = Paginator(queryset_list, 4) # Show 25 contacts per page
		page_request_var="page"
		page = request.GET.get(page_request_var)
		try:
			queryset = paginator.page(page)
		except PageNotAnInteger:
		# If page is not an integer, deliver first page.
			queryset = paginator.page(1)
		except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
			queryset = paginator.page(paginator.num_pages)
		context={
			"object_list":queryset,
			"title":"Posts",
			"page_request_var":page_request_var
		}
		return render(request,"post_list.html",context)






def post_update(request, id=None):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	instance=get_object_or_404(Post,id=id)
	form=PostForm(request.POST or None, request.FILES or None, instance=instance)
	if form.is_valid():
		instance=form.save(commit=False)
		instance.save()
		messages.success(request,"<a href='#'>Item</a> Saved", extra_tags='html_safe')
		return HttpResponseRedirect(instance.get_absolute_url())

	context={
		"title":instance.title,
		"instance":instance,
		"form":form,
	}
	return render(request,"post_form.html",context)

def post_delete(request,id=None):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	instance=get_object_or_404(Post,id=id)
	instance.delete()
	messages.success(request,"Successfully deleted")
	return redirect("posts:list")