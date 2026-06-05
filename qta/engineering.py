"""Engineering readiness gates and fixes registry."""

from .constants import (
    BLOCKING, gate_status_3layer,
)
from .model import Gate, CURRENT_CHAMBER, CURRENT_MODE_B


def _g(gid, name, mode, eq, comp, thresh, spec, inst, verif, reason_detail, fix, unit=""):
    status = gate_status_3layer(spec, inst, verif,
        physics_ok=(comp < thresh if isinstance(comp, (int, float)) and
                    isinstance(thresh, (int, float)) else True),
        blocking_if_not_specified=(not spec))
    reason = (f"SPECIFIED:{['No','Yes'][spec]}  INSTALLED:{['No','Yes'][inst]}  "
              f"VERIFIED:{['No','Yes'][verif]}. Status={status}. {reason_detail}")
    return Gate(gid, name, mode, eq, comp, thresh, status, reason, fix, unit)


def engineering_readiness_gates():
    """Build E01-E14 and shielding/RTB gates."""
    gates = []
    _ch = CURRENT_CHAMBER
    _mb = CURRENT_MODE_B

    gates.append(_g("E01", "250°C/48h UHV Bakeout", "MODE_A_BASELINE",
        "bakeout_executed=True; T_bake>=250C; t_bake>=48h",
        int(_ch.bakeout_done), 1,
        False, False, False,
        "O-ring chamber NOT BAKE-COMPATIBLE. CF flanges required.",
        "Rebuild with CF flanges. Execute 250°C/48h bake."))

    gates.append(_g("E02", "SAES St707 NEG Pump", "MODE_A_BASELINE",
        "NEG_installed=True; H2 pumping speed S_H2>=5L/s verified",
        int(_ch.NEG_installed), 1,
        True, False, False,
        "Design: SAES St707, 5 L/s H2. NOT INSTALLED.",
        "Source SAES St707. Activate (400°C/1h). Install."))

    gates.append(_g("E03", "77K Charcoal Cryotrap", "MODE_A_BASELINE",
        "cryotrap_installed=True; S_cryo>=0.5m3/s for CH4 verified",
        int(_ch.cryotrap_installed), 1,
        True, False, False,
        "Design: 50g charcoal in OFHC Cu. NOT INSTALLED.",
        "Fabricate 50g charcoal cryotrap. Install."))

    gates.append(_g("E04", "RGA Engineering Readiness", "MODE_A_BASELINE",
        "RGA: CH4<5e-14, H2<2e-14 Pa (FC-corrected)",
        int(_ch.RGA_verified), 1,
        False, False, False,
        "RGA not performed. FC correction not calibrated.",
        "Perform RGA after each purge. Calibrate FC."))

    gates.append(_g("E05", "Ag Sinter Thermal Interface (45cm²)", "MODE_A_BASELINE",
        "sinter_fabricated=True; G_eff measured",
        int(_ch.sinter_fabricated), 1,
        True, False, False,
        "G_eff=1e-5 ASSUMED from Kapitza. NOT FABRICATED.",
        "Fabricate 45cm² Ag sinter. Measure G_eff."))

    gates.append(_g("E06", "Kevlar/G10 Intercepted Suspension", "MODE_A_BASELINE",
        "suspension_installed=True; G_cond measured",
        0, 1, True, False, False,
        "NOT INSTALLED. G_cond ASSUMED=2.46 nW.",
        "Fabricate Kevlar/G10 suspension. Measure S_vib."))

    gates.append(_g("E07", "Independent Gas Delivery Lines (×5)", "MODE_A_BASELINE",
        "5 lines installed; leak-checked; thermally anchored",
        0, 5, True, False, False,
        "NOT INSTALLED. Valve leakage gives P_CH4=1e-9 Pa steady-state.",
        "Install 5 SS lines. Leak-check. Anchor at all stages."))

    gates.append(_g("E08", "Shuttered Cryo-Baffle / Molecular Beam Shutter", "MODE_A_BASELINE",
        "shutter_installed=True; conductance model verified",
        0, 1, True, False, False,
        "3-shutter stack + labyrinth DESIGN_SPECIFIED. NOT INSTALLED.",
        "Fabricate shutter stack + labyrinth."))

    gates.append(_g("E09", "MW Attenuation and Thermal Anchoring", "MODE_A_BASELINE",
        "MW_thermal_anchored=True; P_mw at CPW <= 1nW",
        0, 1, True, False, False,
        "Thermocoax + RC filters DESIGN_SPECIFIED. NOT INSTALLED.",
        "Install Thermocoax + RC filters. Calibrate P_mw."))

    gates.append(_g("E10", "Vibration Isolation (Helmholtz)", "MODE_A_BASELINE",
        "Helmholtz installed; S_vib at NV measured",
        0, 1, True, False, False,
        "S_vib=1e-10 ASSUMED (Oxford spec). NOT MEASURED.",
        "Install Helmholtz. Measure S_vib and dB/dz."))

    gates.append(_g("E11", "Optical Collection Calibration", "MODE_A_BASELINE",
        "eta_col measured in cryostat; dark_frac < 20%",
        0, 1, False, False, False,
        "eta_col=6.35% ASSUMED. NOT MEASURED in cryostat.",
        "Calibrate eta_col in cryostat."))

    gates.append(_g("E12", "NV Charge-State at 10mK (C_contr)", "MODE_A_BASELINE",
        "ODMR_10mK performed; C_contr > 0.05 confirmed",
        int(_ch.ODMR_10mK_done), 1,
        False, False, False,
        "C_contr at 10mK UNKNOWN. Co-equal bottleneck with tau_c.",
        "ODMR at 10mK post-cycle (F15)."))

    gates.append(_g("E13", "Rabi Calibration in Cryostat", "MODE_A_BASELINE",
        "Omega_R measured; tau_pi2 < T2*",
        0, 1, False, False, False,
        "Omega_R=139591 rad/s ASSUMED. tau_pi2~T2*: DEGRADED.",
        "Measure Rabi oscillations. If tau_pi2>T2*, increase P_mw."))

    gates.append(_g("E14", "Ramsey T2*/tau_c Measurement", "MODE_A_BASELINE",
        "tau_c measured; tau_c > 292us confirmed",
        0, 1, False, False, False,
        "tau_c UNKNOWN. DOMINANT MC failure (66.2% of samples).",
        "Ramsey on He-3 vs He-4 at 10mK."))

    # Shielding gates
    gates.append(_g("Shield-RAD", "Radiation load below Mode D budget", "MODE_A_BASELINE",
        "P_rad_10mK_measured < P_Mode_D_budget",
        0, 1, False, False, False,
        "SHIELD-001/002/003 DESIGN_SPECIFIED only.",
        "Radiometric sample-stage heat load measurement."))

    gates.append(_g("Shield-RF", "RF leakage below heat AND dephasing budget", "MODE_A_BASELINE",
        "(P_RF_10mK + P_blackbody) < P_RF_budget",
        0, 1, False, False, False,
        "SHIELD-004 RF-tight can NOT_INSTALLED.",
        "Install SHIELD-004 + SHIELD-005."))

    gates.append(_g("Shield-OPT", "No optical LOS to 10 mK", "MODE_A_BASELINE",
        "LOS_300K_to_10mK = FALSE AND P_scatter < budget",
        0, 1, False, False, False,
        "SHIELD-006/007 NOT_INSTALLED. LOS audit not performed.",
        "Install aperture chain + cold beam dumps."))

    gates.append(_g("Shield-MAG", "Magnetic noise reduced, NV bias stable", "MODE_A_BASELINE",
        "B_noise_rms_reduced AND |delta_B_NV_bias| < tolerance",
        0, 1, False, False, False,
        "SHIELD-010/011 NOT_INSTALLED.",
        "Install SHIELD-010. Field map with shield in/out."))

    gates.append(_g("Shield-CHEM", "Cryopanel prevents chemical memory", "MODE_A_BASELINE",
        "RGA_species_residual < Mode_D_threshold AND QCM < spec",
        0, 1, False, False, False,
        "SHIELD-008/009 NOT_INSTALLED.",
        "Install SHIELD-008 + SHIELD-009. Through-cycle RGA+QCM."))

    gates.append(_g("C_to_D_Readiness", "Composite Mode D entry readiness", "MODE_A_BASELINE",
        "ALL sub-conditions within Mode D spec",
        0, 1, False, False, False,
        "None of the Mode C readiness sub-conditions measured.",
        "Execute T-C2D coordinated measurement."))

    gates.append(_g("RTB_JT_OPTIONAL_COOLING_PLANT",
        "Optional RTB/JT upstream cooling plant (4-8 modules)", "MODE_A_BASELINE",
        "RTB_JT_selected=true AND installed AND lift_curves_measured",
        0, 1, False, False, False,
        "DESIGN_OPTION only. Not a 10 mK cooler. Not selected/installed.",
        "Vendor lift curves. Measure derated thermal-link. Verify Mode D isolation."))

    return gates


