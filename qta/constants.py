"""Physical constants, parameter registry, and engineering status."""

import math
from dataclasses import dataclass

k_B = 1.380649e-23
hbar = 1.054571817e-34
mu_0 = 1.25663706212e-6
sigma_SB = 5.670374419e-8
m_p = 1.67262192369e-27
pi = math.pi

def safe_exp(x):
    return float('inf') if x > 700 else math.exp(x)

# Source-class taxonomy
MEASURED = "MEASURED"
LITERATURE = "LITERATURE"
ASSUMED = "ASSUMED"
UNKNOWN = "UNKNOWN"
DESIGN = "DESIGN"
MANUFACTURER_SPEC = "MANUFACTURER_SPEC"
PHYSICAL_CONSTANT = "PHYSICAL_CONSTANT"
LITERATURE_CONSTANT = "LITERATURE_CONSTANT"
DESIGN_ASSUMPTION = "DESIGN_ASSUMPTION"

# Hardware status vocabulary
NOT_INSTALLED = "NOT_INSTALLED"
DESIGN_SPECIFIED = "DESIGN_SPECIFIED"
INSTALLED_UNTESTED = "INSTALLED_UNTESTED"
VALIDATED = "VALIDATED"
FAILED = "FAILED"
BLOCKING = "BLOCKED"


@dataclass
class EngStatus:
    """Three-layer engineering status for hardware components."""
    name: str
    specified: bool = False
    installed: bool = False
    verified: bool = False

    def layer_status(self) -> str:
        if self.verified:   return "VERIFIED"
        if self.installed:  return "INSTALLED_UNVERIFIED"
        if self.specified:  return "DESIGN_SPECIFIED"
        return "NOT_SPECIFIED"

    def gate_status(self) -> str:
        if self.verified:   return "PASS"
        if self.installed:  return "CONDITIONAL"
        if self.specified:  return "CONDITIONAL"
        return BLOCKING

    def reason(self) -> str:
        s = f"[{self.layer_status()}]"
        if not self.specified:  return f"{s} Not designed."
        if not self.installed:  return f"{s} Design complete; hardware NOT installed."
        if not self.verified:   return f"{s} Installed; measurement NOT performed."
        return f"{s} Installed and measurement confirmed."


ENG = {
    "bakeout":       EngStatus("250°C/48h UHV bakeout", True, False, False),
    "NEG":           EngStatus("SAES St707 NEG pump", True, False, False),
    "cryotrap":      EngStatus("77K charcoal cryotrap", True, False, False),
    "RGA":           EngStatus("RGA all-species post-purge verification", True, False, False),
    "pump_train":    EngStatus("Ion + turbo + NEG pump train", True, False, False),
    "leak_check":    EngStatus("He leak check (<1e-10 Pa·m³/s)", True, False, False),
    "Ag_sinter":     EngStatus("Ag sinter thermal interface (45 cm²)", True, False, False),
    "SC_switch":     EngStatus("Al superconducting heat switch", True, False, False),
    "G10_suspension": EngStatus("Kevlar/G10 intercepted suspension", True, False, False),
    "gas_lines":     EngStatus("Independent per-species gas delivery lines (5×)", True, False, False),
    "cryo_nozzle":   EngStatus("Shuttered cryogenic pulsed molecular beam", True, False, False),
    "mw_attenuation": EngStatus("Microwave attenuation chain", True, False, False),
    "helmholtz":     EngStatus("Helmholtz gradient-cancellation coil pair", True, False, False),
    "vibration_iso": EngStatus("Vibration isolation (cryostat + optical bench)", True, False, False),
    "shutter_4K":    EngStatus("4K OFHC Cu radiation shutter", True, False, False),
    "radiation_shield": EngStatus("Radiation shield + labyrinth baffles", True, False, False),
    "eta_col_cal":   EngStatus("Optical collection efficiency calibration", True, False, False),
    "eta_abs_meas":  EngStatus("Laser absorption fraction measurement", True, False, False),
    "NV_charge_val": EngStatus("NV charge-state validation (ODMR at 10 mK)", True, False, False),
    "Rabi_cal":      EngStatus("Rabi frequency calibration in cryostat", True, False, False),
    "T2star_tau_c":  EngStatus("Ramsey T2* and tau_c measurement on He-3/F-diamond", True, False, False),
    "G_eff_meas":    EngStatus("G_eff step-response thermometry", True, False, False),
    "S_vib_meas":    EngStatus("Vibration PSD measurement at NV position", True, False, False),
    "He4_control":   EngStatus("He-4 Ramsey control experiment", True, False, False),
}


