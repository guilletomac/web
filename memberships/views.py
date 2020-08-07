from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth import authenticate, login
import json
import stripe

from .forms import RegistrationForm
from .models import Member

stripe.api_key = settings.STRIPE_SECRET_KEY


def register(request):
    if request.user.is_authenticated:
        return HttpResponse("cannot register while logged in", status=403)

    if not request.method == "POST":
        return render(
            request, "memberships/register.html", {"form": RegistrationForm()}
        )

    form = RegistrationForm(request.POST)
    if not form.is_valid():
        return render(request, "memberships/register.html", {"form": form})

    if not form.cleaned_data["preferred_name"]:
        form.cleaned_data["preferred_name"] = form.cleaned_data["full_name"]

    member = Member.create(
        full_name=form.cleaned_data["full_name"],
        preferred_name=form.cleaned_data["preferred_name"],
        email=form.cleaned_data["email"],
        password=form.cleaned_data["password"],
        birth_date=form.cleaned_data["birth_date"],
        constitution_agreed=form.cleaned_data["constitution_agreed"],
    )

    login(request, member.user)

    donation = request.POST.get("donation")
    if donation:
        confirmation_url = "{}?donation={}".format(reverse("confirm"), donation)
        return HttpResponseRedirect(confirmation_url)

    return HttpResponseRedirect(reverse("confirm"))


def confirm(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("register"))

    donation = request.GET.get("donation")
    total = 1 if not donation else int(donation) + 1

    url = request.build_absolute_uri
    cancel_url = (
        "{}?donation={}".format(reverse("confirm"), donation)
        if donation
        else reverse("confirm")
    )
    session = stripe.checkout.Session.create(
        payment_method_types=["bacs_debit"],
        mode="setup",
        customer=request.user.member.stripe_customer_id,
        success_url=url(reverse("thanks")),
        cancel_url=url(cancel_url),
    )

    return render(
        request,
        "memberships/confirm.html",
        {
            "donation": donation,
            "total": total,
            "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
            "stripe_session_id": session.id,
        },
    )


def thanks(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("register"))
    return HttpResponse("Registration successful.")
