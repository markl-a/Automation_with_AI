"""Advanced automation tools for AI framework."""

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
import sqlite3
import json
from datetime import datetime, timedelta
import re


class EmailAutomationTool:
    """Tool for email automation (SMTP/IMAP)."""

    def __init__(self, smtp_server: str = None, smtp_port: int = 587,
                 imap_server: str = None, imap_port: int = 993):
        """
        Initialize email automation tool.

        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port
            imap_server: IMAP server address
            imap_port: IMAP port
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.imap_server = imap_server
        self.imap_port = imap_port

    def send_email(
        self,
        sender: str,
        password: str,
        recipient: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> Dict[str, Any]:
        """
        Send an email via SMTP.

        Args:
            sender: Sender email address
            password: Email password or app password
            recipient: Recipient email address
            subject: Email subject
            body: Email body
            html: Whether body is HTML

        Returns:
            Result dictionary
        """
        try:
            msg = MIMEMultipart('alternative') if html else MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = recipient

            if html:
                msg.attach(MIMEText(body, 'html'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)

            return {
                "success": True,
                "message": f"Email sent to {recipient}",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_emails(
        self,
        username: str,
        password: str,
        folder: str = "INBOX",
        limit: int = 10,
        unread_only: bool = False
    ) -> Dict[str, Any]:
        """
        Read emails from IMAP server.

        Args:
            username: Email username
            password: Email password
            folder: Mail folder to read from
            limit: Maximum number of emails to read
            unread_only: Only read unread emails

        Returns:
            Dictionary with emails
        """
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(username, password)
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
        except Exception as e:
            return {"success": False, "error": str(e)}

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

    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize database automation tool.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn = None

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
        Generate SELECT query.

        Args:
            table: Table name
            columns: Columns to select
            where: WHERE conditions
            limit: LIMIT clause

        Returns:
            Generated SQL query
        """
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table}"

        if where:
            conditions = " AND ".join([f"{k} = ?" for k in where.keys()])
            query += f" WHERE {conditions}"

        if limit:
            query += f" LIMIT {limit}"

        return query

    def generate_insert_query(self, table: str, data: Dict[str, Any]) -> tuple:
        """
        Generate INSERT query.

        Args:
            table: Table name
            data: Data to insert

        Returns:
            Tuple of (query, values)
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return query, tuple(data.values())

    def create_table(self, table: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """
        Create a table.

        Args:
            table: Table name
            schema: Column schema {column_name: column_type}

        Returns:
            Result dictionary
        """
        columns_def = ", ".join([f"{name} {dtype}" for name, dtype in schema.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table} ({columns_def})"
        return self.execute_query(query)

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


class WebScraperTool:
    """Tool for web scraping and data extraction."""

    @staticmethod
    def fetch_url(url: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Fetch content from URL.

        Args:
            url: URL to fetch
            timeout: Request timeout

        Returns:
            Response data
        """
        try:
            import requests
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            return {
                "success": True,
                "status_code": response.status_code,
                "content": response.text,
                "headers": dict(response.headers),
                "url": url
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

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
