# Copyright Notice:
# Copyright 2020-2022 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link:
# https://github.com/DMTF/Redfish-Protocol-Validator/blob/master/LICENSE.md

import unittest
from unittest import mock, TestCase

import colorama
import requests

from redfish_protocol_validator import utils
from redfish_protocol_validator.constants import Assertion, Result, SSDP_REDFISH
from redfish_protocol_validator.system_under_test import SystemUnderTest


class MyTimeout(OSError):
    def __init__(self, *args, **kwargs):
        pass


class Utils(TestCase):
    def setUp(self):
        super(Utils, self).setUp()
        self.sut = SystemUnderTest('http://127.0.0.1:8000', 'oper', 'xyzzy')
        self.uri = '/redfish/v1/AccountsService/Accounts/3'
        self.etag = 'A89B031B62'
        response = mock.Mock(spec=requests.Response)
        response.status_code = requests.codes.OK
        response.ok = True
        response.headers = mock.Mock()
        response.headers.get.return_value = self.etag
        session = mock.Mock(spec=requests.Session)
        session.get.return_value = response
        self.response = response
        self.session = session
        self.sut.log(Result.PASS, 'GET', 200, '/redfish/v1/foo',
                     Assertion.PROTO_JSON_RFC, 'Test passed')
        self.sut.log(Result.PASS, 'GET', 200, '/redfish/v1/bar',
                     Assertion.PROTO_JSON_RFC, 'Test passed')

    def test_get_etag_header_good(self):
        headers = utils.get_etag_header(self.sut, self.session, self.uri)
        self.assertEqual(headers, {'If-Match': self.etag})

    def test_get_etag_header_no_header(self):
        self.response.headers.get.return_value = None
        headers = utils.get_etag_header(self.sut, self.session, self.uri)
        self.assertEqual(headers, {})

    def test_get_etag_header_get_fail(self):
        self.response.status_code = requests.codes.NOT_FOUND
        self.response.ok = False
        headers = utils.get_etag_header(self.sut, self.session, self.uri)
        self.assertEqual(headers, {})

    def test_get_response_etag_from_header(self):
        etag = utils.get_response_etag(self.response)
        self.assertEqual(etag, self.etag)

    def test_get_response_etag_from_property(self):
        response = mock.Mock(requests.Response)
        response.headers = mock.Mock()
        response.headers.get.side_effect = [None, 'application/json']
        odata_etag = '9F5DA024'
        response.json.return_value = {'@odata.etag': odata_etag}
        etag = utils.get_response_etag(response)
        self.assertEqual(etag, odata_etag)

    def test_get_extended_error(self):
        response = mock.Mock(spec=requests.Response)
        body = {
            "error": {
                "@Message.ExtendedInfo": [
                    {
                        "MessageId": "Base.1.4.NoValidSession",
                        "Message": "No valid session found"
                    }
                ]
            }
        }
        response.json.return_value = body
        msg = utils.get_extended_error(response)
        self.assertEqual(msg, 'No valid session found')

        body = {
            "error": {
                "@Message.ExtendedInfo": [
                    {
                        "MessageId": "Base.1.4.NoValidSession"
                    }
                ]
            }
        }
        response.json.return_value = body
        msg = utils.get_extended_error(response)
        self.assertEqual(msg, 'Base.1.4.NoValidSession')

        body = {
            "error": {
                "code": "Base.1.8.GeneralError",
                "message": "A general error has occurred. See Resolution for "
                           "information on how to resolve the error.",
                "@Message.ExtendedInfo": []
            }
        }
        response.json.return_value = body
        msg = utils.get_extended_error(response)
        self.assertEqual(msg, 'A general error has occurred. See Resolution '
                              'for information on how to resolve the error.')

        body = {
            "error": {
                "code": "Base.1.8.GeneralError",
                "@Message.ExtendedInfo": []
            }
        }
        response.json.return_value = body
        msg = utils.get_extended_error(response)
        self.assertEqual(msg, 'Base.1.8.GeneralError')

        response.json.side_effect = ValueError
        msg = utils.get_extended_error(response)
        self.assertEqual(msg, '')

    def test_get_extended_info_message_keys(self):
        body = {
            "error": {
                "@Message.ExtendedInfo": [
                    {
                        "MessageId": "Base.1.0.Success"
                    },
                    {
                        "MessageId": "Base.1.0.PasswordChangeRequired"
                    }
                ]
            }
        }
        keys = utils.get_extended_info_message_keys(body)
        self.assertEqual(keys, {'Success', 'PasswordChangeRequired'})
        body = {
            "@Message.ExtendedInfo": [
                {
                    "MessageId": "Base.1.0.Success"
                },
                {
                    "MessageId": "Base.1.0.PasswordChangeRequired"
                }
            ]
        }
        keys = utils.get_extended_info_message_keys(body)
        self.assertEqual(keys, {'Success', 'PasswordChangeRequired'})
        body = {}
        keys = utils.get_extended_info_message_keys(body)
        self.assertEqual(keys, set())

    @mock.patch('builtins.print')
    @mock.patch('redfish_protocol_validator.utils.colorama.init')
    @mock.patch('redfish_protocol_validator.utils.colorama.deinit')
    def test_print_summary_all_pass(self, mock_colorama_deinit,
                                    mock_colorama_init, mock_print):
        utils.print_summary(self.sut)
        self.assertEqual(mock_print.call_count, 1)
        self.assertEqual(mock_colorama_init.call_count, 1)
        self.assertEqual(mock_colorama_deinit.call_count, 1)
        args = mock_print.call_args[0]
        self.assertIn('PASS: 2', args[0])
        self.assertIn('FAIL: 0', args[0])
        self.assertIn('WARN: 0', args[0])
        self.assertIn('NOT_TESTED: 0', args[0])
        self.assertIn(colorama.Fore.GREEN, args[0])
        self.assertNotIn(colorama.Fore.RED, args[0])
        self.assertNotIn(colorama.Fore.YELLOW, args[0])

    @mock.patch('builtins.print')
    @mock.patch('redfish_protocol_validator.utils.colorama.init')
    @mock.patch('redfish_protocol_validator.utils.colorama.deinit')
    def test_print_summary_not_all_pass(self, mock_colorama_deinit,
                                        mock_colorama_init, mock_print):
        self.sut.log(Result.FAIL, 'GET', 200, '/redfish/v1/accounts/1',
                     Assertion.PROTO_ETAG_ON_GET_ACCOUNT,
                     'did not return an ETag')
        self.sut.log(Result.WARN, 'PATCH', 200, '/redfish/v1/accounts/1',
                     Assertion.PROTO_ETAG_ON_GET_ACCOUNT,
                     'some warning message')
        self.sut.log(Result.NOT_TESTED, 'TRACE', 500, '/redfish/v1/',
                     Assertion.PROTO_HTTP_UNSUPPORTED_METHODS,
                     'some other message')
        utils.print_summary(self.sut)
        self.assertEqual(mock_print.call_count, 1)
        self.assertEqual(mock_colorama_init.call_count, 1)
        self.assertEqual(mock_colorama_deinit.call_count, 1)
        args = mock_print.call_args[0]
        self.assertIn('PASS: 2', args[0])
        self.assertIn('FAIL: 1', args[0])
        self.assertIn('WARN: 1', args[0])
        self.assertIn('NOT_TESTED: 1', args[0])
        # TODO(bdodd): Do these work on Windows systems?
        self.assertIn(colorama.Fore.GREEN, args[0])
        self.assertIn(colorama.Fore.RED, args[0])
        self.assertIn(colorama.Fore.YELLOW, args[0])

    def test_redfish_version_to_tuple(self):
        v = utils.redfish_version_to_tuple('1.0.6')
        self.assertEqual(v, (1, 0, 6))
        self.assertEqual(v.major, 1)
        self.assertEqual(v.minor, 0)
        self.assertEqual(v.errata, 6)
        v = utils.redfish_version_to_tuple('1')
        self.assertEqual(v, (1, 0, 0))
        v = utils.redfish_version_to_tuple('1.0')
        self.assertEqual(v, (1, 0, 0))
        v = utils.redfish_version_to_tuple('1.0.0')
        self.assertEqual(v, (1, 0, 0))
        v = utils.redfish_version_to_tuple('1.9')
        self.assertEqual(v, (1, 9, 0))
        v = utils.redfish_version_to_tuple('2.0.1')
        self.assertEqual(v, (2, 0, 1))
        with self.assertRaises(ValueError):
            utils.redfish_version_to_tuple('')
        with self.assertRaises(ValueError):
            utils.redfish_version_to_tuple('1.0.6b')
        with self.assertRaises(TypeError):
            utils.redfish_version_to_tuple('1.6.0.2')

    def test_normalize_media_type(self):
        n = utils.normalize_media_type('text/html;charset=utf-8')
        self.assertEqual(n, 'text/html;charset=utf-8')
        n = utils.normalize_media_type('text/html;charset=UTF-8')
        self.assertEqual(n, 'text/html;charset=utf-8')
        n = utils.normalize_media_type('Text/HTML;Charset="utf-8"')
        self.assertEqual(n, 'text/html;charset=utf-8')
        n = utils.normalize_media_type('text/html; charset="utf-8"')
        self.assertEqual(n, 'text/html;charset=utf-8')

    def test_sanitize(self):
        self.assertEqual(20, utils.sanitize(20, minimum=1, maximum=255))
        self.assertEqual(1, utils.sanitize(0, minimum=1, maximum=255))
        self.assertEqual(255, utils.sanitize(256, minimum=1, maximum=255))
        self.assertEqual(1, utils.sanitize(1, minimum=1))
        self.assertEqual(1, utils.sanitize(0, minimum=1))
        self.assertEqual(256, utils.sanitize(256, minimum=1))
        pass

    @mock.patch('redfish_protocol_validator.utils.socket')
    @mock.patch('redfish_protocol_validator.utils.http.client')
    def test_discover_ssdp_ipv4(self, mock_http_client, mock_socket):
        mock_sock = mock.Mock()
        mock_sock.recv.return_value = b'foo'
        mock_socket.socket.return_value = mock_sock
        mock_socket.timeout = MyTimeout
        mock_http_client.HTTPResponse.side_effect = MyTimeout
        services = utils.discover_ssdp()
        self.assertEqual({}, services)

    @mock.patch('redfish_protocol_validator.utils.socket')
    @mock.patch('redfish_protocol_validator.utils.http.client')
    def test_discover_ssdp_ipv6(self, mock_http_client, mock_socket):
        mock_sock = mock.Mock()
        mock_sock.recv.return_value = b'foo'
        mock_socket.socket.return_value = mock_sock
        mock_socket.timeout = MyTimeout
        mock_http_client.HTTPResponse.side_effect = MyTimeout
        services = utils.discover_ssdp(protocol='ipv6')
        self.assertEqual({}, services)

    @mock.patch('redfish_protocol_validator.utils.socket')
    @mock.patch('redfish_protocol_validator.utils.http.client')
    def test_discover_ssdp_iface(self, mock_http_client, mock_socket):
        mock_sock = mock.Mock()
        mock_sock.recv.return_value = b'foo'
        mock_socket.socket.return_value = mock_sock
        mock_socket.timeout = MyTimeout
        mock_http_client.HTTPResponse.side_effect = MyTimeout
        services = utils.discover_ssdp(iface='eth0')
        self.assertEqual({}, services)

    @mock.patch('redfish_protocol_validator.utils.socket')
    @mock.patch('redfish_protocol_validator.utils.http.client')
    def test_discover_ssdp_bad_proto(self, mock_http_client, mock_socket):
        mock_sock = mock.Mock()
        mock_sock.recv.return_value = b'foo'
        mock_socket.socket.return_value = mock_sock
        mock_socket.timeout = MyTimeout
        mock_http_client.HTTPResponse.side_effect = MyTimeout
        with self.assertRaises(ValueError):
            utils.discover_ssdp(protocol='ipsec')

    def test_process_ssdp_response(self):
        mock_response = mock.Mock()
        uuid = '92384634-2938-2342-8820-489239905423'
        usn = 'uuid:%s::urn:dmtf-org:service:redfish-rest:1:0' % uuid
        mock_response.getheader.return_value = usn
        headers = {
            'ST': SSDP_REDFISH,
            'USN': usn,
            'AL': 'http://0.0.0.0:8007/redfish/v1'
        }
        mock_response.headers = headers
        discovered_services = {}
        utils.process_ssdp_response(mock_response, discovered_services,
                                    utils.redfish_usn_pattern)
        expected = {
            uuid: headers
        }
        self.assertEqual(discovered_services, expected)
        self.assertEqual(discovered_services.get(uuid, {}).get('USN'), usn)
        self.assertEqual(discovered_services.get(uuid, {}).get('ST'),
                         SSDP_REDFISH)
        self.assertEqual(discovered_services.get(uuid, {}).get('AL'),
                         'http://0.0.0.0:8007/redfish/v1')

    def test_fake_socket(self):
        sock = utils.FakeSocket(b'foo')
        s = sock.makefile()
        self.assertEqual(s, sock)

    def test_hex_to_binary_str(self):
        self.assertEqual('01111100', utils.hex_to_binary_str('7c'))
        self.assertEqual('000000001010101111000001001000111110111111111111',
                         utils.hex_to_binary_str('00ABC123EFFF'))
        self.assertIsNone(utils.hex_to_binary_str('3VyZS4='))

    def test_monobit_frequency(self):
        p = utils.monobit_frequency('1011010101')
        self.assertTrue(0.52708 <= p <= 0.52709)
        p = utils.monobit_frequency(
            '11001001000011111101101010100010001000010110100011'
            '00001000110100110001001100011001100010100010111000')
        self.assertTrue(0.10959 <= p <= 0.10960)

    def test_runs(self):
        p = utils.runs('1111111111')
        self.assertEqual(p, 0.0)
        p = utils.runs('1001101011')
        self.assertTrue(0.14723 <= p <= 0.14724)
        p = utils.runs(
            '11001001000011111101101010100010001000010110100011'
            '00001000110100110001001100011001100010100010111000')
        self.assertTrue(0.50079 <= p <= 0.50080)

    def test_random_sequence(self):
        self.assertFalse(utils.random_sequence('00040000'))
        self.assertFalse(utils.random_sequence('fffffffe'))
        self.assertFalse(utils.random_sequence('0000ffff'))
        token = 'C90FDAA22168C234C4C6628B8'
        self.assertTrue(utils.random_sequence(token))
        self.assertIsNone(utils.random_sequence('c3VyZS4='))


if __name__ == '__main__':
    unittest.main()
