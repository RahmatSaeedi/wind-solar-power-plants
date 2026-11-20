# Notation register

One symbol, one meaning, in every chapter. Add a symbol here before using it in a chapter.
Appendix A is generated from this file and `terms-fa-en.csv`.

Conventions: quantities in italic math (`$V$`), units upright (`\text{V}`), subscripts that are
words upright (`$V_\text{oc}$`), subscripts that are indices italic (`$R_k$`). Lower-case `v, i, p`
for instantaneous values, upper-case `V, I, P` for DC or RMS values. Vectors and phasors are
introduced in chapters 3 and 7.

## Electrical

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $q$, $Q$ | electric charge | C | 6 |
| $V$, $v$ | voltage (potential difference) | V | 6 |
| $I$, $i$ | current | A | 6 |
| $R$ | resistance | Ω | 6 |
| $G$ | conductance | S | 6 |
| $\rho$ | resistivity (in circuit chapters) | Ω·m | 6 |
| $\alpha$ | temperature coefficient of resistance | 1/°C (1/K) | 6 |
| $P$, $p$ | active power | W | 6 |
| $E$ | energy | J, Wh | 6 |
| $\eta$ | efficiency | – | 6 |
| $V_\text{s}$ | source voltage | V | 6 |
| $R_\text{s}$ | source internal resistance | Ω | 6 |
| $R_\text{L}$ | load resistance | Ω | 6 |
| $R_\text{c}$ | conductor (cable) resistance, both directions | Ω | 6 |
| $\Delta V$ | voltage drop | V | 6 |
| $P_\text{loss}$ | power lost in conductors | W | 6 |
| $V_\text{oc}$, $I_\text{sc}$ | open-circuit voltage, short-circuit current | V, A | 6 |
| $V_\text{mp}$, $I_\text{mp}$, $P_\text{max}$ | PV module values at the maximum-power point | V, A, W | 6 |
| $N_\text{s}$, $N_\text{p}$ | number in series, number in parallel | – | 6 |
| $L$ | one-way route length of a circuit | m | 6 |
| $A$ | conductor cross-sectional area | mm² (m²) | 6 |
| $J$ | current density | A/mm² | 6 |
| $T$ | temperature | °C (K) | 6 |
| $t$ | time | s, h | 6 |

## Plant-level

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $P_\text{PV,dc}$ | PV array DC capacity | MWp | 1 |
| $P_\text{PV,ac}$ | PV inverter AC capacity | MW | 1 |
| $P_\text{W}$ | wind capacity | MW | 1 |
| $P_\text{exp,max}$ | export limit at the point of connection | MW | 1 |
| $P_\text{B}$, $E_\text{B}$ | BESS power and energy capacity | MW, MWh | 1 |
| $\text{CF}$ | capacity factor | – | 1 |

## Units, energy bases and resource (chapter 2)

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $\{Q\}$, $[Q]$ | numerical value and unit of a quantity $Q$ | – | 2 |
| $\mathsf{L, M, T, I, \Theta, N, J}$ | dimensions of the seven base quantities | – | 2 |
| $G$ | irradiance (in solar chapters; conductance in circuit chapters) | W/m² | 2 |
| $G_\text{STC}$ | irradiance at standard test conditions, 1000 W/m² | W/m² | 2 |
| $H$ | irradiation (energy per area over a period) | kWh/m² | 2 |
| $P_\text{STC}$ | PV power at standard test conditions | W | 2 |
| $P_\text{ref}$ | reference power stated for a capacity factor | W | 2 |
| $h_\text{FL}$ | full-load hours | h | 2 |
| $Y_\text{sp}$ | specific yield | kWh/kWp (h) | 2 |
| $v$ | wind speed (in wind and resource chapters) | m/s | 2 |
| $\rho_\text{air}$, $R_\text{d}$ | air density; specific gas constant of dry air | kg/m³; J/(kg·K) | 2 |
| $A_\text{r}$ | rotor swept area | m² | 2 |
| $K_\text{e}$ | energy pattern factor $\overline{v^3}/\bar v^3$ | – | 2 |
| $z$, $z_0$, $\alpha$ | height; roughness length; shear exponent | m; m; – | 2 |
| $\lambda$ | tip-speed ratio $\omega R/v$ | – | 2 |
| $\omega$ | angular speed | rad/s | 2 |
| $\theta_\text{w}$ | wind direction (FROM, clockwise from true north) | ° | 2 |
| $u$, $v_\text{N}$ | eastward and northward wind components | m/s | 2 |
| $S$, $Q$ | apparent and reactive power (AC) | VA, var | 2 |
| $V_\text{LL}$, $I_\text{L}$ | line-to-line voltage, line current | V, A | 2 |
| $t_\text{WC}$, $t_\text{RSS}$ | worst-case and root-sum-square stacked tolerance | as the parts | 2 |
| $f_v$, $f_H$ | uncertain scale factors on wind speed and irradiation | – | 2 |

