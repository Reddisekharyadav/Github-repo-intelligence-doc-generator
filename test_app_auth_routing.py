import unittest
from unittest.mock import patch

import app


class SelectGithubTokenForRepoTests(unittest.TestCase):
    def test_private_repo_404_prompts_github_sign_in(self):
        with patch("app.parse_github_url", return_value=("owner", "repo")), \
             patch("app._get_user_github_token", return_value=None), \
             patch("app._get_github_token", return_value=None), \
             patch("app._fetch_repo_metadata", return_value=(404, None)), \
             patch("app._build_github_oauth_authorize_url", return_value="https://github.com/login/oauth/authorize?x=1"):
            with self.assertRaises(app.GitHubSignInRequired) as cm:
                app._select_github_token_for_repo("https://github.com/owner/repo")

        self.assertIn("private", str(cm.exception).lower())
        self.assertEqual(
            cm.exception.authorize_url,
            "https://github.com/login/oauth/authorize?x=1",
        )

    def test_private_repo_404_with_user_token_continues_and_uses_user_access(self):
        with patch("app.parse_github_url", return_value=("owner", "repo")), \
             patch("app._get_user_github_token", return_value="user-token"), \
             patch("app._get_github_token", return_value=None), \
             patch("app._fetch_repo_metadata", side_effect=[(404, None), (200, {"private": True})]), \
             patch("app._build_github_oauth_authorize_url", return_value="https://unused"):
            token, mode = app._select_github_token_for_repo("https://github.com/owner/repo")

        self.assertEqual(token, "user-token")
        self.assertEqual(mode, "user-token-private")


if __name__ == "__main__":
    unittest.main()
