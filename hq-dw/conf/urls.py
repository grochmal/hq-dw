'''
hq-dw URL Configuration
'''

from django.conf.urls import url, include
from django.contrib import admin
from hq_stage import urls as stage_urls
from hq_warehouse import urls as warehouse_urls
from hq_hotel_mart import urls as hotel_mart_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls)
,   url(r'^stage/', include(stage_urls))
,   url(r'^warehose/', include(warehouse_urls))
,   url(r'', include(hotel_mart_urls))
]

