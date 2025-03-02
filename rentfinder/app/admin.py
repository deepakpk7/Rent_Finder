from django.contrib import admin
from .models import House
from django.utils.html import format_html

# Register your models here.

admin.site.register(House)