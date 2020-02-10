from datetime import date
from datetime import datetime
from typing import Dict

import requests
from django.db import IntegrityError
from django.db import transaction
from django.http import JsonResponse
from dynaconf import settings
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.api.custom_types import DynFuelT
from apps.api.custom_types import DynPriceT
from apps.api.custom_types import DynT
from apps.api.impl.auth import CustomTokenAuthentication
from apps.api.impl.v1.serializers import CurrencySerializer
from apps.api.impl.v1.serializers import DynamicsSerializer
from apps.api.impl.v1.serializers import FuelSerializer
from apps.api.impl.v1.serializers import PriceHistorySerializer
from apps.dynamics.models import Currency
from apps.dynamics.models import Fuel
from apps.dynamics.models import PriceHistory


class CurrencyViewSet(ReadOnlyModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class FuelViewSet(ReadOnlyModelViewSet):
    queryset = Fuel.objects.all()
    serializer_class = FuelSerializer


class PriceHistoryViewSet(
    ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet
):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = PriceHistory.objects.all()
    serializer_class = PriceHistorySerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as err:
            return JsonResponse(
                data={"error": str(err)}, status=status.HTTP_400_BAD_REQUEST
            )


class DynamicsViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DynamicsSerializer
    lookup_field = "at"

    def get_queryset(self):
        qs = self.get_grouped()

        return sorted(qs.values(), key=lambda _i: _i.at, reverse=True)

    def get_object(self):
        qs = self.get_queryset()
        if qs:
            return qs[0]
        return None

    def get_grouped(self) -> Dict[date, DynT]:
        queryset = PriceHistory.objects.all()

        if self.detail:
            at_raw = self.kwargs[self.lookup_field]
            at = datetime.strptime(at_raw, "%Y-%m-%d").date()
            queryset = queryset.filter(at=at)

        raw = {}

        for item in queryset:
            dyns = raw.setdefault(item.at, {})
            fuels = dyns.setdefault(item.fuel, {})
            fuels[item.currency] = item.price

        result = {}

        for at, fuels in raw.items():
            dyn = DynT(at=at, fuels=[])

            for fuel, prices in fuels.items():
                d_fuel = DynFuelT(fuel=fuel, prices=[])
                for currency, price in prices.items():
                    d_price = DynPriceT(currency=currency, value=price)
                    d_fuel.prices.append(d_price)
                d_fuel.prices.sort(key=lambda _i: _i.currency.name)
                dyn.fuels.append(d_fuel)

            dyn.fuels.sort(key=lambda _i: _i.fuel.name)
            result[at] = dyn

        return dict(result)


class TelegramView(APIView):
    def get_actual_prices(self):
        fuels = Fuel.objects.all()
        currency = Currency.objects.filter(name="BYN").first()

        prices = []

        n = datetime.now().date()

        for fuel in fuels:
            ph: PriceHistory = PriceHistory.objects.filter(
                fuel=fuel, currency=currency
            ).order_by("-at").first()
            price = f"{fuel.name}: {round(ph.price, 2)} р. ({(n - ph.at).days} д.)"
            prices.append(price)

        return prices

    def bot_respond(self, chat, reply, message_id=None):
        bot_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BENZAKBOT_TOKEN}/sendMessage"

        payload = {"chat_id": chat["id"], "text": reply}

        if message_id:
            payload["reply_to_message_id"] = message_id

        tg_resp = requests.post(bot_url, json=payload)

        return tg_resp

    def post(self, request: Request, *_args, **_kw):
        if (
            not settings.TELEGRAM_BENZAKBOT_TOKEN
            or not request
            or "message" not in request.data
        ):
            raise PermissionDenied("invalid bot configuration")

        message = request.data["message"]
        chat = message["chat"]
        user = message["from"]
        text = message.get("text")

        if text == "/actual":
            bot_response = "Актуальные цены:\n\n" + "\n".join(self.get_actual_prices())
        else:
            bot_response = ""
            if user.get("username"):
                bot_response += "@" + user["username"]
            elif user.get("first_name"):
                bot_response += user["first_name"]
                if user.get("last_name"):
                    bot_response += " " + user["last_name"]

            bot_response += "! За слова ответишь?"

        tg_resp = self.bot_respond(chat, bot_response, message["message_id"])

        return Response(
            data={
                "chat": chat["id"],
                "message": text,
                "ok": True,
                "status": tg_resp.status_code,
                "tg": tg_resp,
                "user": (
                    f"id={user.get('id')},"
                    f"fn={user.get('first_name')}, "
                    f"username={user.get('username')}"
                ),
            },
            content_type="application/json",
        )
