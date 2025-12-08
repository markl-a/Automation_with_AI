"""Advanced automation tools for AI framework."""

import os
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional, Callable
import sqlite3
import json
from datetime import datetime, timedelta
from urllib.parse import urlparse
import re
import warnings


class EmailAutomationTool:
    """
    Tool for email automation (SMTP/IMAP).

    Security Note:
        For production use, configure credentials via environment variables:
        - EMAIL_USERNAME: Email address/username
        - EMAIL_PASSWORD: Email password or app-specific password
        - SMTP_SERVER: SMTP server address
        - IMAP_SERVER: IMAP server address

        Avoid passing plaintext passwords in code. Use app-specific passwords
        or OAuth2 authentication when possible.
    """

    # Environment variable names for secure credential storage
    ENV_EMAIL_USERNAME = "EMAIL_USERNAME"
    ENV_EMAIL_PASSWORD = "EMAIL_PASSWORD"
    ENV_SMTP_SERVER = "SMTP_SERVER"
    ENV_IMAP_SERVER = "IMAP_SERVER"

    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: int = 587,
        imap_server: Optional[str] = None,
        imap_port: int = 993,
        use_env_credentials: bool = True
    ):
        """
        Initialize email automation tool.

        Args:
            smtp_server: SMTP server address (or use SMTP_SERVER env var)
            smtp_port: SMTP port
            imap_server: IMAP server address (or use IMAP_SERVER env var)
            imap_port: IMAP port
            use_env_credentials: Whether to use environment variables for credentials
        """
        self.smtp_server = smtp_server or os.getenv(self.ENV_SMTP_SERVER)
        self.smtp_port = smtp_port
        self.imap_server = imap_server or os.getenv(self.ENV_IMAP_SERVER)
        self.imap_port = imap_port
        self.use_env_credentials = use_env_credentials

    def _get_credentials(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> tuple:
        """
        Get email credentials securely.

        Prioritizes environment variables over passed parameters.
        Issues warning if plaintext password is used.

        Args:
            username: Optional username override
            password: Optional password override

        Returns:
            Tuple of (username, password)

        Raises:
            ValueError: If no credentials are available
        """
        # Try environment variables first
        env_username = os.getenv(self.ENV_EMAIL_USERNAME)
        env_password = os.getenv(self.ENV_EMAIL_PASSWORD)

        final_username = username or env_username
        final_password = password or env_password

        if not final_username or not final_password:
            raise ValueError(
                "Email credentials not provided. Set EMAIL_USERNAME and "
                "EMAIL_PASSWORD environment variables or pass credentials directly."
            )

        # Warn if using passed password instead of environment variable
        if password and not env_password:
            warnings.warn(
                "Passing password as parameter is not recommended for security. "
                "Consider using EMAIL_PASSWORD environment variable instead.",
                SecurityWarning,
                stacklevel=3
            )

        return final_username, final_password

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        sender: Optional[str] = None,
        password: Optional[str] = None,
        html: bool = False
    ) -> Dict[str, Any]:
        """
        Send an email via SMTP.

        Credentials can be provided via:
        1. Environment variables (recommended): EMAIL_USERNAME, EMAIL_PASSWORD
        2. Method parameters (for backwards compatibility, not recommended)

        Args:
            recipient: Recipient email address
            subject: Email subject
            body: Email body
            sender: Sender email address (optional if using env vars)
            password: Email password (optional if using env vars, not recommended)
            html: Whether body is HTML

        Returns:
            Result dictionary
        """
        try:
            if not self.smtp_server:
                return {"success": False, "error": "SMTP server not configured"}

            # Get credentials securely
            final_sender, final_password = self._get_credentials(sender, password)

            # Validate recipient email format
            if not self._validate_email(recipient):
                return {"success": False, "error": f"Invalid recipient email: {recipient}"}

            msg = MIMEMultipart('alternative') if html else MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = final_sender
            msg['To'] = recipient

            if html:
                msg.attach(MIMEText(body, 'html'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(final_sender, final_password)
                server.send_message(msg)

            return {
                "success": True,
                "message": f"Email sent to {recipient}",
                "timestamp": datetime.now().isoformat()
            }
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except smtplib.SMTPAuthenticationError:
            return {"success": False, "error": "Authentication failed. Check credentials."}
        except smtplib.SMTPException as e:
            return {"success": False, "error": f"SMTP error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    def read_emails(
        self,
        folder: str = "INBOX",
        limit: int = 10,
        unread_only: bool = False,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Read emails from IMAP server.

        Credentials can be provided via:
        1. Environment variables (recommended): EMAIL_USERNAME, EMAIL_PASSWORD
        2. Method parameters (for backwards compatibility, not recommended)

        Args:
            folder: Mail folder to read from
            limit: Maximum number of emails to read
            unread_only: Only read unread emails
            username: Email username (optional if using env vars)
            password: Email password (optional if using env vars, not recommended)

        Returns:
            Dictionary with emails
        """
        try:
            if not self.imap_server:
                return {"success": False, "error": "IMAP server not configured"}

            # Get credentials securely
            final_username, final_password = self._get_credentials(username, password)

            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(final_username, final_password)
            mail.select(folder)

            search_criteria = '(UNSEEN)' if unread_only else 'ALL'
            _, messages = mail.search(None, search_criteria)

            email_ids = messages[0].split()
            email_ids = email_ids[-limit:]  # Get latest emails

            emails = []
            for email_id in email_ids:
                _, msg_data = mail.fetch(email_id, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)

                emails.append({
                    "id": email_id.decode(),
                    "from": email_message.get('From'),
                    "subject": email_message.get('Subject'),
                    "date": email_message.get('Date'),
                    "body": self._get_email_body(email_message)
                })

            mail.close()
            mail.logout()

            return {
                "success": True,
                "count": len(emails),
                "emails": emails
            }
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except imaplib.IMAP4.error as e:
            return {"success": False, "error": f"IMAP error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    @staticmethod
    def _validate_email(email_addr: str) -> bool:
        """Validate email address format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email_addr))

    @staticmethod
    def _get_email_body(email_message) -> str:
        """Extract body from email message."""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        else:
            return email_message.get_payload(decode=True).decode()
        return ""


class DatabaseAutomationTool:
    """Tool for database automation and SQL query generation."""

    # Valid SQL identifier pattern (prevents SQL injection)
    VALID_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    # Reserved SQL keywords that cannot be used as identifiers
    SQL_RESERVED_KEYWORDS = {
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'TABLE', 'INDEX', 'VIEW', 'DATABASE', 'SCHEMA', 'GRANT', 'REVOKE',
        'WHERE', 'FROM', 'JOIN', 'ON', 'AND', 'OR', 'NOT', 'NULL', 'TRUE',
        'FALSE', 'ORDER', 'BY', 'GROUP', 'HAVING', 'LIMIT', 'OFFSET', 'UNION',
        'ALL', 'DISTINCT', 'AS', 'IN', 'BETWEEN', 'LIKE', 'IS', 'EXISTS'
    }

    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize database automation tool.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn = None

    @classmethod
    def _validate_identifier(cls, name: str, identifier_type: str = "identifier") -> None:
        """
        Validate SQL identifier to prevent SQL injection.

        Args:
            name: The identifier name to validate
            identifier_type: Type of identifier (for error messages)

        Raises:
            ValueError: If identifier is invalid or potentially dangerous
        """
        if not name:
            raise ValueError(f"Empty {identifier_type} name")

        if not cls.VALID_IDENTIFIER_PATTERN.match(name):
            raise ValueError(
                f"Invalid {identifier_type} name '{name}': "
                "must start with letter/underscore and contain only alphanumeric/underscore"
            )

        if name.upper() in cls.SQL_RESERVED_KEYWORDS:
            raise ValueError(
                f"Invalid {identifier_type} name '{name}': SQL reserved keyword"
            )

        if len(name) > 128:
            raise ValueError(
                f"Invalid {identifier_type} name '{name}': exceeds maximum length of 128"
            )

    def connect(self) -> Dict[str, Any]:
        """Connect to database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return {"success": True, "message": "Connected to database"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_query(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """
        Execute SQL query.

        Args:
            query: SQL query to execute
            params: Query parameters

        Returns:
            Query results
        """
        try:
            if not self.conn:
                self.connect()

            cursor = self.conn.cursor()
            cursor.execute(query, params or ())

            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                results = [dict(row) for row in rows]
                return {
                    "success": True,
                    "rows": len(results),
                    "data": results
                }
            else:
                self.conn.commit()
                return {
                    "success": True,
                    "affected_rows": cursor.rowcount,
                    "message": "Query executed successfully"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_select_query(
        self,
        table: str,
        columns: List[str] = None,
        where: Dict[str, Any] = None,
        limit: int = None
    ) -> str:
        """
        Generate SELECT query with SQL injection prevention.

        Args:
            table: Table name (validated for safety)
            columns: Columns to select (validated for safety)
            where: WHERE conditions (keys validated, values use parameterized queries)
            limit: LIMIT clause

        Returns:
            Generated SQL query

        Raises:
            ValueError: If table or column names are invalid
        """
        # Validate table name
        self._validate_identifier(table, "table")

        # Validate and build column list
        if columns:
            for col in columns:
                self._validate_identifier(col, "column")
            cols = ", ".join(columns)
        else:
            cols = "*"

        query = f"SELECT {cols} FROM {table}"

        if where:
            # Validate WHERE column names
            for key in where.keys():
                self._validate_identifier(key, "column")
            conditions = " AND ".join([f"{k} = ?" for k in where.keys()])
            query += f" WHERE {conditions}"

        if limit:
            if not isinstance(limit, int) or limit < 0:
                raise ValueError("LIMIT must be a non-negative integer")
            query += f" LIMIT {limit}"

        return query

    def generate_insert_query(self, table: str, data: Dict[str, Any]) -> tuple:
        """
        Generate INSERT query with SQL injection prevention.

        Args:
            table: Table name (validated for safety)
            data: Data to insert (keys validated, values use parameterized queries)

        Returns:
            Tuple of (query, values)

        Raises:
            ValueError: If table or column names are invalid
        """
        # Validate table name
        self._validate_identifier(table, "table")

        # Validate column names
        for col in data.keys():
            self._validate_identifier(col, "column")

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return query, tuple(data.values())

    # Valid SQL data types for schema validation
    VALID_SQL_TYPES = {
        'INTEGER', 'INT', 'SMALLINT', 'BIGINT', 'TINYINT',
        'TEXT', 'VARCHAR', 'CHAR', 'NCHAR', 'NVARCHAR', 'CLOB',
        'REAL', 'FLOAT', 'DOUBLE', 'DECIMAL', 'NUMERIC',
        'BLOB', 'BINARY', 'VARBINARY',
        'BOOLEAN', 'BOOL',
        'DATE', 'TIME', 'DATETIME', 'TIMESTAMP',
        'PRIMARY', 'KEY', 'NOT', 'NULL', 'UNIQUE', 'DEFAULT', 'AUTOINCREMENT',
        'REFERENCES', 'FOREIGN', 'CHECK', 'CONSTRAINT'
    }

    def _validate_sql_type(self, dtype: str) -> None:
        """
        Validate SQL data type to prevent injection.

        Args:
            dtype: SQL data type string

        Raises:
            ValueError: If data type is invalid
        """
        # Parse type and validate each token
        tokens = re.findall(r'[a-zA-Z_]+|\d+', dtype.upper())
        for token in tokens:
            if not token.isdigit() and token not in self.VALID_SQL_TYPES:
                # Allow type with size like VARCHAR(255)
                if not re.match(r'^[A-Z]+$', token):
                    raise ValueError(f"Invalid SQL data type component: {token}")

    def create_table(self, table: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """
        Create a table with SQL injection prevention.

        Args:
            table: Table name (validated for safety)
            schema: Column schema {column_name: column_type} (validated for safety)

        Returns:
            Result dictionary

        Raises:
            ValueError: If table name, column names, or data types are invalid
        """
        # Validate table name
        self._validate_identifier(table, "table")

        # Validate column names and data types
        validated_columns = []
        for name, dtype in schema.items():
            self._validate_identifier(name, "column")
            self._validate_sql_type(dtype)
            validated_columns.append(f"{name} {dtype}")

        columns_def = ", ".join(validated_columns)
        query = f"CREATE TABLE IF NOT EXISTS {table} ({columns_def})"
        return self.execute_query(query)

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None


class WebScraperTool:
    """
    Tool for web scraping and data extraction with security protections.

    Security features:
    - URL validation and sanitization
    - SSRF (Server-Side Request Forgery) prevention
    - Blocked internal/private network access by default
    """

    # Allowed URL schemes
    ALLOWED_SCHEMES = {'http', 'https'}

    # Blocked hosts (private networks, localhost, etc.)
    BLOCKED_HOSTS = {
        'localhost', '127.0.0.1', '0.0.0.0', '::1',
        'metadata.google.internal',  # GCP metadata
        '169.254.169.254',  # AWS/Azure metadata
    }

    # Private IP ranges (SSRF prevention)
    PRIVATE_IP_PREFIXES = (
        '10.', '172.16.', '172.17.', '172.18.', '172.19.',
        '172.20.', '172.21.', '172.22.', '172.23.', '172.24.',
        '172.25.', '172.26.', '172.27.', '172.28.', '172.29.',
        '172.30.', '172.31.', '192.168.', '127.', '0.',
    )

    @classmethod
    def _validate_url(cls, url: str, allow_private: bool = False) -> str:
        """
        Validate and sanitize URL to prevent SSRF attacks.

        Args:
            url: URL to validate
            allow_private: Whether to allow private/internal network access

        Returns:
            Validated URL string

        Raises:
            ValueError: If URL is invalid or potentially dangerous
        """
        if not url or not url.strip():
            raise ValueError("Empty URL")

        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValueError(f"Invalid URL format: {e}")

        # Check scheme
        if parsed.scheme.lower() not in cls.ALLOWED_SCHEMES:
            raise ValueError(
                f"Invalid URL scheme '{parsed.scheme}'. "
                f"Allowed: {', '.join(cls.ALLOWED_SCHEMES)}"
            )

        # Check for empty host
        if not parsed.netloc:
            raise ValueError("URL must include a host")

        # Extract hostname (remove port if present)
        hostname = parsed.hostname or ''

        # Check blocked hosts
        if hostname.lower() in cls.BLOCKED_HOSTS:
            raise ValueError(f"Access to '{hostname}' is blocked for security")

        # Check private IP ranges (SSRF prevention)
        if not allow_private:
            if any(hostname.startswith(prefix) for prefix in cls.PRIVATE_IP_PREFIXES):
                raise ValueError(
                    f"Access to private IP '{hostname}' is blocked. "
                    "Set allow_private=True to override."
                )

        return url

    @classmethod
    def fetch_url(
        cls,
        url: str,
        timeout: int = 30,
        allow_private: bool = False,
        verify_ssl: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch content from URL safely.

        Includes URL validation and SSRF prevention.

        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            allow_private: Whether to allow private/internal network access
            verify_ssl: Whether to verify SSL certificates

        Returns:
            Response data
        """
        try:
            import requests

            # Validate URL
            validated_url = cls._validate_url(url, allow_private=allow_private)

            # Make request with security settings
            response = requests.get(
                validated_url,
                timeout=timeout,
                verify=verify_ssl,
                allow_redirects=True,
                headers={'User-Agent': 'AI-Automation-Framework/1.0'}
            )
            response.raise_for_status()

            return {
                "success": True,
                "status_code": response.status_code,
                "content": response.text,
                "headers": dict(response.headers),
                "url": response.url,  # Final URL after redirects
                "original_url": url
            }
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except requests.exceptions.SSLError:
            return {"success": False, "error": "SSL certificate verification failed"}
        except requests.exceptions.Timeout:
            return {"success": False, "error": f"Request timed out after {timeout}s"}
        except requests.exceptions.ConnectionError as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": f"HTTP error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    @staticmethod
    def extract_links(html_content: str, base_url: str = None) -> Dict[str, Any]:
        """
        Extract all links from HTML.

        Args:
            html_content: HTML content
            base_url: Base URL for relative links

        Returns:
            Extracted links
        """
        try:
            from bs4 import BeautifulSoup
            from urllib.parse import urljoin

            soup = BeautifulSoup(html_content, 'html.parser')
            links = []

            for link in soup.find_all('a', href=True):
                href = link['href']
                if base_url:
                    href = urljoin(base_url, href)
                links.append({
                    "url": href,
                    "text": link.get_text(strip=True)
                })

            return {
                "success": True,
                "count": len(links),
                "links": links
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def extract_text(html_content: str, tag: str = None) -> Dict[str, Any]:
        """
        Extract text from HTML.

        Args:
            html_content: HTML content
            tag: Specific tag to extract (optional)

        Returns:
            Extracted text
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, 'html.parser')

            if tag:
                elements = soup.find_all(tag)
                text = [elem.get_text(strip=True) for elem in elements]
            else:
                text = soup.get_text(strip=True)

            return {
                "success": True,
                "text": text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def extract_table_data(html_content: str) -> Dict[str, Any]:
        """
        Extract table data from HTML.

        Args:
            html_content: HTML content

        Returns:
            Extracted table data
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, 'html.parser')
            tables = []

            for table in soup.find_all('table'):
                rows = []
                for tr in table.find_all('tr'):
                    cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                    if cells:
                        rows.append(cells)
                tables.append(rows)

            return {
                "success": True,
                "table_count": len(tables),
                "tables": tables
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# Tool schemas for function calling
ADVANCED_TOOL_SCHEMAS = {
    "send_email": {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email via SMTP",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "Recipient email"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body"}
                },
                "required": ["recipient", "subject", "body"]
            }
        }
    },
    "execute_sql": {
        "type": "function",
        "function": {
            "name": "execute_sql",
            "description": "Execute SQL query on database",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query to execute"}
                },
                "required": ["query"]
            }
        }
    },
    "scrape_url": {
        "type": "function",
        "function": {
            "name": "scrape_url",
            "description": "Scrape content from URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to scrape"}
                },
                "required": ["url"]
            }
        }
    }
}
