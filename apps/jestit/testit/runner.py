import os
import sys
import time
import traceback
import argparse
from importlib import import_module

# Import logging and helper modules
from jestit.helpers import paths
paths.configure_paths(__file__, 2)
TEST_ROOT = paths.APPS_ROOT / "tests"
# from test import helpers  # noqa: E402
from jestit.helpers import logit
from testit import helpers


def setup_parser():
    """Setup command-line arguments for the test runner."""
    parser = argparse.ArgumentParser(description="Django Test Runner")

    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose logging")
    parser.add_argument("-f", "--force", action="store_true",
                        help="Force the test to run now")
    parser.add_argument("-u", "--user", type=str, default="nobody",
                        help="Specify the user the test should run as")
    parser.add_argument("-m", "--module", type=str, default=None,
                        help="Run only this app/module")
    parser.add_argument("--method", type=str, default=None,
                        help="Run only a specific test method")
    parser.add_argument("-t", "--test", type=str, default=None,
                        help="Specify a specific test method to run")
    parser.add_argument("-q", "--quick", action="store_true",
                        help="Run only tests flagged as critical/quick")
    parser.add_argument("-x", "--extra", type=str, default=None,
                        help="Specify extra data to pass to test")
    parser.add_argument("-l", "--list", action="store_true",
                        help="List available tests instead of running them")
    parser.add_argument("-s", "--stop", action="store_true",
                        help="Stop on errors")
    parser.add_argument("-e", "--errors", action="store_true",
                        help="Show errors")
    parser.add_argument("--host", type=str, default="http://localhost:8001/",
                        help="Specify host for API tests")
    parser.add_argument("--setup", action="store_true",
                        help="Run setup before executing tests")

    return parser.parse_args()


def run_test(opts, module, func_name, module_name, test_name):
    """Run a specific test function inside a module."""
    test_key = f"{module_name}.{test_name}.{func_name}"
    logit.color_print(f"\nRUNNING TEST: {test_key}", logit.ConsoleLogger.BLUE)

    helpers.TEST_RUN.tests.active_test = test_key.replace(".", ":")
    started = time.time()

    try:
        getattr(module, func_name)(opts)
    except Exception as err:
        if opts.verbose:
            print(f"⚠️ Test Error: {err}")
        if opts.stop:
            sys.exit(1)

    duration = time.time() - started
    print(f"{helpers.INDENT}---------\n{helpers.INDENT}run time: {duration:.2f}s")


def import_module_for_testing(module_name, test_name):
    """Dynamically import a test module."""
    try:
        name = f"{module_name}.{test_name}"
        module = import_module(name)
        return module
    except ImportError:
        print(f"⚠️ Failed to import test module: {name}")
        traceback.print_exc()
        return None


def run_module_tests(opts, module_name, test_name):
    """Run all test functions in a specific test module."""
    module = import_module_for_testing(module_name, test_name)
    if not module:
        return

    prefix = "test_" if not opts.quick else "quick_"
    for func_name in dir(module):
        if func_name.startswith(prefix) and callable(getattr(module, func_name, None)):
            run_test(opts, module, func_name, module_name, test_name)


def run_tests_for_module(opts, module_name):
    """Discover and run tests for a given module."""
    module_path = os.path.join(TEST_ROOT, module_name)
    test_files = [f for f in os.listdir(module_path)
                  if f.endswith(".py") and f not in ["__init__.py", "setup.py"]]

    for test_file in sorted(test_files):
        test_name = test_file.rsplit('.', 1)[0]  # Remove .py extension
        run_module_tests(opts, module_name, test_name)


def setup_modules():
    """Run setup scripts for all test modules."""
    logit.color_print("\n[TEST PREFLIGHT SETUP]\n", logit.ConsoleLogger.BLUE)

    test_modules = [d for d in os.listdir(TEST_ROOT) if os.path.isdir(os.path.join(TEST_ROOT, d))]

    for module_name in sorted(test_modules):
        setup_file = os.path.join(TEST_ROOT, module_name, "setup.py")
        if os.path.isfile(setup_file):
            module = import_module_for_testing(module_name, "setup")
            if module and hasattr(module, "run_setup"):
                logit.color_print(f"Setting up {module_name}...", logit.ConsoleLogger.YELLOW)
                module.run_setup(opts)
                logit.color_print("✔ DONE\n", logit.ConsoleLogger.GREEN)


def main(opts):
    """Main function to run tests."""
    if opts.setup:
        setup_modules()

    if opts.list:
        print("\n------------------------")
        print("Listing available test modules & tests")
        print("[module]")
        print("  [test1]")
        print("  [test2]")
        print("------------------------")
        return

    if opts.module and opts.test:
        run_module_tests(opts.module, opts.test)
    elif opts.module:
        run_tests_for_module(opts, opts.module)
    else:
        test_root = os.path.join(paths.APPS_ROOT, "tests")
        test_modules = sorted([d for d in os.listdir(test_root) if os.path.isdir(os.path.join(test_root, d))])
        for module_name in test_modules:
            run_tests_for_module(opts, module_name)

    # Summary Output
    print("\n" + "=" * 80)

    logit.color_print(f"TOTAL RUN: {helpers.TEST_RUN.total}\t", logit.ConsoleLogger.YELLOW)
    logit.color_print(f"TOTAL PASSED: {helpers.TEST_RUN.passed}\n", logit.ConsoleLogger.GREEN)
    if helpers.TEST_RUN.failed > 0:
        logit.color_print(f"TOTAL FAILED: {helpers.TEST_RUN.failed}\n", logit.ConsoleLogger.RED)

    print("=" * 80)

    # Save Test Results
    helpers.TEST_RUN.save(os.path.join(paths.VAR_ROOT, "test_results.json"))

    # Exit with failure status if any test failed
    if helpers.TEST_RUN.failed > 0:
        sys.exit("❌ Tests failed!")


if __name__ == "__main__":
    opts = setup_parser()
    main()
