"""
timer for performance testing
"""

from datetime import datetime


class Timer:
    """
    What to time mutiple steps in a process.

    To use:

    Create a timer to start it:

    t = Time()  # It will set the start time when it is created.

    After a step you want to time, call it with a message:

    t("First step:")  # it will print the time since the last step, and record it.

    If you don't want it to print, set verbose to False:

    t("I don't want it to print", False)

    When you are done and want to see the total elapsed time:

    t.end()  # all this does is print the total ...

    # if you want a report of the whole thing:

    t.report()

    # if you want to do somethign the the report, e.g. write to to file

    report_as_str = report(verbose=False)
    logfile.write(report_as_str)

    """
    def __init__(self, verbose=True):
        # self.time_0 = datetime.now()
        self.steps = [("start", datetime.now())]

    def __call__(self, name, verbose=True):
        now = datetime.now()
        if verbose:
            print(f"{name} took: {now - self.steps[-1][1]}")
        self.steps.append((name, now))

    def report(self, verbose=True):
        report = []
        for i, step in enumerate(self.steps[1:]):
            elapsed = step[1] - self.steps[i][1]
            report.append(f"{step[0]} took {elapsed}")
        report.append(f"Total elapsed time: {self.steps[-1][1] - self.steps[0][1]!s}")
        report = "\n".join(report)
        if verbose:
            print(report)
        return report

    def end(self):
        """
        All this does is print the elapsed time.
        """
        print(f"Total elapsed time: {self.steps[-1][1] - self.steps[0][1]!s}")

    def __str__(self):
        return self.report(verbose=False)


if __name__ == "__main__":
    # run a test / example
    import time
    t = Timer()
    time.sleep(0.5)
    t("first one")
    time.sleep(0.2)
    t("second one")
    time.sleep(0.3)
    t("third one", False)
    time.sleep(0.2)
    t("not printed one", False)

    t.end()


    print("And the report ...")
    time.sleep(1)

    report = t.report()

    open("test_log_file", 'w').write(report)





