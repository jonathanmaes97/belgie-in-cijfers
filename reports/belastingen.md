# Verkenning: PISA, energieprijzen, mazout, BBSZ

## Dataflows
- TAX_ITR: Implicit tax rate
- TAX_LEVEL: Tax revenue by level of government
- VAP_COMPL_GAP: VAT Compliance Gap – How much VAT goes uncollected
- VAT_POL_GAP: VAT Policy Gap – How VAT rules shape revenue
- TAX_ITR_CAPITAL: Implicit tax rates on capital
- TAX_TYPE: Tax revenue by type of tax
- TAX_EC_FUNC: Tax revenue by economic function
- TAX_ETR: Effective tax rates
## TAX_ITR (Implicit tax rate)
- https://webgate.ec.europa.eu/taxation_customs/redisstat/api/dissemination/statistics/1.0/data/TAX_ITR?geo=BE&lastTimePeriod=1&lang=EN
- HTTP 200
- **FREQ**: A (Annual)
- **ITR**: C (Implicit Tax rate on Consumption), L (Implicit Tax rate on Labour)
- **UNIT**: PC_TOT (Percentage of total)
- **GEO**: BE (Belgium)
- **TIME_PERIOD**: 2024 (2024)
- eerste waarden: [('0', 15.47), ('1', 40.68)]
## TAX_LEVEL (Tax revenue by level of government)
- https://webgate.ec.europa.eu/taxation_customs/redisstat/api/dissemination/statistics/1.0/data/TAX_LEVEL?geo=BE&lastTimePeriod=1&lang=EN
- HTTP 200
- **FREQ**: A (Annual)
- **LEVEL_GOV**: S1311 (Central government), S1312 (State government), S1313 (Local government), S1314 (Social security funds), S212 (EU Institutions)
- **UNIT**: MIO_EUR (Million euro), PC_TOT (Percentage of total), PC_GDP (Percentage of gross domestic product (GDP))
- **GEO**: BE (Belgium)
- **TIME_PERIOD**: 2024 (2024)
- eerste waarden: [('0', 138348.2), ('2', 22.3), ('1', 52.15), ('3', 27657.0), ('5', 4.46), ('4', 10.43), ('6', 12197.4), ('8', 1.97)]
## VAP_COMPL_GAP (VAT Compliance Gap – How much VAT goes uncollected)
- https://webgate.ec.europa.eu/taxation_customs/redisstat/api/dissemination/statistics/1.0/data/VAP_COMPL_GAP?geo=BE&lastTimePeriod=1&lang=EN
- HTTP 200
- **FREQ**: A (Annual)
- **INDIC_VAT_COMPL_GAP**: VAT_COMPL_GAP (VAT compliance gap), VTTL (VAT Total Theoretical Liability), LIAB_HH (Household VAT liability), LIAB_NPISH_GOV (NPISH and government VAT liability), LIAB_IC (Intermediate consumption VAT liability), LIAB_GFCF (Gross Fixed Capital Formation VAT liability), LIAB_NET_ADJ (VAT Base Net Adjustments), VAT_REVENUE (VAT revenue)
- **UNIT**: PC_VTTL (Percentage of VAT Total Theoretical Liability), MIO_EUR (Million euro), MIO_NAC (Million in national currency)
- **GEO**: BE (Belgium)
- **TIME_PERIOD**: 2024 (2024)
- eerste waarden: [('1', 6125.6846), ('0', 13.94125858), ('22', 37813.5664), ('4', 43939.251), ('5', 43939.251)]
## VAT_POL_GAP (VAT Policy Gap – How VAT rules shape revenue)
- https://webgate.ec.europa.eu/taxation_customs/redisstat/api/dissemination/statistics/1.0/data/VAT_POL_GAP?geo=BE&lastTimePeriod=1&lang=EN
- HTTP 200
- **FREQ**: A (Annual)
- **INDIC_VAT_POL_GAP**: VAT_ACT_POL_GAP (Actionable VAT policy gap), VAT_RATE_GAP (VAT rate gap), VAT_EX_GAP_NAT (National policy-driven VAT exemption gap), VAT_EX_GAP_EU (EU policy-mandated VAT exemption gap), VAT_EX_GAP_NON (Non-actionable VAT policy gap), VAT_POL_GAP (VAT policy gap), NOTIONAL_ID_REV (Notional ideal revenue)
- **UNIT**: PC_NIR (Percentage of Notional Ideal VAT Revenue), MIO_EUR (Million euro), MIO_NAC (Million in national currency)
- **GEO**: BE (Belgium)
- **TIME_PERIOD**: 2024 (2024)
- eerste waarden: [('19', 97315.93167), ('20', 97315.93167), ('1', 26854.81792), ('2', 26854.81792), ('0', 27.5955), ('10', 4884.091979), ('11', 4884.091979), ('9', 5.0188)]
## TAX_ITR_CAPITAL (Implicit tax rates on capital)
- https://webgate.ec.europa.eu/taxation_customs/redisstat/api/dissemination/statistics/1.0/data/TAX_ITR_CAPITAL?geo=BE&lastTimePeriod=1&lang=EN
- HTTP 200
- **FREQ**: A (Annual)
- **ITR_CAPITAL**: ITR_C (Overall implicit tax rates on capital), ITR_INC (Overall implicit tax rates on capital income), CORP_T (Implicit tax rates on corporate income - traditional), CORP_NOD (Implicit tax rates on corporate income - no dividends), CORP_NOS (Implicit tax rates on corporate income - Net operating surplus)
- **UNIT**: PC_TOT (Percentage of total)
- **GEO**: BE (Belgium)
- **TIME_PERIOD**: 2024 (2024)
- eerste waarden: [('3', 30.41), ('4', 30.08), ('2', 20.03), ('0', 32.98), ('1', 21.79)]
## TAX_TYPE (Tax revenue by type of tax)
- https://webgate.ec.europa.eu/taxation_customs/redisstat/api/dissemination/statistics/1.0/data/TAX_TYPE?geo=BE&lastTimePeriod=1&lang=EN
- HTTP 200
- **FREQ**: A (Annual)
- **INDIC**: D2_D5_D91_D61_M_D611V_D612_M_M_D613V_D614_M_D995 (Total taxes (including compulsory actual social contributions)), D2_D5_D91 (Total taxes (excluding social contributions)), D2 (Indirect taxes), D211 (VAT), D212 (Taxes and duties on imports excluding VAT), D214 (Taxes on products, except VAT and import duties), D29 (Other taxes on production), D5_D91 (Direct taxes), D51A_C1 (Taxes on individual or household income including holding gains), D51B_C2 (Taxes on the income or profits of corporations including holding gains), D5_D91_M_D51A_C1_D51B_C2 (Other direct taxes), D611C_D613C (Total actual compulsory social contributions), D611C (Actual compulsory social contributions - employers), D613C (Actual compulsory social contributions - households), D995 (Capital transfers representing taxes assessed but not collected)
- **UNIT**: MIO_EUR (Million euro), PC_TOT (Percentage of total), PC_GDP (Percentage of gross domestic product (GDP))
- **GEO**: BE (Belgium)
- **TIME_PERIOD**: 2024 (2024)
- eerste waarden: [('6', 74880.8), ('8', 12.07), ('7', 28.23), ('9', 37697.9), ('11', 6.08), ('10', 14.21), ('12', 2838.7), ('14', 0.46)]
## TAX_EC_FUNC (Tax revenue by economic function)
- https://webgate.ec.europa.eu/taxation_customs/redisstat/api/dissemination/statistics/1.0/data/TAX_EC_FUNC?geo=BE&lastTimePeriod=1&lang=EN
- HTTP 200
- **FREQ**: A (Annual)
- **EF**: C (Taxes on consumption), AT (Taxes on consumption - Tobacco and alcohol), LAB (Taxes on labour Total), LAB_EMPL (Taxes on labour - Income from employment), LEYRS ("Taxes on labour - Income from employment, paid by employers"), LEES ("Taxes on labour - Income from employment, paid by employees"), LNON ("Taxes on labour - Income from employment, paid by non-employed"), CAP (Taxes on capital Total), KIC (Taxes on capital - Income of corporations), KIH (Taxes on capital - Income of households), KISE (Taxes on capital - Income of self-employed), KS (Taxes on capital - Stock of capital), ENV (Environmental taxes  Total), E (Environmental taxes - Taxes on energy), T (Environmental taxes - Transport taxes (excluding fuel taxes)), P_RS (Environmental taxes - Taxes on pollution and resources), PROP (Taxes on property Total), RP (Taxes on property - Recurrent taxes on immovable property), IG (Taxes on property - Inheritance and gift taxes), O (Taxes on property - Other taxes on property), FUEL (Taxes on energy from transport fuel taxes)
- **UNIT**: MIO_EUR (Million euro), PC_TOT (Percentage of total), PC_GDP (Percentage of gross domestic product (GDP))
- **GEO**: BE (Belgium)
- **TIME_PERIOD**: 2024 (2024)
- eerste waarden: [('3', 3282.1), ('5', 0.53), ('4', 1.24), ('0', 58746.2), ('2', 9.47), ('1', 22.14), ('21', 68145.3), ('23', 10.99)]
## TAX_ETR (Effective tax rates)
- https://webgate.ec.europa.eu/taxation_customs/redisstat/api/dissemination/statistics/1.0/data/TAX_ETR?geo=BE&lastTimePeriod=1&lang=EN
- HTTP 200
- **FREQ**: A (Annual)
- **INDIC_ETR**: COST_CAP (Cost of capital), EATR (Effective average tax rate), EMTR (Effective marginal tax rate), STATCIT (Statutory corporate income tax rate (top rate)), SURCHARGE (Surcharge on corporate income tax rate), STATLOCCIT (Statutory local profit tax), EFFCIT (Effective corporate income tax rate)
- **LEVEL**: CORP (Corporate domestic)
- **UNIT**: PC_TOT (Percentage of total)
- **GEO**: BE (Belgium)
- **TIME_PERIOD**: 2024 (2024)
- eerste waarden: [('0', 6.0), ('1', 22.5), ('6', 25.0), ('2', 12.9), ('3', 25.0), ('5', 0.0), ('4', 0.0)]
