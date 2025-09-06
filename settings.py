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


def load_config() -> dict:
    """
    Prefer st.secrets on Streamlit Cloud, BUT fall back silently to env files
    if secrets.toml is missing locally. You can force env files with PREFER_ENV_FILES=1.
    """
    prefer_st_secrets = os.getenv("PREFER_ENV_FILES") not in ("1", "true", "True")

    # --- Try Streamlit secrets (guarded) ---
    if prefer_st_secrets and st is not None:
        try:
            s = st.secrets  # this may raise if no secrets.toml
            return {
                "APP_ENV": str(s.get("APP_ENV", "production")).lower(),
                "FACEBOOK_APP_ID": s.get("FACEBOOK_APP_ID", ""),
                "FACEBOOK_APP_SECRET": s.get("FACEBOOK_APP_SECRET", ""),
                "FACEBOOK_REDIRECT_URI": _with_trailing_slash(s.get("FACEBOOK_REDIRECT_URI", "")),
            }
        except Exception:
            pass  # no secrets.toml locally -> fall back to env files

    # --- Env files/local ---
    from pathlib import Path
    here = Path(__file__).resolve().parent
    app_env = os.getenv("APP_ENV", "development").lower()

    # Accept .env.development, .env.dev, or .env
    for name in (f".env.{app_env}", f".env.{app_env[:3]}", ".env"):
        p = here / name
        if p.exists():
            load_dotenv(p, override=False)
            break
    load_dotenv(here / ".env.local", override=True)

    return {
        "APP_ENV": app_env,
        "FACEBOOK_APP_ID": os.getenv("FACEBOOK_APP_ID", os.getenv("META_APP_ID", "")),
        "FACEBOOK_APP_SECRET": os.getenv("FACEBOOK_APP_SECRET", os.getenv("META_APP_SECRET", "")),
        "FACEBOOK_REDIRECT_URI": _with_trailing_slash(os.getenv("FACEBOOK_REDIRECT_URI", "http://localhost:8501/")),
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
