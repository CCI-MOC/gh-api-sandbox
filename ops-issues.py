import click
import csv
import dotenv
import ghapi.all
import ghapi.core
import sys

dotenv.load_dotenv()


def flatten(op, *args, **kwargs):
    for page in ghapi.all.paged(op, *args, **kwargs):
        for item in page:
            yield item


class GitHub:
    def __init__(self, token, org):
        self.api = ghapi.all.GhApi(token, org=org)

    def boards(self):
        return flatten(self.api.projects.list_for_org)

    def columns(self, board):
        return flatten(self.api.projects.list_columns, board["id"])

    def cards(self, column):
        return flatten(self.api.projects.list_cards, column["id"])


@click.command()
@click.option("--token", "-T", envvar="GITHUB_TOKEN")
@click.option("--org", "-O", envvar="GITHUB_ORGANIZATION")
@click.option("--output", "-o", type=click.File(mode="w"), default=sys.stdout)
@click.argument("board")
def list_issues(token, output, org, board):
    try:
        with output:
            writer = csv.writer(output)
            writer.writerow(
                [
                    "project",
                    "bucket",
                    "repo",
                    "number",
                    "url",
                    "title",
                    "state",
                    "assignees",
                    "labels",
                ]
            )
            gh = GitHub(token, org)
            board = next(b for b in gh.boards() if b["name"] == board)
            for column in gh.columns(board):
                for card in gh.cards(column):
                    if content_url := card.get("content_url"):
                        issue = gh.api(content_url)
                        repo = gh.api(issue["repository_url"])
                        writer.writerow(
                            [
                                board["name"],
                                column["name"],
                                repo["name"],
                                issue["number"],
                                issue["html_url"],
                                issue["title"],
                                issue["state"],
                                "|".join(
                                    assignee["login"] for assignee in issue["assignees"]
                                ),
                                "|".join(label["name"] for label in issue["labels"]),
                            ]
                        )
    except StopIteration:
        raise click.ClickException(f"No board named {board}")
    except ghapi.core.HTTPError as err:
        raise click.ClickException(f"API error: {err}")


if __name__ == "__main__":
    list_issues()
