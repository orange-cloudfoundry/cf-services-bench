# -*- encoding: utf-8; -*-
import sh


class Bench():
    def __init__(self, scenario):
        """initialises properties needed for your bench
        self.cmd should contain a sh.Command object refering a command, for
        more information please go through documentation
        self.options contains a list of argument that will be passed to the
        command
        """

        self.cmd = sh.Command('')
        self.options = []
        self.raw_result = None
        self.results = {}

    def _format_results(self):
        """This method format raw_results in a type that must be JSON 
        serializable.
        You MUST store the result in self.results

        Raises:
            NotImplementedError -- [description]
        """

        raise NotImplementedError("you must override this method")

    def run_bench(self):
        """runs benchmark using cmd options
        if your bench returns an error code, stderr will be stored in 
        results.
        """

        try:
            run = self.cmd(self.options)
            self.raw_result = run.stdout
            self._format_results()
        except sh.ErrorReturnCode as output:
            self.raw_result = str(output.stderr)
            self.results['error'] = self.raw_result