INTERLOCKS = [
    ("IL-01", "LCVD_on AND sensing_on", "IMPOSSIBLE", "thermal: 250x overload"),
    ("IL-02", "precursor_on AND He3_dosing_on", "IMPOSSIBLE", "chemical: He-3 film in 2.6s"),
    ("IL-03", "LCVD_on AND heat_switch_closed", "IMPOSSIBLE", "thermal: heats MC"),
    ("IL-04", "sensing_on AND heat_switch_open", "IMPOSSIBLE", "thermal: sample not at 10mK"),
    ("IL-05", "sensing_on AND NOT RGA_pass_CH4", "BLOCKED", "CH4 contamination"),
    ("IL-06", "sensing_on AND NOT RGA_pass_H2", "BLOCKED", "H2 coverage"),
    ("IL-07", "sensing_on AND T_sample>12mK", "BLOCKED", "too warm for Ramsey"),
    ("IL-08", "sensing_on AND NOT vib_settled", "BLOCKED", "vibration corrupts Ramsey"),
    ("IL-09", "He3_present AND LCVD_on", "IMPOSSIBLE", "thermal+chemical"),
    ("IL-10", "He3_present AND precursor_on", "IMPOSSIBLE", "CH4 poisons He-3"),
    ("IL-11", "Mode_D AND NOT Mode_B_complete", "BLOCKED", "purge required"),
    ("IL-12", "charcoal_regen AND IVC_valve_open", "BLOCKED", "gas burst contaminates"),
    ("IL-13", "growth_on AND He3_dosing_on", "IMPOSSIBLE", "modes mutually exclusive"),
    ("IL-14", "LCVD_on AND helium_film_present", "IMPOSSIBLE", "He film blocks LCVD"),
]

