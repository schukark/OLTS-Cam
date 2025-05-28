import re
from typing import Tuple, Dict

class CameraSettingsValidator:
    """
    Validates camera connection parameters and converts between field values and RTSP URL.

    Methods:
        - validate_ip: Checks the format of an IP address.
        - validate_port: Checks the validity of a port number.
        - validate_rtsp_url: Validates the RTSP URL format.
        - validate_login: Validates login credentials (allows empty values).
        - update_rtsp_from_fields: Generates RTSP URL from individual field values.
        - update_fields_from_rtsp: Parses RTSP URL into individual field values.
    """

    def validate_ip(self, ip: str) -> Tuple[bool, str]:
        """
        Validates the format of an IP address.

        Args:
            ip: The IP address string to validate.

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not ip or ip == "":
            return False, "IP address cannot be empty."

        ip = ip.strip()

        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
            return False, "Invalid IP address format. Example: 192.168.1.1"

        octets = ip.split('.')
        if len(octets) != 4:
            return False, "IP address must contain 4 octets."

        for octet in octets:
            if not octet.isdigit():
                return False, "Each octet must be a number."

            num = int(octet)
            if not 0 <= num <= 255:
                return False, "Each octet must be between 0 and 255."

            if len(octet) > 1 and octet[0] == '0':
                return False, "Octets must not have leading zeros."

        return True, ""

    def validate_port(self, port: str) -> Tuple[bool, str]:
        """
        Validates the port number (optional field).

        Args:
            port: The port number string to validate.

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not port:
            return True, ""

        if not port.isdigit():
            return False, "Port must be a number."

        port_num = int(port)
        if not 1 <= port_num <= 65535:
            return False, "Port must be between 1 and 65535."

        return True, ""

    def validate_rtsp_url(self, url: str) -> Tuple[bool, str]:
        """
        Validates the RTSP URL format.

        Args:
            url: The RTSP URL string to validate.

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not url:
            return False, "RTSP URL cannot be empty."

        rtsp_pattern = r'^rtsp://(?:[^:@/]+(?::[^@/]+)?@)?[^:/]+(?::\d+)?(?:/.*)?$'
        if not re.match(rtsp_pattern, url, re.IGNORECASE):
            return False, "Invalid RTSP URL format. Example: rtsp://admin:12345@8.8.8.8:554/stream"

        return True, ""

    def validate_login(self, login: str) -> Tuple[bool, str]:
        """
        Validates the login field (allows empty value).

        Args:
            login: The login string to validate.

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        return True, ""

    def update_rtsp_from_fields(self, fields: Dict[str, str]) -> Dict[str, str]:
        """
        Generates RTSP URL from individual field values while preserving the existing path.

        Args:
            fields: Dictionary containing camera settings fields:
                {'ip': str, 'port': str, 'login': str, 'password': str, 'rtsp_url': str}

        Returns:
            Dictionary with updated 'rtsp_url' field
        """
        ip = fields.get('ip', '').strip()
        port = fields.get('port', '').strip()
        login = fields.get('login', '').strip()
        password = fields.get('password', '').strip()
        current_url = fields.get('rtsp_url', '').strip()

        # Extract existing path from current URL if it exists
        path = "/stream"  # default path
        if current_url:
            path_match = re.search(r'^rtsp://[^/]+(/.+)$', current_url)
            if path_match:
                path = path_match.group(1)
                # Ensure path starts with /
                if not path.startswith('/'):
                    path = '/' + path

        rtsp_url = ""
        if ip:
            if login and password:
                rtsp_url = f"rtsp://{login}:{password}@{ip}"
            elif login:
                rtsp_url = f"rtsp://{login}@{ip}"
            else:
                rtsp_url = f"rtsp://{ip}"

            if port:
                rtsp_url += f":{port}"
            
            rtsp_url += path

        return {**fields, 'rtsp_url': rtsp_url}

    def update_fields_from_rtsp(self, fields: Dict[str, str]) -> Dict[str, str]:
        """
        Parses RTSP URL into individual field values.

        Args:
            fields: Dictionary containing at least 'rtsp_url' field

        Returns:
            Dictionary with updated fields: {'ip', 'port', 'login', 'password'}
        """
        rtsp_url = fields.get('rtsp_url', '').strip()
        result = {
            'ip': '',
            'port': '',
            'login': '',
            'password': '',
            'rtsp_url': rtsp_url
        }

        pattern = r'^rtsp://(?:([^:]+)(?::([^@]+))?@)?([^:/]+)(?::(\d+))?(?:/(.*))?$'
        match = re.match(pattern, rtsp_url)

        if match:
            login, password, ip, port, _ = match.groups()
            result.update({
                'ip': ip or '',
                'port': port or '',
                'login': login or '',
                'password': password or ''
            })

        return result