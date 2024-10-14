from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts_app.forms import InviteUserForm
from accounts_app.models import UserInvitation


class InviteUserView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.method == "GET":
            if request.user.is_authenticated:
                return redirect("home")
            else:
                return redirect("sign_in")

    def post(self, request, *args, **kwargs):
        form = InviteUserForm(request.POST)
        
        if form.is_valid():
            # We could further improve this here to first check if an invitation for this email already exists and is not expired
            invited_user = UserInvitation.objects.filter(email=form.cleaned_data['email']).first()
            today = timezone.now()
            # today = datetime.combine(today, datetime.max.time())
            if invited_user:  # Check if user exists in the database
                if invited_user.expires_at > today:  # Check invitation expiry date
                    print(f"There's an existing invitation for this user and it's waiting for response")
                else:
                    invited_user.delete()  # Delete the user and send a new invitation

                    invitation = UserInvitation(email=form.cleaned_data["email"], invited_by=request.user)
                    invitation.save()
                    invitation.send_invitation_email()
            else:
                invitation = UserInvitation(email=form.cleaned_data["email"], invited_by=request.user)
                invitation.save()
                invitation.send_invitation_email()

            context = {"invite_user_form": form, "invited": True}
            response = render(request, "accounts_app/profile.html", context)
            response['HX-Refresh'] = "true"
            return response

        else:
            return render(request, "accounts_app/profile.html", {"invite_user_form": form})