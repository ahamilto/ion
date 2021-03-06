# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import ldap
import ldap.sasl
from threading import local
from django.core.signals import request_finished
from django.core.handlers.wsgi import WSGIHandler
from django.dispatch import receiver
from intranet import settings

logger = logging.getLogger(__name__)
_thread_locals = local()


class LDAPFilter(object):
    @staticmethod
    def operator(operator, *conditions):
        return "(" + operator + "".join(("(" + c + ")" for c in conditions)) + ")"

    @staticmethod
    def and_filter(*conditions):
        return LDAPFilter.operator("&", *conditions)

    @staticmethod
    def or_filter(*conditions):
        return LDAPFilter.operator("|", *conditions)

    @staticmethod
    def attribute_in_list(attribute, values):
        """Returns a filter for selecting all entries for which a
        specified attribute is contained in a specified list of values.
        """
        conditions = (attribute + "=" + v for v in values)
        return LDAPFilter.or_filter(*conditions)

    @staticmethod
    def all_users():
        """Returns a filter for selecting all user objects in LDAP
        """

        user_object_classes = settings.LDAP_OBJECT_CLASSES.values()
        return LDAPFilter.attribute_in_list("objectclass", user_object_classes)


class LDAPConnection(object):
    """Represents an LDAP connection with wrappers for the raw ldap
    queries.

    Attributes:
        conn: The singleton LDAP connection.

    """
    def __init__(self):
        """Initialize a singleton LDAPConnection object.

        Connect to the LDAP server specified in settings and bind
        using the GSSAPI protocol. The requisite KRB5CCNAME
        environmental variable should have already been set by the
        SetKerberosCache middleware.

        """
        if (not hasattr(_thread_locals, "ldap_conn")) \
           or (_thread_locals.ldap_conn is None):
            logger.info("Connecting to LDAP...")
            _thread_locals.ldap_conn = ldap.ldapobject.ReconnectLDAPObject(settings.LDAP_SERVER, trace_stack_limit=None)

            try:
                auth_tokens = ldap.sasl.gssapi()
                _thread_locals.ldap_conn.sasl_interactive_bind_s('', auth_tokens)
                logger.info("Successfully connected to LDAP.")
            except (ldap.LOCAL_ERROR, ldap.INVALID_CREDENTIALS):
                _thread_locals.ldap_conn.simple_bind_s(settings.AUTHUSER_DN, settings.AUTHUSER_PASSWORD)
                logger.error("SASL bind failed - using simple bind")
            # logger.debug(_thread_locals.ldap_conn.whoami_s())

    @property
    def raw_connection(self):
        """Return the raw connection from threadlocals
        """

        return _thread_locals.ldap_conn

    def search(self, dn, filter, attributes):
        """Search LDAP and return an LDAPResult.

        Search LDAP with the given dn and filter and return the given
        attributes in an LDAPResult object.

        Args:
            dn: The string representation of the distinguished name
                (DN) of the entry at which to start the search.
            filter: The string representation of the filter to apply to
                the search.
            attributes: A list of LDAP attributes (as strings)
                to retrieve.

        Returns:
            An LDAPResult object.

        Raises:
            Should raise stuff but it doesn't yet

        """
        logger.debug("Searching ldap - dn: {}, filter: {}, "
                     "attributes: {}".format(dn, filter, attributes))

        # tip-toe around unicode bugs
        attributes = [str(attr) for attr in attributes]

        return _thread_locals.ldap_conn.search_s(dn, ldap.SCOPE_SUBTREE,
                                                 filter, attributes)

    def user_attributes(self, dn, attributes):
        """Fetch a list of attributes of the specified user.

        Fetch LDAP attributes of a tjhsstStudent or a tjhsstTeacher. The
        LDAPResult will contain an empty set of results if the user does
        not exist.

        Args:
            dn: The full DN of the user
            attributes: A list of the LDAP fields to fetch (strings)

        Returns:
            LDAPResult object (empty if no results)

        """
        logger.debug("Fetching attributes '{}' of user "
                     "{}".format(str(attributes), dn))

        filter = LDAPFilter.all_users()

        try:
            r = self.search(dn, filter, attributes)
        except ldap.NO_SUCH_OBJECT as e:
            logger.error("No such user " + dn)
            raise
        return LDAPResult(r)

    def class_attributes(self, dn, attributes):
        """Fetch a list of attributes of the specified class.

        Fetch LDAP attributes of a tjhsstClass. The LDAPResult will
        contain an empty set of results if the class does not exist.

        Args:
            dn: The full DN of the class
            attributes: A list of the LDAP fields to fetch (strings)

        Returns:
            LDAPResult object (empty if no results)

        """
        logger.debug("Fetching attributes '" + str(attributes) +
                     "' of class " + dn)
        filter = '(objectclass=tjhsstClass)'

        try:
            r = self.search(dn, filter, attributes)
        except ldap.NO_SUCH_OBJECT:
            logger.error("No such class " + dn)
            raise
        return LDAPResult(r)


class LDAPResult(object):
    """Represents the result of an LDAP query.

    LDAPResult stores the raw result of an LDAP query and can process
    the results in various ways.

    Attributes:
        result: the raw result of an LDAP query

    """

    def __init__(self, result):
        self.result = result

    def first_result(self):
        """Fetch the first LDAP object in the response."""
        if len(self.result) > 0:
            return self.result[0][1]
        else:
            return []

    def results_array(self):
        """Return the full array of results."""
        return self.result


@receiver(request_finished,
          dispatch_uid="close_ldap_connection",
          sender=WSGIHandler)
def close_ldap_connection(sender, **kwargs):
    """Closes the request's LDAP connection.

    Listens for the request_finished signal from Django and upon
    receit, unbinds from the directory, terminates the current
    association, and frees resources.

    It would be nice if we could leave the connections open in a pool,
    but it looks like rebinding on an open connection isn't possible
    with GSSAPI binds.

    """
    if hasattr(_thread_locals, 'ldap_conn'):
        if _thread_locals.ldap_conn is not None:
            _thread_locals.ldap_conn.unbind_s()
            _thread_locals.ldap_conn = None
            logger.info("LDAP connection closed.")
