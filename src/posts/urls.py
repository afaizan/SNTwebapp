from django.conf.urls import url
from django.contrib import admin

from .views import (
	post_list,
	post_create,
	# snt,
	# game,
	# cultural,
	# fmc,
	# vox,
	# senate,
	post_detail,
	post_update,
	post_delete,
	ContactWizard,
	process_form_data,
	)

from accounts.views import (login_view, register_view, logout_view)
from posts.forms import (PostForm1, PostForm2, PostForm3)

urlpatterns = [
	url(r'^$', login_view, name='login'),
	url(r'^list/$', post_list, name='list'),
    url(r'^create/$', post_create),
    url(r'^contact/$', ContactWizard.as_view([PostForm1, PostForm2, PostForm3])),
	# url(r'^snt/$', snt, name='sntcouncil'),
	# url(r'^game/$', game, name='game'),
	# url(r'^cultural/$', cultural, name='cultural'),
	# url(r'^fmc/$', fmc, name='fmc'),
	# url(r'^vox/$', vox, name='vox'),
	# url(r'^senate/$', senate, name='senate'),
    url(r'^(?P<slug>[\w-]+)/$', post_detail, name='detail'),
    url(r'^(?P<slug>[\w-]+)/edit/$', post_update, name='update'),
    url(r'^(?P<slug>[\w-]+)/delete/$', post_delete),

	# url(r'^snt/$', "posts.views.snt"),
    #url(r'^posts/$', "<appname>.views.<function_name>"),
]
