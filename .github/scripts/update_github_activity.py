import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
OUTPUT_PATH = Path("assets/github-activity.svg")
QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
      }
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalRepositoriesWithContributedCommits
    }
  }
}
"""


def get_activity(username: str, token: str) -> dict[str, int]:
    end = datetime.now(timezone.utc).replace(microsecond=0)
    start = end - timedelta(days=365)
    payload = json.dumps(
        {
            "query": QUERY,
            "variables": {
                "login": username,
                "from": start.isoformat().replace("+00:00", "Z"),
                "to": end.isoformat().replace("+00:00", "Z"),
            },
        }
    ).encode("utf-8")
    request = Request(
        GRAPHQL_ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "adillpickles-profile-readme",
        },
    )

    with urlopen(request, timeout=30) as response:
        result = json.load(response)

    if result.get("errors"):
        raise RuntimeError(f"GitHub GraphQL request failed: {result['errors']}")

    collection = result["data"]["user"]["contributionsCollection"]
    return {
        "contributions": collection["contributionCalendar"]["totalContributions"],
        "pull_requests": collection["totalPullRequestContributions"],
        "reviews": collection["totalPullRequestReviewContributions"],
        "repositories": collection["totalRepositoriesWithContributedCommits"],
    }


def get_fixture_activity(path: Path) -> dict[str, int]:
    fixture = json.loads(path.read_text(encoding="utf-8"))
    return {
        "contributions": fixture["total"],
        "pull_requests": fixture["pullRequests"],
        "reviews": fixture["reviews"],
        "repositories": fixture["repositories"],
    }


def render_activity_svg(activity: dict[str, int]) -> str:
    metrics = (
        (activity["contributions"], "contributions"),
        (activity["pull_requests"], "pull requests"),
        (activity["reviews"], "reviews"),
        (activity["repositories"], "repositories"),
    )
    cards = []
    for index, (value, label) in enumerate(metrics):
        x = 12 + index * 186
        cards.append(
            f"""  <g transform="translate({x} 8)">
    <rect class="card" width="172" height="56" rx="8" />
    <text class="value" x="86" y="27" text-anchor="middle">{value:,}</text>
    <text class="label" x="86" y="46" text-anchor="middle">{label}</text>
  </g>"""
        )

    description = ", ".join(
        f"{value:,} {label}" for value, label in metrics
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="760" height="72" viewBox="0 0 760 72" role="img" aria-labelledby="title description">
  <title id="title">GitHub activity, last 12 months</title>
  <desc id="description">{description}</desc>
  <style>
    .card {{ fill: #f6f8fa; stroke: #d0d7de; }}
    .value {{
      fill: #1f2328;
      font: 700 18px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    }}
    .label {{
      fill: #57606a;
      font: 500 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    }}

    @media (prefers-color-scheme: dark) {{
      .card {{ fill: #161b22; stroke: #30363d; }}
      .value {{ fill: #f0f6fc; }}
      .label {{ fill: #8c959f; }}
    }}
  </style>
{chr(10).join(cards)}
</svg>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path)
    arguments = parser.parse_args()

    if arguments.fixture:
        activity = get_fixture_activity(arguments.fixture)
    else:
        username = os.environ["GITHUB_USERNAME"]
        token = os.environ["GITHUB_TOKEN"]
        activity = get_activity(username, token)

    source = render_activity_svg(activity)
    if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != source:
        OUTPUT_PATH.write_text(source, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
