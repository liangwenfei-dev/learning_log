from django.shortcuts import render,redirect,get_object_or_404
from .forms import TopicForm,EntryForm
from .models import Topic,Entry
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView,DeleteView,ListView,CreateView,DetailView
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncMonth
class IndexView(LoginRequiredMixin,ListView):
    model = Topic
    template_name = 'learning_logs/index.html'
    context_object_name = 'topics'
    paginate_by = 6

    def get_queryset(self):
        search_query = self.request.GET.get('q')
        queryset = Topic.objects.filter(owner=self.request.user,is_deleted=False).order_by('-date_added')
        if search_query:
            queryset = queryset.filter(text__icontains=search_query)

        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q','')
        return context
    
    
class TopicDetailView(LoginRequiredMixin,DetailView):
    model = Topic
    template_name = 'learning_logs/topic.html'
    context_object_name = 'topic'

    def get_queryset(self):
        return Topic.objects.filter(owner=self.request.user,is_deleted=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entries'] = self.object.entry_set.filter(is_deleted=False).order_by('-date_added')
        return context 
class NewTopicView(LoginRequiredMixin, CreateView):
    model = Topic
    form_class = TopicForm
    template_name = 'learning_logs/new_topic.html'
    success_url = reverse_lazy('learning_logs:index')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
class NewEntryView(LoginRequiredMixin,CreateView):
    model = Entry
    form_class = EntryForm
    template_name = 'learning_logs/new_entry.html'

    def dispatch(self, request, *args, **kwargs):
        self.topic = get_object_or_404(Topic,id=kwargs['topic_id'],owner=request.user)
        return super().dispatch(request,*args,**kwargs)
    def form_valid(self, form):
        form.instance.topic = self.topic
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topic'] = self.topic
        return context

    def get_success_url(self):
        return reverse_lazy('learning_logs:topic', kwargs={'pk': self.topic.id})


class EditTopicView(LoginRequiredMixin,UpdateView):
    model = Topic
    form_class = TopicForm
    template_name = 'learning_logs/edit_topic.html'
    success_url = reverse_lazy('learning_logs:index')

    def get_queryset(self):
        return Topic.objects.filter(owner=self.request.user)
class EditEntryView(LoginRequiredMixin,UpdateView):
    model = Entry
    form_class = EntryForm
    template_name = 'learning_logs/edit_entry.html'

    def get_queryset(self):
        return Entry.objects.filter(topic__owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('learning_logs:topic', kwargs={'pk': self.object.topic_id})
class DeleteTopicView(LoginRequiredMixin,DeleteView):
    model = Topic
    success_url = reverse_lazy('learning_logs:index')
    template_name = 'learning_logs/delete_topic.html'

    def get_queryset(self):
        return Topic.objects.filter(owner=self.request.user)
    def form_valid(self,form):
        topic = self.get_object()
        topic.is_deleted = True
        topic.entry_set.filter(is_deleted=False).update(is_deleted=True)
        topic.save()
        return redirect(self.success_url)
    
class DeleteEntryView(LoginRequiredMixin,DeleteView):
    model = Entry
    template_name = 'learning_logs/delete_entry.html'

    def get_queryset(self):
        return Entry.objects.filter(topic__owner=self.request.user)

    def form_valid(self,form):
        self.object = self.get_object()
        self.object.is_deleted = True
        self.object.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('learning_logs:topic', kwargs={'pk': self.object.topic_id})
class TrashListView(LoginRequiredMixin,ListView):
    model = Topic
    template_name = 'learning_logs/trash.html'
    context_object_name = 'topics'

    def get_queryset(self):
        return Topic.objects.filter(owner=self.request.user,is_deleted=True).order_by('-date_added')
@login_required
def search_suggestions(request):
    query = request.GET.get('q','')
    if query:
        topics = Topic.objects.filter(owner=request.user,is_deleted=False,text__icontains=query)[:5]
        data = [{'id': t.id,'text': t.text} for t in topics ]
        return JsonResponse(data, safe=False)
    return JsonResponse([],safe=False)
@login_required
def restore_topic(request,topic_id):
    topic = get_object_or_404(Topic,id=topic_id,owner=request.user,is_deleted=True)
    topic.is_deleted = False
    topic.entry_set.update(is_deleted=False)
    topic.save()

    return redirect('learning_logs:trash')
@login_required
def dashboard(request):
    return render(request,'learning_logs/dashboard.html')
@login_required
def chart_data(request):
    data = Entry.objects.filter(topic__owner=request.user, is_deleted=False, topic__is_deleted=False) \
        .annotate(month=TruncMonth('date_added')) \
        .values('month') \
        .annotate(count=Count('id')) \
        .order_by('month')

    labels = []
    counts = []
    for item in data:
        if item['month']:
            # 👇 注意这里的括号！先格式化，再 append
            labels.append(item['month'].strftime('%Y年%m月'))
            counts.append(item['count'])

    return JsonResponse({'labels': labels, 'counts': counts})
@login_required
def profile(request):
    topic_count = Topic.objects.filter(owner=request.user,is_deleted=False).count()
    entry_count = Entry.objects.filter(topic__owner=request.user,is_deleted=False).count()
    context = {
        'topic_count':topic_count,
        'entry_count':entry_count
    }
    return render(request,'learning_logs/profile.html',context)
@login_required
def empty_trash(request):
    if request.method == 'POST':
        Topic.objects.filter(owner=request.user,is_deleted=True).delete()
        

        
    return redirect('learning_logs:trash')
def custom_404(request, exception):
    return render(request, '404.html', status=404)
# 👇 放到文件最顶部（和其他 import 放在一起）
from accounts.models import Profile
from accounts.forms import ProfileForm

# 👇 放到文件最底部
@login_required
def edit_profile(request):
    # 获取当前用户的 Profile 对象（如果不存在则自动创建）
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # 一定要加 request.FILES，否则图片传不上去
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            # 保存后跳回个人主页（这里的 'profile' 是你之前展示统计数据的那个路由）
            return redirect('learning_logs:profile') 
    else:
        form = ProfileForm(instance=user_profile)
        
    context = {
        'form': form,
        'profile': user_profile,  # 把 profile 传给模板，上面才能显示头像
    }
    # 注意这里的模板路径，必须和你的 HTML 文件位置对应
    return render(request, 'accounts/profile.html', context)