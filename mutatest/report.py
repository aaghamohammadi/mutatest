"""Results analysis and report creation..
"""
from collections import Counter
from typing import List, NamedTuple

from mutatest.maker import Mutant, MutantTrialResult


class ReportedMutants(NamedTuple):
    """Container for reported mutants to pair status with the list of mutants."""

    status: str
    mutants: List[Mutant]


def get_reported_results(trial_results: List[MutantTrialResult], status: str) -> ReportedMutants:
    """Utility function to create filtered lists of mutants based on status.

    Args:
        trial_results: list of mutant trial results
        status: the status to filter by

    Returns:
        The reported mutants as a ReportedMutants container.
    """
    mutants = [t.mutant for t in trial_results if t.status == status]
    return ReportedMutants(status, mutants)


def analyze_mutant_trials(trial_results: List[MutantTrialResult]) -> str:
    """Create the analysis text report string for the trials.

    It will look like:

    Overall mutation trial summary:
    ===============================
    DETECTED: x
    SURVIVED: y
    ...

    Breakdown by section:
    =====================

    Section title
    -------------
    source_file.py: (l: 1, c: 10) - mutation from op.Original to op.Mutated
    source_file.py: (l: 3, c: 10) - mutation from op.Original to op.Mutated

    Args:
        trial_results: list of MutantTrial results

    Returns:
        str, the text report
    """

    status = dict(Counter([t.status for t in trial_results]))
    status["TOTAL RUNS"] = len(trial_results)

    detected = get_reported_results(trial_results, "DETECTED")
    survived = get_reported_results(trial_results, "SURVIVED")
    errors = get_reported_results(trial_results, "ERROR")
    unknowns = get_reported_results(trial_results, "UNKNOWN")

    report_sections = []

    # build the summary section
    summary_header = "Overall mutation trial summary"
    report_sections.append("\n".join([summary_header, "=" * len(summary_header)]))
    for s, n in status.items():
        report_sections.append(f"{s}: {n}")

    # build the breakout sections for each type
    section_header = "Breakdown by section"
    report_sections.append("\n".join(["\n", section_header, "=" * len(section_header)]))
    for rpt_results in [survived, detected, errors, unknowns]:
        if rpt_results.mutants:
            report_sections.append(build_report_section(rpt_results.status, rpt_results.mutants))

    return "\n".join(report_sections)


def build_report_section(title: str, mutants: List[Mutant]) -> str:
    """Build a readable mutation report section from the list of mutants.

    It will look like:

    Title
    -----
    source_file.py: (l: 1, c: 10) - mutation from op.Original to op.Mutated
    source_file.py: (l: 3, c: 10) - mutation from op.Original to op.Mutated


    Args:
        title: title for the section.
        mutants: list of mutants for the formatted lines.

    Returns:
        The report section as a formatted string.
    """

    fmt_list = []

    fmt_template = (
        "{src_file}: (l: {lineno}, c: {col_offset}) - mutation from {op_type} to {mutation}"
    )

    for mutant in mutants:
        summary = {}
        summary["src_file"] = str(mutant.src_file)
        summary["lineno"] = str(mutant.src_idx.lineno)
        summary["col_offset"] = str(mutant.src_idx.col_offset)
        summary["op_type"] = str(mutant.src_idx.op_type)
        summary["mutation"] = str(mutant.mutation)

        fmt_list.append(fmt_template.format_map(summary))

    report = "\n".join(["\n", title, "-" * len(title)] + [s for s in fmt_list])
    return report