from django.urls import path
from . import views

app_name = 'learning_logs'

urlpatterns = [
    # 主页（显示所有主题）
    path('', views.IndexView.as_view(), name='index'),
    # 详情页（显示某个主题的具体笔记）
    path('topics/<int:pk>/', views.TopicDetailView.as_view(), name='topic'),
    path('new_topic/',views.NewTopicView.as_view(),name='new_topic'),
    path('new_entry/<int:topic_id>/',views.NewEntryView.as_view(),name='new_entry'),
    path('delete_entry/<int:pk>/',views.DeleteEntryView.as_view(),name='delete_entry'),
    path('edit_entry/<int:pk>/',views.EditEntryView.as_view(),name='edit_entry'),
    path('edit_topic/<int:pk>/', views.EditTopicView.as_view(), name='edit_topic'),
    path('delete_topic/<int:pk>/', views.DeleteTopicView.as_view(), name='delete_topic'),
    path('api/search/', views.search_suggestions, name='search_suggestions'),
    path('trash/',views.TrashListView.as_view(),name='trash'),
    path('restore_topic/<int:topic_id>/', views.restore_topic, name='restore_topic'),
     # 仪表盘页面（对应你写的 dashboard 函数）
    path('dashboard/', views.dashboard, name='dashboard'),
    # 图表数据 API（对应你写的 chart_data 函数）
    path('api/chart_data/', views.chart_data, name='chart_data'),
    path('profile/',views.profile,name='profile'),
    path('empty_trash/',views.empty_trash,name='empty_trash'),
    path('profile_edit/', views.edit_profile, name='profile_edit'),
    
]