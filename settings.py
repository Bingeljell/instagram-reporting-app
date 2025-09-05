# settings.py — tiny env loader based on git branch
# Keep your .env files untracked: .env.development, .env.production, plus optional .env.local

import os
import subprocess
from typing import Optional, Dict

from dotenv import load_dotenv

try:
    import streamlit as st  # Optional: makes this work on Streamlit Cloud without env files
except Exception:
    st = None


def _git_branch() -> Optional[str]:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL
        )
        return out.decode().strip().lower()
    except Exception:
        return None


def current_env() -> str:
    """Infer env from branch. main/master => production, dev/develop => development.
    APP_ENV (if set) wins. Anything else defaults to development.
    """
    # Allow manual override when needed
    env = os.getenv("APP_ENV")
    if env:
        return env.lower()

    branch = _git_branch()
    if branch in {"main", "master"}:
        return "production"
    if branch in {"dev", "develop"}:
        return "development"
    return "development"


def _with_trailing_slash(url: str) -> str:
    return url if not url or url.endswith("/") else url + "/"


def load_config() -> Dict[str, str]:
    """Return a dict of config values. Super small and predictable.

    Priority:
      1) If running on Streamlit Cloud and st.secrets exist, use those.
      2) Else, infer env from git branch and load `.env.<env>` + optional `.env.local`.
    """
    # 1) Streamlit Cloud (per-app secrets)
    if st is not None and getattr(st, "secrets", None):
        s = st.secrets
        return {
            "APP_ENV": str(s.get("APP_ENV", "production")).lower(),
            "FACEBOOK_APP_ID": s.get("FACEBOOK_APP_ID", ""),
            "FACEBOOK_APP_SECRET": s.get("FACEBOOK_APP_SECRET", ""),
            "FACEBOOK_REDIRECT_URI": _with_trailing_slash(s.get("FACEBOOK_REDIRECT_URI", "")),
        }

    # 2) Local dev: branch-driven env files
    env = current_env()
    load_dotenv(f".env.{env}", override=False)
    load_dotenv(".env.local", override=True)  # optional machine-only tweaks

    return {
        "APP_ENV": env,
        "FACEBOOK_APP_ID": os.getenv("FACEBOOK_APP_ID", ""),
        "FACEBOOK_APP_SECRET": os.getenv("FACEBOOK_APP_SECRET", ""),
        "FACEBOOK_REDIRECT_URI": _with_trailing_slash(os.getenv("FACEBOOK_REDIRECT_URI", "")),
    }


# ---- Usage example (in your app) -------------------------------------------
# from settings import load_config
# cfg = load_config()
# APP_ENV = cfg["APP_ENV"]
# FACEBOOK_APP_ID = cfg["FACEBOOK_APP_ID"]
# FACEBOOK_APP_SECRET = cfg["FACEBOOK_APP_SECRET"]
# FACEBOOK_REDIRECT_URI = cfg["FACEBOOK_REDIRECT_URI"]
# settings.py — tiny env loader based on git branch
# Keep your .env files untracked: .env.development, .env.production, plus optional .env.local
