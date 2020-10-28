import nox


@nox.session
def typecheck(session):
    session.install("mypy", "sqlalchemy-stubs")
    session.run("mypy", "babu")
