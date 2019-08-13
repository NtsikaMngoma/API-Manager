# -*- coding: utf-8 -*-
"""
Views of config app
"""

import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from obp.api import API, APIError
from .forms import MethodRoutingForm
from django.urls import reverse_lazy

def error_once_only(request, err):
    """
    Just add the error once
    :param request:
    :param err:
    :return:
    """
    storage = messages.get_messages(request)
    if str(err) not in [str(m.message) for m in storage]:
        messages.error(request, err)

class IndexView(LoginRequiredMixin, FormView):
    """Index view for config"""
    template_name = "methodrouting/index.html"
    form_class = MethodRoutingForm
    success_url = reverse_lazy('methodrouting-index')

    def dispatch(self, request, *args, **kwargs):
        self.api = API(request.session.get('obp'))
        return super(IndexView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        method_routhings=json.loads("""{
  "method_routings": [
    {
      "method_name": "getChallengeThreshold",
      "connector_name": "rest_vMar2019"
    },
    {
      "method_name": "getChargeLevel",
      "connector_name": "akka_vDec2018"

    },
    {
      "method_name": "getBank",
      "connector_name": "kafka_vMar2017"

    },
    {
      "method_name": "getUser",
      "connector_name": "mapped"

    },
    {
      "method_name": "getBankAccounts",
      "connector_name": "mapped"

    },
    {
      "method_name": "getCounterparty",
      "connector_name": "mapped"

    },
    {
      "method_name": "getCoreBankAccounts",
      "connector_name": "mapped"

    },
    {
      "method_name": "getBankAccountByIban",
      "connector_name": "mapped"

    },
    {
      "method_name": "getBankAccountByRouting",
      "connector_name": "mapped"

    },
    {
      "method_name": "getBankAccountsBalances",
      "connector_name": "mapped"

    },
    {
      "method_name": "checkBankAccountExists",
      "connector_name": "mapped"

    },
    {
      "method_name": "getCounterpartiesFromTransaction",
      "connector_name": "mapped"

    },
    {
      "method_name": "getCounterpartyTrait",
      "connector_name": "mapped"

    },
    {
      "method_name": "getCounterparty",
      "connector_name": "mapped"

    }
  ]
}""")
        context.update({'method_routhings': method_routhings["method_routings"]})
        return context

    def get_form(self, *args, **kwargs):
        form = super(IndexView, self).get_form(*args, **kwargs)
        # Cannot add api in constructor: super complains about unknown kwarg
        fields = form.fields
        form.api = self.api
        try:
            fields['method_routing_body'].initial = ""

        except APIError as err:
            messages.error(self.request, APIError(Exception("OBP-API server is not running or do not response properly. "
                                     "Please check OBP-API server.   Details: " + str(err))))
        except Exception as err:
            messages.error(self.request, "Unknown Error. Details: "+ str(err))

        return form

    def form_valid(self, form):
        try:
            data = form.cleaned_data
            urlpath = '/management/method_routings'
            payload = json.loads(data["method_routing_body"])
            result = self.api.post(urlpath, payload=payload)
        except APIError as err:
            error_once_only(self.request, APIError(Exception("OBP-API server is not running or do not response properly. "
                                     "Please check OBP-API server.   Details: " + str(err))))
            return super(IndexView, self).form_invalid(form)
        except Exception as err:
            error_once_only(self.request, "Unknown Error. Details: "+ str(err))
            return super(IndexView, self).form_invalid(form)
        if 'code' in result and result['code']>=400:
            error_once_only(self.request, result['message'])
            return super(IndexView, self).form_valid(form)
        msg = 'Submission successfully!'
        messages.success(self.request, msg)
        return super(IndexView, self).form_valid(form)