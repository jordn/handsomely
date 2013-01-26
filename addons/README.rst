=====================
django_localflavor_gb
=====================

Country-specific Django helpers for the United Kingdom.

What's in the United Kingdom localflavor?
=========================================

* forms.GBPostcodeField: A form field that validates input as a UK postcode.
  The regular expression used is sourced from the schema for British Standard
  BS7666 address types at http://www.cabinetoffice.gov.uk/media/291293/bs7666-v2-0.xml

* forms.GBCountySelect: A ``Select`` widget that uses a list of UK
  counties/regions as its choices.

* forms.GBNationSelect: A ``Select`` widget that uses a list of UK nations as
  its choices.

See the source code for full details.

About localflavors
==================

Django's "localflavor" packages offer additional functionality for particular
countries or cultures.

For example, these might include form fields for your country's postal codes,
phone number formats or government ID numbers.

This code used to live in Django proper -- in django.contrib.localflavor -- but
was separated into standalone packages in Django 1.5 to keep the framework's
core clean.

For a full list of available localflavors, see https://github.com/django/
