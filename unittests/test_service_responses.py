# Copyright Notice:
# Copyright 2020-2022 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link:
# https://github.com/DMTF/Redfish-Protocol-Validator/blob/master/LICENSE.md

import unittest
from unittest import mock, TestCase

import requests

from redfish_protocol_validator import service_responses as resp
from redfish_protocol_validator.system_under_test import SystemUnderTest
from redfish_protocol_validator.constants import Assertion, RequestType, ResourceType, Result
from unittests.utils import add_response, get_result


class ServiceResponses(TestCase):

    def setUp(self):
        super(ServiceResponses, self).setUp()
        self.sut = SystemUnderTest('https://127.0.0.1:8000', 'oper', 'xyzzy')
        self.sut.set_sessions_uri('/redfish/v1/SessionService/Sessions')
        self.sut.set_nav_prop_uri('Systems', '/redfish/v1/Systems')
        self.mock_session = mock.MagicMock(spec=requests.Session)
        self.sut._set_session(self.mock_session)

    def test_test_allow_header_method_not_allowed_not_tested(self):
        resp.test_allow_header_method_not_allowed(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_HEADERS_ALLOW_METHOD_NOT_ALLOWED, '', '')
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No responses found that returned a %s status code' %
                      requests.codes.METHOD_NOT_ALLOWED, result['msg'])

    def test_test_allow_header_method_not_allowed_fail(self):
        uri = '/redfish/v1/'
        add_response(self.sut, uri, 'POST',
                     status_code=requests.codes.METHOD_NOT_ALLOWED, headers={})
        resp.test_allow_header_method_not_allowed(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_HEADERS_ALLOW_METHOD_NOT_ALLOWED,
            'POST', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The Allow header was missing from response to %s '
                      'request to %s' % ('POST', uri), result['msg'])

    def test_test_allow_header_method_not_allowed_pass(self):
        uri = '/redfish/v1/'
        add_response(self.sut, uri, 'POST',
                     status_code=requests.codes.METHOD_NOT_ALLOWED,
                     headers={'Allow': 'GET, HEAD, PATCH'})
        resp.test_allow_header_method_not_allowed(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_HEADERS_ALLOW_METHOD_NOT_ALLOWED,
            'POST', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])
        self.assertIn('Test passed for header %s: %s'
                      % ('Allow', 'GET, HEAD, PATCH'), result['msg'])

    def test_test_allow_header_get_or_head_not_tested(self):
        uri = '/redfish/v1/'
        resp.test_allow_header_get_or_head(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_ALLOW_GET_OR_HEAD,
                            'HEAD', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No response found for %s request to %s' %
                      ('HEAD', uri), result['msg'])

    def test_test_allow_header_get_or_head_fail(self):
        uri = '/redfish/v1/'
        method = 'HEAD'
        add_response(self.sut, uri, method, status_code=requests.codes.OK,
                     headers={})
        resp.test_allow_header_get_or_head(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_ALLOW_GET_OR_HEAD,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The %s header was missing from the response to the %s '
                      'request to URI %s' % ('Allow', method, uri),
                      result['msg'])

    def test_test_allow_header_get_or_head_pass(self):
        uri = '/redfish/v1/'
        add_response(self.sut, uri, 'GET', status_code=requests.codes.OK,
                     headers={'Allow': 'GET, HEAD, PATCH'})
        resp.test_allow_header_get_or_head(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_ALLOW_GET_OR_HEAD,
                            'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])
        self.assertIn('Test passed for header %s: %s'
                      % ('Allow', 'GET, HEAD, PATCH'), result['msg'])

    def test_test_cache_control_header_not_tested1(self):
        uri = '/redfish/v1/'
        method = 'GET'
        resp.test_cache_control_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_CACHE_CONTROL,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No successful response found for %s request to %s' %
                      (method, uri), result['msg'])

    def test_test_cache_control_header_not_tested2(self):
        uri = '/redfish/v1/'
        method = 'GET'
        add_response(self.sut, uri, method,
                     status_code=requests.codes.NOT_FOUND, headers={})
        resp.test_cache_control_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_CACHE_CONTROL,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No successful response found for %s request to %s' %
                      (method, uri), result['msg'])

    def test_test_cache_control_header_fail(self):
        uri = '/redfish/v1/'
        method = 'GET'
        add_response(self.sut, uri, method, status_code=requests.codes.OK,
                     headers={})
        resp.test_cache_control_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_CACHE_CONTROL,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The %s header was missing from the response to the %s '
                      'request to URI %s' % ('Cache-Control', method, uri),
                      result['msg'])

    def test_test_cache_control_header_pass(self):
        uri = '/redfish/v1/'
        method = 'GET'
        add_response(self.sut, uri, method, status_code=requests.codes.OK,
                     headers={'Cache-Control': 'no-cache'})
        resp.test_cache_control_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_CACHE_CONTROL,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])
        self.assertIn('Test passed for header %s: %s'
                      % ('Cache-Control', 'no-cache'), result['msg'])

    def test_test_content_type_header_not_tested1(self):
        uri = '/redfish/v1/'
        method = 'GET'
        resp.test_content_type_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_CONTENT_TYPE,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No successful response found for %s request to %s' %
                      (method, uri), result['msg'])

    def test_test_content_type_header_not_tested2(self):
        uri = '/redfish/v1/'
        method = 'GET'
        add_response(self.sut, uri, method,
                     status_code=requests.codes.NOT_FOUND, headers={})
        resp.test_content_type_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_CONTENT_TYPE,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertEqual(requests.codes.NOT_FOUND, result['status'])
        self.assertIn('No successful response found for %s request to %s' %
                      (method, uri), result['msg'])

    def test_test_content_type_header_fail1(self):
        uri = '/redfish/v1/'
        method = 'GET'
        add_response(self.sut, uri, method, status_code=requests.codes.OK,
                     headers={})
        resp.test_content_type_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_CONTENT_TYPE,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The %s header was missing from the response to the %s '
                      'request to URI %s' % ('Content-Type', method, uri),
                      result['msg'])

    def test_test_content_type_header_fail2(self):
        uri = '/redfish/v1/EventService/SSE'
        self.sut.set_server_sent_event_uri(uri)
        method = 'GET'
        add_response(self.sut, uri, method, status_code=requests.codes.OK,
                     headers={'Content-Type': 'text/html'},
                     request_type=RequestType.STREAMING)
        resp.test_content_type_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_CONTENT_TYPE,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The %s header value from the response to the %s '
                      'request to URI %s was %s; expected %s' %
                      ('Content-Type', method, uri, 'text/html',
                       'text/event-stream'), result['msg'])

    def test_test_content_type_header_pass(self):
        uri = '/redfish/v1/'
        method = 'GET'
        add_response(self.sut, uri, method, status_code=requests.codes.OK,
                     headers={'Content-Type': 'application/json'})
        resp.test_content_type_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_CONTENT_TYPE,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])
        self.assertIn('Test passed for header %s: %s' %
                      ('Content-Type', 'application/json'), result['msg'])

    def test_test_etag_header_not_tested(self):
        uri = '/redfish/v1/AccountsService/Accounts/1'
        method = 'GET'
        add_response(self.sut, uri, method,
                     status_code=requests.codes.NOT_FOUND,
                     res_type=ResourceType.MANAGER_ACCOUNT)
        resp.test_etag_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_ETAG,
                            method, '')
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No successful response found for %s request to %s' %
                      (method, 'ManagerAccount'), result['msg'])

    def test_test_etag_header_fail(self):
        uri = '/redfish/v1/AccountsService/Accounts/1'
        method = 'GET'
        r = add_response(self.sut, uri, method,
                         status_code=requests.codes.OK,
                         res_type=ResourceType.MANAGER_ACCOUNT)
        r.headers['ETag'] = None
        resp.test_etag_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_ETAG,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The %s header was missing from the response to the '
                      '%s request to URI %s' % ('ETag', method, uri),
                      result['msg'])

    def test_test_etag_header_pass(self):
        uri = '/redfish/v1/AccountsService/Accounts/1'
        method = 'GET'
        r = add_response(self.sut, uri, method,
                         status_code=requests.codes.OK,
                         res_type=ResourceType.MANAGER_ACCOUNT)
        r.headers['ETag'] = 'abcd1234'
        resp.test_etag_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_ETAG,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])
        self.assertIn('Test passed for header %s: %s' % ('ETag', 'abcd1234'),
                      result['msg'])

    def test_test_link_header_not_tested(self):
        uri = '/redfish/v1/'
        method = 'GET'
        add_response(self.sut, uri, method,
                     status_code=requests.codes.NOT_FOUND)
        resp.test_link_header(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_HEADERS_LINK_REL_DESCRIBED_BY,
            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No successful response found for %s request to %s' %
                      (method, uri), result['msg'])

    def test_test_link_header_fail1(self):
        uri = '/redfish/v1/'
        method = 'GET'
        r = add_response(self.sut, uri, method,
                         status_code=requests.codes.OK,
                         headers={})
        r.links = {}
        resp.test_link_header(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_HEADERS_LINK_REL_DESCRIBED_BY,
            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The response did not include a Link header',
                      result['msg'])

    def test_test_link_header_fail2(self):
        uri = '/redfish/v1/'
        method = 'GET'
        uri_ref = '/redfish/v1/SchemaStore/en/ServiceRoot.json'
        r = add_response(
            self.sut, uri, method, status_code=requests.codes.OK,
            headers={'Link': '<%s>; rel=next' % uri_ref})
        r.links = {
            'next': {
                'url': uri_ref,
                'rel': 'next'
            }
        }
        resp.test_link_header(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_HEADERS_LINK_REL_DESCRIBED_BY,
            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The response included a Link header, but not one with '
                      'a rel=describedby param; %s: %s' %
                      ('Link', '<%s>; rel=next' % uri_ref), result['msg'])

    def test_test_link_header_pass(self):
        uri = '/redfish/v1/'
        method = 'GET'
        uri_ref = '/redfish/v1/SchemaStore/en/ServiceRoot.json'
        r = add_response(
            self.sut, uri, method, status_code=requests.codes.OK,
            headers={'Link': '<%s>; rel=describedby' % uri_ref})
        r.links = {
            'describedby': {
                'url': uri_ref,
                'rel': 'describedby'
            }
        }
        resp.test_link_header(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_HEADERS_LINK_REL_DESCRIBED_BY,
            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])
        self.assertIn('Test passed for header %s: %s' %
                      ('Link', '<%s>; rel=describedby' % uri_ref),
                      result['msg'])

    def test_test_link_header_schema_ver_match_fail1(self):
        uri = '/redfish/v1/'
        method = 'GET'
        uri_ref = ''
        r = add_response(self.sut, uri, method,
                         status_code=requests.codes.OK)
        resp.test_link_header_schema_ver_match(
            self.sut, uri_ref, uri, method, r)
        result = get_result(
            self.sut, Assertion.RESP_HEADERS_LINK_SCHEMA_VER_MATCH,
            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The Link header with a rel=describedby param did not '
                      'include a URI reference', result['msg'])

    def test_test_link_header_schema_ver_match_fail2(self):
        uri = '/redfish/v1/'
        method = 'GET'
        uri_ref = '/redfish/v1/SchemaStore/en/ServiceRoot.v1_5_0.json'
        odata_type = '#ServiceRoot.v1_5_1.ServiceRoot'
        r = add_response(self.sut, uri, method, status_code=requests.codes.OK,
                         json={'@odata.type': odata_type})
        resp.test_link_header_schema_ver_match(
            self.sut, uri_ref, uri, method, r)
        result = get_result(
            self.sut, Assertion.RESP_HEADERS_LINK_SCHEMA_VER_MATCH,
            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('Link header (%s) did not match the resource version '
                      'from the @odata.type property (%s)' %
                      (uri_ref, odata_type), result['msg'])

    def test_test_link_header_schema_ver_match_pass1(self):
        uri = '/redfish/v1/'
        method = 'GET'
        uri_ref = '/redfish/v1/SchemaStore/en/ServiceRoot.json'
        odata_type = '#ServiceRoot.v1_5_1.ServiceRoot'
        r = add_response(self.sut, uri, method, status_code=requests.codes.OK,
                         json={'@odata.type': odata_type})
        resp.test_link_header_schema_ver_match(
            self.sut, uri_ref, uri, method, r)
        result = get_result(
            self.sut, Assertion.RESP_HEADERS_LINK_SCHEMA_VER_MATCH,
            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])
        self.assertIn('Test passed for unversioned resource %s' %
                      'ServiceRoot', result['msg'])

    def test_test_link_header_schema_ver_match_pass2(self):
        uri = '/redfish/v1/'
        method = 'GET'
        uri_ref = '/redfish/v1/SchemaStore/en/ServiceRoot.v1_5_1.json'
        odata_type = '#ServiceRoot.v1_5_1.ServiceRoot'
        r = add_response(self.sut, uri, method, status_code=requests.codes.OK,
                         json={'@odata.type': odata_type})
        resp.test_link_header_schema_ver_match(
            self.sut, uri_ref, uri, method, r)
        result = get_result(
            self.sut, Assertion.RESP_HEADERS_LINK_SCHEMA_VER_MATCH,
            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])
        self.assertIn('Test passed for versioned resource %s' %
                      'ServiceRoot.v1_5_1', result['msg'])

    def test_test_location_header_not_tested(self):
        method = 'POST'
        resp.test_location_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_LOCATION,
                            method, '')
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No successful POST (create) response found',
                      result['msg'])

    def test_test_location_header_fail1(self):
        method = 'POST'
        uri = '/redfish/v1/Foo'
        add_response(self.sut, uri, method, status_code=requests.codes.CREATED,
                     headers={})
        resp.test_location_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_LOCATION,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The %s header was missing from the response to the '
                      '%s request to URI %s' % ('Location', method, uri),
                      result['msg'])

    def test_test_location_header_fail2(self):
        method = 'POST'
        uri = self.sut.sessions_uri
        add_response(self.sut, uri, method, status_code=requests.codes.CREATED,
                     headers={'Location': uri + '/c123'})
        resp.test_location_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_LOCATION,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The %s header was missing from the response to the '
                      '%s request to URI %s' % ('X-Auth-Token', method, uri),
                      result['msg'])

    def test_test_location_header_pass(self):
        method = 'POST'
        uri = self.sut.sessions_uri
        add_response(self.sut, uri, method, status_code=requests.codes.CREATED,
                     headers={'Location': uri + '/c123',
                              'X-Auth-Token': '1a2b3c4'})
        resp.test_location_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_LOCATION,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])
        self.assertIn('Test passed for header %s' % 'X-Auth-Token',
                      result['msg'])

    def test_test_odata_version_header_fail1(self):
        method = 'GET'
        uri = '/redfish/v1/'
        add_response(self.sut, uri, method, status_code=requests.codes.OK,
                     headers={})
        resp.test_odata_version_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_ODATA_VERSION,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The %s header was missing from the response to the '
                      '%s request to URI %s' % ('OData-Version', method, uri),
                      result['msg'])

    def test_test_odata_version_header_fail2(self):
        method = 'GET'
        uri = '/redfish/v1/'
        add_response(self.sut, uri, method, status_code=requests.codes.OK,
                     headers={'OData-Version': '4.1'})
        resp.test_odata_version_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_ODATA_VERSION,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The %s header value from the response to the '
                      '%s request to URI %s was %s; expected %s' %
                      ('OData-Version', method, uri, '4.1', '4.0'),
                      result['msg'])

    def test_test_odata_version_header_pass(self):
        method = 'GET'
        uri = '/redfish/v1/'
        add_response(self.sut, uri, method, status_code=requests.codes.OK,
                     headers={'OData-Version': '4.0'})
        resp.test_odata_version_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_ODATA_VERSION,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])
        self.assertIn('Test passed for header %s: %s' %
                      ('OData-Version', '4.0'), result['msg'])

    def test_test_www_authenticate_header_not_tested(self):
        resp.test_www_authenticate_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_WWW_AUTHENTICATE,
                            '', '')
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No 401 Unauthorized responses found', result['msg'])

    def test_test_www_authenticate_header_fail(self):
        uri = '/redfish/v1/Systems'
        method = 'GET'
        add_response(self.sut, uri, method,
                     status_code=requests.codes.UNAUTHORIZED,
                     request_type=RequestType.NO_AUTH,
                     headers={})
        resp.test_www_authenticate_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_WWW_AUTHENTICATE,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The %s header was missing from the response to the '
                      '%s request to URI %s' %
                      ('WWW-Authenticate', method, uri), result['msg'])

    def test_test_www_authenticate_header_pass(self):
        uri = self.sut.systems_uri
        method = 'GET'
        add_response(self.sut, uri, method,
                     status_code=requests.codes.UNAUTHORIZED,
                     request_type=RequestType.NO_AUTH,
                     headers={'WWW-Authenticate': 'Basic'})
        resp.test_www_authenticate_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_WWW_AUTHENTICATE,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])
        self.assertIn('Test passed for header %s: %s' %
                      ('WWW-Authenticate', 'Basic'), result['msg'])

    def test_test_x_auth_token_header_not_tested1(self):
        method = 'POST'
        uri = self.sut.sessions_uri
        resp.test_x_auth_token_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_X_AUTH_TOKEN,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No successful response found for POST to Sessions URI',
                      result['msg'])

    def test_test_x_auth_token_header_not_tested2(self):
        method = 'POST'
        uri = self.sut.sessions_uri
        add_response(self.sut, uri, method, status_code=requests.codes.CREATED,
                     headers={'X-Auth-Token': 'YXN1cmUu'})
        resp.test_x_auth_token_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_X_AUTH_TOKEN,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('The security token is not a hexadecimal string',
                      result['msg'])

    def test_test_x_auth_token_header_warn(self):
        method = 'POST'
        uri = self.sut.sessions_uri
        add_response(self.sut, uri, method, status_code=requests.codes.CREATED,
                     headers={'X-Auth-Token': '00002000'})
        resp.test_x_auth_token_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_X_AUTH_TOKEN,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.WARN, result['result'])
        self.assertIn('The security token from the %s header may not be '
                      'sufficiently random' % 'X-Auth-Token', result['msg'])

    def test_test_x_auth_token_header_fail(self):
        method = 'POST'
        uri = self.sut.sessions_uri
        add_response(self.sut, uri, method, status_code=requests.codes.CREATED,
                     headers={})
        resp.test_x_auth_token_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_X_AUTH_TOKEN,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The %s header was missing from the response to the '
                      'POST request to the Sessions URI' % 'X-Auth-Token',
                      result['msg'])

    def test_test_x_auth_token_header_pass(self):
        method = 'POST'
        uri = self.sut.sessions_uri
        add_response(self.sut, uri, method, status_code=requests.codes.CREATED,
                     headers={'X-Auth-Token': 'C90FDAA22168C234C4C6628B8'})
        resp.test_x_auth_token_header(self.sut)
        result = get_result(self.sut, Assertion.RESP_HEADERS_X_AUTH_TOKEN,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])
        self.assertIn('Test passed for header %s' % 'X-Auth-Token',
                      result['msg'])

    def test_test_status_bad_request_not_tested(self):
        resp.test_status_bad_request(self.sut)
        result = get_result(self.sut, Assertion.RESP_STATUS_BAD_REQUEST,
                            '', '')
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No response with a %s status code was found' %
                      requests.codes.BAD_REQUEST, result['msg'])

    def test_test_status_bad_request_fail1(self):
        uri = '/redfish/v1/Managers/BMC/NetworkProtocol'
        method = 'PATCH'
        add_response(self.sut, uri, method,
                     status_code=requests.codes.BAD_REQUEST,
                     request_type=RequestType.PATCH_BAD_PROP,
                     json={})
        resp.test_status_bad_request(self.sut)
        result = get_result(self.sut, Assertion.RESP_STATUS_BAD_REQUEST,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The required "error" property was missing from the '
                      'error response', result['msg'])

    def test_test_status_bad_request_fail2(self):
        uri = '/redfish/v1/Managers/BMC/NetworkProtocol'
        method = 'PATCH'
        add_response(self.sut, uri, method,
                     status_code=requests.codes.BAD_REQUEST,
                     request_type=RequestType.PATCH_BAD_PROP,
                     json={'error': {'code': 'Base.1.8.GeneralError'}})
        resp.test_status_bad_request(self.sut)
        result = get_result(self.sut, Assertion.RESP_STATUS_BAD_REQUEST,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The required "code" or "message" properties were '
                      'missing from the error response', result['msg'])

    def test_test_status_bad_request_fail3(self):
        uri = '/redfish/v1/Managers/BMC/NetworkProtocol'
        method = 'PATCH'
        add_response(self.sut, uri, method,
                     status_code=requests.codes.BAD_REQUEST,
                     request_type=RequestType.PATCH_BAD_PROP,
                     headers={'Content-Type': 'text/html'},
                     text='<html></html>')
        resp.test_status_bad_request(self.sut)
        result = get_result(self.sut, Assertion.RESP_STATUS_BAD_REQUEST,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The response payload type was %s; expected %s' %
                      ('text/html', 'application/json'), result['msg'])

    def test_test_status_bad_request_pass(self):
        uri = '/redfish/v1/Managers/BMC/NetworkProtocol'
        method = 'PATCH'
        add_response(self.sut, uri, method,
                     status_code=requests.codes.BAD_REQUEST,
                     request_type=RequestType.PATCH_BAD_PROP,
                     json={'error': {'code': 'Base.1.8.GeneralError',
                                     'message': 'The property ...'}})
        resp.test_status_bad_request(self.sut)
        result = get_result(self.sut, Assertion.RESP_STATUS_BAD_REQUEST,
                            method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])

    def test_test_status_internal_server_error_not_tested(self):
        resp.test_status_internal_server_error(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_STATUS_INTERNAL_SERVER_ERROR, '', '')
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No response with a %s status code was found' %
                      requests.codes.SERVER_ERROR, result['msg'])

    def test_test_status_internal_server_error_pass(self):
        uri = '/redfish/v1/SSE'
        method = 'GET'
        add_response(self.sut, uri, method,
                     status_code=requests.codes.SERVER_ERROR,
                     request_type=RequestType.STREAMING,
                     json={'error': {'code': 'Base.1.8.GeneralError',
                                     'message': 'The property ...'}})
        resp.test_status_internal_server_error(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_STATUS_INTERNAL_SERVER_ERROR, method, uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])

    def test_test_odata_metadata_mime_type_not_tested(self):
        uri = '/redfish/v1/$metadata'
        resp.test_odata_metadata_mime_type(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_METADATA_MIME_TYPE, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No response found for URI %s' %
                      uri, result['msg'])

    def test_test_odata_metadata_mime_type_fail1(self):
        uri = '/redfish/v1/$metadata'
        add_response(self.sut, uri, 'GET',
                     status_code=requests.codes.OK,
                     headers={'Content-Type': 'text/xml'})
        resp.test_odata_metadata_mime_type(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_METADATA_MIME_TYPE, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The MIME type for the OData metadata document is %s' %
                      'text/xml', result['msg'])

    def test_test_odata_metadata_mime_type_fail2(self):
        uri = '/redfish/v1/$metadata'
        add_response(self.sut, uri, 'GET',
                     status_code=requests.codes.NOT_FOUND)
        resp.test_odata_metadata_mime_type(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_METADATA_MIME_TYPE, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('%s request to URI %s failed with status %s' %
                      ('GET', uri, requests.codes.NOT_FOUND), result['msg'])

    def test_test_odata_metadata_mime_type_pass1(self):
        uri = '/redfish/v1/$metadata'
        add_response(self.sut, uri, 'GET',
                     status_code=requests.codes.OK,
                     headers={'Content-Type': 'application/xml'})
        resp.test_odata_metadata_mime_type(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_METADATA_MIME_TYPE, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])

    def test_test_odata_metadata_mime_type_pass2(self):
        uri = '/redfish/v1/$metadata'
        add_response(self.sut, uri, 'GET',
                     status_code=requests.codes.OK,
                     headers={'Content-Type': 'application/xml;charset=utf-8'})
        resp.test_odata_metadata_mime_type(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_METADATA_MIME_TYPE, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])

    def test_test_odata_metadata_mime_type_pass3(self):
        uri = '/redfish/v1/$metadata'
        add_response(self.sut, uri, 'GET',
                     status_code=requests.codes.OK,
                     headers={'Content-Type':
                              'application/xml ; charset=UTF-8'})
        resp.test_odata_metadata_mime_type(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_METADATA_MIME_TYPE, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])

    def test_test_odata_metadata_entity_container_not_tested(self):
        uri = '/redfish/v1/$metadata'
        resp.test_odata_metadata_entity_container(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_METADATA_ENTITY_CONTAINER, 'GET',
            uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No response found for URI %s' %
                      uri, result['msg'])

    def test_test_odata_metadata_entity_container_fail1(self):
        uri = '/redfish/v1/$metadata'
        add_response(self.sut, uri, 'GET',
                     status_code=requests.codes.NOT_FOUND)
        resp.test_odata_metadata_entity_container(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_METADATA_ENTITY_CONTAINER, 'GET',
            uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('%s request to URI %s failed with status %s' %
                      ('GET', uri, requests.codes.NOT_FOUND), result['msg'])

    def test_test_odata_metadata_entity_container_fail2(self):
        uri = '/redfish/v1/$metadata'
        doc = '{"@odata.id": "/redfish/v1/$metadata"}'
        add_response(self.sut, uri, 'GET', status_code=requests.codes.OK,
                     text=doc)
        resp.test_odata_metadata_entity_container(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_METADATA_ENTITY_CONTAINER, 'GET',
            uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('ParseError received while trying to read '
                      'EntityContainer element from the OData metadata '
                      'document', result['msg'])

    def test_test_odata_metadata_entity_container_fail3(self):
        uri = '/redfish/v1/$metadata'
        doc = ('<Edmx><DataServices><Schema>'
               '</Schema></DataServices></Edmx>')
        add_response(self.sut, uri, 'GET', status_code=requests.codes.OK,
                     text=doc)
        resp.test_odata_metadata_entity_container(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_METADATA_ENTITY_CONTAINER, 'GET',
            uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('EntityContainer element not found in OData metadata '
                      'document', result['msg'])

    def test_test_odata_metadata_entity_container_pass(self):
        uri = '/redfish/v1/$metadata'
        doc = ('<Edmx><DataServices><Schema><EntityContainer/>'
               '</Schema></DataServices></Edmx>')
        add_response(self.sut, uri, 'GET', status_code=requests.codes.OK,
                     text=doc)
        resp.test_odata_metadata_entity_container(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_METADATA_ENTITY_CONTAINER, 'GET',
            uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])

    def test_test_odata_service_mime_type_not_tested(self):
        uri = '/redfish/v1/odata'
        resp.test_odata_service_mime_type(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_SERVICE_MIME_TYPE, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No response found for URI %s' %
                      uri, result['msg'])

    def test_test_odata_service_mime_type_fail1(self):
        uri = '/redfish/v1/odata'
        add_response(self.sut, uri, 'GET',
                     status_code=requests.codes.NOT_FOUND)
        resp.test_odata_service_mime_type(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_SERVICE_MIME_TYPE, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('%s request to URI %s failed with status %s' %
                      ('GET', uri, requests.codes.NOT_FOUND), result['msg'])

    def test_test_odata_service_mime_type_fail2(self):
        uri = '/redfish/v1/odata'
        add_response(self.sut, uri, 'GET',
                     status_code=requests.codes.OK,
                     headers={'Content-Type': 'application/xml'})
        resp.test_odata_service_mime_type(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_SERVICE_MIME_TYPE, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The MIME type for the OData service document is %s; '
                      'expected %s' % ('application/xml', 'application/json'),
                      result['msg'])

    def test_test_odata_service_mime_type_pass(self):
        uri = '/redfish/v1/odata'
        add_response(self.sut, uri, 'GET',
                     status_code=requests.codes.OK,
                     headers={'Content-Type': 'application/json'})
        resp.test_odata_service_mime_type(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_SERVICE_MIME_TYPE, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])

    def test_test_odata_service_context_not_tested(self):
        uri = '/redfish/v1/odata'
        resp.test_odata_service_context(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_SERVICE_CONTEXT, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No response found for URI %s' %
                      uri, result['msg'])

    def test_test_odata_service_context_fail1(self):
        uri = '/redfish/v1/odata'
        add_response(self.sut, uri, 'GET',
                     status_code=requests.codes.NOT_FOUND)
        resp.test_odata_service_context(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_SERVICE_CONTEXT, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('%s request to URI %s failed with status %s' %
                      ('GET', uri, requests.codes.NOT_FOUND), result['msg'])

    def test_test_odata_service_context_fail2(self):
        uri = '/redfish/v1/odata'
        add_response(self.sut, uri, 'GET',
                     status_code=requests.codes.OK,
                     json={'@odata.context': uri})
        resp.test_odata_service_context(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_SERVICE_CONTEXT, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The @odata.context property for the OData service '
                      'document is %s; expected %s' %
                      (uri, '/redfish/v1/$metadata'), result['msg'])

    def test_test_odata_service_context_pass(self):
        uri = '/redfish/v1/odata'
        add_response(self.sut, uri, 'GET',
                     status_code=requests.codes.OK,
                     json={'@odata.context': '/redfish/v1/$metadata'})
        resp.test_odata_service_context(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_SERVICE_CONTEXT, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])

    def test_test_odata_service_value_prop_not_tested(self):
        uri = '/redfish/v1/odata'
        resp.test_odata_service_value_prop(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_SERVICE_VALUE_PROP, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.NOT_TESTED, result['result'])
        self.assertIn('No response found for URI %s' %
                      uri, result['msg'])

    def test_test_odata_service_value_prop_fail1(self):
        uri = '/redfish/v1/odata'
        add_response(self.sut, uri, 'GET',
                     status_code=requests.codes.NOT_FOUND)
        resp.test_odata_service_value_prop(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_SERVICE_VALUE_PROP, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('%s request to URI %s failed with status %s' %
                      ('GET', uri, requests.codes.NOT_FOUND), result['msg'])

    def test_test_odata_service_value_prop_fail2(self):
        uri = '/redfish/v1/odata'
        add_response(self.sut, uri, 'GET',
                     status_code=requests.codes.OK,
                     json={})
        resp.test_odata_service_value_prop(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_SERVICE_VALUE_PROP, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The value property for the OData service '
                      'document is missing', result['msg'])

    def test_test_odata_service_value_prop_fail3(self):
        uri = '/redfish/v1/odata'
        add_response(self.sut, uri, 'GET',
                     status_code=requests.codes.OK,
                     json={'value': {}})
        resp.test_odata_service_value_prop(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_SERVICE_VALUE_PROP, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.FAIL, result['result'])
        self.assertIn('The value property for the OData service '
                      'document is type %s; expected list' % 'dict',
                      result['msg'])

    def test_test_odata_service_value_prop_pass(self):
        uri = '/redfish/v1/odata'
        add_response(self.sut, uri, 'GET',
                     status_code=requests.codes.OK,
                     json={'value': []})
        resp.test_odata_service_value_prop(self.sut)
        result = get_result(
            self.sut, Assertion.RESP_ODATA_SERVICE_VALUE_PROP, 'GET', uri)
        self.assertIsNotNone(result)
        self.assertEqual(Result.PASS, result['result'])

    def test_test_service_responses_cover(self):
        resp.test_service_responses(self.sut)


if __name__ == '__main__':
    unittest.main()
