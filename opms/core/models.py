from django.db import models
from django.utils.encoding import smart_str, smart_unicode

# Remember: this application is managed by Django South so when you change this file, do the following:
# python manage.py schemamigration core --auto
# python manage.py migrate core
# NB: Can't convert existing fields to foreignkeys in one step. Need to do two migrations. http://south.aeracode.org/ticket/498

class PersonManager(models.Manager):
    def get_all_guids(self):
#        from django.db import connection
#        cursor = connection.cursor()
#        cursor.execute("""
#            SELECT p.titles, p.first_name, p.last_name, i.title, fif.guid
#            FROM ffm_person as p
#              LEFT OUTER JOIN ffm_role as r ON p.id = r.person_id
#              LEFT OUTER JOIN ffm_item as i ON r.item_id = i.id
#              LEFT OUTER JOIN ffm_file as f ON i.id = f.item_id
#              LEFT OUTER JOIN ffm_fileinfeed as fif ON f.id = fif.file_id
#            ORDER BY 3,2;
#        """)
#        desc = cursor.description
#        return [
#        dict(zip([col[0] for col in desc], row))
#        for row in cursor.fetchall()
#        ]
        return None

class Person(models.Model):
    titles = models.CharField("Honorifics and Titles", max_length=100, default='')
    first_name = models.CharField("First Name", max_length=50, default='Unknown')
    middle_names = models.CharField("Middle Names", max_length=200, default='')
    last_name = models.CharField("Last Name", max_length=50, default='Person')
    suffix = models.CharField("Further honorifics and titles", max_length=100, default='')
    additional_information = models.TextField("Additional Information (e.g. University of Oxford)", default='')
    biography = models.TextField("Unformated biographical information", default='')
    email = models.EmailField(null=True)

    def full_name(self):
        string = self.titles
        if string != '':
            string += ' ' + self.first_name
        if self.middle_names != '':
            string += ' ' + self.middle_names
        string += ' ' + self.last_name
        if self.suffix != '':
            string += ' ' + self.suffix
        if self.additional_information != '':
            string += ' (' + self.additional_information + ')'
        return smart_unicode(string)

    def short_name(self):
        return smart_unicode(self.first_name + ' ' + self.last_name)

    def __unicode__(self):
        return self.full_name()

    extended = PersonManager() # Manager for merged data
    objects = models.Manager() # Default manager


class Unit(models.Model):
    full_name = models.CharField("unit name", max_length=250)
    oucs_unitcode = models.CharField("oucs unit code", max_length=50)
    oxpoints_id = models.IntegerField("OxItems ID", null=True)

    def __unicode__(self):
        return smart_unicode(self.full_name)