EXPERIMENTS = [
    ("ODMR at 10mK bare diamond [MUST BE FIRST]", "C_contr_10mK",
     "ODMR contrast before any He-3.", "C_contr>0.05."),
    ("Ramsey: He-3 vs He-4 control [CRITICAL]", "tau_c",
     "tau_c measurement via Ramsey.", "tau_c>=292us."),
    ("250C/48h bakeout + SAES NEG + RGA", "RGA_P_H2",
     "Bake; activate NEG; RGA verify.", "P_H2<2e-12Pa; P_CH4<5e-12Pa."),
    ("G_eff step-response thermometry", "G_eff_meas",
     "Apply P=1nW; measure dT_ss.", "G_eff=(1.0±0.3)e-5W/K."),
    ("Fabricate 45cm2 Ag sinter", "A_sinter",
     "Direct-contact sinter to diamond.", "G_Kap>=1e-5W/K at 10.43mK."),
    ("RGA CH4 after each purge", "RGA_P_CH4",
     "Verify P_CH4<5e-12Pa post-purge.", "IL-05 hard interlock."),
    ("Vibration PSD + dB/dz", "S_vib",
     "Accelerometer on fridge; field probe.", "S_a<1e-10; dB/dz<1mT/cm."),
    ("Rabi oscillation in cryostat", "Omega_R",
     "Measure tau_pi2.", "Deviation >10% indicates miscalibration."),
    ("s_He / E_b on F-diamond (TPD/QCM)", "s_He",
     "Temperature-programmed desorption.", "Closes coverage model."),
    ("eta_abs measurement", "eta_abs",
     "Measure 532nm absorption in diamond.", "Closes gates D6, D7."),
]


