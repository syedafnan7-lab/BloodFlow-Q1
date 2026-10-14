# BloodFlow-Q product workflow and interoperability boundaries

## Product scope

BloodFlow-Q is a synthetic-network decision-support and research prototype. It models bank inventory, hospital demand, compatibility, routes and transportation costs; compares allocation methods; and applies synthetic disruptions before re-optimization. Its distinct research question is how candidate initialization affects a constrained post-disruption allocation search. It does not identify live stock, contact a facility, reserve units, authorize a transfer, or confirm delivery.

The primary workflow is: select a synthetic scenario → inspect bank/hospital supply and demand → identify a bottleneck → run an allocator → review allocations and unmet demand → apply a simulated demand, inventory or route event → re-optimize on the changed scenario → compare before/after results in the saved session.

## Existing Indian blood-service workflows

e-RaktKosh already provides blood-availability search across registered centres with state, district, blood group, component and location filters, along with centre directory, donation-camp and donor services. Its own system description covers centralized blood inventory and other blood-centre management functions. BloodFlow-Q must not claim that these services are absent. A possible future role is a separately authorized optimization and resilience layer that evaluates allocation alternatives across a modeled network under changing demand or route conditions; it would complement, not replace, existing inventory, request or clinical workflows.

The public portal describes availability search and centre discovery. The blood-bank login page says stock is entered by blood banks and access requires authorization/approval. In the sources reviewed for this sprint, we did not find published public API documentation suitable for an authorized integration. This is a limited finding, not proof that no private, partner, or otherwise authorized interface exists. No portal scraping, access-control bypass, or live data integration is used.

## Quantum research direction

Selected direction: **post-disruption multi-bank/multi-hospital reallocation, testing QAOA candidate initialization as a warm start for the existing bounded classical local search**. The existing Round 2 artifact is a pilot: it contains a synthetic two-bank/two-hospital/four-route tradeoff, ten QAOA seeds, ten classical-multistart seeds, and QAOA-seeded local refinement, with a 100 objective-evaluation search budget and independent feasibility checks. It is not a large disruption benchmark and does not demonstrate quantum advantage.

Next confirmatory experiment: create paired pre-event and post-event versions of larger synthetic networks; apply route-capacity disruption or demand spike to generate the second case; compare QAOA-derived feasible starts against greedy and seeded feasible classical starts under the same objective, feasible neighborhood, evaluation budget, and preregistered seed schedule. Report raw QAOA feasibility separately; do not repair infeasible samples into successful starts. Independently validate every allocation. Record feasible-run rate, objective distribution, unmet demand, runtime (QAOA time and search time separately), first-feasible/time-to-target, and variability. Retain failed/skipped runs and specify the target before execution. This proposed extension still needs to be run before making claims about this problem class.

## Research transparency

The Quantum Optimization Lab reads its sample, histogram counts, circuit depth, shot count, seed, runtime, objective and validator checks from the saved raw experiment artifact. It shows the twelve highest-count observed bitstrings only when the bit lengths and count totals pass consistency checks. The complete sample remains inspectable and exportable. The Solver Lab and Experiment Reports remain the detailed locations for measured findings, including negative and infeasible outcomes.

## Product inspiration and scope boundaries

The referenced Blood Boys segment (about 08:12–10:18) presents an urgent path from blood group/location to nearby centre discovery, then a fallback to eligible and responsive donors with a low-friction request and response flow. The transferable product principle is to make the next useful action obvious and keep the urgent workflow short. BloodFlow-Q applies that principle to operations research: inspect shortage, run the allocation, and show what changes after a modeled disruption. Donor-facing UX and real outreach remain outside this research workflow; no simulated request is represented as an actual donor contact or delivery.

## Government references

- [e-RaktKosh portal: availability search and services](https://eraktkosh.mohfw.gov.in/eraktkoshPortal/)
- [e-RaktKosh system description](https://eraktkosh.mohfw.gov.in/BLDAHIMS/bloodbank/about.cnt)
- [e-RaktKosh blood-bank login and stock entry / authorization notice](https://eraktkosh.mohfw.gov.in/eRaktKosh/hissso/loginLogin)
- [DGHS: Blood Transfusion Services and national framework](https://dghs.mohfw.gov.in/bts.php)
- [MoHFW: National Standards for Blood Centres](https://www.mohfw.gov.in/sites/default/files/National%20Standards%20for%20Blood%20Centres.pdf)