## Measurement uncertainty (chapter 2)

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $\bar x$, $s$ | mean and experimental standard deviation of $n$ observations | as $x$ | 2 |
| $u(x)$ | standard uncertainty of $x$ | as $x$ | 2 |
| $u_\text{c}(y)$ | combined standard uncertainty | as $y$ | 2 |
| $U$ | expanded uncertainty | as $y$ | 2 |
| $k$ | coverage factor (Boltzmann's constant is $k_\text{B}$) | – | 2 |
| $c_i$ | sensitivity coefficient $\partial f/\partial x_i$ | ratio of units | 2 |
| $\nu$ | degrees of freedom | – | 2 |
| $r_{ij}$ | correlation coefficient | – | 2 |
| $a$ | half-width of a Type B distribution | as $x$ | 2 |
| $w$ | guard band | as $y$ | 2 |
| $s_\text{fit}$, $r_i$ | residual standard deviation and residuals of a fit | as $y$ | 2 |

## Mathematics, geometry and dynamics (chapter 3)

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $\delta$ | solar declination | ° | 3 |
| $\omega$ | hour angle (solar chapters); angular speed elsewhere | °; rad/s | 3 |
| $\phi$ | latitude | ° | 3 |
| $\alpha_\text{s}$, $A$ | solar elevation, solar azimuth | ° | 3 |
| $\beta$, $\gamma$ | surface tilt, surface azimuth | ° | 3 |
| $\theta$ | angle of incidence (solar); voltage angle (power flow) | °, rad | 3 |
| $\mathbf{s}$, $\mathbf{n}$ | unit vectors to the sun and normal to a surface | – | 3 |
| $\mathbf{A}$, $\mathbf{x}$, $\mathbf{b}$ | matrix, unknown vector, right-hand side | – | 3 |
| $\mathbf{G}$, $\mathbf{B}$ | conductance matrix; susceptance (DC power-flow) matrix | S; pu | 3 |
| $x_{ij}$ | reactance of the line from $i$ to $j$ | pu | 3 |
| $\lambda$ | eigenvalue (mathematics); tip-speed ratio (wind) | 1/s; – | 3 |
| $\kappa$ | condition number | – | 3 |
| $\mathbf{Z}$, $\mathbf{S}$ | impedance, complex power | Ω, VA | 3 |
| $a$ | operator $1\angle 120^\circ$ | – | 3 |
| $\mathbf{I}_0, \mathbf{I}_1, \mathbf{I}_2$ | zero, positive, negative sequence currents | A | 3 |
| $\tau$ | time constant | s | 3 |
| $E$ | energy stored in a battery (state variable) | MWh | 3 |
| $k$, $c$ | Weibull shape and scale (wind chapters) | –, m/s | 3 |
| $\Gamma$ | gamma function | – | 3 |
| $r_1$, $n_\text{eff}$ | lag-1 autocorrelation, effective sample size | – | 3 |
| $h$ | step size of a numerical method | as the variable | 3 |
| $\mathbf{Y}_\text{bus}$, $\mathbf{Z}_\text{bus}$ | bus admittance and bus impedance matrices | pu | 3 |
| $Z_{kk}$, $I_{\text{f},k}$ | Thevenin impedance and three-phase fault current at bus $k$ | pu; pu or kA | 3 |
| $g$ | annual growth (or decay) rate | 1/yr | 3 |
| $L$, $W$ | level in decibels; sound power (noise sections) | dB; W | 3 |
| $\eta$ | step size of gradient descent (that section only) | as $\mathbf{x}$ over $f$ | 3 |
| $\nabla f$ | gradient of $f$ | units of $f$ per unit of $\mathbf{x}$ | 3 |
| $r$ | discount rate (money sections) | 1/yr | 3 |
| $\text{AF}$, $\text{CRF}$ | annuity factor, capital recovery factor | yr; 1/yr | 3 |
| $\text{LCOE}$; $I_0$, $O_t$, $E_t$ | levelised cost; capex, opex and energy of year $t$ | money/MWh; money; MWh | 3 |
| $h$ | harmonic order (signal sections) | – | 3 |
| $f_1$, $f_s$, $f_c$ | fundamental, sampling and corner frequency | Hz | 3 |
| $A_h$, $\varphi_h$, $X_h$ | peak amplitude, phase and DFT coefficient of harmonic $h$ | as the signal; rad | 3 |
| $\text{THD}$ | total harmonic distortion | – (or %) | 3 |
| $L_0$ | distance constant of a cup anemometer | m | 3 |
| $\mu$, $\beta$; $T$, $x_T$ | Gumbel location and scale; return period, $T$-year value | as $x$; yr | 3 |
| $\mathbf{P}$, $\boldsymbol{\pi}$ | transition matrix, stationary distribution (Markov chains) | – | 3 |
| $\lambda$, $\mu$ | failure and repair rates (Markov sections) | 1/h | 3 |
| $V_t(e)$ | value function of dynamic programming at hour $t$, stored energy $e$ | money | 3 |
| $A^{*}$ | economic conductor cross-section (Kelvin's law) | mm² | 3 |
| $\lambda$ (geodesy) | longitude, east positive; $\lambda_0$ reference meridian | ° | 3 |
| $R$ (geodesy) | mean Earth radius, 6 371.0 km | m | 3 |
| $P(A \mid B)$; $F$, $\bar F$, $+$ | conditional probability; fault, no fault, positive alarm | – | 3 |
| $u(z, t)$, $\alpha$ | temperature field in soil, thermal diffusivity | °C; m²/s | 3 |
| $r$ (PDE) | mesh ratio $\alpha\,\Delta t/\Delta z^{2}$ | – | 3 |
| $d$ | damping depth $\sqrt{2\alpha/\omega}$ | m | 3 |
| $\mathbf{H}$ | Hessian matrix of second derivatives | units of $f$ per unit$^2$ | 3 |

## Physics, materials and manufacturing (chapter 4)

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $F$, $W$, $T$ | force, weight, torque (mechanics sections) | N, N, N m | 4 |
| $C_T$, $C_p$, $a$ | thrust and power coefficients, axial induction factor | – | 4 |
| $I$ | moment of inertia (rotation); second moment of area (beams) | kg m²; m⁴ | 4 |
| $S$ | elastic section modulus (beams) | m³ | 4 |
| $H$ | inertia constant | s | 4 |
| $q$ | dynamic pressure; heat flux in heat-transfer sections | Pa; W/m² | 4 |
| $R_\text{d}$ | specific gas constant of dry air, 287.05 | J/(kg K) | 4 |
| $\alpha$ | wind-shear exponent; thermal expansion coefficient; each section states which | –; 1/K | 4 |
| $z_0$ | roughness length | m | 4 |
| $k$, $h$ | thermal conductivity, convection coefficient | W/(m K), W/(m² K) | 4 |
| $\alpha_R$ | temperature coefficient of resistance | 1/K | 4 |
| $\varepsilon_r$, $\tan\delta$ | relative permittivity, dielectric loss factor | – | 4 |
| $E_g$ | band gap | eV | 4 |
| $\sigma$, $\varepsilon$, $E$ | stress, strain, elastic modulus (materials sections) | Pa, –, Pa | 4 |
| $\Delta\sigma$, $N$, $m$, $D$ | stress range, cycles, S-N slope, Miner damage | Pa, –, –, – | 4 |
| $K$, $K_{IC}$, $a_c$ | stress intensity, fracture toughness, critical crack length | Pa m^0.5, Pa m^0.5, m | 4 |
| $E_a$ | activation energy | J/mol | 4 |
| $C_p$, $C_{pk}$ | process capability indices (quality sections; not the power coefficient) | – | 4 |
| $R_a$, $R_q$ | arithmetic and root-mean-square profile roughness | µm | 4 |
| $a_{50}$, $a_{90}$ | flaw sizes detected with 50 and 90 % probability | mm | 4 |

## Computing and engineering data (chapter 5)

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $b_k$, $N$ | binary digit $k$ and the integer it builds (number-base lesson only) | – | 5 |
| $u$, $x$ | unsigned register value and its signed reading (register lesson only) | – | 5 |
| $s$, $e$, $f$ | sign bit, stored exponent and fraction of a float (floating-point lesson only) | – | 5 |
| $\bar v$, $\overline{v^{3}}$ | mean speed and mean of the cubed speed | m/s; m³/s³ | 5 |
| $\bar\theta$ | vector-mean wind direction | ° | 5 |
| $T_\text{c}$, $T_\text{a}$ | cell and air temperature | °C | 5 |
| $\gamma$, $k_\text{o}$, $\eta_\text{inv}$ | PV temperature coefficient, other-loss factor, inverter efficiency | 1/K; –; – | 5 |
| $v_\text{eq}$ | equivalent wind speed at reference density 1.225 kg/m³ | m/s | 5 |
| $E_k$, $E_\text{use}$ | stored energy at the end of hour $k$; usable energy | MWh | 5 |
| $c_k$, $d_k$, $\eta_\text{rt}$ | battery charge and discharge power (AC); round-trip efficiency | MW; – | 5 |
| $R_{20}$, $R_T$, $\ell$ | resistance per km at 20 °C, total resistance at temperature $T$, route length | Ω/km; Ω; km | 5 |
| $P_0$, $P_k$, $S_\text{r}$ | transformer no-load loss, load loss at rating, rated apparent power | MW; MW; MVA | 5 |
| $\text{CFADS}_t$, $\text{DS}_t$, $\text{DSCR}_t$ | cash flow available for debt service, debt service, coverage ratio in year $t$ | money; money; – | 5 |
| $D$, $r_\text{d}$, $n$ | debt, debt interest rate, debt tenor | money; 1/yr; yr | 5 |
| $\beta_1$ | first root of $\cos\beta\cosh\beta = -1$ (clamped-free beam) | – | 5 |

## AC circuits and three-phase power (chapter 7)

Phasors are bold with RMS magnitude ($\mathbf{V} = V\angle\theta$); plain $V$, $I$ are RMS values;
peaks carry the subscript m.

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $V_\text{m}$, $I_\text{m}$ | peak (amplitude) of a sinusoid | V, A | 7 |
| $\omega$, $f$, $T_1$ | angular frequency, frequency, period of the fundamental | rad/s, Hz, s | 7 |
| $\theta_v$, $\theta_i$, $\varphi$ | phase angles of voltage and current; $\varphi = \theta_v - \theta_i$ (lag positive) | ° | 7 |
| $\mathbf{V}$, $\mathbf{I}$, $\mathbf{I}^{*}$ | phasors (RMS magnitude) and the conjugate | V, A | 7 |
| $k_\text{cr}$, $k_\text{f}$ | crest factor, form factor | – | 7 |
| $L$, $C$ | inductance, capacitance (in AC sections; route length is $\ell$ there) | H, F | 7 |
| $X$, $X_L$, $X_C$ | reactance, inductive and capacitive reactance | Ω | 7 |
| $\mathbf{Y}$, $G$, $B$ | admittance, conductance, susceptance | S | 7 |
| $f_0$, $\omega_0$, $Q_\text{f}$ | resonant frequency, quality factor | Hz, rad/s, – | 7 |
| $S_\text{sc}$, $X_\text{sc}$, $h_\text{r}$ | short-circuit power, network reactance, resonance order | MVA, Ω, – | 7 |
| $Q_\text{c}$ | reactive power of capacitors (bank or cable) | var | 7 |
| $V_\text{LL}$, $V_\text{ph}$, $I_\text{line}$, $I_\text{ph}$ | line and phase voltage; line and phase (branch) current | V, A | 7 |
| $\mathbf{V}_\text{a}$, $\mathbf{V}_\text{ab}$, $\mathbf{I}_\text{N}$, $\mathbf{V}_\text{n}$ | phase and line-to-line voltages, neutral current, star-point voltage | V, A | 7 |
| $S_\text{base}$, $V_\text{base}$, $I_\text{base}$, $Z_\text{base}$; $z$, $r$, $x$ | per-unit bases; impedances in per unit (lower case) | –, pu | 7 |
| $u_2$ | voltage (or current) unbalance factor $|\mathbf{V}_2|/|\mathbf{V}_1|$ | – | 7 |
| $W_1$, $W_2$ | two-wattmeter readings (that lesson only) | W | 7 |
| $p(t)$, $S$, $\mathbf{S}$, $\text{pf}$ | instantaneous power, apparent power, complex power, power factor | W, VA, VA, – | 7 |
| $I_h$, $\varphi_h$, $\text{THD}_I$, $\text{THD}_V$, $K$ | RMS of harmonic $h$, its phase, current and voltage THD, K-factor | A, °, –, –, – | 7 |
| $D$, $Q_1$ | distortion power; reactive power of the fundamental | VA, var | 7 |
| $n$ | transformer turns ratio (transformer lessons only) | – | 7 |
| $I_\text{k}$, $\tau$ | symmetrical short-circuit current; DC time constant $L/R$ | A, s | 7 |
| $E_P$, $E_Q$ | active and reactive energy of a period | kWh, kvarh | 7 |
| $\alpha$ | harmonic summation exponent (that example only) | – | 7 |

## Electrical machines (chapter 8)

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $e$, $B$, $\ell$, $v$ | motional EMF of a conductor, flux density, active length, surface speed | V, T, m, m/s | 8 |
| $\Phi$, $N$, $\mathcal{R}$, $\mu_0$, $\mu_r$ | flux per pole, turns, reluctance, permeability of vacuum, relative permeability | Wb, –, A/Wb, H/m, – | 8 |
| $H_k$, $\ell_k$ | field strength and path length of segment $k$ of a magnetic circuit | A/m, m | 8 |
| $p$, $n_\text{s}$, $s$ | number of poles (not pole pairs), synchronous speed $120f/p$, slip | –, rpm, – | 8 |
| $\omega_\text{s}$, $\omega_e$ | synchronous (mechanical) and electrical angular speed | rad/s | 8 |
| $k_w$, $k_d$, $k_p$, $k_{w,h}$ | winding, distribution and pitch factors; winding factor of harmonic $h$ | – | 8 |
| $q$, $y$, $\gamma$, $Q$ | slots per pole and phase, coil pitch (fraction of a pole pitch), slot angle, number of slots | –, –, °, – | 8 |
| $k_\text{sk}$, $\theta_\text{sk}$ | skew factor, skew angle (electrical) | –, ° | 8 |
| $E$, $X_\text{s}$, $R_a$, $\delta$ | internal EMF, synchronous reactance, armature resistance, load angle | V, Ω, Ω, ° | 8 |
| $x_d$, $x_d'$, $x_d''$, $x_q$ | direct-axis synchronous, transient, subtransient reactances; quadrature axis (per unit) | pu | 8 |
| $T_d'$, $T_d''$, $T_a$ | transient and subtransient time constants, armature (DC) time constant | s | 8 |
| $\psi_\text{m}$, $L_d$, $L_q$, $i_d$, $i_q$ | magnet flux linkage, $d$/$q$ inductances and currents | Wb, H, A | 8 |
| $R_1$, $X_1$, $X_m$, $R_2$, $X_2$ | induction-machine equivalent circuit (per phase, star values) | Ω | 8 |
| $P_\text{ag}$, $P_\text{mech}$, $T_\text{e}$, $T_\text{L}$ | air-gap power, mechanical power, electromagnetic and load torque | W, W, N m, N m | 8 |
| $I_\text{lr}$, $I_\text{r}$ | locked-rotor (starting) current, rated current | A | 8 |
| $J_\text{m}$, $t_\text{run}$, $E_\text{r}$ | moment of inertia of a drive, run-up time, rotor heat in a start | kg m², s, J | 8 |
| $H$, $E_\text{k}$, $K_s$, $\omega_n$ | inertia constant (chapter 4), kinetic energy, synchronising power, natural angular frequency | s, J, pu, rad/s | 8 |
| $\sigma$, $V_r$ | air-gap shear stress, rotor volume $T/(2\sigma)$ | Pa, m³ | 8 |
| $P_0$, $P_k$, $x$ | fixed and load losses at rated load, load in per unit | W, W, – | 8 |
| $P_\text{cu}$, $P_\text{fe}$ | copper and iron (core) losses | W | 8 |
| $R_\text{th}$, $G_{wc}$, $G_{ca}$ | thermal resistance; conductances winding–coolant and coolant–ambient | K/W, W/K | 8 |
| $C_w$, $C_c$, $T_w$, $T_c$, $T_a$ | heat capacities and temperatures of winding and coolant; ambient (two-node model; $T_a$ is the armature time constant in fault sections) | J/K, °C | 8 |
| $p_\text{e}$, $\rho_\text{m}$ | classical eddy loss per kilogram, density of the steel (there $\sigma$ is conductivity) | W/kg, kg/m³ | 8 |
| $\lambda_\text{opt}$ | optimum tip-speed ratio | – | 8 |
| $f_\text{sb}$ | sideband frequency $(1 \pm 2s)f$ of a broken rotor bar | Hz | 8 |
| $L_{10}$, $C$, $P_\text{eq}$ | basic rating life, dynamic load rating, equivalent bearing load | h, N, N | 8 |
| $f_r$, $N_\text{slot}$ | rotational frequency, number of stator slots in the slot-passing tone | Hz, – | 8 |
| $\delta_\text{max}$ | load-angle limit in a capability chart | ° | 8 |

## Power electronics (chapter 9)

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $D$, $f_\text{sw}$, $T$ | duty cycle, switching frequency, switching period (converter sections) | –, Hz, s | 9 |
| $V_\text{dc}$, $V_\text{dc,min}$, $h_\text{m}$ | DC-link voltage, its minimum for a given AC voltage, headroom fraction | V, V, – | 9 |
| $m$, $m_f$ | modulation index, carrier frequency ratio $f_\text{sw}/f_1$ | – | 9 |
| $V_0$, $r$, $R_\text{on}$ | threshold voltage and slope resistance of an IGBT or diode; MOSFET on-resistance | V, Ω, Ω | 9 |
| $\hat I$ | peak of a sinusoidal current | A | 9 |
| $E_\text{on}$, $E_\text{off}$, $E_\text{rr}$ | turn-on, turn-off and diode reverse-recovery energies | J | 9 |
| $P_\text{c,T}$, $P_\text{c,D}$, $P_\text{sw,T}$, $P_\text{rr,D}$ | conduction and switching losses of IGBT and diode | W | 9 |
| $T_j$, $R_\text{jc}$, $R_\text{ch}$, $R_\text{hc}$, $Z_\text{th}$, $C_\text{th}$ | junction temperature; thermal resistances junction–case, case–heatsink, heatsink–coolant; transient thermal impedance; heat capacity | °C, K/W, K/W, J/K | 9 |
| $c_0$, $c_1$, $c_2$, $p$, $p_\text{loss}$ | coefficients of the three-term loss model; output and loss in per unit | – | 9 |
| $L_1$, $L_2$, $C$, $f_\text{res}$, $R_\text{d}$ | LCL filter inductances, capacitance, resonance, damping resistance (filter sections) | H, F, Hz, Ω | 9 |
| $I_\text{C,rms}$ | RMS ripple current of the DC-link capacitor | A | 9 |
| $k_p$, $k_i$, $\omega_n$, $\zeta$, $\omega_c$ | PI gains, natural frequency, damping ratio, current-loop bandwidth | –, 1/s, rad/s, –, rad/s | 9 |
| $I_q$, $I_p$, $I_\text{max}$, $k$ | reactive and active current in a dip, current limit, reactive-current gain (FRT sections) | pu | 9 |
| $V^+$, $V^-$, $I^+$, $I^-$ | positive- and negative-sequence voltage and current magnitudes | pu | 9 |
| $\text{SCR}$ | short-circuit ratio $S_\text{sc}/P_\text{r}$ | – | 9 |
| $Q_\text{g}$, $t_\text{d}$, $L_\sigma$ | gate charge, dead time, stray inductance of the commutation loop | C, s, H | 9 |
| $C_1$, $C_2$ | constants of the explicit four-point PV curve | – | 9 |
| $\varphi$ | phase shift of a dual active bridge (that lesson); otherwise the power-factor angle | rad | 9 |

## PV modules and arrays (chapter 10)

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $E_\text{ph}$, $\lambda$, $\lambda_\text{g}$ | photon energy, wavelength, cut-off wavelength $hc_0/E_g$ | eV, nm, nm | 10 |
| $h$, $c_0$, $q$, $k_\text{B}$ | Planck constant, speed of light, elementary charge, Boltzmann constant | – | 10 |
| $J_\text{max}$, $\Phi$, $\alpha(\lambda)$ | maximum photocurrent density, photon flux, absorption coefficient (photon lessons) | A/m², 1/(m² s), 1/cm | 10 |
| $I_\text{L}$, $I_0$, $I_\text{D}$ | photocurrent, dark saturation current, diode current | A | 10 |
| $n$, $a$, $V_t$, $N_\text{s}$ | ideality factor, modified ideality factor $a = n N_\text{s} k_\text{B} T_\text{c}/q$, thermal voltage, cells in series | –, V, V, – | 10 |
| $R_\text{s}$, $R_\text{sh}$ | series and shunt resistance of the single-diode model | Ω | 10 |
| $\text{FF}$, $W(x)$ | fill factor; Lambert W function | – | 10 |
| $\mu_I$, $\mu_V$, $\gamma$ | absolute temperature coefficients of $I_\text{sc}$ and $V_\text{oc}$; relative coefficient of $P_\text{max}$ | A/K, V/K, 1/K | 10 |
| $T_\text{c}$, $T_\text{a}$, $T_\text{NOCT}$ | cell temperature, air temperature, nominal operating cell temperature | °C | 10 |
| $U_0$, $U_1$, $v$ | Faiman heat-loss coefficients; wind speed at module height | W/(m² K), W s/(m³ K), m/s | 10 |
| $B_\text{f}$, $K(\theta)$, $b_0$, $M$ | bifaciality factor; incidence angle modifier and its ASHRAE coefficient; spectral mismatch factor | – | 10 |
| $V_\text{br}$, $a_\text{br}$, $m$ | avalanche breakdown voltage and Bishop coefficients (reverse-bias lesson) | V, –, – | 10 |
| $n$, $c$, $P_\text{a}$ | sample size, acceptance number, probability of acceptance (sampling lesson) | – | 10 |
| $N$, $N_\text{max}$, $N_\text{min}$, $N_\text{p}$ | modules per string and its bounds; strings in parallel | – | 10 |
| $V_\text{sys}$, $V_\text{floor}$ | maximum system voltage; floor of the MPPT window | V | 10 |
| $G_\text{b}$, $G_\text{d}$, $G_\text{g}$, $G_\text{POA}$ | beam, sky-diffuse and ground components of plane-of-array irradiance; their sum | W/m² | 10 |
| $A_i$, $R_\text{b}$, $\rho_\text{g}$, $G_\text{0n}$, $\theta_z$ | anisotropy index, beam ratio, ground albedo, extraterrestrial normal irradiance, zenith angle | –, –, –, W/m², ° | 10 |
| $\text{GCR}$, $d$, $L$, $\alpha_\text{p}$, $f$ | ground coverage ratio, row pitch, table slope length (row lessons), sun profile angle, shaded share of the slope | –, m, m, °, – | 10 |
| $\text{PR}$, $Y_\text{f}$, $H_\text{POA}$ | performance ratio, specific yield, annual plane-of-array irradiation | –, kWh/kWp, kWh/m² | 10 |
| $SR$, $r_\text{s}$, $L(t)$, $\bar L_T$ | soiling ratio, soiling rate, soiling loss after $t$ days and its mean over $T$ | –, %/d, %, % | 10 |
| $C_\text{cl}$, $p_\text{e}$, $E_\text{d}$, $\eta$, $T^*$ | cost per cleaning, energy price, daily energy, share of dirt removed (cleaning lessons), optimal interval | u, u/MWh, MWh, –, d | 10 |
| $U_{\bar P}$, $u_\text{cal}$, $s$ | expanded uncertainty of a sample mean, calibration standard uncertainty, sample standard deviation | W | 10 |

Chapter 10 notes: the surface tilt stays $\beta$ (chapter 3), so the data-sheet temperature coefficients
of $I_\text{sc}$ and $V_\text{oc}$ are written $\mu_I$, $\mu_V$ (never $\alpha$, $\beta$); $\gamma$ keeps its
chapter 5 meaning (relative coefficient of power).

## Wind turbines (chapter 11)

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $\omega$, $\lambda$, $\lambda_r$, $\lambda_\text{opt}$ | rotor speed; tip-speed ratio $\omega R/v$; local ratio $\omega r/v$; optimum | rad/s, – | 11 |
| $A_\text{r}$, $R$, $H$ | rotor swept area, tip radius, hub height | m², m, m | 11 |
| $C_p$, $C_T$, $F_\text{T}$ | power and thrust coefficients; rotor thrust | –, –, N | 11 |
| $a$, $a'$, $\phi$, $\alpha$ | axial and tangential induction; inflow angle; angle of attack | –, –, °, ° | 11 |
| $\theta_\text{p}$, $\theta_\text{tw}$, $c_\text{b}$, $N_\text{b}$ | pitch angle, twist, chord, number of blades | °, °, m, – | 11 |
| $\sigma_r$, $F$, $C_L$, $C_D$ | local solidity; Prandtl tip-and-hub loss factor; lift and drag coefficients | – | 11 |
| $T_\text{a}$, $T_\text{g}$, $k$ | aerodynamic and generator torque (low-speed shaft); torque-law constant $T_\text{g} = k\omega^2$ | N m, N m s² | 11 |
| $J_\text{m}$, $\tau$, $G$, $D$ | drivetrain inertia; time constant; $-\partial T_\text{a}/\partial\theta_\text{p}$; $-\partial T_\text{a}/\partial\omega$ | kg m², s, N m/rad, N m s | 11 |
| $K_p$, $K_i$, $\omega_n$, $\zeta$ | PI gains of the pitch loop; closed-loop natural frequency and damping | s, –, rad/s, – | 11 |
| $v_\text{eq}$, $v_\text{rews}$, $v_\text{n}$ | density-equivalent speed; rotor-equivalent speed; density-normalised speed | m/s | 11 |
| $\alpha_\text{sh}$, $a_\text{t}$, $x$, $y$ | shear exponent (ch 11, where $\alpha$ is the angle of attack); tower radius; distances from the tower axis | –, m, m, m | 11 |
| $k_\text{w}$, $S_\text{eq}$, $m$ | Jensen wake decay constant; damage-equivalent load; S-N slope | –, N m, – | 11 |
| $f_\text{BPFO}$, $f_\text{mesh}$, $z$, $i$ | outer-race defect frequency; gear mesh frequency; tooth count; stage ratio | Hz, Hz, –, – | 11 |
| $L_{10}$, $C$, $P_\text{eq}$, $p$ | basic rating life (10⁶ rev in ch 11); dynamic rating; equivalent load; life exponent | 10⁶ rev, N, N, – | 11 |
| $M$, $t_\text{c}$, $b$, $h$, $\kappa$ | flap bending moment; spar-cap thickness, width, cap spacing; curvature | N m, m, m, m, 1/m | 11 |
| $\sigma_\text{b}$, $\sigma_\text{a}$, $F_\text{w}$, $D_\text{b}$, $\Phi$ | tower bending and axial stress; weight above a section; bolt circle; joint load factor | Pa, Pa, N, m, – | 11 |
| $L_W$, $L_p$, $\alpha_\text{air}$, $d$ | sound power level, sound pressure level, air absorption, slant distance | dB, dB, dB/m, m | 11 |

Chapter 11 notes: $\alpha$ is the angle of attack throughout chapter 11, so the shear exponent is
$\alpha_\text{sh}$ there; $c$ (no subscript) stays the Weibull scale and the blade chord is $c_\text{b}$;
$\phi$ is the inflow angle; $D$ is the aerodynamic damping only in the pitch-loop lessons (rotor
diameter is written $2R$ in formulas, "D" as a spacing unit in prose); $G$ is the torque sensitivity
to pitch only there; $p$ is the bearing life exponent in the main-bearing lesson; $\Phi$ is the
flange joint load factor (photon flux in chapter 10); $L_{10}$ is in millions of revolutions in
chapter 11 and in hours in chapter 8.

## Solar-resource assessment (chapter 12)

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $G_\text{h}$, $G_\text{b,n}$, $G_\text{d}$ | global horizontal, direct normal, diffuse horizontal irradiance | W/m² | 12 |
| $G_\text{0n}$, $G_\text{sc}$, $H_0$, $H$ | extraterrestrial normal irradiance, solar constant, daily extraterrestrial and ground irradiation | W/m², W/m², kWh/m² | 12 |
| $k_t$, $K_T$, $k_d$, $k_c$ | hourly and monthly clearness index, diffuse fraction, clear-sky index | – | 12 |
| $\mu_0$, $\omega_\text{s}$, $AM$ | cosine of the zenith angle, sunset hour angle, relative air mass | –, °, – | 12 |
| $t_\text{s}$, $t_\text{std}$, $E_t$, $L_\text{loc}$, $L_\text{std}$ | solar time, standard time, equation of time, site and zone longitudes | h, h, min, °, ° | 12 |
| $A_i$, $R_\text{b}$, $G_\text{sky}$ | anisotropy (circumsolar) index, beam ratio, sky-diffuse irradiance on the plane | –, –, W/m² | 12 |
| $u_\text{c}$, $P_{50}$, $P_{90}$ | combined relative standard uncertainty; median and 90 %-exceedance values | –, as quantity | 12 |
| $L_\text{module}$, $L_\text{sensor}$ | soiling loss of the modules and of the irradiance sensor | – | 12 |
| MBE, RMSE | mean bias error, root-mean-square error of one source against another | as quantity | 12 |

Chapter 12 notes: $G$ with a subscript is an irradiance throughout chapter 12 (never a conductance);
$H$ is a daily or annual irradiation; $k_t$ (hourly) and $K_T$ (monthly) keep the cases distinct;
$\mu_0$ replaces $\cos\theta_z$ in the quality-control limits; $P_{50}$ and $P_{90}$ are values
(not powers) and are written with the quantity they qualify.

## Wind measurement and assessment (chapter 13)

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $\alpha$, $z_0$, $u_*$, $\kappa$ | shear exponent, roughness length, friction velocity, von Kármán constant | –, m, m/s, – | 13 |
| $I$, $\sigma_v$, $I_\text{rep}$ | turbulence intensity, standard deviation of the ten-minute speed, representative turbulence | –, m/s, – | 13 |
| $\theta$, $\Gamma_d$, $\mathit{Ri}_b$ | potential temperature, dry-adiabatic lapse rate, bulk Richardson number | K, K/m, – | 13 |
| $v_\text{eq}$, $\varphi(z)$ | rotor-equivalent wind speed, veer relative to the hub direction | m/s, ° | 13 |
| $G$, $g$ | gust factor, peak factor | – | 13 |
| $v_r$, $\phi$, $u_\text{E}$, $v_\text{N}$ | lidar radial speed, beam angle from vertical, eastward and northward wind | m/s, °, m/s, m/s | 13 |
| $\gamma$ | temperature lapse rate used to carry the 2 m temperature to the hub | K/m | 13 |
| $u_\text{LT}$, $u_\text{IAV}$, $u_N$ | long-term estimate uncertainty, year-to-year variability, uncertainty of an $N$-year mean | – | 13 |

Chapter 13 notes: $\alpha$ is the shear exponent (thermal diffusivity keeps its own sections, the
solar elevation stays $\alpha_\text{s}$); $G$ is the gust factor only in the gust lesson (irradiance
elsewhere in Part III); $g$ is the peak factor there and the gravitational acceleration in the
Richardson and barometric formulas, where the peak factor does not appear; $\phi$ (beam angle) is
kept apart from $\varphi$ (veer).

## Site screening and micro-siting (chapter 14)

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $H$, $L$ | hill height above its surroundings, horizontal length scale (speed-up) | m | 14 |
| $I_\text{add}$, $I_\text{amb}$, $I_\text{eff}$ | wake-added, ambient and effective turbulence intensity | – | 14 |
| $x/D$ | distance behind a turbine in rotor diameters | – | 14 |
| $s$, $L$, $W$ | ground slope (fraction), pad length along the slope, pad width (earthworks) | –, m, m | 14 |
| $V_\text{cut}$, $V_\text{fill}$ | cut and fill volumes | m³ | 14 |
| $m$ | corridor margin over the least route cost | – | 14 |

Chapter 14 notes: $H$ is a hill height in the speed-up lesson only (irradiation elsewhere in Part III);
$L$ is the hill length scale in A and the pad length in C (each inside its own lesson); positions are
in a local grid, x east and y north in metres or km from the window's south-west corner.

## Energy-yield modelling and forecasting (chapter 15)

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $\tau$ | quantile level of a probabilistic forecast | – | 15 |
| $L_\tau(q, y)$ | pinball (quantile) loss of the $\tau$-quantile $q$ for the observation $y$ | as quantity | 15 |
| $\tau^*$ | best offered quantile (newsvendor) | – | 15 |
| $p$, $p_\text{short}$, $p_\text{sur}$ | scheduled price, shortfall price, surplus price | u/MWh | 15 |
| RMSE, MAE | root-mean-square and mean absolute error | as quantity or % of capacity | 15 |
| $P_0$, $\ell$, $P_\text{n}$ | no-load loss, load-loss share at rated power, rated (export) power | MW, –, MW | 15 |
| $\phi(v;\ \bar v, \sigma_v)$ | normal density used to smooth a power curve | s/m | 15 |
| $T_\text{c,w}$ | irradiance-weighted cell temperature of a period | °C | 15 |
| $\sigma_\text{w}$, $\sigma_\text{pv}$, $\sigma_\text{h}$ | year-to-year standard deviation of wind, PV and hybrid energy | GWh | 15 |
| $M$ | number of ensemble members | – | 15 |
| $w_L$, $\hat P_L$ | blending weight and blended forecast at lead $L$ | –, MW | 15 |
| CRPS, $x_i$, $y$ | continuous ranked probability score, ensemble members, observation | MW | 15 |

Chapter 15 notes: $\tau$ is the quantile level only in forecast sections (a time constant elsewhere);
error measures are given in MW or in per cent of the installed capacity (110 MW for the hybrid,
60 MW wind, 50 MW PV AC), always with the horizon and the hours they cover (all or daylight).

## Uncertainty and yield assessment (chapter 16)

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $P_p$, $z_p$ | value exceeded with probability $p$; normal quantile with $P_p = P_{50}(1 - z_p\,u)$ | as quantity; – | 16 |
| $u_\text{lt}$, $u_\text{iav}$ | long-term and year-to-year relative standard uncertainty | – | 16 |
| $u_n$ | uncertainty of the mean of $n$ future years | – | 16 |
| $\mathbf{u}$, $\mathbf{R}$ | vector of component uncertainties; their correlation matrix | as quantity; – | 16 |
| $c_E$ | energy sensitivity ratio: relative change of energy per relative change of speed | – | 16 |
| $\sigma_\text{h}$ | standard deviation of the hybrid energy (also ch 15) | GWh | 15 |
| $N$ | number of Monte Carlo draws | – | 16 |

Chapter 16 notes: $u$ without subscript is a relative standard uncertainty (one sigma); $P_{90}$ is
exceeded with probability 0.90 (the 10th percentile). $N$ is the number of turns in chapter 8 and of
draws only in chapter 16's Monte Carlo lessons. Finance symbols ($\text{CFADS}$, $\text{DSCR}$,
$\text{AF}$) are those of chapters 3 and 5.

## Load, grid and requirements (chapter 17)

| Symbol | Quantity | Unit | First used |
|---|---|---|---|
| $\text{LF}$ | load factor, mean over peak (also ch 7) | – | 7 |
| $\text{CF}$, $\text{DF}$ | coincidence factor (peak of the sum over the sum of the peaks) and diversity factor ($1/\text{CF}$) | – | 17 |
| $P_\text{up}$ | net flow from a node to the upstream network (generation minus local load) | MW | 17 |
| $\text{SOC}_0$, $\text{SOC}_\text{min}$, $E_\text{B}$, $P_\text{crit}$ | initial and lowest state of charge, battery energy, critical load | –, –, MWh, MW | 17 |
| $\Delta V / V$ | relative voltage rise along a line, $(R P + X Q)/V^2$ | % | 17 |

Chapter 17 notes: $\text{CF}$ is the coincidence factor only in load lessons (a capacity factor is
always written out in words there); $T$ in the load-factor formula is the period in hours.

## Reserved meanings (to avoid clashes later)

- $k$ and $c$ are the Weibull shape and scale in wind chapters, the coverage factor and the
  sensitivity coefficients ($c_i$, with subscript) in uncertainty work; specific heat capacity is
  written $c_p$ where it could clash.
- $\lambda$ is an eigenvalue in mathematical sections and the tip-speed ratio in wind chapters.

- $G$ is conductance in circuit chapters and irradiance in solar chapters.
- $v$ is the instantaneous voltage in circuit chapters and the wind speed in wind and resource
  chapters; the northward wind component is $v_\text{N}$.
- $k$ is the coverage factor in uncertainty work; Boltzmann's constant is $k_\text{B}$; the adiabatic
  constant of chapter 6 keeps $k$ inside its own section.
- $Q$ is charge in circuit chapters and reactive power in AC chapters.

- $\rho$ is resistivity in circuit chapters and air density in wind chapters; where both appear,
  write $\rho_\text{el}$ and $\rho_\text{air}$.
- $A$ is conductor area in cable calculations and rotor swept area in wind chapters ($A_\text{r}$).
- $E$ is energy; electric field strength is $\mathcal{E}$.
- $\eta$ is efficiency everywhere except the gradient-descent section of chapter 3, where it is
  the step size; later optimisation chapters write the step size $\eta_\text{step}$.
- $L$ is a circuit route length in cable work and a decibel level in noise sections ($L_W$ for
  sound power level, $L_p$ for sound pressure level where both appear).
- $r$ is the correlation coefficient in statistics, the discount rate in money sections ($r_1$ is
  the lag-1 autocorrelation); chapter 21 writes the discount rate $i$ or $r_\text{d}$ if both meet.
- $h$ is a numerical step size, an hour index, or a harmonic order; each section states which.
- $C_p$ is the power coefficient in wind sections and the process capability index in quality
  sections; $E$ is energy, elastic modulus (materials) or photon energy (light sections); $T$ is
  temperature, torque (mechanics) or a return period (extremes); $\sigma$ is stress in materials
  sections and a standard deviation in statistics; $a$ is the induction factor or a crack length.
- $\lambda$ is also longitude in geodesy sections; $r$ is also the mesh ratio of a diffusion
  scheme; $\alpha$ (no subscript) is thermal diffusivity in heat-diffusion sections ($\alpha_\text{s}$
  stays the solar elevation).
- Chapter 8 (machines): $J$ stays current density, the moment of inertia of a drive is $J_\text{m}$
  (chapter 4's $I$ would clash with currents); $p$ is the number of poles, never pole pairs (write
  $p/2$); $Q$ is the number of slots in winding sections, reactive power elsewhere; $\delta$ is the
  load angle (solar declination in solar chapters); $B$ is flux density (susceptance in AC
  circuits); $E$ is the internal EMF (energy carries a subscript there: $E_\text{k}$, $E_\text{r}$);
  $G$ is the balance grade in balancing sections only; $q$ is slots per pole and phase.
- Chapter 9 (power electronics): $D$ is the duty cycle (distortion power in chapter 7, Miner damage
  in chapter 4); $p$ is output in per unit of rating in the efficiency model (number of poles in
  machine sections); $C$ is the filter capacitance in filter sections; $k$ is the reactive-current
  gain in fault-ride-through sections; $r$ is a device slope resistance in loss sections.
- $\lambda$ and $\mu$ are failure and repair rates in Markov sections (an eigenvalue and the
  Gumbel location elsewhere); $\mathbf{P}$ is a transition matrix there, a power vector in power flow.

- $\lambda$ is also the wavelength in the photon lessons of chapter 10.
- $\eta$ is the share of dirt removed in the cleaning lessons of chapter 10 (efficiency elsewhere).
- $n$ is the ideality factor in the cell lessons and the sample size in the sampling lesson of chapter 10;
  $c$ is the acceptance number there.
- $L$ is the table slope length in the row-geometry lessons and $L(t)$ the soiling loss in chapter 10.

## Chapter 18 (architecture)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $\eta_\text{b}$, $\eta_\text{dc}$, $\eta_\text{c}$ | battery-inverter, DC/DC-converter and cell round-trip efficiencies | – | 18 |
| $\eta_\text{AC}$, $\eta_\text{DC}$ | share of stored PV energy returned to the grid, AC and DC coupling | – | 18 |
| $C_\text{MWh}$, $o$, $E_\text{d}$ | teaching cost per delivered MWh; yearly opex share of capex; delivered energy | money/MWh; –; MWh | 18 |
| $\lambda$, $t_\text{r}$ | failure rate (per year in chapter 18); repair time | 1/yr; h | 18 |
| $\bar{P}_\text{lost}$, $E_\text{u}$ | mean power lost during an outage; expected unserved energy | MW; MWh/yr | 18 |
| $Q_\text{c}$, $C$, $\ell$ | cable charging reactive power; capacitance per km; length | Mvar; µF/km; km | 18 |
| $I_k$, $r$ | current of the $k$-th string section; resistance per km | kA; Ω/km | 18 |
| $q$, $C_\text{now}$, $C_\text{later}$ | chance of an extension; cost of preparing now, of retrofitting later | –; money | 18 |
| $m$, $n$, $t_\text{L}$ | mean spares demand over the lead time; units installed; lead time | –; –; weeks | 18 |
| $x$, $S_\text{r}$ | per-unit reactance of a transformer; its rating | –; MVA | 18 |

## Chapter 19 (battery storage)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $Q$, $V_\text{n}$ | cell or battery capacity; nominal voltage | Ah; V | 19 |
| $V_\text{oc}(\text{SOC})$ | open-circuit voltage as a function of state of charge | V | 19 |
| $R_0$, $R_1$, $C_1$, $v_1$ | series resistance; polarisation resistance, capacitance and voltage | Ω; Ω; F; V | 19 |
| $\text{SOC}$, $\text{SOH}$ | state of charge, state of health | – | 19 |
| $k$, $b$ | gain error and offset of a current sensor (SOC lessons) | –; A | 19 |
| $N(d)$, $N_{100}$, $d$ | cycles to end of life at depth $d$; at full depth; depth of cycle | – | 19 |
| $E_\text{usable}$, $E_\text{nom}$, $E_\text{poc}$ | usable, nominal and delivered-at-POC energy | MWh | 19 |
| $w$, $\eta_\text{out}$, $a$ | SOC window width; one-way efficiency; auxiliary share | – | 19 |
| $C_\text{th}$, $UA$, $q$ | heat capacity of a container; envelope conductance; heat flows | kWh/K; kW/K; kW | 19 |
| $i_\text{l}$, $\Delta V$ | self-discharge (leak) current; drop of open-circuit voltage | A; mV | 19 |
| $p$, $\bar{n}$, $m$ | chance that a neighbour follows; expected cells involved; cells on each side | –; –; – | 19 |

- In chapter 19, $k$ is a current-sensor gain in the SOC lesson and the cycle-life exponent in the
  fade lesson (stated where used); $Q$ is a capacity (reactive power elsewhere); $C_1$ a capacitance.

- In chapter 18 $\lambda$ counts failures per year (per hour in the Markov sections of chapter 3);
  $C$ is a capacitance per km in the charging formula only.

## Chapter 20 (plant control and energy management)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $\tau$, $y$, $u$, $e$ | time constant of the controlled plant; its output; the command; the error | s; pu; pu; pu | 20 |
| $k_p$, $k_i$ | proportional and integral gains of a PI controller | –; 1/s | 20 |
| $\omega_\text{n}$, $\zeta$ | natural frequency and damping ratio of a closed loop | rad/s; – | 20 |
| $s_\text{d}$, $s_\text{q}$, $f_\text{db}$ | frequency droop; voltage-reactive slope; deadband | –; –; Hz | 20 |
| $P_\text{r}$, $Q_\text{max}$, $S_\text{r}$ | rated active power; reactive limit; apparent-power rating | MW; Mvar; MVA | 20 |
| $c_t$, $d_t$, $E_t$, $\pi_t$ | charge and discharge power, stored energy, price in hour $t$ | MW; MW; MWh; u/MWh | 20 |
| $E_\text{floor}$, $h_\text{s}$ | least stored energy that keeps a service; its duration | MWh; h | 20 |
| $V_t(E)$ | value of the rest of the day from energy $E$ at hour $t$ (dynamic programming) | u | 20 |
| $c_\text{s}$, $c_\text{l}$, $q^\ast$ | imbalance penalty short and long; best bid quantile | u/MWh; u/MWh; – | 20 |
| $m_i$, $f_i^\text{set}$ | droop of grid-forming unit $i$ (Hz per rated power); its no-load frequency | Hz; Hz | 20 |
| $\Delta f_\text{s}$, $\theta_\text{w}$ | slip frequency before reconnection; half-width of the angle window | Hz; degree | 20 |

- In chapter 20, $e$ is a control error (not energy: energy is $E$) and $m_i$ a droop slope;
  $s$ with a subscript is a droop or slope, never the Laplace variable (written $\sigma$ where needed).

## Chapter 21 (project economics and contracts)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $r$, $r_\text{real}$, $i$ | discount rate (nominal), real rate, inflation | – | 21 |
| $C_t$, $E_t$ | cash flow and energy of year $t$ | k u; MWh | 21 |
| $\text{NPV}$, $\text{IRR}$ | net present value; internal rate of return | k u; – | 21 |
| $\text{CFADS}_t$ | cash flow available for debt service in year $t$ | k u | 21 |
| $\text{DS}_t$, $I_t$, $P_t$, $B_t$ | debt service, interest, principal, balance at the start of year $t$ | k u | 21 |
| $\text{DSCR}_t$, $\text{LLCR}_t$ | debt service cover ratio; loan life cover ratio | – | 21 |
| $D$, $g$ | debt amount; gearing (debt over total uses) | k u; – | 21 |
| $n$, $n_\text{d}$ | economic life; debt tenor | years | 21 |
| $\text{CRF}$ | capital recovery factor $r/(1-(1+r)^{-n})$ | – | 21 |
| $\tau_\text{tax}$ | tax rate (teaching) | – | 21 |

- In chapter 21, $P_t$ is a principal repayment (power is $P$ elsewhere), $I_t$ an interest
  payment and $i$ an inflation rate; $\tau_\text{tax}$ keeps the tax rate apart from the time
  constant $\tau$ of chapter 20.

## Chapter 22 (feasibility and option selection)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $s_{ik}$, $w_k$, $S_i$ | normalised score of option $i$ on criterion $k$; weight; weighted total | – | 22 |
| $q$, $s^\text{adj}$ | evidence quality (0 guess, 1 measured and reviewed); quality-adjusted score | – | 22 |
| $M$, $\Delta_k$ | lead of the first option over the second; score fall that removes it | – | 22 |
| $C_\text{base}$, $C_{P80}$, $C_\text{cont}$ | most-likely cost; 80th percentile; contingency to P80 | k u | 22 |
| $V_k$, $p_k$, $c_k$ | value of gate node $k$; pass probability; spend at the gate | k u; –; k u | 22 |
| $m$, $\text{NPV}_\text{today}$ | months to financial close; NPV brought back to the review date | months; k u | 22 |

- In chapter 22, $M$ is a score margin and $m$ a number of months (not a mass or a droop);
  $q$ is an evidence quality, not a reactive power ($Q$).

## Chapter 23 (electrical one-line and system boundaries)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $S_\text{r}$, $z$, $z_\text{src}$ | rated power of a transformer; its impedance; source impedance on its base | kVA; pu; pu | 23 |
| $S_\text{sc}$, $S_\text{start}$ | short-circuit power behind a bus; starting kVA of a motor | kVA | 23 |
| $\Delta u$ | voltage dip at motor starting | – | 23 |
| $I_\text{k}$ | three-phase fault current | kA | 23 |
| $S_\text{k}$, $S_i$ | fault power at a bus; fault power of element $i$ (MVA method) | MVA | 23 |
| $C$, $I_k$, $t_k$ | battery capacity; current and duration of duty period $k$ | Ah; A; h | 23 |
| $k_T$, $k_A$, $k_M$ | temperature, ageing and design-margin factors | – | 23 |

- In chapter 23, $z$ is a per-unit impedance (lower case), $I_k$ with an index $k$ is a duty-cycle
  current while $I_\text{k}$ (upright k) is a fault current.

## Chapter 24 (cables, switchgear and electrical installation)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $R_{20}$, $R_\theta$, $\alpha$ | resistance at 20 C and at $\theta$; temperature coefficient | ohm/km; 1/K | 24 |
| $I_0$, $I_\text{z}$, $f_k$ | rating in reference conditions; rating in place; installation factor $k$ | A; A; – | 24 |
| $\theta_\text{c}$, $\theta_\text{a}$, $T_\text{th}$, $R'$ | conductor and ambient temperature; thermal resistance; resistance per metre | C; C; K m/W; ohm/m | 24 |
| $S$, $k$, $t$ | conductor section; adiabatic constant; fault duration | mm2; A s^0.5/mm2; s | 24 |
| $i_\text{p}$, $\kappa$ | peak short-circuit current; peak factor | kA; – | 24 |
| $T_1$, $T_2$, $\mu$, $\theta$ | pulling tension before and after a bend; friction; bend angle | N; –; rad | 24 |
| $E$, $s$, $d$ | standing sheath voltage; trefoil spacing; sheath diameter | V; mm; mm | 24 |
| $f$, $w$, $L$, $H$ | sag; conductor weight; span; horizontal tension | m; N/m; m; N | 24 |

- In chapter 24, $k$ is the adiabatic constant (not an index), $\theta$ is a temperature in the
  rating formulas and a bend angle in the capstan equation, $f$ is a sag (frequency is $F$ in code).

## Chapter 25 (transformers and substations)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $\hat{B}$, $A_\text{c}$, $N$ | peak flux density; core section; turns | T; m2; – | 25 |
| $P_0$, $I_0$ | no-load loss; no-load current | kW; % | 25 |
| $P_\text{k}$, $u_\text{k}$ | load loss at rated current; short-circuit impedance | kW; % | 25 |
| $r$, $x$, $g$, $b$ | series resistance and leakage reactance; shunt conductance and susceptance | pu | 25 |
| $\varepsilon$, $u_r$, $u_x$ | regulation; resistive and reactive voltage at the load | % | 25 |
| $k$ | per-unit load (in efficiency and thermal formulas) | – | 25 |
| $A$, $B$ | capitalisation factors of no-load and load loss | k u/kW | 25 |
| $\theta_\text{h}$, $V$ | hot-spot temperature; relative ageing rate | C; – | 25 |
| $Z_{12}$, $Z_1$ | pairwise test impedance of a three-winding transformer; star branch | % | 25 |
| $\mathrm{DP}$, $c_\text{2FAL}$ | degree of polymerisation; 2-furaldehyde in oil | –; mg/kg | 25 |
| $\mathrm{HI}$, $w_k$, $s_k$ | health index; weight and score of factor $k$ | –; –; 1-4 | 25 |
| $r(t)$ | residual: measured minus modelled top oil | K | 25 |
| $\delta$, $z$ | relative air density; altitude above sea level | –; m | 25 |
| $\Delta\varphi$ | phase-angle error of a measuring chain | rad | 25 |
| $\alpha$ | solar absorptivity of a surface | – | 25 |

- In chapter 25, $k$ is a per-unit load (not the adiabatic constant of chapter 24) and $b$ a
  susceptance; $A$ and $B$ are money factors, not areas or flux densities. $H$ is the hot-spot
  factor (altitude is $z$), and $\delta$ the relative air density (as in chapter 4), not a
  declination or a load angle.

## Chapter 26 (protection, grounding and lightning)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $I_0$, $I_1$, $I_2$ | zero-, positive- and negative-sequence currents | A | 26 |
| $Z_0$, $Z_1$, $Z_2$ | sequence impedances | ohm; pu | 26 |
| $I_\text{s}$, $\mathrm{TMS}$ | pickup current; time multiplier setting | A; – | 26 |
| $k$, $\alpha$ | constants of an inverse-time curve | s; – | 26 |
| $V_\text{k}$, $R_\text{ct}$, $R_\text{b}$ | CT knee-point voltage; CT winding and burden resistance | V; ohm | 26 |
| $V_\text{s}$, $R_\text{L}$ | stability voltage of a high-impedance differential; lead resistance | V; ohm | 26 |
| $\rho_\text{a}$, $a$ | apparent soil resistivity; Wenner probe spacing | ohm m; m | 26 |
| $N_\text{g}$ | ground flash density | 1/(km2 a) | 26 |
| $E_\text{inc}$, $d_\text{B}$ | incident energy of an arc; arc-flash boundary | cal/cm2; m | 26 |
| $\bar{A}$, $\lambda$, $T$ | unavailability; rate of hidden failures; test interval | –; 1/a; a | 26 |
| $T_\text{BF}$ | breaker-failure timer | s | 26 |

- In chapter 26, $k$ and $\alpha$ are curve constants (not a load or an absorptivity), $a$ is a
  probe spacing or an electrode radius as stated, and $\bar{A}$ is an unavailability; $U$ stays a
  voltage.

## Chapter 27 (power quality and plant behaviour)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $\text{TDD}$ | total demand distortion (harmonic current over the maximum demand current) | % | 27 |
| $P_\text{st}$, $P_\text{lt}$ | short-term (10 min) and long-term (2 h) flicker severity | – | 27 |
| $c$, $S_\text{n}$ | flicker coefficient of a turbine; its rated apparent power | –; MVA | 27 |
| $h_\text{t}$ | tuning order of a filter | – | 27 |
| $U_h$, $u_k$ | harmonic voltage of order $h$; short-circuit voltage of a supplying transformer | %; pu | 27 |
| $\Lambda$, $\hat{p}_1$, $\hat{p}_2$ | logarithmic decrement; two successive peaks of a power oscillation | –; MW | 27 |
| $U_0$, $x$, $k$ | dip voltage without support; grid impedance on the plant's base; reactive-current gain | pu; pu; – | 27 |
| $\Delta\varphi$ | angle error of a measurement chain | rad | 27 |

- In chapter 27, $\alpha$ is the harmonic summation exponent (as in chapter 7), $a$ the operator
  $1\angle 120^\circ$, $S_\text{sc}$ the short-circuit power and $h_\text{r}$ the resonance order
  (chapter 7), $\zeta$ a damping ratio; $U_0$ there is a dip voltage, not a Faiman coefficient.

## Chapter 28 (grid studies and performance requirements)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $\mathbf{Y}$, $Y_{kj}$ | bus admittance matrix and its elements | pu | 28 |
| $S_k$, $P_k$, $Q_k$ | complex, active and reactive power injected at bus $k$ | pu; MW, Mvar | 28 |
| $z_\text{th}$, $R_\text{th}$, $X_\text{th}$, $S_\text{b}$ | Thevenin impedance of the grid at the POC and its parts; base power | pu, ohm; MVA | 28 |
| $c$ | voltage factor of the equivalent-source fault calculation | – | 28 |
| $Z_1$, $Z_2$, $Z_0$ | positive-, negative- and zero-sequence impedance at a fault | pu | 28 |
| $\kappa$, $i_\text{p}$ | peak factor; peak (first-cycle) fault current | –; kA | 28 |
| $Z_\text{app}$, $R_\text{f}$ | impedance a distance relay sees; fault resistance | ohm | 28 |
| $H$, $D$, $S_\text{sys}$ | inertia constant, load damping, size of an aggregated system | s; –; MW | 28 |
| $Q_\text{f}$ | quality factor of a parallel RLC load (islanding) | – | 28 |
| $\mathrm{ESCR}$, $\mathrm{WSCR}$ | effective and weighted short-circuit ratios | – | 28 |
| $k_2$ | negative-sequence current gain | – | 28 |

- In chapter 28, $c$ is the voltage factor (not a flicker coefficient as in chapter 27), $H$ an
  inertia constant, $D$ load damping (% of load per % of frequency), $k$ the reactive-current gain
  of a dip (as in chapter 27) and $x$ a grid impedance on the plant's base; $\delta$ is not used.

## Chapter 29 (site investigation and civil works)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $w$, $\ell$, $\ell_i$, $a_\text{l}$, $\delta_i$ | levelling misclosure; loop and leg length; class constant; leg correction | mm; km; mm | 29 |
| $\text{GSD}$, $p_\text{x}$, $H_\text{f}$, $f$ | ground sample distance; pixel size; flight height; focal length | cm; µm; m; mm | 29 |
| $x_c$, $v_1$, $v_2$, $h$ | crossover distance; layer velocities; refractor depth | m; m/s; m | 29 |
| $w_i$, $d_i$, $\alpha$ | inverse-distance weights, distances, power | –; m; – | 29 |
| $P_\text{f}$, $r_\text{l}$, $R_\text{f}$ | chance of finding a lens; lens and footprint radius | –; m | 29 |
| $LL$, $PI$, $PI_A$ | liquid limit, plasticity index, A-line value | % | 29 |
| $N$, $N_{60}$, $\varphi$ | SPT blow count, at 60 % energy; friction angle | –; ° | 29 |
| $N_c$, $N_q$, $N_\gamma$, $q_\text{ult}$ | bearing capacity factors; ultimate bearing pressure | –; kPa | 29 |
| $s$, $E$, $\nu$, $I$ | settlement; soil modulus; Poisson ratio; shape factor | m; kPa; –; – | 29 |
| $U$, $\gamma_w$, $h_\text{w}$ | uplift; unit weight of water; submerged depth | kN; kN/m³; m | 29 |
| $\Delta b$, $R$, $L$ | curve widening; inner radius; rigid length | m | 29 |
| $M(s)$, $V_\text{cut}$, $V_\text{fill}$ | mass-haul ordinate; cut and fill volumes | m³ | 29 |
| $n_\text{E}$, $P_a$ | equivalent standard axles; axle load | –; kN | 29 |
| $p(z)$, $F$, $a$, $b$ | pressure at depth by 2:1 spread; load; pad sides | kPa; kN; m | 29 |
| $Q$, $C$, $i$, $A$, $t_\text{c}$, $L_\text{c}$, $S$ | rational peak flow; runoff coefficient; intensity; area; time of concentration; flow length; slope | m³/s; –; mm/h; km²; min; m; – | 29 |
| $n$, $A_\text{w}$, $P_\text{w}$, $R_\text{h}$ | Manning roughness; flow area; wetted perimeter; hydraulic radius | –; m²; m; m | 29 |
| $Q_1$, $C_\text{d}$, $A_\text{p}$, $D_\text{p}$, $H_\text{w}$ | flow a pipe; discharge coefficient; pipe area and diameter; headwater | m³/s; –; m²; m; m | 29 |
| $D_{50}$, $C_\text{I}$, $s_\text{g}$, $h_\text{d}$ | rock size; Isbash coefficient; specific gravity; check-dam height | m; –; –; m | 29 |
| $E_\text{s}$, $R_\text{e}$, $K_\text{e}$, $LS$, $C_\text{e}$, $P_\text{e}$ | USLE soil loss and its factors | t/ha/yr | 29 |
| $q'$, $k$, $h_1$, $h_2$, $R_\text{i}$ | trench inflow per metre; permeability; heads; radius of influence | m³/s/m; m/s; m; m | 29 |
| $\bar x$, $k$, $x_\text{min}$, $x_\text{abs}$ | lot mean; acceptance constant; limit; absolute floor | as $x$ | 29 |
| $E_\text{v}$, $r_\text{p}$ | plate-load modulus; plate radius | MPa; m | 29 |
| $f_\text{ck}$, $\bar f$ | characteristic and mean strength | MPa | 29 |
| $T$, $W$ (subscripts a, c, w, wa, i) | ingredient temperatures and masses of fresh concrete | °C; kg/m³ | 29 |
| $\Delta T_\text{ad}$, $m_\text{b}$, $H_\text{b}$ | adiabatic temperature rise; binder content; heat of hydration | K; kg/m³; kJ/kg | 29 |
| $P_n$ | chance of at least one $T$-year event in $n$ years | – | 29 |
| $V_\text{fw}$, $q_j$, $t_j$ | firewater volume; rate and duration of case $j$ | m³; L/min; min | 29 |
| $s_\text{w}$, $T_\text{aq}$, $S_\text{aq}$ | drawdown; transmissivity; storativity | m; m²/s; – | 29 |
| $V_m$, $I_m$, $D_m$, $V_\text{tank}$ | usable stock, inflow and demand in month $m$; tank volume | m³ | 29 |
| $r_\text{RO}$, $c_\text{feed}$, $c_\text{brine}$ | RO recovery; feed and brine concentration | –; mg/L | 29 |
| $n_\text{truck}$, $q_\text{pour}$, $t_\text{cycle}$, $V_\text{truck}$ | trucks; pour rate; cycle time; truck volume | –; m³/h; h; m³ | 29 |
| $P_\text{acc}(p)$, $n$, $c$ | acceptance probability; sample size; acceptance number | – | 29 |

- In chapter 29, $T$ is a return period (as in chapter 3) except inside the fresh-concrete balance,
  where $T$ with a subscript is an ingredient temperature; transmissivity is $T_\text{aq}$. $s$ is a
  settlement in the bearing lesson and a standard deviation in the acceptance rules; $n$ is Manning's
  roughness in hydraulics and a sample size in sampling; $c$ is cohesion in bearing and an acceptance
  number in sampling; $w$ is the levelling misclosure and $w_i$ an interpolation weight.

## Chapter 30 (structures, turbine foundations and mechanical loads)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $v(z)$, $v_\text{ref}$, $z_\text{ref}$, $\alpha$ | wind speed at height; reference speed and height; power-law exponent | m/s; m; – | 30 |
| $q$, $C_\text{d}$, $A$, $F$ | dynamic pressure; drag coefficient; area; force | Pa; –; m²; N | 30 |
| $v_\text{cr}$, $St$, $f$, $D$ | vortex lock-in speed; Strouhal number; frequency; diameter | m/s; –; Hz; m | 30 |
| $V$, $S_a(T)$, $a_g$, $T_c$, $q_\text{b}$ | base shear; spectral acceleration; ground acceleration; corner period; behaviour factor | N; g; g; s; – | 30 |
| $\sigma_\text{el}$, $\kappa$, $\sigma_\text{R}$, $f_y$ | elastic buckling stress; knock-down factor; Rankine strength; yield strength | MPa; –; MPa; MPa | 30 |
| $N$, $\Delta\sigma$, $\Delta\sigma_C$, $\Delta\sigma_D$ | cycles to failure; stress range; detail category; knee stress | –; MPa | 30 |
| $\Delta M_\text{eq}$, $n_i$, $m$, $N_\text{eq}$ | damage-equivalent moment; counted cycles; S-N slope; reference cycles | MN m; –; –; – | 30 |
| $K_\theta$, $G$, $\nu$, $f_\theta$ | rocking stiffness; shear modulus; Poisson ratio; rocking frequency | N m/rad; Pa; –; Hz | 30 |
| $e$, $A'$, $q'$ | eccentricity; effective area; pressure on it | m; m²; kPa | 30 |
| $F_\text{up}$, $p$, $f_\text{s}$, $H_\text{u}$, $K_\text{p}$ | pile uplift; perimeter; skin friction; lateral capacity; passive coefficient | kN; m; kPa; kN; – | 30 |
| $F_\text{max}$, $n$, $V$ | worst anchor-bolt pull; number of bolts; vertical load | kN; –; MN | 30 |
| $A_\text{s}$, $f_\text{yd}$, $z$ | reinforcement area; design yield; lever arm | mm²; MPa; m | 30 |
| $Q$, $\eta$, $U$, $I$, $v_\text{w}$ | welding heat input; efficiency; voltage; current; travel speed | kJ/mm; –; V; A; mm/s | 30 |
| $F_\text{t}$, $T$, $\theta$ | transverse pull at an angle point; wire tension; deviation | kN; kN; ° | 30 |
| $F'$, $i_\text{p}$, $a$ | short-circuit force per metre; peak current; spacing | N/m; kA; m | 30 |

- In chapter 30, $q$ is the dynamic pressure (as in chapter 4) and $q'$ a foundation pressure; $T$ is
  a wire tension in the line lessons and a period in the seismic lesson; $V$ is a base shear in the
  seismic lesson and a vertical load in the foundation and anchor lessons; $e$ is an eccentricity
  (ch 4's symbol) and also the load height in Broms' formula, written there with the formula.

## Chapter 31 (transport, lifting and installation logistics)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $P_\text{axle}$, $m_\text{tr}$, $m_\text{pay}$, $\beta$, $n_\text{axle}$ | axle load; trailer and payload mass; tractor share; trailer axles | kN; t; –; – | 31 |
| $M$, $P$, $L$, $a$ | bridge mid-span moment; convoy load; span; axle-group length | kN m; kN; m; m | 31 |
| $u$, $C(r)$, $m_\text{load}$, $m_\text{rig}$ | lift utilisation; chart capacity at radius $r$; load and rigging mass | –; t | 31 |
| $t$, $t_\text{mob}$, $t_\text{acc}$, $d$, $v$ | response time; mobilisation; access time; distance; speed | min; km; km/h | 31 |

- In chapter 31, $P$ is a vehicle load (not a power) and $L$ a bridge span; $a$ is the length of an
  axle group; wind force on a suspended load uses chapter 30's $F = q\,C_\text{d}\,A$.

## Chapter 32 (occupational safety, fire protection and emergency response)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $R$, $L$, $S$ | risk score; likelihood level; severity level (teaching 1-5) | – | 32 |
| $\lambda$, $n$, $H$ | incident rate per 200,000 h; number of events; hours worked | 1/200,000 h; –; h | 32 |
| $h_\text{need}$, $\ell_\text{lan}$, $d_\text{dec}$, $d_\text{har}$, $d_\text{body}$, $d_\text{m}$ | clearance below an anchor; lanyard; deceleration; harness stretch; D-ring to feet; margin | m | 32 |
| $C/C_0$, $Q$, $V$, $t$ | purge fraction; fresh-air flow; space volume; time | –; m³/h; m³; h | 32 |
| $T_\text{wc}$, $v$ | wind-chill temperature; wind speed | °C; km/h | 32 |
| $d$, $t_\text{r}$, $\mu$ | stopping distance; reaction time; friction coefficient | m; s; – | 32 |
| $L_\text{EX,8h}$, $L_i$, $t_i$ | daily noise exposure; task level; task hours | dB(A); dB(A); h | 32 |
| $G$, $c$, $k$ | gas release rate; limiting fraction; mixing factor | m³/h; –; – | 32 |
| $q''$, $\chi$, $\dot Q$, $r$, $\dot m''$, $\Delta H_\text{c}$, $A$ | radiant flux; radiant fraction; heat release; distance; burning rate; heat of combustion; pool area | kW/m²; –; kW; m; kg/(m² s); MJ/kg; m² | 32 |
| $\dot V$ | firewater draw | L/min | 32 |
| $f_0$, $f_\text{event}$ | initiating and top-event frequency | 1/year | 32 |
| $\alpha$ (fire) | t-squared growth coefficient | kW/s² | 32 |
| $L_\text{W}$, $L_\text{p}$ | sound power level; sound pressure level at distance $r$ | dB(A) | 32 |
| $\text{PFD}$, $T$ | probability of failure on demand; proof-test interval | –; years | 32 |
| $U$, $R_\text{body}$, $I$ | touch voltage; body resistance; body current | V; Ω; A | 32 |
| $A(8)$, $a_i$, $t_i$ | daily hand-arm vibration exposure; task vibration; task hours | m/s²; m/s²; h | 32 |
| $\dot m$, $\dot Q_\text{c}$, $z$ | plume mass flow; convective heat release; height above the fire | kg/s; kW; m | 32 |
| $I$ (fire), $H$, $w$, $r$, $L$ | Byram intensity; heat of combustion; fuel load; spread rate; flame length | kW/m; kJ/kg; kg/m²; m/s; m | 32 |
| $d$ (radio), $h_1$, $h_2$ | line-of-sight range; antenna heights | km; m | 32 |
| $E_\text{a}$, $E_\text{a,0}$, $\lambda_i$, $f_i$, $C_i$, $O_i$, $c_j$, $N$ | expected annual loss; the same without measures; events of type $i$ a year; product of the measures' rate factors; direct cost; outage cost; yearly cost of measure $j$; net saving | k u/year; k u/year; 1/year; –; k u; k u; k u/year; k u/year | 32 |

- In chapter 32, $S$ is a severity level (not apparent power), $L$ a likelihood level (not a span),
  $\lambda$ an incident or failure rate (not a wavelength), and $T$ a test interval.
- Chapter 29 (lesson R) adds $x_\text{k,mean}$, $x_\text{k,local}$ (cautious estimates from $n$ tests
  with mean $\bar x$, standard deviation $s$, Student factor $t$) and the infinite-slope factors
  $F_\text{dry}$, $F_\text{seep}$ with slope angle $\beta$ and unit weights $\gamma_\text{sat}$, $\gamma_\text{w}$.

## Chapter 33 (environmental and social management)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $L_\text{W}$, $L_\text{p}$, $r$, $\alpha$ (sound), $L_\text{sum}$ | sound power level; sound pressure level at distance $r$; air absorption; energy sum of levels | dB(A); dB(A); m; dB/m; dB(A) | 33 |
| $N$, $n_\text{pass}$, $p_\text{c}$, $p_\text{av}$ | collisions a year; rotor-zone passages; collision chance per passage; avoidance share | 1/yr; 1/yr; –; – | 33 |
| $\Delta L$, $Q_\text{l}$, $Q_\text{h}$, $w$ | change in road-traffic noise; light and heavy vehicles a day; heavy-vehicle weighting | dB; 1/day; 1/day; – | 33 |
| $r$ (carcass), $\bar t$, $I$, $s$, $a$, $n_\text{found}$, $\hat N$ | persistence share; mean carcass persistence; search interval; searcher efficiency; share of area searched; carcasses found; estimated fatalities | –; days; days; –; –; –; 1/yr | 33 |
| $L_\text{tot}$, $L_\text{bg}$, $L_\text{t}$ | measured total; background; turbines alone | dB(A) | 33 |
| $s$, $Q$, $T$, $S$, $t$, $r$ | drawdown (Cooper-Jacob, as ch 29); pumping rate; transmissivity; storativity; time; distance | m; m³/s; m²/s; –; s; m | 33 |
| $EC_0$, $EC_\text{trig}$, $k$ | electrical conductivity at the start; trigger; yearly growth rate | µS/cm; µS/cm; 1/yr | 33 |
| $e_\text{kWh}$, $a_i$, $f_i$, $M_\text{op}$, $E_\text{POC}$ | lifecycle footprint per kWh; amount of item $i$; its emission factor; operating emissions; yearly energy at the POC | g CO₂e/kWh; various; kg CO₂e per unit; t CO₂e; kWh | 33 |
| $\mathrm{CoV}$, $w_i$ | coefficient of variation; item share of the footprint | – | 33 |
| $PV$, $A$, $i$, $n$ | present value; yearly amount; discount rate; years | k u; k u/yr; 1/yr; yr | 33 |

- In chapter 33, $s$ is both the drawdown (lesson F, as in ch 29) and the searcher efficiency (lesson C,
  carcass search); $r$ is a distance except in the carcass estimator, where it is the persistence share;
  $w$ is the heavy-vehicle weighting and $w_i$ an item's share of the footprint; $a_i$ is an amount (the
  avoidance share is $p_\text{av}$); $k$ is a yearly growth rate. $\alpha$ (sound) is air absorption,
  unlike $\alpha$ (fire) of chapter 32.


## Chapter 34 (instrumentation and control)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $I$, $x$, $x_\text{lo}$, $x_\text{hi}$ | loop current; engineering value; range ends | mA; as measured | 34 |
| $\ell_\text{max}$, $V_\text{s}$, $V_\text{tx}$, $I_\text{max}$, $R_\text{rx}$, $\rho$, $A$ | longest loop (one way); supply voltage; transmitter minimum; top loop current; receiver resistance; copper resistivity; conductor area | m; V; V; A; Ω; Ω mm²/m; mm² | 34 |
| $u_i$, $u_\text{c}$, $U$, $k$ | standard uncertainty of a link; combined; expanded; coverage factor | % | 34 |
| $R(t)$, $R_0$, $A$, $B$ | platinum sensor resistance; at 0 °C; Callendar-Van Dusen coefficients | Ω; Ω; 1/K; 1/K² | 34 |
| $t_\text{max}$, $t_\text{in}$, $t_\text{scan}$, $t_\text{out}$, $t_\text{net}$ | worst-case response; input filter; scan time; output update; network delay | ms | 34 |
| $u_k$, $e_k$, $\Delta t$, $K_\text{p}$, $K_\text{i}$ | controller output and error at cycle $k$; controller cycle; PI gains (as ch 20) | –; s; –; 1/s | 34 |
| $N_\text{false}$, $p$, $n$, $N_\text{s}$ | false watchdog timeouts a year; share of lost beats; beats in a row; seconds in a year | 1/yr; –; –; s | 34 |
| $A$, $A_2$, $\beta$, MTBF, MTTR | availability of one unit; of a redundant pair; common-cause share; mean time between failures; to repair | –; –; –; h; h | 34 |
| $\Delta T$, $P$, $A_\text{s}$, $k$, $\dot V$ | cabinet temperature rise; losses; free surface; heat-transfer coefficient; fan air flow | K; W; m²; W/(m² K); m³/h | 34 |
| $D(t)$, $N$, $b$ | defects found by day $t$; total defects; finding rate | –; –; 1/day | 34 |
| $t_\text{a}$, $C$, $\eta_\text{u}$, $\Delta V$ | battery autonomy; capacity; usable share; DC feeder drop | h; Ah; –; V | 34 |
| $\varepsilon_\text{s}$, $\varepsilon_\text{r}$ | accuracy as a share of span; error as a share of the reading | % | 34 |
| $E_\text{sh}$, $P_\text{sh}$, $r$ | self-heating coefficient; power in the sensor; rate of temperature rise | K/mW; mW; K/s | 34 |
| $L(j\omega)$, $\omega_\text{c}$, $\varphi_\text{m}$, $d$ | open-loop frequency response; gain-crossover frequency; phase margin; total loop delay | –; rad/s; degree; s | 34 |
| $w$, $t_\text{scan}$ | pulse width; scan time | ms | 34 |
| $t_\text{h}$, $C_\text{b}$, $V_1$, $V_2$, $P_\text{in}$ | hold-up time; bulk capacitance; capacitor voltage at the loss of input; at which the supply stops; input power | ms; µF; V; V; W | 34 |
| $\delta f$, $\delta V$, $\Delta P_\text{e}$, $\Delta Q_\text{e}$ | frequency and voltage measurement errors; resulting active and reactive power errors (with $s_\text{d}$, $s_\text{q}$ of ch 20) | mHz; %; MW; Mvar | 34 |

- In chapter 34, $A$ is a conductor area in the loop formula, a Callendar-Van Dusen coefficient in
  the Pt100 formula and an availability in the redundancy formula; each formula states which. $k$ is
  a coverage factor in the uncertainty formula and a heat-transfer coefficient in the cabinet formula.
  $I$ is a loop current (mA) in lesson A and a battery current (A) in lesson E.
- $\varphi_\text{m}$ is the phase margin, not the power-factor angle $\varphi$ of the phase-error
  formula; $d$ is a loop delay in lesson B. The open loop is written with $j\omega$, so $s$ keeps
  its chapter 20 meaning of a droop slope.

## Chapter 35 (SCADA and communications)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $t_\text{s}$, $N_\text{b}$, $R_\text{b}$, $n_\text{m}$, $U_\text{L}$ | time to send one frame; message size; bit rate; messages a second; link utilisation | ms; byte; bit/s; 1/s; – | 35 |
| $T_\text{poll}$, $N_\text{d}$, $N_\text{q}$, $N_\text{r}$, $t_\text{ta}$ | polling cycle; devices on the line; request and reply size; turnaround in each device | s; –; byte; byte; ms | 35 |
| $L_\text{opt}$, $\alpha_\text{f}$, $\ell$, $n_\text{sp}$, $a_\text{sp}$, $n_\text{c}$, $a_\text{c}$, $M$, $P_\text{opt}$ | optical loss; fibre attenuation; length; splices and loss each; connectors and loss each; margin; budget of the optics | dB; dB/km; km; –; dB; –; dB; dB; dB | 35 |
| $A_\ell$, $A_\text{chain}$, $A_\text{ring}$, $k$, $k_1$, $k_2$ | availability of one link; of a device on a chain or ring; links in series; links on the two ways round | –; –; –; – | 35 |
| $\varepsilon_\text{t}$, $\varepsilon_i$ | worst-case time error; contribution of link $i$ of the time chain | µs | 35 |
| $S$, $N_\text{tag}$, $T$, $\Delta t$, $b$ | storage; tags; period kept; sampling interval; bytes a value | byte; –; s; s; byte | 35 |
| $W$, $\rho$ | mean wait in a switch port; port load | ms; – | 35 |
| $N_\text{false}$, $T_\text{hb}$, $m$, $p$ | false 'link lost' alarms a year; heartbeat period; heartbeats missed in a row; chance one message is lost | –; s; –; – | 35 |
| $P_\text{rev}$, $\Phi$, $\sigma$ | chance two events are logged in reversed order; standard normal distribution function (in that formula only); standard error of one clock | –; –; ms | 35 |

- In chapter 35, $t_\text{s}$ is the time to send one frame (as in the queue formula), not a sampling time;
  $\rho$ is a port load (not a resistivity or a density); $M$ is a margin in dB; $k$ counts links.

## Chapter 36 (IT and industrial cybersecurity)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $R$, $L$, $C$ | teaching risk score; likelihood; consequence | –; 1-5; 1-5 | 36 |
| $H$, $n$, $A$ | bits of a random secret; its length; size of its alphabet | bit; –; – | 36 |
| $\bar{t}_\text{p}$, $t_\text{p,max}$, $t_\text{test}$, $T_\text{w}$ | mean and worst days from a maker's fix to installation; test time; interval of outage windows | day | 36 |

- In chapter 36, $L$ and $C$ are the likelihood and consequence of the risk scale (not an inductance or
  a capacitance) and $A$ is the size of an alphabet (not an area or an availability).

## Chapter 37 (performance monitoring and analytics)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $Y_\text{r}$, $\text{PR}_{25}$, $\bar{T}_\text{c}$ | reference yield; PR corrected to 25 °C; irradiance-weighted mean cell temperature | h; –; °C | 37 |
| $A_\text{t}$, $A_\text{E}$, $A_\text{s}$ | time-based, production-based and service availability | – | 37 |
| $T_\text{up}$, $T_\text{p}$, $T_\text{ex}$, $T_\text{call}$, $T_\text{fail}$ | up time; period; excluded time; hours a service was called; hours it failed | h | 37 |
| $E_\text{act}$, $E_\text{lost}$, $E_\text{ex}$ | actual energy; lost energy charged; lost energy excluded by agreement | MWh | 37 |
| $r_d$, $S_d$, $\kappa$, $h_\text{s}$ | daily residual (actual/model − 1); CUSUM sum; allowance; decision threshold | – | 37 |
| $z_\text{r}$, $\tilde{y}$, MAD | robust z-score; median; median absolute deviation | –; as $y$; as $y$ | 37 |
| $\hat{\lambda}$, $n_\text{f}$, $T_\text{exp}$ | failure-rate estimate; number of failures; exposure (operating hours) | 1/h; –; h | 37 |
| $k$, $c$, $F(t)$ | Weibull shape and scale (as chapter 3); share failed by age $t$ | –; h; – | 37 |
| $\beta_\text{g}$ | Crow-AMSAA reliability-growth slope | – | 37 |
| $u_\text{PR}$, $z_d$, $\lambda_\text{e}$, $\sigma_z$ | relative standard uncertainty of PR; EWMA of the residual; its weight; its standard deviation | %; –; –; – | 37 |
| SS, POD, FAR | skill score against a reference; probability of detection; false-alarm ratio | – | 37 |
| $t_{90}$, $t_\text{s}$, $t_\text{d}$, $\epsilon_\text{rms}$ | time to 90 % of a step; settling time; delay; RMS tracking error after settling | s; s; s; MW | 37 |

- In chapter 37, $\lambda$ is a failure rate (as in the Markov sections of chapter 3), $k$ and $c$ are the
  Weibull shape and scale of failure ages (not wind speeds), and the CUSUM allowance is $\kappa$ so that
  $k$ keeps its Weibull meaning; the program output prints the allowance as `k`.

## Chapter 38 (detailed design and document control)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| PV, EV, AC, BAC, EAC | planned value; earned value; actual cost; budget at completion; estimate at completion (engineering hours) | h | 38 |
| SPI, CPI | schedule performance index EV/PV; cost performance index EV/AC | – | 38 |
| $P_\text{find}$, $N$, $k$, $n$ | chance a sample check finds at least one error; documents; errors among them; documents checked | –; –; –; – | 38 |
| $I_\text{LV}$ | current on the low-voltage side of a skid | A | 38 |
| $L$, $\lambda$, $W$ | documents waiting; documents arriving a week; weeks in the queue (Little's law) | –; 1/week; week | 38 |
| $p_\text{C}$, $N_\text{s}$ | chance a review returns code C; submissions until accepted | –; – | 38 |
| TCPI | to-complete performance index (BAC − EV)/(BAC − AC) | – | 38 |

- In chapter 38, $\lambda$ is an arrival rate of documents (not a failure rate) and $L$ a queue
  length (not a likelihood level); $k$ counts errors in a set of documents (not a Weibull shape) and $N$, $n$ are counts of
  documents; PV is planned value (not photovoltaic) only inside the earned-value formulas.

## Chapter 39 (procurement, contracts and supplier evaluation)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $P_\text{chain}$, $P_i$ | chance a supply chain is on time; chance of supplier $i$ | – | 39 |
| $D$, $w$, $r$, $P$, $c$ | delay damages; weeks late; rate a week; contract price; cap as a share of the price | k u; –; 1/week; k u; – | 39 |
| $P_\text{eval}$, $\Delta_\text{dev}$, $w_\text{late}$, $f_\text{fx}$, $a_\text{fx}$ | evaluated price; priced deviations; weeks late against need; foreign share; currency allowance | k u; k u; –; –; – | 39 |
| $A_\text{block}$, $A_\text{t}$, $A_i$ | availability of a block of parts in series; its target; share of part $i$ | – | 39 |
| $x_k$, $r_k$, $u$ | part of a footprint; its relative uncertainty; combined uncertainty (root-sum-square) | t CO₂e; –; t CO₂e | 39 |
| $\mu$, $n$, $\lambda$, $T$, $N$, $k$ | expected failures; units; failure rate of a unit; window; failures counted; their bound (Poisson) | –; –; 1/year; year; –; – | 39 |
| $N$, $k$, $n$ (witness) | units; faulty units among them; tests witnessed | – | 39 |
| $p$, $c$ (audit), $n$ | share of sites with a problem; confidence wanted; sites to audit | –; –; – | 39 |

- In chapter 39, $P$ is a contract price (not a power) and $r$ a weekly rate; in lessons C and G
  $p$ is a share of sites and $c$ a confidence (the delay-damages cap keeps $c$ in lesson C's
  formula of damages), and in the Poisson law of lesson C $\lambda$ is a failure rate as in ch 37; $A$ and $B$ keep their
  chapter 25 meaning as loss-capitalisation factors, while $A_\text{block}$, $A_\text{t}$, $A_i$ are availabilities.

## Chapter 40 (manufacturing systems, quality engineering and factory tests)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $Y_\text{RT}$, $y_i$ | rolled throughput yield; first-pass yield of step $i$ | – | 40 |
| $T_\text{takt}$, $H_\text{avail}$, $D$ (demand), $\eta_\text{bal}$, $t_j$, $m$ | takt time; hours available; units demanded; line-balance efficiency; load of station $j$; stations | h; h; –; –; h; – | 40 |
| TUR, $T$ (tolerance), $U_{95}$ | test uncertainty ratio; tolerance band; expanded uncertainty | –; as measured | 40 |
| RPN, $S$, $O$, $D$ (detection), $C$ | risk priority number; severity, occurrence and detection ratings 1-10; criticality $S \times O$ | – | 40 |
| $\%\text{GRR}$, $\sigma^2_\text{rep}$, $\sigma^2_\text{repro}$, $\sigma^2_\text{part}$ | share of the measurement system; repeatability, reproducibility and part variances | %; unit² | 40 |
| $C_\text{p}$, $C_\text{pk}$, USL, LSL, $\bar x$, $s$ | process capability indices; specification limits; mean; standard deviation | –; as measured | 40 |
| $A_2$, $D_4$, $d_2$, $d_3$, $\bar R$, $\bar{\bar x}$ | Shewhart constants; mean and sd of the range of $n$ normal values; mean range; grand mean | –; as measured | 40 |
| $P_\text{a}(p)$, $n$, $c$ | chance a lot with defective share $p$ is accepted; sample size; acceptance number | – | 40 |
| $N(t)$, $\lambda$, $\beta$, $t_i$, $T$ (test), MTBF | cumulative failures; power-law scale and growth slope; failure times; test end; mean time between failures | –; –; –; h; h; h | 40 |
| $P_\text{esc}$, $d_i$ | share of defects leaving the factory; detection share of stage $i$ | – | 40 |
| $\kappa$, $p_o$, $p_e$ | Cohen's kappa; observed agreement; agreement expected by chance | – | 40 |
| $\bar p$, $n_i$, $\text{UCL}_i$ | mean defective share; tests in period $i$; its upper control limit | – | 40 |
| AOQ, $N$ (lot) | average outgoing quality of rectifying inspection; lot size | –; – | 40 |
| $\text{MTBF}_\text{lower}$, $r$, $\chi^2_{1-\alpha;\nu}$ | lower confidence bound of MTBF; failures; chi-square quantile | h; –; – | 40 |
| OEE | overall equipment effectiveness (availability x performance x quality) | – | 40 |
| $k$ (variables plan), $k_1$, $k_2$, $p^{*}$ | acceptance constant; cost to inspect one unit; cost of one escape; break-even defective share | –; k u; k u; – | 40 |
| $\text{MS}_\text{b}$, $\text{MS}_\text{w}$, $\sigma^2_\text{b}$, $\sigma^2_\text{w}$, $g$ | mean squares and variance components between and within groups; number of groups | unit²; – | 40 |
| $P_\text{f}$, $\mu_L$, $\sigma_L$, $\mu_S$, $\sigma_S$ | chance of failure; mean and sd of load and of strength | –; kN | 40 |

- In chapter 40, $D$ is the number of units demanded in the takt formula and the detection rating in the
  FMEA; $T$ is a tolerance band in the TUR and the test end time in the growth model; $S$ is a severity
  rating (as in ch 32), not apparent power; $\beta$ is the growth slope (as in ch 37), and $C$ is
  criticality, not a cost. In the stress-strength lesson $L$ and $S$ (as subscripts) are load and strength,
  not the severity rating.

## Chapter 41 (PV cells and module manufacturing engineering)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $n_i$, $n$, $p$, $N_A$, $N_D$, $\mu_n$, $\mu_p$, $\rho$ | intrinsic carrier density; electron and hole densities; acceptor and donor densities; mobilities; resistivity | cm$^{-3}$; cm$^2$/(V s); $\Omega$ cm | 41 |
| $V_\text{bi}$, $w_\text{d}$, $\varepsilon_\text{Si}$ | built-in voltage; depletion width; permittivity of silicon | V; µm; F/cm | 41 |
| $\tau$, $\tau_\text{b}$, $\tau_\text{eff}$, $D$, $L$ | carrier lifetime; bulk and effective lifetime; diffusion coefficient; diffusion length | s; cm$^2$/s; µm | 41 |
| $S$, $W$, $G$, $\Delta n$, $C_p$, $C_a$ | surface recombination velocity; wafer thickness; carriers generated per area and time; excess density; Auger coefficients | cm/s; cm; cm$^{-2}$ s$^{-1}$; cm$^{-3}$; cm$^6$/s | 41 |
| $iV_\text{oc}$, $J_0$, $J_\text{sc}$, $J_\text{mp}$, $E_{g0}$, $\gamma$ | implied open-circuit voltage; saturation, short-circuit and MPP current densities; band gap at 0 K; temperature exponent | V; A/cm$^2$; eV; – | 41 |
| $w_\text{f}$, $s$, $\rho_\square$, $b$, $r_\text{line}$ | finger width; finger spacing; sheet resistance; finger length; line resistance | cm; cm; $\Omega$/sq; cm; $\Omega$/cm | 41 |
| $\sigma$, $v_\text{th}$, $N_t$ | capture cross-section; thermal velocity; trap density | cm$^2$; cm/s; cm$^{-3}$ | 41 |
| $k_\text{s}$, $f$, $C_s$, $C_0$ | segregation coefficient; share solidified; dopant in the solid and in the starting melt | –; –; cm$^{-3}$ | 41 |
| $n_0$, $n_1$, $n_\text{Si}$, $d$, $\lambda_0$, $R_\square$ | refractive indices (medium, coating, silicon); coating thickness; design wavelength; sheet resistance by four-point probe | –; nm; nm; $\Omega$/sq | 41 |
| AF, $E_a$, RH, $n_\text{c}$, $L_\text{m}$, $a$, $w$ | acceleration factor; activation energy; relative humidity; cycling exponent; module length; support distance; load per length | –; eV; %; –; m; m; N/m | 41 |
| $z_i$, $\tilde x$, MAD, $A$, $r$, $\beta$ | robust z-score; median; median absolute deviation; loop area; distance to a strike; chance of missing (sample size) | –; W; W; m$^2$; m; – | 41 |
| $A(\lambda)$, $\delta_\text{min}$, $u_\text{sys}$, $u_\text{rand}$, $z_{1-\alpha}$, $\Delta I$, $V_1$, $V_2$ | absorbed share at a wavelength; smallest shortfall a sample shows; systematic and random standard uncertainty; normal quantile; current shift between two curves; voltages on the two curves | –; %; %; –; A; V | 41 |
| $\rho_c$, $r_c$, $N_s$ | specific contact resistivity; contact part of the series resistance; cells in series | $\Omega$ cm$^2$; $\Omega$ cm$^2$; – | 41 |

- In chapter 41, $k$ is Boltzmann's constant (as in $kT/q$), so the segregation coefficient is $k_\text{s}$;
  $W$ is the wafer thickness and the depletion width is $w_\text{d}$; $L$ is the diffusion length and the
  module length is $L_\text{m}$; $n$ is the electron density and the cycling exponent is $n_\text{c}$;
  $S$ is the surface recombination velocity (ch 40's severity rating does not appear); $\rho_\square$ and
  $R_\square$ are the same quantity, the second as read by the four-point probe.

## Chapter 42 (wind-turbine component design and manufacturing)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $F_\text{max}$, $M$, $n$, $D$, $\phi$ | largest bolt pull; root bending moment; bolts on the circle; bolt-circle diameter; joint factor | N; N m; –; m; – | 42 |
| $V_f$, $w_f$, $\rho_f$, $\rho_m$, $E_1$, $E_f$, $E_m$, $v_\text{void}$, $\rho_\text{th}$ | fibre volume and mass fractions; fibre and resin densities; modulus along the fibres; fibre and resin moduli; void share; void-free density | –; –; g/cm$^3$; GPa; –; g/cm$^3$ | 42 |
| $\alpha$ (cure), $H_\text{res}$, $H_\text{tot}$, $T_g$, $T_{g0}$, $T_{g\infty}$ | degree of cure; residual and total reaction heat; glass transition temperature, uncured and fully cured | –; J/g; °C | 42 |
| POD, $a$, $a_{50}$, $a_{90}$, $\beta$ (POD) | probability of detection; flaw size; sizes found half and nine times in ten; log-normal spread | –; mm; mm; – | 42 |
| $S_k$, $U$, $U_\text{per}$, $G$, $e$, $\omega$ | first mass moment of blade k; residual unbalance; permissible unbalance; balance grade; eccentricity; angular speed | t m; t m or g mm; g mm; mm/s; um; rad/s | 42 |
| $\Delta T$, $\delta$, $c$, $\alpha$ (expansion), $d$ | shrink temperature rise; interference; assembly clearance; expansion coefficient; diameter | K; m; m; 1/K; m | 42 |
| $P_\text{grid}$, $P_\text{test}$, $\eta$, $\beta$ (filter), $\dot Q$, $\dot m$, $c_p$ | grid power of a back-to-back test; test power; gearbox efficiency; filter ratio; heat flow; mass flow; specific heat | kW; kW; –; –; kW; kg/s; kJ/(kg K) | 42 |
| $L(T)$, $L_\text{ref}$, $T_\text{ref}$, $n_\text{cal}$, $k$, $M_\text{yaw}$, $\mu$, $F$, $r$ | insulation life at T; life at the reference temperature; calipers; margin; yaw moment; friction coefficient; clamp force; braking radius | years; °C; –; –; N m; –; N; m | 42 |

| $E(\theta)$, $G_{12}$, $\nu_{12}$, $E_2$ | ply modulus at angle; shear modulus; Poisson ratio; transverse modulus | GPa; GPa; –; GPa | 42 |
| $t$ (Darcy, Chvorinov), $\mu$ (viscosity), $\phi$ (porosity), $K$ (permeability), $\Delta P$, $L$ (flow), $B$, $V/A$ | fill or solidification time; resin viscosity; preform porosity; permeability; pressure difference; flow length; mould constant; casting modulus | s or min; Pa s; –; m$^2$; Pa; m; min/m$^2$; m | 42 |
| $N_\text{eq}$, $N_\text{test}$, $k$ (load factor), $m$ | equivalent and test cycles; test load factor; S-N slope | –; –; –; – | 42 |
| $P_0$, $P_k$, $\ell$, $P_r$, $\tau$, $b$, $\Delta$ | no-load and load losses; load share; rated power; time constant; settling band; final rise | kW; kW; –; kW; min; K; K | 42 |
| $a_c$, $K_{IC}$, $Y$, $\sigma$ | critical crack depth; fracture toughness; geometry factor; stress | mm; MPa m$^{1/2}$; –; MPa | 42 |

| $R_1$, $R_2$, $T_1$, $T_2$ | winding resistance cold and hot; their temperatures (copper constant 234.5) | $\Omega$; $^\circ$C | 42 |

| $f$, $f_0$, $\epsilon_{EI}$, $\epsilon_m$ | blade flap frequency and its nominal; relative stiffness and mass deviations | Hz; Hz; –; – | 42 |
| $F'$, $R'$, $E^*$, $b$ (contact), $p_\text{H}$, $\zeta$, $\tau$ | load per face width; equivalent radius; contact modulus; contact half width; peak contact pressure; depth over half width; shear | N/mm; mm; MPa; mm; MPa; –; MPa | 42 |
| $p_1$, $p_2$, $T_1$, $T_2$ (leak test) | absolute gas pressure and temperature at start and end | bar; K | 42 |
| $\delta_\text{s}$, $k_\text{b}$, $k_\text{c}$, $\Delta F_\text{V}$ | joint settling; bolt and clamped-part stiffness; preload lost | mm; kN/mm; kN/mm; kN | 42 |
| $x_\text{G}$, $y_\text{G}$, $F_i$, $x_i$, $y_i$; $a_1..a_3$, $x_c$, $y_c$, $r$ | centre of gravity from load cells; circle fit coefficients, centre and radius | m; t; m; –; mm | 42 |

| $K_\gamma$, $k$ (mesh), $\delta$ (pin), $F$ (mesh) | planet load sharing factor; mesh stiffness; pin position error; mesh force | –; N/m; µm; N | 42 |
| $e_x$, $e_y$, $g_k$, $\theta_k$, $N$ (readings) | rotor offset in the air gap; gap reading at angle; number of readings | mm; mm; rad; – | 42 |

- In chapter 42, $\alpha$ is the degree of cure in the cure lesson and the expansion coefficient in
  the shrink fit; $\beta$ is the POD spread in the inspection lesson and the filter ratio in the oil
  lesson; $n$ counts bolts on a circle; $k$ is a safety margin (not Boltzmann or segregation, ch 41);
  $G$ is a balance grade (not a shear modulus; $G_{12}$ is the ply's); $\phi$ is the joint factor in the
  root joint and the porosity in Darcy's law; $\mu$ is the friction coefficient of the brakes and
  the resin viscosity in the infusion lesson; $t$ is a time in both Darcy and Chvorinov.
  $b$ is the contact half width in the Hertz lesson and the settling band of the oil lesson;
  $T_1$, $T_2$ are winding temperatures in the resistance lesson (Celsius) and gas temperatures
  in the leak test (kelvin).

## Chapter 43 (power-transformer design and factory manufacture)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $e_\text{t}$, $k_\text{st}$, $k_\text{f}$, $D_\text{c}$ | volts per turn; stacking factor; fill factor of the stepped core; core circle diameter | V; –; –; m | 43 |
| $y_k$, $n$ | half-height of step $k$ on a unit circle; number of steps | –; – | 43 |
| $a_1$, $a_2$, $a_{12}$, $h$, $D_\text{m}$, $K_\text{R}$ | radial builds of the windings; main gap; winding height; mean gap diameter; Rogowski factor | m; m; m; m; – | 43 |
| $k_\text{e}$, $k_\text{s}$ | eddy and stray loss as shares of the I2R loss | – | 43 |
| $E_\text{o}$, $E_\text{p}$, $d_\text{o}$, $d_\text{p}$, $\varepsilon_\text{o}$, $\varepsilon_\text{p}$ | field, thickness and permittivity of oil and pressboard | kV/mm; mm; – | 43 |
| $F_\text{r}$, $\sigma_\text{h}$, $\sigma_\text{cr}$, $t$, $s$, $a$ | radial short-circuit force; hoop stress; buckling stress; conductor thickness; stick span; conductor area a turn | N; MPa; MPa; m; m; mm$^2$ | 43 |
| $m_\text{c}$, $p_\text{Fe}$, $k_\text{b}$ | core mass; loss per kg at the working flux; building factor | kg; W/kg; – | 43 |
| $c_\text{Cu}$, $J^*$ | copper price; current density of least evaluated cost | u/kg; A/mm$^2$ | 43 |
| $\overline{B^2}$, $\hat{B}_\text{g}$ | mean square leakage field in a winding; peak field in the main gap | T$^2$; T | 43 |
| $H$, $l_\text{Fe}$, $g$ | field strength in the steel; steel path; effective joint gap | A/m; m; m | 43 |
| $S_\text{w}$, $w$, RS | water solubility in oil; water measured; relative saturation | ppm; ppm; – | 43 |
| $P_\text{m}$, $U'$, $U$, $d$ | measured no-load loss; mean-value and rms voltmeter readings; waveform correction | kW; V; V; – | 43 |
| $\tau$, $a$, $b$ (cooling) | time constant and coefficients of the cooling-curve fit | min; ohm; ohm | 43 |
| $L_{WA}$, $\overline{L_{pA}}$, $S$ | sound power; mean sound pressure on the contour; radiating area | dB(A); dB(A); m$^2$ | 43 |
| $i_\text{d}$, $\tau_\text{tap}$ | differential spill current; tap position as a fraction | pu; – | 43 |

| $p_\text{e}$, $t$ (sheet), $\rho$, $\rho_\text{m}$ | classical eddy loss per kg; sheet thickness; resistivity and density of the steel | W/kg; m; ohm m; kg/m$^3$ | 43 |
| $E_\text{void}$, $\varepsilon_\text{r}$ | field in a flat gas void; relative permittivity of the solid around it | kV/mm; – | 43 |
| $r_0$, $r_1$ | conductor and flange radii of a bushing | mm | 43 |

| $\Delta\theta$, $J_\text{sc}$, $c_V$ | adiabatic rise in a short circuit; fault current density; volumetric heat capacity | K; A/mm$^2$; J/(m$^3$ K) | 43 |

| $\dot{m}$, $c_p$, $\Delta\theta_\text{o}$ | natural oil mass flow; specific heat of oil; bottom-to-top oil rise | kg/s; kJ/(kg K); K | 43 |
| $R_{ab}$, $R_a$ | line-to-line reading of a delta; phase resistance | ohm | 43 |

| $p$, $q$, $C_\text{f}$, $C_\text{r}$, $C_\text{t}$ | chance of a weak design; share a review catches; field failure, review and test costs | –; –; k u | 43 |
| $n$ (no-load), $P_1$, $P_2$, $U_1$, $U_2$ | exponent of no-load loss with voltage; two readings | –; kW; pu | 43 |

| $\theta_\text{top}$, $g$ (thermal), $H$ | top-oil temperature; winding gradient; hot-spot factor | C; K; – | 43 |

- In chapter 43, $\varepsilon_\text{o}$ and $\varepsilon_\text{p}$ are permittivities (chapter 25's $\varepsilon$ is the
  regulation); $a$ is a conductor area in the hoop formula and a fit coefficient in the cooling curve;
  $b$ is a fit coefficient (not a susceptance); $k_\text{st}$ is the stacking factor (chapter 41's
  $k_\text{s}$ is segregation, chapter 43's $k_\text{s}$ the stray-loss share); $\tau$ is the cooling time
  constant and $\tau_\text{tap}$ a tap fraction; $h$ is the winding height; $p$ is a chance in the
  short-circuit decision (not a pressure) and $n$ an exponent there (not a count of steps);
  $g$ is a joint gap in the magnetising lesson and the winding gradient in the hot-spot lesson.

## Chapter 44 (power converters, inverters and control-electronics manufacturing)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $\lambda_\text{unit}$, $n_i$, $\lambda_i$, $N_\text{y}$ | failure rate of one unit; count and rate of part $i$; expected failures a year | FIT; –; FIT; 1/year | 44 |
| $P_\text{leg}$, $P_\text{stack}$ | semiconductor loss of one NPC leg and one stack (simplified) | W | 44 |
| $R_\text{ch}$, $d_\text{tim}$, $k_\text{tim}$, $A_\text{chip}$, $f_\text{v}$ | interface resistance (as ch 9); layer thickness; conductivity; area under the chips; void share | K/W; µm; W/(m K); cm²; – | 44 |
| $N/N_0$, $\Delta T_j$ | relative power-cycling life; junction swing | –; K | 44 |
| $I_k/I$, $r_k$, $P_\text{pos}$ | current share of branch $k$; its on-state resistance; loss of one switch position | –; Ω; W | 44 |
| $\text{ESR}_k$, $L/L_0$ | equivalent series resistance of capacitor $k$; relative life | mΩ; – | 44 |
| $\Delta\gamma$, $L_\text{D}$, $\Delta\alpha$, $h_\text{s}$, $N_\text{f}$, $\varepsilon_\text{f}$, $c_\text{f}$ | shear strain range of a solder joint; distance from the neutral point; CTE mismatch; joint height; cycles to failure; fatigue ductility coefficient and exponent | –; mm; ppm/K; mm; –; –; – | 44 |
| $d_\text{need}$, $r_\text{PD}$ | creepage needed (teaching); teaching rate per kV for a pollution degree | mm; mm/kV | 44 |
| $S/S_\text{rated}$, $\rho_\text{rule}$ | stress ratio; derating rule | – | 44 |
| $R_\text{c}$, $F$, $F_0$ | contact resistance of a bolted joint; clamping force and its design value | µΩ; kN | 44 |
| $d_k$, $d_k^\text{out}$, $p_{s,k}$ | defects of type $k$ in and out of the line; detection chance of station $s$ | ppm; ppm; – | 44 |
| $m_\text{tim}$, $A_\text{base}$, $\rho_\text{tim}$ | paste mass; baseplate area; paste density | g; cm²; g/cm³ | 44 |
| $n$ (demonstration), $R$, $C$ | units to run without failure; reliability; confidence | –; –; – | 44 |
| $\eta_\text{MPPT}$, $P_{\text{mpp},t}$ | tracking efficiency; available power at step $t$ | –; W | 44 |
| $T_\text{L}$, $\mu$, $k$ (spares), $c$ (cover) | resupply time; mean failures in it; stock; no-stock-out chance | h; –; –; – | 44 |
| $T_\text{R}$, $\bar P$, $E_\text{lost}$ | mean time to restore; mean power lost while down; energy lost a year | h; MW; MWh | 44 |
| $\Delta T_\text{c}$, $\dot m$, $c_p$ | coolant rise along a plate; mass flow; specific heat | K; kg/s; J/(kg K) | 44 |
| $K$, $Q_k$, $Q$ | flow resistance of a plate ($\Delta p = K Q^2$); its flow; total flow | –; kg/s; kg/s | 44 |
| $N$, $m$, $n$ (audit) | joints in a unit; untorqued joints; joints audited | – | 44 |
| $\sigma_\text{total}$, $b$, $b_\text{total}$ | spread of the plant total; shared bias of a sensor lot; its effect on the total | % | 44 |
| $C_\text{b}$, $R_\text{b}$ | body capacitance and resistance of the discharge model | pF; Ω | 44 |
| $F(t)$, $\eta$, $\beta$, $a_\text{f}$, $t_\text{b}$ | Weibull failure share, scale and shape; acceleration factor; burn-in time | –; h; –; –; h | 44 |
| $p_\text{FA}$, $p_\text{FR}$, $C_\text{field}$, $C_\text{part}$ | false accept and reject rates; cost of a bad part in the field and of a rejected part | –; k u | 44 |
| $L_\text{loop}$, $L_\text{fixed}$, $L_\text{bus}$, $d$, $d_0$, $V_\text{peak}$ | commutation-loop inductance and its parts; layer spacing and design value; peak voltage on the switch | nH; mm; V | 44 |
| $\text{RH}$, $p_\text{s}$, $P_\text{h}$, $UA$ | relative humidity; saturation vapour pressure; heater power; cabinet loss coefficient | –; hPa; W; W/K | 44 |
| $P_\text{coll}$, $b$ (bits) | chance two sets share a fingerprint; fingerprint length | –; bit | 44 |
| $T_\text{app}$, $\varepsilon$, $\varepsilon_\text{set}$, $T_\text{r}$ | temperature a camera shows; emissivity of the surface and as set; reflected temperature | K | 44 |
| $z(t)$, $\Delta_\text{bad}$, $\sigma_\text{peer}$, $\sigma_\text{n}$, $\tau$ | distance of a module from its peers in sd; its steady excess; peers' spread; sensor noise; rise time constant | –; K; K; K; min | 44 |
| $r$, $t_\text{p}$, $c$ (rollout) | trip rate of a bad image; pilot time; chance the pilot finds it | 1/day; day; – | 44 |
| $E_\text{kept}$, $T_\text{swap}$, $p_\text{e}$, $C_\text{stack}$ | energy kept by a spare stack; swap time; energy price; stack cost | MWh; h; u/MWh; k u | 44 |
| $t_k$, $r_k$, $t_\text{wc}$, $t_\text{RSS}$ | time and relative tolerance of a protection stage; worst-case and RSS totals | µs; –; µs; µs | 44 |
| $\sigma_\text{DC}$, $\sigma_\text{offset}$ | DC current of a phase and offset of one sensor (sd) | A | 44 |
| $u_\text{m}$, $u_\text{s}$, $s$, $P_\text{pair}$ | meter, supply-meter and split uncertainties; loss of a back-to-back pair | –; –; –; kW | 44 |
| $T_\text{in}$, $T_\text{air}$, $n_\text{fans}$ | coolant inlet; air temperature; working fans | °C; °C; – | 44 |
| $t_\text{h}$, $V_1$, $V_2$ | hold-up time; bulk voltage at the start and at drop-out | ms; V; V | 44 |
| $p_\text{board}$, $m$ (coating), $p$ | chance a board has a bare critical spot; critical spots a board; chance one is missed | –; –; – | 44 |
| $D$, $N_0$, $\Delta T_0$, $\Delta T_y$ | accumulated damage (Miner); reference life; design swing; swing in year $y$ | –; –; K; K | 44 |
| $t_k$ (learning), $t_1$, $\ell$ | hours of unit $k$; of the first unit; learning rate | h; h; – | 44 |
| $\lambda_\text{lo}$, $\lambda_\text{hi}$, $f$, $T$ | interval of a constant failure rate from $f$ failures in $T$ unit-hours | 1/h; 1/h; –; h | 44 |

- In chapter 44, $C$ is a confidence in the demonstration formula (not a capacitance), $R$ a
  reliability there (not a resistance); $b$ is a sensor bias in the calibration lesson and a bit count in the fingerprint lesson; $c$ is a no-stock-out chance, then a pilot's chance of finding a defect; $h_\text{s}$ is the solder joint height; $L_\text{D}$ a distance
  (not an inductance) and $L/L_0$ a relative life; $r_k$ an on-state resistance of a module branch.

## Chapter 45 (battery cells, packs, BMS and storage-container manufacturing)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $c_\text{A}$, $w$, $a$, $q$ | areal capacity; coating loading; active share; specific capacity | mAh/cm²; mg/cm²; –; mAh/g | 45 |
| N/P | capacity ratio of facing negative and positive electrodes | – | 45 |
| $E/m$, $m_\text{cell}$, $f$ | energy per mass; cell mass; mass overhead factor | Wh/kg; kg; – | 45 |
| $\rho_\text{w}$, $p_\text{s}$, $T_\text{d}$ | water in air; saturation vapour pressure; dew point | g/m³; hPa; °C | 45 |
| $K$, $t_\text{rest}$, $\sigma_\text{v}$, $\sigma_K$ | daily OCV drop at rest; rest time; reading sd; noise of $K$ | mV/day; day; mV; mV/day | 45 |
| $S_\text{hi}$, $S_\text{lo}$, $L_\text{hi}$, $L_\text{lo}$, $m$ (BMS) | BMS limits; cell data-sheet limits; required margin | V or °C | 45 |
| $V_\text{part}$, $E_\text{part}$ | voltage and energy of a divided part of a battery | V; kWh | 45 |
| $t_\text{bal}$, $I_\text{bal}$ | time and current of balancing | h; A | 45 |
| $m_\text{rec}$, $m_k$, $r_k$ | recovered mass; mass and recovery rate of material $k$ | kg; kg; – | 45 |
| $\eta_\text{c}$, $Q_\text{in}$, $Q_\text{out}$ | charge kept of charge put in; charge in and out | –; Ah; Ah | 45 |
| $I_\text{leak}$, $dV/d\text{SOC}$ | self-discharge current; slope of the OCV curve | mA; V | 45 |
| $k_\text{c}$, $k_\text{f}$, $x_\text{f}$, $F$, $F_0$, $\delta$ | cell and frame stiffness; frame stretch; strap force and its start; free growth | kN/mm; mm; kN; mm | 45 |
| $h_\text{hot}$, $f_0$ | health of the hottest cell; fade a year at the mean temperature | –; 1/year | 45 |
| $\Delta T_\text{unseen}$, $g$, $s$ | excess a sensor does not see; gradient per cell; sensors | K; K; – | 45 |
| $R_{25}$, $R_T$, $\alpha_R$ | pulse resistance at 25 °C and at $T$; temperature coefficient | µΩ; µΩ; 1/K | 45 |
| $N_\text{WIP}$, $\lambda$ (cells) | cells resting; cells made a day | –; 1/day | 45 |
| $K_\text{max}$, $\bar K$ | expected highest and mean $K$ of $n$ cells | mV/day | 45 |
| $\Delta Q$, $\sigma(t)$, $\sigma_0$, $g$ (decay) | string loss; capacity spread at age $t$; at assembly; growth | Ah | 45 |
| CE, $N_{80}$ | coulombic efficiency; cycles to lose 20 % | –; – | 45 |
| $m_\text{w}$, $s$, $L$ (leak), $t$ | water entering a cell; teaching scale; leak rate; time | mg; mg/(mbar l/s year); mbar l/s; year | 45 |
| $t_\text{drain}$, $I_\text{self}$, $I_\text{BMS}$ | time to the lowest SOC; self-discharge; BMS draw | day; mA; mA | 45 |
| $t_\text{detect}$, $r$ (reading) | rest needed to see a leaker; reading resolution | day; mV | 45 |
| $n$ (requal), $z_\alpha$, $z_\beta$, $\Delta$ | cells from each factory; normal quantiles of confidence and power; mean shift to see | –; –; –; Ah | 45 |
| $R_\text{rack}$, $R_i$ | insulation of a rack; of module $i$ | MΩ | 45 |
| $N_\text{y}$, $T_\text{R}$, $\bar P$, $E_\text{lost}$ (from ch 44) | used again for module spares | – | 45 |
| $n_\text{s}$, $n_\text{p}$, $c_\text{max}$, $I_\text{max}$ | cells in series and parallel; C-rate limit; current limit | –; –; 1/h; A | 45 |
| $n$ (propagation), $s$, $m$, $c_p$, $\Delta T$ | neighbours heated; share of a cell's energy reaching them; mass and heat capacity of a neighbour; temperature rise | –; –; kg; J/(g K); K | 45 |
| $P_\text{heat}$, $T_\text{c}$, $T_\text{air}$ | heat to hold the cells; cell and air temperatures | kW; °C; °C | 45 |

- In chapter 45, $m$ is a BMS margin in the limit check and a mass in the recovery sum; $g$ is a
  temperature gradient per cell in the sensor lesson and a spread growth in the decay lesson;
  $f$ is a mass overhead and $f_0$ a yearly fade; $\lambda$ is a production rate (not a failure rate).

## Chapter 46 (cable, connector, switchgear and protection-panel manufacture)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $E(r)$, $U_0$, $r_\text{c}$, $r_\text{i}$ | field in the insulation at radius $r$; phase-to-earth voltage; radii of the conductor and insulation screens | kV/mm; kV; mm | 46 |
| $R_\theta$, $R_{20}$, $\alpha_{20}$ | resistance read at $\theta$ and corrected to 20 °C; temperature coefficient (Al 0.00403) | Ω; Ω; 1/K | 46 |
| $a$, $n$, $H$, $R_\text{c}$ (contact) | contact-spot radius; number of spots; hardness; constriction resistance | m; –; Pa; µΩ | 46 |
| $P_\text{loss}$, $\Delta U$ | three-phase Joule loss; voltage drop | kW; V | 46 |
| $I_k$, $t_k$, $c$ (cover) | short-time current and its duration; share of the ordered $I_k^2 t_k$ a report covers | kA; s; – | 46 |
| $b$, $s_b$ | least-squares slope and its standard error | per month or per year | 46 |
| $N$, $k$, $n$ (sampling), $P$ | drums in a lot; bad drums; drums sampled; chance to find one | –; –; –; – | 46 |
| $C$ (cable), $\varepsilon_0$, $\varepsilon_\text{r}$ | capacitance per length; vacuum and relative permittivity | µF/km; F/m; – | 46 |
| $\Delta T_1$, $\Delta T_2$, $I_1$, $I_2$, $n$ (rise) | temperature rises at two currents; exponent of the rise | K; A; – | 46 |
| $V_\text{coil}$, $V_\text{end}$, $I_\text{coil}$, $L$, $A$ | voltage at a coil; battery end voltage; coil current; one-way length; wire section | V; V; A; m; mm² | 46 |

- In chapter 46, $n$ is a number of contact spots, a sample size or a rise
  exponent by lesson; $R_\text{c}$ is a constriction resistance (in chapter 10 $R_\text{c}$ may differ by
  context), $H$ a hardness, $c$ the type-test cover share and $a$ a contact-spot radius.

## Chapter 47 (civil, structural, tower, tracker and balance-of-plant manufacture)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $m$, $\bar D$, $t$, $L$, $\rho$ | shell mass; mean diameter; wall thickness; section length; steel density | t; m; mm; m; kg/m³ | 47 |
| $F_\text{bolt}$, $M$, $n$, $D_\text{b}$, $W$ | worst flange-bolt pull; base moment; bolts; bolt circle; weight above | kN; MN m; –; m; MN | 47 |
| $e$, $V$, $A'$ | eccentricity; vertical load; compressed area under a base | m; MN; m² | 47 |
| $T$, $q$, $C_m$, $A$, $c$ (tracker) | hinge moment of a row; dynamic pressure; moment coefficient; row area; chord | kN m; Pa; –; m²; m | 47 |
| CEV | carbon equivalent of a steel | – | 47 |
| $m'$, $d$ | bar mass per metre; bar diameter | kg/m; mm | 47 |
| $f_\text{ck}$ | specified characteristic strength | MPa | 47 |
| $z(\theta)$, $a$, $b$, $c$ (tilt), $R$ | flange level around the circle and its plane fit; bolt-circle radius | mm; m | 47 |
| $f_\text{new}/f_\text{old}$, $m_\text{top}$ | frequency ratio from a mass change; mass at the top | –; t | 47 |
| $L$, $\lambda$, $W$ (queue) | items open; arrivals a day; time to decide (Little) | –; 1/day; day | 47 |

- In chapter 47, $c$ is a module chord in the tracker lesson and a plane-fit coefficient in the
  anchor-cage lesson; $n$ is a count of bolts; $m$ is a mass (in ch 46 a contact count was $n$).

## Chapter 48 (instrumentation, metering, control-panel and plant-network hardware manufacture)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $I$, $x$, $x_\text{lo}$, $x_\text{hi}$ | loop current; measured value and its range | mA; unit of $x$ | 48 |
| $u$, $u_\text{acc}$, $u_\text{T}$, $u_\text{drift}$, $u_\text{lin}$ | combined site error; accuracy, temperature, drift and linearity terms | unit of the reading | 48 |
| $\varepsilon_\text{RSS}$, $\varepsilon_\text{worst}$, $\varepsilon_\text{CT}$, $\varepsilon_\text{VT}$, $\varepsilon_\text{m}$ | metering chain error and its parts | % | 48 |
| $A_\text{exp}$, $\alpha$ (fibre), $L$, $n_\text{c}$, $A_\text{c}$, $n_\text{s}$, $A_\text{s}$ | expected link loss; loss per km; length; connectors and their loss; splices and their loss | dB; dB/km; km; –; dB; –; dB | 48 |
| $e(\theta)$, $\theta$, $\delta$ | relative error of a tilted plane-of-array sensor; angle of incidence; mounting tilt error | –; deg; deg | 48 |
| $V_\text{tx}$, $V_\text{s}$, $V_\text{iso}$, $I_\text{max}$, $R_\text{in}$, $R_\text{c}$ | voltage left at the transmitter; loop supply; isolator drop; highest loop current; input resistance; cable loop resistance | V; V; V; A; Ω; Ω | 48 |
| $T_\text{d}$, $\gamma$, $b$, $c$ | dew point; Magnus intermediate; Magnus coefficients (17.62; 243.12 °C) | °C; –; –; °C | 48 |
| $W$, $\rho$, $\mu$ | mean waiting time in a single-server queue; link utilisation; packets served a second | s; –; 1/s | 48 |

- In chapter 48, $\alpha$ is a fibre's loss per kilometre (not a temperature coefficient) and $I$ a loop
  current.

## Chapter 49 (construction and installation)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $e$, $\Delta x$, $\Delta y$ | radial position error of a post and its components | mm | 49 |
| $p$, $w_i$, $d_i$ | earned progress; weight of step $i$ (summing to 1); share of step $i$ done | – | 49 |
| $n_\text{j}$, $L$, $L_\text{drum}$ | joints in a cable section; section length; drum length | –; m; m | 49 |
| $t$, $t_\text{m}$, $d$, $v$ | response time to a work front; mobilisation time; distance by site road; speed | min; min; km; km/h | 49 |

- In chapter 49, $d_i$ is a share of work done and $d$ a road distance; $p$ is progress (not pressure or
  poles).

## Chapter 50 (commissioning, grid acceptance and handover)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $V_\text{oc,s}$, $I_\text{sc,s}$, $n$, $G$, $T_\text{c}$ | string open-circuit voltage and short-circuit current; modules in the string; irradiance; cell temperature | V; A; –; W/m²; °C | 50 |
| $R$, $f_\text{n}$, $k$, $\Delta f_\text{e}$, $\Delta P$ | measured droop; nominal frequency; slope; frequency deviation beyond the deadband; power change | %; Hz; pu/Hz; Hz; pu | 50 |

- In chapter 50, $R$ is a droop in per cent (not a resistance) and $n$ the modules of a string.

## Chapter 51 (plant operation)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $T_\text{out}$, $q$, $UA$, $C_\text{th}$ | outdoor air temperature; heat from equipment in a room; room loss coefficient; room heat capacity | °C; kW; kW/K; kJ/K | 19 (51 for a control room) |
| $E_\text{floor}$, $\eta$ | battery energy kept for the service; one-way efficiency | MWh; – | 20 |

- In chapter 51, the room model reuses the chapter 19 symbols; $C_\text{th}$ is given in kJ/K and the time constant $C_\text{th}/UA$ in hours after dividing by 3,600.

## Chapter 52 (maintenance, troubleshooting and RAM)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $A_\text{i}$, $A_\text{o}$, MTBF, MTTR, MTBM, MDT | inherent and operational availability; mean time between failures, to repair, between maintenance; mean down time | –; h | 52 (MTBF, MTTR ch 3) |
| $R(t)$, $h(t)$, $k$, $c$ | reliability and hazard rate; Weibull shape and scale | –; 1/h; –; h | 3 |
| $\lambda$, $r$, $T$, $\chi^2$ | failure rate; failures seen; exposure; chi-square quantile | 1/h; –; h; – | 37 |
| $q$, $\beta_\text{c}$, $Q_\text{pair}$ | unavailability of a unit; common-cause share; unavailability of a redundant pair | – | 52 |
| $m$, $s$ | mean demand in the lead time; spares held | – | 52 |
| $c_\text{d}$, $C$, $T^{*}$, $r$, $E$, $p$ | cleaning cost per day; cost of a campaign; best interval; soiling rate; daily PV energy; price | u/day; u; day; 1/day; MWh; u/MWh | 52 |

- In chapter 52, $h$ is the hazard rate in the Weibull lesson and the CUSUM threshold in lesson D; $r$ counts failures in lesson E and is the soiling rate in lesson G; $p$ is a detection probability in lesson B and a price in lesson G; the CUSUM allowance is $\kappa$ (as ch 37). The common-cause share is $\beta_\text{c}$, never the Weibull shape.

## Chapter 53 (performance improvement, repowering and retirement)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $R(\Delta t \mid t_0)$, $t_0$, $\Delta t$ | conditional reliability for $\Delta t$ more after surviving $t_0$ | –; h; h | 53 |
| $p$, $F$, $i$, $n$ | sinking-fund payment; target fund; interest rate; years | k u/yr; k u; –; yr | 53 (ch 21 for money) |
| EAC, $v$ | equivalent annual cost; virtual age of a repaired unit | k u/yr; h | 53 |

- In chapter 53, $p$ is a yearly payment (not a price or a probability), and the Weibull shape and scale stay $k$, $c$ (ch 3).

## Chapter 54 (identifying applicable requirements)

| Symbol | Meaning | Unit | First chapter |
|---|---|---|---|
| $\cos\varphi$, $\tan\varphi$ | power factor and its tangent at the POC | – | 7 (reused) |
| $Q_\text{req}$, $P_\text{cap}$ | reactive power a requirement asks; export cap at which a capability meets it | Mvar; MW | 54 |
| $\lambda_\text{r}$ | rate of changes to a set of rules (Poisson) | 1/yr | 54 |
| $r$, $w$, $r_\text{g}$ | contract interest rate; withholding-tax rate; grossed-up rate | – | 54 (ch 21 for $r$) |

- In chapter 54, $\lambda_\text{r}$ is a rate of rule changes (not a failure rate $\lambda$ of ch 37/52).
