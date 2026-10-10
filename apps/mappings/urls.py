from django.urls import path
from .views import MappingListCreateView, MappingDetailDeleteView

urlpatterns = [
    path('', MappingListCreateView.as_view(), name='mapping-list-create'),
    path('<int:id>/', MappingDetailDeleteView.as_view(), name='mapping-detail-delete'),
]
