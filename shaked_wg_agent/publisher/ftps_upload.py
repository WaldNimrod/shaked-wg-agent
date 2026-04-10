"""FTPS upload to uPress — push HTML report to nimrod.bio.

CRITICAL: uPress requires TLS session reuse on data connections.
Standard ftplib.FTP_TLS returns 425 without the ReusedSessionFTP_TLS subclass.
Pattern copied from SmallFarmsAgents/organic_market_agent/publisher/ftps_upload.py
"""
from __future__ import annotations

import ftplib
import os
import time
from pathlib import Path

MAX_RETRIES = 3
BACKOFF = (5, 10, 20)
CONNECT_TIMEOUT = 15
UPLOAD_TIMEOUT = 60

UPLOAD_PATH = "wp-content/uploads/shaked-wg"
REMOTE_FILENAME = "index.html"


class MissingCredentialsError(EnvironmentError):
    """Raised when FTPS credentials are not configured."""


class ReusedSessionFTP_TLS(ftplib.FTP_TLS):
    """FTP_TLS that reuses the control TLS session for data connections.

    uPress returns 425 unless the data connection presents the same TLS
    session ticket as the control connection.
    """

    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(
                conn,
                server_hostname=self.host,
                session=self.sock.session,
            )
        return conn, size


def _get_env(key: str) -> str:
    val = os.environ.get(key, "")
    if not val:
        raise MissingCredentialsError(f"Missing required env var: {key}")
    return val


def _connect() -> ReusedSessionFTP_TLS:
    host = _get_env("UPRESS_SFTP_HOST")
    port = int(os.environ.get("UPRESS_SFTP_PORT", "21"))
    user = _get_env("UPRESS_SFTP_USER")
    passwd = _get_env("UPRESS_SFTP_PASS")

    ftp = ReusedSessionFTP_TLS()
    ftp.connect(host, port, timeout=CONNECT_TIMEOUT)
    ftp.login(user, passwd)
    ftp.prot_p()
    ftp.set_pasv(True)
    return ftp


def _ensure_remote_dir(ftp: ReusedSessionFTP_TLS, path: str) -> None:
    """Create remote directory tree idempotently."""
    parts = path.strip("/").split("/")
    current = ""
    for part in parts:
        current = f"{current}/{part}" if current else part
        try:
            ftp.mkd(current)
        except ftplib.error_perm:
            pass  # already exists


def _upload_file(ftp: ReusedSessionFTP_TLS, local_path: Path, remote_path: str) -> None:
    """Upload a single file with retry logic."""
    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            with open(local_path, "rb") as f:
                ftp.storbinary(f"STOR {remote_path}", f)
            return
        except (ftplib.Error, OSError) as exc:
            last_exc = exc
            if attempt < MAX_RETRIES - 1:
                time.sleep(BACKOFF[attempt])
    raise RuntimeError(f"Upload failed after {MAX_RETRIES} attempts: {last_exc}") from last_exc


def upload_report(html_path: Path) -> str:
    """Upload index.html to upress and return the public URL.

    Reads credentials from environment variables:
      UPRESS_SFTP_HOST, UPRESS_SFTP_PORT, UPRESS_SFTP_USER, UPRESS_SFTP_PASS
      UPRESS_PUBLIC_BASE  (default: https://www.nimrod.bio)

    Returns the public URL of the uploaded file.
    Raises MissingCredentialsError or RuntimeError on failure.
    """
    public_base = os.environ.get("UPRESS_PUBLIC_BASE", "https://www.nimrod.bio").rstrip("/")
    upload_path = os.environ.get("UPRESS_UPLOAD_PATH", UPLOAD_PATH)
    remote_file = f"{upload_path}/{REMOTE_FILENAME}"
    public_url = f"{public_base}/{upload_path}/{REMOTE_FILENAME}"

    ftp = _connect()
    try:
        _ensure_remote_dir(ftp, upload_path)
        _upload_file(ftp, html_path, remote_file)
    finally:
        try:
            ftp.quit()
        except Exception:
            pass

    return public_url
