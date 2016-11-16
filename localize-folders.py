#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
import kopano
from MAPI.Util import *
import locale
import gettext


def opt_args():
    parser = kopano.parser('skpfucm')

    parser.add_option("--lang", dest="lang", action="store", help="A <lang> could be: nl_NL.UTF-8")
    parser.add_option("--reset", dest="reset", action="store_true", help="Reset the folder names to Default English")
    parser.add_option("--dry-run", dest="dryrun", action="store_true", help="Run script without making modifications")
    parser.add_option("--verbose", dest="verbose", action="store_true", help="Run script with output")

    return parser.parse_args()


def translate(lang, reset):
    if reset:
        trans = {"sentmail": "Sent Items",
                 "outbox": "Outbox",
                 "wastebasket": "Deleted Items",
                 "inbox": "Inbox",
                 "calendar": "Calendar",
                 "contacts": "Contacts",
                 "drafts": "Drafts",
                 "journal": "Journal",
                 "notes": "Notes",
                 "tasks": "Tasks",
                 "junk": "Junk E-mail"}
    else:
        try:
            locale.setlocale(locale.LC_ALL, lang)
        except locale.Error:
            print 'Error: %s Is not a language pack or is not installed' % lang
            sys.exit(1)

        encoding = locale.getlocale()[1]

        if "UTF-8" not in encoding:
            print 'Error: Locale "%s" is in "%s" not in UTF-8, please select an appropriate UTF-8 locale.' % (
                lang, encoding)
            sys.exit(1)
        try:
            t = gettext.translation('kopano', "/usr/share/locale", languages=[locale.getlocale()[0]])
            _ = t.gettext
        except (ValueError, IOError):
            print 'Error: kopano is not translated in %s' % lang
            sys.exit(1)

        trans = {"sentmail": _("Sent Items"),
                 "outbox": _("Outbox"),
                 "wastebasket": _("Deleted Items"),
                 "inbox": _("Inbox"),
                 "calendar": _("Calendar"),
                 "contacts": _("Contacts"),
                 "drafts": _("Drafts"),
                 "journal": _("Journal"),
                 "notes": _("Notes"),
                 "tasks": _("Tasks"),
                 "junk": _("Junk E-mail")}
    return trans


def main():
    options, args = opt_args()

    if not options.lang and not options.reset:
        print 'Usage:\n%s -u <username> --lang <language>  ' % sys.argv[0]
        sys.exit(1)

    trans = translate(options.lang, options.reset)
    for user in kopano.Server(options).users(options.users):
        print user.name
        print '%s: Changing localized folder names to \"%s\"' % (user.name, options.lang)

        if options.verbose:
            print 'Running in verbose mode'
        if options.dryrun:
            print 'Running in dry mode no changes will be made'

        for mapifolder in trans:
            try:
                folderobject = getattr(user.store, mapifolder)
            except AttributeError as e:
                print 'Warning: Cannot find MAPI folder %s, error code: %s' % (mapifolder, e)
                continue

            localizedname = trans[mapifolder]
            if options.verbose or options.dryrun:
                print 'Changing MAPI "%s" -> Renaming "%s" to "%s"' % (mapifolder, folderobject.name, localizedname)
            if not options.dryrun:
                folderobject.prop(PR_DISPLAY_NAME).set_value(localizedname)


if __name__ == "__main__":
    main()