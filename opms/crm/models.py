from django.db import models

# Remember: this application is managed by Django South so when you change this file, do the following:
# python manage.py schemamigration crm --auto
# python manage.py migrate crm
# NB: Can't convert existing fields to foreignkeys in one step. Need to do two migrations. http://south.aeracode.org/ticket/498
