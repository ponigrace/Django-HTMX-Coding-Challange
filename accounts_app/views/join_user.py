from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.shortcuts import render

from accounts_app.forms import EditUserForm, InviteUserForm
from accounts_app.forms.new_user_form import NewUserForm
from accounts_app.models import UserInvitation


class AcceptInvitation(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, "accounts_app/profile.html",
                          {"form": EditUserForm(instance=request.user), "invite_user_form": InviteUserForm()})

        token = request.GET.get('token').replace("-", "")
        if not token:
            return HttpResponse("No token provided", status=400)

        invited_user = UserInvitation.objects.filter(id=token).first()
        if invited_user and invited_user.expires_at > timezone.now():
            new_user_form = NewUserForm()
            context = {
                "new_user_form": new_user_form,
                "token": token,
                "email": invited_user.email
            }
            return render(request, "accounts_app/new_user.html", context=context)
        else:
            return HttpResponse("Invalid invitation", status=404)

    def post(self, request, *args, **kwargs):
        token = request.POST.get('token').replace("-", "")

        invited_user = UserInvitation.objects.filter(id=token).first()

        new_user_form = NewUserForm(request.POST)
        if invited_user and invited_user.expires_at > timezone.now():
            if new_user_form.is_valid():
                User = get_user_model()
                User.objects.create_user(
                    email=new_user_form.cleaned_data['email'],
                    password=new_user_form.cleaned_data['password'],
                    first_name=new_user_form.cleaned_data['first_name'],
                    last_name=new_user_form.cleaned_data['last_name'],
                )
                invited_user.delete()
                response = HttpResponse()
                response["HX-Redirect"] = reverse("sign_in")
                return response

        return render(request, "accounts_app/new_user.html", context={"new_user_form": new_user_form})
