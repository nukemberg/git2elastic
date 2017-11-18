# MIT license, see LICENSE.txt

import click
import git
import elasticsearch, elasticsearch.helpers
import pkg_resources
import json
import os.path
import itertools
import hashlib
from collections import defaultdict


def default_es_mappings():
    resource_package = __name__
    resource_path = 'mapping.json'
    return pkg_resources.resource_string(resource_package, resource_path)


def infer_repo_name(path):
    return os.path.split(os.path.abspath(path))[1]

@click.command()
@click.option('--repo-name', help='Git repo name', default=None)
@click.option('--es-index', help='ElasticSearch index name', required=True)
@click.option('--branch', '-b', help='Branch to index', default='master')
@click.option('--since', '-s', help='When to start reading the git log', default='1970-01-01')
@click.option('--es-mappings', help='ElasticSearch index mapping', type=click.File(), default=None)
@click.argument('path', default='.', type=click.Path(exists=True, dir_okay=True, file_okay=True))
def git2elastic(repo_name, es_index, branch, since, es_mappings, path):
    es_mappings = json.load(es_mappings) if es_mappings else json.loads(default_es_mappings())
    repo_name = repo_name if repo_name else infer_repo_name(path)
    es = elasticsearch.Elasticsearch()
    es.indices.create(es_index, es_mappings, ignore=[400])
    index(es, repo_name, es_index, git_log(path, branch, since))


def index(es, repo_name, index_name, commits):
    elasticsearch.helpers.bulk(
        es,
        gen_docs(repo_name, commits),
        index=index_name,
        doc_type='git'
    )


def gen_docs(repo_name, commits):
    for commit in commits:
        yield {
                '_id': commit.hexsha,
                'repo': repo_name,
                'sha': commit.hexsha,
                'author': {
                    'name': commit.author.name,
                    'email': commit.author.email
                },
                'message': commit.message,
                'summary': commit.summary,
                'commit_type': commit.type,
                'date': commit.authored_datetime.isoformat(),
                'stats': commit.stats.total,
                'files': list(map(str, commit.stats.files.keys())),
                'merge': len(commit.parents) > 1
        }
        for file, stats in commit.stats.files.items():
            s = stats.copy()
            s.update({
                '_id': commit.hexsha + '-' + hashlib.sha1(file.encode()).hexdigest(),
                'commit': commit.hexsha,
                'path': file,
                'stats': stats,
                'repo': repo_name,
                'date': commit.authored_datetime.isoformat(),
                'author': {
                    'name': commit.author.name,
                    'email': commit.author.email
                }
            })
            yield s

def git_log(repo_path, branch, since):
    repo = git.Repo(repo_path)
    return repo.iter_commits(branch, since=since)


if __name__ == '__main__':
    git2elastic()
