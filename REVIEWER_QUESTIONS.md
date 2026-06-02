# REVIEWER QUESTIONS

These are the specific technical questions a reviewer is asked to engage
with. They are deliberately phrased so that "I don't know" or "this is
the wrong question" are themselves useful answers.

The package status — BLOCKED now, CONDITIONAL after measurement, 0 PASS,
no claimed validation, no breakthrough claim — is not in dispute and is
not the subject of these questions.

---

### Q1. Is the 292 µs τ_c requirement physically plausible for the proposed surface state?

Context: the canonical threshold τ_c ≥ 292 µs (v3.3) is the combined
SNR ≥ 5 plus pulse-dephasing acceptance for the proposed shallow-NV /
³He-on-diamond geometry. The 27.728 µs (v3.0) figure is SUPERSEDED.
What ranges of τ_c are physically plausible on a fluorinated or
otherwise terminated diamond surface at 10 mK? Are there published or
expected upper bounds on ³He surface dynamics that would already settle
this?

### Q2. Can shallow NV ensembles retain usable contrast at 10 mK under this architecture?

Context: C_contr at 10 mK is treated by the package as UNKNOWN and as a
co-equal bottleneck with τ_c. Does the reviewer know of measurements,
either published or in their own lab, that bound C_contr for shallow NV
ensembles at sub-100 mK temperatures under realistic readout
illumination?

### Q3. Is ³He vs ⁴He contrast experimentally separable from other decoherence sources?

Context: gate D11 (He-3 coverage) and the τ_c question both implicitly
assume that the ³He-induced decoherence signature can be separated from
phonon, paramagnetic-impurity, and ¹³C nuclear-spin bath contributions
to NV dephasing. Is that separation plausible in this geometry, and
what control experiment (e.g. matched ⁴He dosing) would best establish
or rule it out?

### Q4. Is the residual hydrogen coverage requirement realistic?

Context: gates D10a / D10b assume a residual H2 surface coverage well
below 0.1% after bakeout, NEG, and cryotrap conditioning. Is that
combination of vacuum conditioning steps known to reach the assumed
coverage on the actual chamber surfaces, given typical real-world
outgassing from feedthroughs, microwave lines, and gas-handling
hardware?

### Q5. Is the cryogenic pulsed molecular beam / purge isolation architecture credible?

Context: Mode B LCVD uses a warm differentially pumped molecular beam to
avoid chamber-fill cryocondensation; Mode C purge plus cryotrap is
supposed to remove byproducts before Mode D. Is there a known successful
analogue in cryogenic surface chemistry, or are there architectural
flaws — coupling between the warm beam line and the 10 mK region,
shutter leakage, witness coupon transfer geometry — that would prevent
this from working in practice?

### Q6. Is the fs-pulse thermal recovery model too optimistic?

Context: gate D7 uses τ_recovery_D = 42 ns and T_peak_D = 0.673 K as
assumed values for the Mode D readout pulse. Diamond phonon transport
at 10 mK is not the same as at room temperature. Is the assumed
recovery time within an order of magnitude of reality, or does the
package quietly assume a thermal conductance that is implausible at
base temperature?

### Q7. Which blocked gate is most likely to kill the architecture?

Of the 21 BLOCKED gates, which one — in the reviewer's judgement — is
most likely to be unresolvable by reasonable engineering effort? The
package's own guess is D13 / C_contr-at-10-mK or A9 (LCVD deposition
yield), but this is not authoritative. The package is robust to being
told the answer is something different.

### Q8. Which first experiment gives the fastest falsification?

`FIRST_VALIDATION_EXPERIMENTS.md` lists experiments A–F in priority
order. Is that order correct? In particular, is there a cheaper or
faster experiment, not on the list, that would falsify a load-bearing
assumption with less hardware investment than A, B, or C?

---

## How to respond

The package owner is most interested in answers that contain at least
one of:

- a measured number or a tight published bound on any of τ_c, C_contr,
  T_peak_D, τ_recovery_D, or residual H2 coverage;
- a reference to prior work that already settles one of these questions;
- a specific architectural objection that would force a redesign;
- a recommendation of which expert or lab would have the most-informed
  view on a specific question.
