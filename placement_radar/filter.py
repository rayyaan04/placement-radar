# cheap first pass on job titles - keep only early careers roles (interns, placement year)
# cowork still makes real eligibility decision later so this isnt only check
import re

# words that mark a student focused role. \b means word boundary, so "intern" matches "Intern" but not "Internal"
EARLY = re.compile(
    r"\b(intern|interns|internship|internships|placement|industrial|year in industry|sandwich|"
    r"spring week|spring insight|insight week|insight programme|insight program|insight day|"
    r"undergraduate|student|summer analyst|co-op)\b",
    re.I,  # ignore case
)
# words that mark an experienced/senior role - these override student words
SENIOR = re.compile(r"\b(senior|staff|principal|manager|director|experienced|chief)\b", re.I)

def is_early_careers(posting):
    # true only if posting has student word AND no senior word.
    # PHD roles are kept, so cowork and flag them under the degree level gate later
    return bool(EARLY.search(posting.title)) and not SENIOR.search(posting.title)
    
