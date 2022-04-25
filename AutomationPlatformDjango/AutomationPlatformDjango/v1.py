# -*- coding: utf-8 -*-
from django.conf.urls import url, include

urlpatterns = [
    url('api/', include("api.urls")),
    url('api/', include('big_data.urls')),
    url('api/',include('data_monior.urls'))
]