def gate_status_3layer(specified, installed, verified, physics_ok=True, blocking_if_not_specified=False):
    if not specified:
        return BLOCKING if blocking_if_not_specified else "CONDITIONAL"
    if not installed:
        return "CONDITIONAL"
    if not verified:
        return "CONDITIONAL"
    return "PASS" if physics_ok else "FAIL"


def hw_status(specified, installed, verified):
    if verified:   return VALIDATED
    if installed:  return INSTALLED_UNTESTED
    if specified:  return DESIGN_SPECIFIED
    return NOT_INSTALLED


def eng_gate_status(key, physics_ok=True):
    e = ENG[key]
    return gate_status_3layer(e.specified, e.installed, e.verified, physics_ok)


def eng_note(key, physics_value=""):
    e = ENG[key]
    layer = hw_status(e.specified, e.installed, e.verified)
    s = f"[{layer}] {e.name}"
    if physics_value:
        s += f" — physics: {physics_value}"
    return s


PARAM_REGISTRY = [
    ("T_fridge", 0.010, "K", MANUFACTURER_SPEC, "Oxford Triton 200 (NOT installed in QTA)", "ABCD", "+-0.5mK"),
    ("P_cool_MC", 200e-6, "W", MANUFACTURER_SPEC, "Oxford Triton 200 (NOT installed in QTA)", "ABCD", "+-20%"),
    ("P_cool_4K", 1.5, "W", MANUFACTURER_SPEC, "Oxford Triton 200 (NOT installed in QTA)", "AB", "+-20%"),
    ("T_4K_plate", 4.0, "K", MANUFACTURER_SPEC, "Oxford Triton 200 (NOT installed in QTA)", "ABCD", "+-0.1K"),
    ("gamma_NV", 2*pi*28.025e9, "rad/s/T", PHYSICAL_CONSTANT, "NIST CODATA gyromagnetic ratio", "D", "0.01%"),
    ("gamma_He3", 2*pi*32.434e6, "rad/s/T", PHYSICAL_CONSTANT, "NIST CODATA gyromagnetic ratio", "D", "0.01%"),
    ("alpha_K_Ag", 2000., "W/m2/K4", LITERATURE, "Pobell 2007 A6.2", "D", "+-20%"),
    ("kappa_Kev_4K", 0.040, "W/m/K", LITERATURE, "Rule 1996 Cryo.36:283", "ABCD", "+-20%"),
    ("kappa_G10_4K", 4.8e-3, "W/m/K", LITERATURE, "Runyan 2008 Cryo.48:448", "ABCD", "+-20%"),
    ("f_th_NV", 0.544, "", LITERATURE, "Doherty 2013", "D", "+-5%"),
    ("eta_QY_NV", 0.70, "", LITERATURE, "Doherty 2013", "D", "+-10%"),
    ("F_abl_diamond", 1e4, "J/m2", LITERATURE, "Diamond lit.", "D", "+-50%"),
    ("s_H2_Cu_4K", 0.3, "", LITERATURE, "Benvenuti 1999", "B", "+-50%"),
    ("G_sw_open", 1e-8, "W/K", LITERATURE, "Al SC switch SC state; Pobell 2007", "AB", "factor 10x"),
    ("B_c_Al", 10e-3, "T", LITERATURE, "Al critical field 10mK", "ACD", "+-1mT"),
    ("P_H2_postbake", 5e-12, "Pa", ASSUMED, "CERN Outgassing 2020", "B", "order mag"),
    ("G_eff", 1e-5, "W/K", ASSUMED, "Design; Kapitza; NOT MEASURED", "D", "factor 10x"),
    ("G_eff_meas", None, "W/K", UNKNOWN, "Step-response not done", "D", "blocks PASS"),
    ("A_sinter", None, "m2", UNKNOWN, "45cm2 design; NOT FABRICATED", "D", "blocks PASS"),
    ("P_cond_wiring", 2.46e-9, "W", ASSUMED, "NbTi/Cu wiring; not measured", "D", "+-50%"),
    ("eta_abs", 0.05, "", ASSUMED, "NV absorption; NOT MEASURED", "D", "factor 3x"),
    ("E_pulse", 50e-12, "J", ASSUMED, "Design", "D", "+-20%"),
    ("f_rep", 200., "Hz", ASSUMED, "Design", "D", "+-factor2"),
    ("r_spot", 361e-9, "m", ASSUMED, "SRIM/NA estimate", "D", "+-50%"),
    ("P_LCVD", 50e-3, "W", ASSUMED, "Typical LCVD spot", "A", "factor 3x"),
    ("P_mw", 1e-9, "W", ASSUMED, "Design; not measured in cryo", "D", "+-factor2"),
    ("Z0_CPW", 50., "Ohm", DESIGN, "Design", "D", "+-1Ohm"),
    ("w_CPW", 5e-6, "m", DESIGN, "Design", "D", "+-1um"),
    ("d_NV", 10e-9, "m", ASSUMED, "SRIM estimate; not measured", "D", "factor 2x"),
    ("T2s_bare", 10e-6, "s", ASSUMED, "Literature; NOT this sample", "D", "factor 3x"),
    ("C_contr", 0.10, "", ASSUMED, "NOT measured in cryo", "D", "blocks PASS G23"),
    ("eta_col", 0.0635, "", ASSUMED, "Free-space chain; not calibrated", "D", "factor 3x"),
    ("dark_cps", 250., "cps", ASSUMED, "Excelitas SPCM spec", "D", "+-50%"),
    ("tau_c", None, "s", UNKNOWN, "PRIMARY BOTTLENECK; not measured", "D", "blocks PASS"),
    ("C_contr_10mK", None, "", UNKNOWN, "Gate 23; not measured", "D", "blocks PASS"),
    ("RGA_P_CH4", None, "Pa", UNKNOWN, "RGA not performed", "B", "blocks Mode B"),
    ("RGA_P_H2", None, "Pa", UNKNOWN, "RGA not performed", "B", "blocks Mode B"),
    ("s_He", 1.0, "", ASSUMED, "UNKNOWN for F-diamond; assume 1", "D", "blocks PASS"),
    ("E_b_He_kB", 30., "K", ASSUMED, "He/graphite proxy; diamond unknown", "D", "factor 2x"),
    ("n_s_target", 3.3e18, "m-2", ASSUMED, "Design", "D", "+-50%"),
    ("P_CH4_work", 1e-4, "Pa", ASSUMED, "Typical LCVD working pressure", "A", "factor 10x"),
    ("P_CH4_purge_tgt", 5e-12, "Pa", DESIGN, "Required before He-3 dosing", "B", "criterion"),
    ("bakeout_done", 0, "", ASSUMED, "Not yet executed", "B", "bool"),
    ("cryotrap_4K", 0, "", ASSUMED, "Not yet installed", "B", "bool"),
    ("NEG_pump", 0, "", ASSUMED, "Not yet installed", "B", "bool"),
    ("S_vib", 1e-10, "m2/Hz", ASSUMED, "Oxford Triton spec; NOT measured here", "CD", "factor 10x"),
    ("t_growth", 30., "s", ASSUMED, "Design growth pulse", "A", "+-factor3"),
    ("t_purge_min", 7200., "s", ASSUMED, "Min pumpout; outgassing dominated", "B", "+0/-50%"),
    ("t_vib_settle", 100., "s", ASSUMED, "Vib settling after shutter", "C", "+-factor3"),
]
