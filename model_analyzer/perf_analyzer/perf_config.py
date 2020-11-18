# Copyright 2020, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from model_analyzer.model_analyzer_exceptions import TritonModelAnalyzerException


class PerfAnalyzerConfig:
    """
    A config class to set arguments to the perf_analyzer.
    An argument set to None will use the perf_analyzer's default.
    """

    def __init__(self):
        self._args = {
            'async': None,
            'sync': None,
            'measurement-interval': None,
            'concurrency-range': None,
            'request-rate-range': None,
            'request-distribution': None,
            'request-intervals': None,
            'binary-search': None,
            'num-of-sequence': None,
            'latency-threshold': None,
            'max-threads': None,
            'stability-percentage': None,
            'max-trials': None,
            'percentile': None,
            'input-data': None,
            'shared-memory': None,
            'output-shared-memory-size': None,
            'shape': None,
            'sequence-length': None,
            'string-length': None,
            'string-data': None,
        }

        self._options = {
            '-m': None,
            '-x': None,
            '-b': None,
            '-u': None,
            '-i': None,
            '-f': None,
            '-H': None
        }

        self._verbose = {'-v': None, '-v -v': None}

        self._input_to_options = {
            'model-name': '-m',
            'model-version': '-x',
            'batch-size': '-b',
            'url': '-u',
            'protocol': '-i',
            'latency-report-file': '-f',
            'streaming': '-H'
        }

        self._input_to_verbose = {'verbose': '-v', 'extra-verbose': '-v -v'}

    def to_cli_string(self):
        """
        Utility function to convert a config into a
        string of arguments to the perf_analyzer with CLI.

        Returns
        -------
        str
            cli command string consisting of all arguments
            to the perf_analyzer set in the config, without
            the executable name.
        """

        # single dashed options, then verbose flags, then main args
        args = [f'{k} {v}' for k, v in self._options.items() if v]
        args += [k for k, v in self._verbose.items() if v]
        args += [f'--{k}={v}' for k, v in self._args.items() if v]

        return ' '.join(args)

    def __getitem__(self, key):
        """
        Gets an arguments value in config

        Parameters
        ----------
        key : str
            The name of the argument to the tritonserver

        Returns
        -------
            The value that the argument is set to in this config

        Raises
        ------
        TritonModelAnalyzerException
            If argument not found in the config
        """

        if key in self._args:
            return self._args[key]
        elif key in self._input_to_options:
            return self._options[self._input_to_options[key]]
        elif key in self._input_to_verbose:
            return self._verbose[self._input_to_verbose[key]]
        else:
            raise TritonModelAnalyzerException(
                f"'{key}' Key not found in config")

    def __setitem__(self, key, value):
        """
        Sets an arguments value in config
        after checking if defined/supported.

        Parameters
        ----------
        key : str
            The name of the argument to the tritonserver
        value : (any)
            The value to which the argument is being set

        Raises
        ------
        TritonModelAnalyzerException
            If key is unsupported or undefined in the
            config class
        """

        if key in self._args:
            self._args[key] = value
        elif key in self._input_to_options:
            self._options[self._input_to_options[key]] = value
        elif key in self._input_to_verbose:
            self._verbose[self._input_to_verbose[key]] = value
        else:
            raise TritonModelAnalyzerException(
                f"The argument '{key}' to the perf_analyzer "
                "is not supported by the model analyzer.")
