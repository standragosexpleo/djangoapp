from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.index_view, name='index'),
    path('image_upload', views.upload_and_save_svg_view, name='save_svg'),
    # path('recognize_emotion', views.upload_and_recognize_emotion, name='image_rec'),
    path('search_quote', views.search, name='search_quote'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
