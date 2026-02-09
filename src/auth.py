from src.infra.githubAuth.githubAuth import GithubAuth
from src.infra.githubAuth.appAuth import GithubAppAuth, GithubAppConfig
from src.infra.githubAuth.patAuth import GithubPatAuth
from dotenv import dotenv_values


def create_github_auth() -> GithubAuth:
    """
    Creates a GithubAuth instance based on environment variables.
    """

    environment = dotenv_values(".env")
    secret_key = environment.get("SECRET_KEY")
    client_id = environment.get("CLIENT_ID")
    pat_token = environment.get("PAT_TOKEN")

    if secret_key is not None and client_id is not None:
        return GithubAppAuth(
            GithubAppConfig(client_id=client_id, private_key_pem=secret_key)
        )

    elif pat_token is not None:
        return GithubPatAuth(pat_token)

    raise ValueError("No valid authentication method found in environment variables.")