ENGINEERING_FIXES = [
    ("F01", "UHV All-Metal Build",
     "REQUIRED", "NOT_INSTALLED",
     ["B4", "B7"],
     "CF flanges, Cu gaskets, all-metal valves.",
     "CF enables 250-450°C bake. Viton limited to 120°C.",
     "CF flange leaks if torqued incorrectly."),

    ("F02", "Differentially Pumped Micro-Nozzle",
     "REQUIRED", "NOT_INSTALLED",
     ["B5"],
     "Reduces P_CH4 at sensing zone.",
     "Capillary (0.5mm ID, 100mm): C_mol=1.61e-7 m3/s.",
     "Nozzle clogging from carbon deposition."),

    ("F03", "Three-Shutter Stack",
     "REQUIRED", "NOT_INSTALLED",
     ["B5", "A3"],
     "Radiation shielding improved (eps_eff=0.0068).",
     "Three 4K OFHC Cu shutters with position sensors.",
     "Motor vibration on actuation; debris from mechanism."),

    ("F04", "Witness Coupons",
     "REQUIRED", "NOT_INSTALLED",
     ["B5", "D11", "D12_G23"],
     "Adds experimental evidence.",
     "Growth-zone + shielded sensing-zone coupons. XPS/Raman/AFM.",
     "Coupons must survive cryogenic cycling."),

    ("F05", "RGA All-Species Acceptance Thresholds",
     "REQUIRED", "NOT_INSTALLED",
     ["B3", "B4"],
     "UNKNOWN->CONDITIONAL once RGA performed.",
     "H2<2e-12Pa, CH4<5e-12Pa, H2O<1e-11Pa, etc.",
     "RGA filament outgasses on first use."),

    ("F06", "Pump Train: NEG + Ion + Cryo",
     "REQUIRED", "NOT_INSTALLED",
     ["B1", "B2"],
     "Accelerates Mode B purge.",
     "77K cryotrap (~100 L/s CH4) + 4K cryotrap + NEG + ion pump.",
     "NEG saturation after ~100 cycles."),

    ("F07", "Residual Hydrogen Mitigation",
     "REQUIRED", "NOT_INSTALLED",
     ["B4"],
     "Post-bake P_H2 achievable in principle.",
     "250°C/48h bakeout + NEG activation.",
     "Bake may desorb contaminants onto NV crystal."),

    ("F08", "Surface Re-Termination / Recovery Protocol",
     "REQUIRED", "NOT_INSTALLED",
     ["D11", "D12_G23"],
     "CONDITIONAL until verified.",
     "XeF2 gas at 100°C for F-termination; XPS confirms.",
     "XeF2 is toxic; requires secondary containment."),

    ("F09", "Geometric Baffle / Labyrinth",
     "REQUIRED", "NOT_INSTALLED",
     ["B5"],
     "1000x CH4 flux reduction to NV zone.",
     "3 baffled right-angle turns, OFHC Cu at 4K.",
     "Restricts optical access."),

    ("F10", "Cryo-QCM at Sensing Surface",
     "RECOMMENDED", "NOT_INSTALLED",
     ["B5", "D11"],
     "Real-time adsorption measurement.",
     "AT-cut 5 MHz quartz; Sauerbrey sensitivity 5.66e5 Hz/(g/m2).",
     "QCM crystal must be thermally anchored to 4K."),

    ("F11", "Thermal-Switch Validation Hardware",
     "REQUIRED", "NOT_INSTALLED",
     ["D4", "D5", "C1"],
     "CONDITIONAL->may pass once step-response done.",
     "NiCr heater + RuO2 thermometer pair.",
     "10mT coil field may shift NV ODMR."),

    ("F12", "Vibration Metrology",
     "REQUIRED", "NOT_INSTALLED",
     ["C2", "D17"],
     "CONDITIONAL until measured.",
     "Cryogenic accelerometer + laser interferometer.",
     "Accelerometer adds heat load."),

    ("F13", "Optical Scatter Audit",
     "REQUIRED", "NOT_INSTALLED",
     ["A2"],
     "CONDITIONAL until measured.",
     "Calibrated photodiode at 4K stage.",
     "Scatter fraction changes with LCVD cycles."),

    ("F14", "Microwave Heat Audit",
     "REQUIRED", "NOT_INSTALLED",
     ["D16"],
     "CONDITIONAL until measured.",
     "NbN CPW: T_c~16K. Attenuator chain 20dB/3dB/0dB.",
     "NbN vortex flux flow at residual fields > B_c1."),

    ("F15", "NV Survival Post-Cycle Pretest",
     "REQUIRED", "NOT_INSTALLED",
     ["D12_G23"],
     "UNKNOWN->CONDITIONAL after first cycle.",
     "ODMR before/after Mode A/B/C cycle.",
     "30min overhead per cycle."),

    ("F16", "He-4 Control Experiment Before He-3",
     "REQUIRED", "DESIGN",
     ["D13"],
     "CONDITIONAL: He-4 establishes isotope specificity.",
     "Same dosing conditions with He-4 (I=0).",
     "He-4 also freezes at 10mK."),

    ("F17", "Multiple NV Depths — Ensemble Branch",
     "RECOMMENDED", "DESIGN",
     ["D13"],
     "CONDITIONAL: single-depth strategy is risky.",
     "Three samples: d=5, 10, 20nm.",
     "Multiple cool-down cycles required."),

    ("F18", "SIL / Waveguide Collection Upgrade",
     "RECOMMENDED", "DESIGN",
     ["D14", "D13"],
     "CONDITIONAL: branch decision if tau_c marginal.",
     "Diamond hemisphere SIL: eta_col->30%.",
     "Must survive LCVD thermal cycling."),

    ("F19", "Magnetic Shielding Package",
     "REQUIRED", "DESIGN",
     ["D17"],
     "CONDITIONAL: Helmholtz geometry required.",
     "SC Pb cylinder + Cryoperm-10 + mu-metal.",
     "SC shield traps flux on cooling."),

    ("F20", "Failure Recovery Path",
     "REQUIRED", "DESIGN",
     ["ALL"],
     "Framework reclassification.",
     "Pre-register go/no-go criteria for each mode.",
     "Must plan before experiments begin."),
]

