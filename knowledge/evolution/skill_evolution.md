# Skill evolution policy

Skill evolution changes published knowledge context, not the Hermes runtime,
agent roles, orchestration rules, model parameters, or audit standards.

Every change follows: source evidence -> candidate assets -> structural and
reference validation -> applicable GEE validation -> explicit approval ->
publication. Analysis execution reads only `knowledge/published/`.

Supported operations are `add`, `modify`, and `merge`. No candidate may update
published capabilities until its referenced Task is approved and published.

