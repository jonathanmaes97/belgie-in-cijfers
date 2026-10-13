# Nationale Bank: codes per dimensie

## DF_CONSN
- HTTP 200

- **FREQ**: `M` Monthly
- **CONSN_INDIC**: `AES` Appraisal economic situation in Belgium (last 12 months); `AFS` Appraisal of actual financial situation of households; `AMP` Appraisal of actual moment whether or not it is favorable to make major purchases; `ASH` Appraisal of actual moment whether or not it is favorable to make savings; `CCI` Consumer confidence indicator; `FCP` Forecasts consumer prices in Belgium (next 12 months); `FES` Forecasts economic situation in Belgium (next 12 months); `FFS` Forecasts financial situation of households (next 12 months); `FMP` Forecasts for major purchase of households (next 12 months); `FSH` Forecasts of savings of households (next 12 months); `FUN` Forecasts unemployment in Belgium (next 12 months); `TCP` Trend in consumer prices in Belgium (last 12 months); `TFS` Trend in financial situation of households (last 12 months)
- **BE_AREA**: `BE` Belgium; `BX` Brussels-Capital Region; `VL` Flemish Region; `WL` Walloon Region
- **OBS_STATUS**: `A` Normal
- **DECIMALS**: `0` Zero

## DF_BUSSURVM
- HTTP 200

- **FREQ**: `M` Monthly
- **BUSSURVM_INDICATOR**: `A_AC` Appraisal of activity; `A_OB` Appraisal of total orders; `A_OE` Appraisal of export orders; `A_SA` Appraisal of sales; `A_ST` Appraisal of stocks; `F_AC` Forecasts on activity; `F_DE` Forecasts on demand; `F_EM` Forecasts on employment; `F_OB` Forecasts on orders; `F_SP` Forecasts on prices; `M_AW` Movement of amount of work to be done; `M_NC` Movement of number of contracts concluded; `M_NT` Movement of number of tenders; `SYNC` Synthetic curve; `T_AC` Trend in activity; `T_EE` Trend in equipement; `T_EM` Trend in employment; `T_OB` Trend in order book; `T_OD` Trend in domestic orders; `T_OE` Trend in export orders; `T_PR` Trend in production rate; `T_SA` Trend in sales; `T_SP` Trend in prices
- **BE_AREA**: `BE` Belgium; `BX` Brussels-Capital Region; `VL` Flemish Region; `WL` Walloon Region
- **BUSSURV_SECTOR**: `A999` Total; `C010` Structural building work; `C011` Construction of residential buildings; `C012` Construction of non-residential buildings; `C020` Construction installation; `C030` Building completion and finishing; `C040` Roofing activities; `C050` Civil engineering and roadworks; `M000` Manufacturing industry; `M001` Consumer goods; `M002` Capital goods; `M003` Intermediate goods; `M010` Food industry; `M020` Textile industry; `M021` Textile industry (excluding clothing and knitwear); `M030` Wood-processing industry; `M040` Paper and paperboard industry; `M050` Graphics industry; `M060` Building materials and flat glass; `M070` Chemical industry; `M071` Basic chemicals; `M072` Chemical consumer goods; `M080` Plastics-processing and rubber industry; `M090` Manufacture of ferrous and non-ferrous basic metals; `M100` Technological industry; `M101` First processing of ferrous metals; `M102` Metal products; `M103` Transport equipment; `M104` Manufacture of machinery; `M105` Electric and electronic manufacture & ICT; `M106` Metallic consumer goods; `M107` Metallic equipment goods; `S000` Business-related services; `S010` Transport and support activities; `S020` Rental activities; `S030` Computer activities; `S040` Other business-related services; `T000` Trade; `T010` Sale of motor vehicles; `T020` Sale of food; `T030` Sale of footwear; `T040` Sale of furniture; `T050` Sale of textiles; `T060` Sale of electrical and electronical appliances
- **BUSSURVM_ADJ**: `S` Seasonally adjusted; `X` Seasonally adjusted and smoothed
- **OBS_STATUS**: `A` Normal
- **DECIMALS**: `1` One

## DF_UNEMPLOY_RATE
- HTTP 200

- **FREQ**: `A` Annual; `M` Monthly; `Q` Quarterly
- **GENDER**: `AA` Total; `ME` Men; `WO` Women
- **AGE**: `E0025` -25 years; `Y2574` Aged over 25; `Z0000` All classes of age
- **ADJUSTMENT**: `N` Neither seasonally adjusted nor calendar adjusted data; `Y` Calendar and seasonally adjusted data
- **REGION**: `B4` EU 27 (fixed composition); `BE` Belgium; `U2` Euro area
- **INDEX_TYPE**: `HUR` Adjusted Harmonized Unemployment Rate
- **DERIVATION**: `RATE` Percentage
- **OBS_STATUS**: `A` Normal
- **UNIT_MEASURE**: `PT` Percent
- **UNIT_MULT**: `0` Units
- **COMPILING_ORG**: `4D1` Statistiek van de Europese Unie
- **DECIMALS**: `1` One

## DF_QNA_DISS
- HTTP 200

- **FREQ**: `A` Annual; `Q` Quarterly
- **ACCOUNT**: `1` Gross value added by industry; `2` Main categories of expenditure of GDP; `3` Main categories of gross domestic income
- **INDICATOR**: `B11` External balance of goods and services; `B1G` Gross value added at basic prices; `B1GM` Gross domestic product; `B2G_B3G` Gross operating surplus and mixed income; `D1` Compensation of employees; `D11` Wages and salaries; `D12` Employers' social contributions; `D21_M_D31` Taxes less subsidies on products; `D2_M_D3` Taxes on production and imports less subsidies; `GDI` Gross domestic income; `P31_S14_S15` Private final consumption; `P3_S13` Final consumption expenditure of general government; `P51` Gross fixed capital formation; `P51_DWE` Gross fixed capital formation by households in dwellings; `P51_ENT` Gross fixed capital formation by enterprises, self-employed workers and non-profit institutions; `P51_PAD` Gross fixed capital formation by public administrations; `P52` Changes in stocks + Acquisitions less disposals of valuables; `P52_A` Acquisitions less disposals of valuables; `P52_CI` Changes in inventories; `P5_DC` Gross domestic capital formation; `P6` Exports of goods and services; `P7` Imports of goods and services
- **BRANCH**: `VA` Agriculture, forestry and fishing; `VB_E` Industry; `VF` Construction; `VG_I` Wholesale and retail trade; transportation; accommodation and food service activities; `VG_U` Services; `VJ` Information and communication; `VK` Financial and insurance activities; `VL` Real estate activities; `VM_N` Professional, scientific and technical activities; administrative and support service activities; `VO` Public administration and defence; education; `VQ` Human health and social work activities; `VR_U` Arts, entertainment and recreation; other service activities; activities of households as employers; `VZ` Total economy
- **PRICES**: `CQ` Contributions to the volume change - Q to Q; `CY` Contributions to the volume change - Y to Y; `D` Deflator; `L` In volume: chain linked, in millions of euro; `LQ` Chain linked - Q to Q percentage change (reference year 2020); `LY` Chain linked - Y to Y percentage change (reference year 2020); `V` Current prices in millions of euro
- **ADJUSTMENT**: `N` Gross data; `Y` Working day and seasonally adjusted
- **OBS_STATUS**: `L` Missing value; data exist but not collected; `P` Provisional value
- **CONF_STATUS**: `F` Free (free for publication)
- **UNIT_MULT**: `6` Millions
- **DECIMALS**: `1` One

