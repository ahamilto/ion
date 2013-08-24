import ldap
import logging
import os
import urllib
import urlparse
from django.contrib.auth import logout
from django.shortcuts import redirect
from intranet.apps.auth.views import login_view
from intranet.db.ldap_db import LDAPConnection
from intranet.utils import urls

logger = logging.getLogger(__name__)


class CheckLDAPBindMiddleware:

    def process_request(self, request):
        if not request.user.is_authenticated():
            # Nothing to check if user isn't already logged in
            return
        try:
            c = LDAPConnection()
        except ldap.LOCAL_ERROR:
            logger.critical("Unable to bind to LDAP")
            try:
                kerberos_cache = request.session["KRB5CCNAME"]
                os.system("/usr/bin/kdestroy -c " + kerberos_cache)
            except KeyError:
                pass
            logger.info("Destroying kerberos cache and logging out")
            logout(request)

            response = redirect("login")
            url = response["Location"]
            response["Location"] = urls.add_get_parameters(
                url, {"next": request.path}, percent_encode=False)
            return response