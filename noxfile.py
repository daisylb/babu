import nox


@nox.session
def typecheck(session):
    session.install("mypy", "sqlalchemy-stubs")
    session.run("mypy", "babu")


@nox.session
def format(session):
    session.install("black")
    session.run("black", ".")