# FA-FO additional fixes
EXTRA_FIXES = [
    ("FA", "Protected NV Cartridge / Load-Lock", "RECOMMENDED", "NOT_INSTALLED",
     ["D12_G23", "F08"], "Protects diamond during LCVD conditioning.",
     "Cartridge carousel; load-lock <1e-9 Pa.",
     "Load-lock leak on opening."),
    ("FB", "All-Metal Bake-Compatible Valve Tree", "REQUIRED", "NOT_INSTALLED",
     ["B1", "B2", "F01"], "Enables full 250C bake.",
     "VAT all-metal angle valves for all lines.",
     "Wrong valve state under power loss."),
    ("FC", "RGA Line-of-Sight Correction", "REQUIRED", "NOT_INSTALLED",
     ["B3", "B4"], "RGA measures at pump port; surface ~100x higher.",
     "Model P_surface = P_RGA*(S_pump/C_orifice).",
     "Overcorrection if model wrong."),
    ("FD", "Cold-Surface Memory / Desorption", "REQUIRED", "NOT_INSTALLED",
     ["B5", "D10"], "Shutters adsorb CH4 during Mode B.",
     "Heat shields >50K before closing sensing zone.",
     "Desorption timing uncertain."),
    ("FE", "Shutter Contamination Replacement", "REQUIRED", "NOT_INSTALLED",
     ["A3", "B5"], "Shutters accumulate carbon after N cycles.",
     "Dual shutter or scheduled replacement.",
     "Carbon buildup changes emissivity."),
    ("FF", "Optical Window Contamination", "REQUIRED", "NOT_INSTALLED",
     ["A2", "D14"], "Carbon deposits on windows.",
     "Heated window option (>100K). Replace every 10-20 cycles.",
     "Alignment changes after replacement."),
    ("FG", "Gas Purity Chain", "REQUIRED", "DESIGN",
     ["B4", "D10", "F05"], "Bottle purity sets residual floor.",
     "CH4>=5N; H2>=6N; He-3>=99.99%. SAES getters.",
     "Getter exhaustion without indicator."),
    ("FH", "Helium Leak Check Requirement", "REQUIRED", "NOT_INSTALLED",
     ["F01", "ALL"], "Prerequisite before any cooldown.",
     "Sensitivity <1e-11 Pa.m3/s. Repeat after bake.",
     "Bake stresses welds."),
    ("FI", "Electrical Filtering Heat Budget", "REQUIRED", "NOT_INSTALLED",
     ["D3"], "Filter heat load must be included in P_total.",
     "Thermocoax + RC powder filters.",
     "Powder filter clogging."),
    ("FJ", "Thermometer Self-Heating Audit", "REQUIRED", "NOT_INSTALLED",
     ["D4", "F11"], "Negligible at correct excitation.",
     "RuO2 (10kOhm): V=10nV => P=1e-23W.",
     "AC excitation at wrong frequency."),
    ("FK", "Magnetic Field Compatibility Map", "REQUIRED", "DESIGN",
     ["D17", "F19", "F11"], "Five field sources must be compatible.",
     "NV bias 1mT; SC switch 10mT; CPW 1.585uT.",
     "Residual flux in SC shield."),
    ("FL", "Eddy-Current Heating", "REQUIRED", "DESIGN",
     ["D3", "F12"], "Small but must be verified.",
     "Cu shutter in 1mT at 1s: P_eddy~1e-12W.",
     "Resonant eddy heating."),
    ("FM", "Acoustic Isolation for Pumps", "REQUIRED", "DESIGN",
     ["C2", "D17"], "Turbo transmits 50Hz vibration.",
     "Pneumatic isolators; bellows; remote pump.",
     "Pump-off leaves only cryo-pumping."),
    ("FN", "Emergency Fail-Safe State", "REQUIRED", "DESIGN",
     ["ALL"], "Prevents catastrophic contamination.",
     "Power-loss: all valves NC; shutter spring-return.",
     "NC solenoids need continuous power."),
    ("FO", "Acceptance Test Matrix", "REQUIRED", "DESIGN",
     ["ALL"], "Converts simulation into physical procedure.",
     "10-step sequence from leak check to reproducibility.",
     "Any failed item requires root-cause investigation."),
]

ALL_FIXES = ENGINEERING_FIXES + EXTRA_FIXES


def print_fixes():
    """Print all engineering fixes."""
    print("\n" + "─"*60)
    print("ENGINEERING FIXES (%d total)" % len(ALL_FIXES))
    print("─"*60)
    print(f"{'Fix':<5} {'Name':<35} {'Priority':<12} {'Status':<15} {'Gates'}")
    print("─"*60)
    for fix in ALL_FIXES:
        fid, name, priority, status, gates, desc, impl, risks = fix
        print(f"{fid:<5} {name:<35} {priority:<12} {status:<15} {','.join(gates)}")
