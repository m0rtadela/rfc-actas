from . import cli as cli_blueprint
import unittest


@cli_blueprint.cli.command()
def tests():
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)