# Copyright 2020 MongoDB Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

"""Pseudo-builders for building and registering libfuzzer tests.
"""
from SCons.Script import Action


def exists(env):
    return True


def libfuzzer_test_list_builder_action(env, target, source):
    with open(str(target[0]), "w") as ofile:
        for s in _libfuzzer_tests:
            print("\t" + str(s))
            ofile.write("%s\n" % s)


def build_cpp_libfuzzer_test(env, target, source, **kwargs):
    myenv = env.Clone()
    if not myenv.IsSanitizerEnabled("fuzzer"):
        return []

    libdeps = kwargs.get("LIBDEPS", [])
    kwargs["LIBDEPS"] = libdeps
    kwargs["INSTALL_ALIAS"] = ["tests"]
    sanitizer_option = "-fsanitize=fuzzer"
    myenv.Prepend(LINKFLAGS=[sanitizer_option])

    libfuzzer_test_components = {"tests", "fuzzertests"}
    if "AIB_COMPONENT" in kwargs and not kwargs["AIB_COMPONENTS"].endswith(
        "-fuzzertest"
    ):
        kwargs["AIB_COMPONENT"] += "-fuzzertest"

    if "AIB_COMPONENTS_EXTRA" in kwargs:
        libfuzzer_test_components = set(kwargs["AIB_COMPONENTS_EXTRA"]).union(
            libfuzzer_test_components
        )

    kwargs["AIB_COMPONENTS_EXTRA"] = libfuzzer_test_components

    result = myenv.Program(target, source, **kwargs)
    myenv.RegisterTest("$LIBFUZZER_TEST_LIST", result[0])
    myenv.Alias("$LIBFUZZER_TEST_ALIAS", result)

    # TODO: remove when hygienic is default
    hygienic = myenv.GetOption("install-mode") == "hygienic"
    if not hygienic:
        myenv.Install("#/build/libfuzzer_tests/", result[0])

    return result


def generate(env):
    env.TestList("$LIBFUZZER_TEST_LIST", source=[])
    env.AddMethod(build_cpp_libfuzzer_test, "CppLibfuzzerTest")
    env.Alias("$LIBFUZZER_TEST_ALIAS", "$LIBFUZZER_TEST_LIST")
