import uuid
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.authz import can_edit_sale
from core.forms import ClientForm, PaymentForm, SaleForm, SaleLineFormSet
from core.models import Client, Payment, Sale, SaleBalance
from core.payments import record_payment


@login_required
def home(request):
    return render(request, "core/home.html")


@login_required
def client_create(request):
    success = None
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            success = client
            form = ClientForm()
    else:
        form = ClientForm()

    context = {"form": form, "success": success}

    if request.method == "POST":
        return render(request, "core/_client_form_fragment.html", context)
    return render(request, "core/client_form.html", context)


@login_required
def sale_create(request):
    success = None

    if request.method == "POST":
        idempotency_key = request.POST.get("idempotency_key") or None
        existing = (
            Sale.objects.filter(idempotency_key=idempotency_key).first()
            if idempotency_key
            else None
        )

        if existing is not None:
            success = existing
            form = SaleForm()
            formset = SaleLineFormSet(instance=Sale(), prefix="lines")
        else:
            form = SaleForm(request.POST)
            formset = SaleLineFormSet(request.POST, instance=Sale(), prefix="lines")
            if form.is_valid() and formset.is_valid():
                with transaction.atomic():
                    sale = form.save(commit=False)
                    sale.seller = request.user
                    sale.idempotency_key = idempotency_key or uuid.uuid4()
                    sale.save()
                    formset.instance = sale
                    formset.save()
                success = sale
                form = SaleForm()
                formset = SaleLineFormSet(instance=Sale(), prefix="lines")
    else:
        form = SaleForm()
        formset = SaleLineFormSet(instance=Sale(), prefix="lines")

    context = {
        "form": form,
        "formset": formset,
        "success": success,
        "new_idempotency_key": uuid.uuid4(),
    }

    if request.method == "POST":
        return render(request, "core/_sale_form_fragment.html", context)
    return render(request, "core/sale_form.html", context)


@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(
        Sale.objects.select_related("client", "seller").prefetch_related("lines"), pk=pk
    )
    balance = SaleBalance.objects.filter(sale_id=sale.pk).first()
    context = {
        "sale": sale,
        "balance": balance,
        "can_edit": can_edit_sale(request.user, sale),
    }
    return render(request, "core/sale_detail.html", context)


@login_required
def sale_edit(request, pk):
    sale = get_object_or_404(Sale.objects.select_related("client", "seller"), pk=pk)
    if not can_edit_sale(request.user, sale):
        raise PermissionDenied

    success = None
    if request.method == "POST":
        formset = SaleLineFormSet(request.POST, instance=sale, prefix="lines")
        if formset.is_valid():
            formset.save()
            success = sale
    else:
        formset = SaleLineFormSet(instance=sale, prefix="lines")

    context = {"sale": sale, "formset": formset, "success": success}

    if request.method == "POST":
        return render(request, "core/_sale_edit_form_fragment.html", context)
    return render(request, "core/sale_edit.html", context)


@login_required
@require_POST
def sale_delete(request, pk):
    with transaction.atomic():
        sale = get_object_or_404(
            Sale.objects.select_for_update().select_related("client"), pk=pk
        )
        if not can_edit_sale(request.user, sale):
            raise PermissionDenied
        if sale.allocations.exists():
            error = (
                "Cette vente a des paiements imputés dessus : retirez d'abord "
                "ces imputations avant de l'annuler."
            )
            balance = SaleBalance.objects.filter(sale_id=sale.pk).first()
            context = {"sale": sale, "balance": balance, "error": error, "can_edit": True}
            return render(request, "core/sale_detail.html", context, status=400)
        client_id = sale.client_id
        sale.delete()

    return redirect("client_detail", pk=client_id)


@login_required
def client_list(request):
    clients = Client.objects.order_by("name")
    return render(request, "core/client_list.html", {"clients": clients})


@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    success_payment = None
    error = None

    if request.method == "POST":
        idempotency_key = request.POST.get("idempotency_key") or None
        existing = (
            Payment.objects.filter(idempotency_key=idempotency_key).first()
            if idempotency_key
            else None
        )

        if existing is not None:
            success_payment = existing
            payment_form = PaymentForm()
        else:
            payment_form = PaymentForm(request.POST)
            if payment_form.is_valid():
                sales_by_id = {sale.id: sale for sale in Sale.objects.filter(client=client)}
                allocations = []
                for sale_id, sale in sales_by_id.items():
                    raw = request.POST.get(f"alloc_{sale_id}")
                    if not raw:
                        continue
                    try:
                        alloc_amount = Decimal(raw)
                    except InvalidOperation:
                        continue
                    if alloc_amount > 0:
                        allocations.append((sale, alloc_amount))

                try:
                    payment = record_payment(
                        client=client,
                        amount=payment_form.cleaned_data["amount"],
                        allocations=allocations,
                        recorded_by=request.user,
                        idempotency_key=idempotency_key or uuid.uuid4(),
                    )
                    success_payment = payment
                    payment_form = PaymentForm()
                except ValidationError as exc:
                    error = exc.messages[0]
    else:
        payment_form = PaymentForm()

    sale_balances = list(
        SaleBalance.objects.filter(client_id=client.id)
        .select_related("sale")
        .order_by("-sale__sold_at")
    )
    unpaid_balances = [balance for balance in sale_balances if balance.balance > 0]

    context = {
        "client": client,
        "sale_balances": sale_balances,
        "unpaid_balances": unpaid_balances,
        "payment_form": payment_form,
        "success_payment": success_payment,
        "error": error,
        "new_idempotency_key": uuid.uuid4(),
    }

    if request.method == "POST":
        return render(request, "core/_client_detail_fragment.html", context)
    return render(request, "core/client_detail.html", context)
