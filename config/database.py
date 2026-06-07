import dj_database_url

from config.env import get_env, get_env_bool


def _build_local_database_url() -> str:
    return (
        f"postgres://{get_env('DATABASE_USER', 'ps_be')}:"
        f"{get_env('DATABASE_PASSWORD', 'ps_be')}@"
        f"{get_env('DATABASE_HOST', 'localhost')}:"
        f"{get_env('DATABASE_PORT', '5432')}/"
        f"{get_env('DATABASE_NAME', 'ps_be')}"
    )


def _build_prod_database_url() -> str:
    return (
        f"postgres://{get_env('DATABASE_USER_PROD')}:"
        f"{get_env('DATABASE_PASSWORD_PROD')}@"
        f"{get_env('DATABASE_HOST_PROD')}:"
        f"{get_env('DATABASE_PORT_PROD', '5432')}/"
        f"{get_env('DATABASE_NAME_PROD')}"
    )


def resolve_database_url() -> str:
    """Resolve database URL with the following priority:
    1. DATABASE_URL (auto-injected by Render when Postgres is linked)
    2. Prod URL when USE_PROD_DATABASE=true
    3. Local dev URL (Docker PostgreSQL)
    """
    render_url = get_env("DATABASE_URL")
    if render_url:
        return render_url

    if get_env_bool("USE_PROD_DATABASE"):
        return get_env("DATABASE_URL_EXTERNAL_PROD") or _build_prod_database_url()

    return _build_local_database_url()


def get_databases(*, debug: bool) -> dict:
    use_prod = get_env_bool("USE_PROD_DATABASE") or bool(get_env("DATABASE_URL"))
    ssl_require = use_prod or not debug

    return {
        "default": dj_database_url.config(
            default=resolve_database_url(),
            conn_max_age=600,
            ssl_require=ssl_require,
        )
    }
