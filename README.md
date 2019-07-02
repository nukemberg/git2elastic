# git2elastic

Ever wanted to analyse the git commits in your repo? dump git log into elasticsearch and analyze it with Kibana with this small tool!

## Install

```
pip install -U git+https://github.com/avishai-ish-shalom/git2elastic.git
```

## Usage

```
git2elastic --es-index git path/to/repo
```

If no path is given, `git2elastic` defaults to `.`

Use `git2elastic --help` to see the full list of options.

# License

MIT license