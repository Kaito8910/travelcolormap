from django.shortcuts import render
from django.contrib.auth.views import ChangePwdView, ChangePwdFinish
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

class base(LoginRequiredMixin, generic.TemplateView):
    template_name = 'templates/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_name"] = "top"
        return context

class ChangePwd(LoginRequiredMixin, ChangePwdView):
    success_url = reverse_lazy('accounts:change_pwd_finish')
    template_name = 'accounts/change_pwd.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_name"] = "change_pwd"
        return context

class ChangePwdFinish(LoginRequiredMixin,ChangePwdFinish):
    template_name = 'accounts/change_pwd_finish.html'




@login_required
def user_info(request):
    user = request.user
    return render(request, 'user_data.html', {'user': user})
