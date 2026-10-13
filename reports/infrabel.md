# Infrabel: datasets over stiptheid

## `gegevens-mobipulse`

- Titel: Barometer van de stiptheid van de treinen tijdens de piekuren per belangrijke verbinding
- Laatst gewijzigd: 2022-07-05T14:22:38.988000+00:00 · records: 55145
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p>Stiptheidsbarometer van de grote treinverbindingen tijdens de weekdagen.</p> <p>Dit percentage houdt rekening met de afgeschafte treinen.</p> <p>Meer informatie over stiptheid vindt u op <a href="https://infrabel.be/en/punctuality" target="_blank">de pagina Stiptheid op Infrabel.be</a><br></p>
- Velden: `dat_dep` (date), `van` (text), `naar` (text), `regperiode_arr` (text), `instant` (text), `moment_of_day` (text), `percentage` (double), `rittijd` (text)
- Voorbeeld: `[{'dat_dep': '2018-09-19', 'van': 'CHARLEROI-SUD', 'naar': 'BRUSSEL-CENTRAAL', 'regperiode_arr': 'Ochtendspits', 'instant': 'Pointe du matin', 'moment_of_day': 'Morning peak hour', 'percentage': 80.0, 'rittijd': '01:00:27'}, {'dat_dep': '2018-09-19', 'van': 'NAMUR', 'naar': 'BRUSSEL-CENTRAAL', 'regperiode_arr': 'Ochtendspits', 'instant': 'Pointe du matin', 'moment_of_day': 'Morning peak hour', 'percentage': 37.5, 'rittijd': '01:17:36'}, {'dat_dep': '2018-09-19', 'van': 'TOURNAI', 'naar': 'BRUSSEL-CENTRAAL', 'regperiode_arr': 'Ochtendspits', 'instant': 'Pointe du matin', 'moment_of_day': 'Morning peak hour', 'percentage': 60.0, 'rittijd': '01:14:36'}]`

## `studie-railspect-2019`

- Titel: Studie Railspect 2019
- Laatst gewijzigd: 2022-07-05T14:23:16.480000+00:00 · records: 0
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p> De studie Railspect werd gemaakt door <a href="https://www.gfk.com/en-be/">GfK</a> na aanvraag van Infrabel en gebeurde bij 1.000 Belgen, die in de buurt van een overweg wonen en/of die af en toe met de trein reizen.</p><p> <img alt="logo Railspect" src="/assets/theme_image/Infrabel_logo_Railspect.png" style="width: 300px; height: auto; "/></p><p> In het kader van de problematiek rond stipthei
- Velden: 
- Voorbeeld: `[]`

## `toewijzing-afgeschafte-treinen`

- Titel: Toewijzing afgeschafte treinen per maand (archive)
- Laatst gewijzigd: 2025-11-07T10:00:00+00:00 · records: 396
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p><span style="background-color: initial;">Maandelijkse gegevens van het aantal </span>afgeschafte treinen op het Infrabel netwerk, opgedeeld per verantwoordelijke.</p><p>Als onafhankelijk infrastructuurbeheerder en beheerder van het treinverkeer zorgt Infrabel voor een correcte toewijzing van de oorzaken van vertragingen. Hiervoor bestaan grosso modo drie hoofdcategorieën: Infrabel, een spoorweg
- Velden: `jaar` (date), `maanddossierniveau` (date), `dashboardname1` (text), `entite` (text), `entity` (text), `sup` (double), `sup_p` (double), `sup_t` (double), `id` (double)
- Voorbeeld: `[{'jaar': '2018', 'maanddossierniveau': '2018-01', 'dashboardname1': 'INFRABEL', 'entite': 'Infrabel', 'entity': 'Infrabel', 'sup': 277.0, 'sup_p': 196.0, 'sup_t': 81.0, 'id': 16.37115839243499}, {'jaar': '2018', 'maanddossierniveau': '2018-03', 'dashboardname1': 'ANDERE', 'entite': 'Autres', 'entity': 'Other', 'sup': 41.0, 'sup_p': 20.0, 'sup_t': 21.0, 'id': 2.191341528594335}, {'jaar': '2018', 'maanddossierniveau': '2018-04', 'dashboardname1': 'ANDERE', 'entite': 'Autres', 'entity': 'Other', 'sup': 15.0, 'sup_p': 8.0, 'sup_t': 7.0, 'id': 1.035911602209945}]`

## `toewijzingvertraging`

- Titel: Toewijzing vertraging per maand
- Laatst gewijzigd: 2025-11-07T10:00:00+00:00 · records: 585
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p>De historische methode die gehanteerd wordt bij de berekening van de statistieken in deze dataset houdt rekening met de som van alle minuten vertraging veroorzaakt door 'grote incidenten' (intern bekend als ‘relazen’**) op het spoorwegnet zoals gemeld aan het <a href="https://www.rail-investigation.be/nl/onderzoeksorgaan/" target="_blank">Onderzoeksorgaan Ongevallen Incidenten Spoor (OOIS)</a> 
- Velden: `jaar` (date), `operator` (text), `entite` (text), `entity` (text), `maand2` (date), `min_hkv` (int), `id` (double)
- Voorbeeld: `[{'jaar': '2017', 'operator': 'Derden', 'entite': 'Tiers', 'entity': 'Third parties', 'maand2': '2017-02', 'min_hkv': 32047, 'id': 29.90630657533735}, {'jaar': '2017', 'operator': 'Derden', 'entite': 'Tiers', 'entity': 'Third parties', 'maand2': '2017-04', 'min_hkv': 30007, 'id': 37.24292859713793}, {'jaar': '2017', 'operator': 'Derden', 'entite': 'Tiers', 'entity': 'Third parties', 'maand2': '2017-05', 'min_hkv': 45967, 'id': 32.91209027250727}]`

## `nationale-stiptheid-per-moment-en-per-maand`

- Titel: Nationale stiptheid per moment en per maand
- Laatst gewijzigd: 2025-11-07T10:00:00+00:00 · records: 516
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p>Nationale stiptheid per maand tijdens de ochtend- en avondspits, het weekend en de daluren.</p><p><p>Het stiptheidspercentage geeft aan hoeveel procent van alle binnenlandse reizigerstreinen over een periode van een maand aangekomen zijn op hun eindbestemmingsstation - voor de treinen die door de Brusselse Noord-Zuid verbinding rijden in het eerste station van de verbinding dat zij op hun reisw
- Velden: `maand` (date), `regperiode` (text), `instant` (text), `moment_of_day` (text), `regelmaat` (double), `tel` (int), `reg` (int), `min_rt` (int)
- Voorbeeld: `[{'maand': '2016-01', 'regperiode': 'Weekends', 'instant': 'Weekends', 'moment_of_day': 'Weekends', 'regelmaat': 93.86940404904477, 'tel': 24549, 'reg': 23044, 'min_rt': 32326}, {'maand': '2016-01', 'regperiode': 'Daluren', 'instant': 'Heures creuses', 'moment_of_day': 'Off-peak hours', 'regelmaat': 90.68999669858039, 'tel': 45435, 'reg': 41205, 'min_rt': 93564}, {'maand': '2016-02', 'regperiode': 'Avondspits', 'instant': 'Pointe du soir', 'moment_of_day': 'Evening peak hour', 'regelmaat': 88.2823829688497, 'tel': 17239, 'reg': 15219, 'min_rt': 40597}]`

## `maandelijkse-stiptheid-per-stopplaats`

- Titel: Maandelijkse stiptheid per stopplaats
- Laatst gewijzigd: 2025-11-07T10:00:00+00:00 · records: 31800
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p>Maandelijks percentage van alle binnenlandse reizigerstreinen die met een vertraging van maximaal 5 minuten en 59 seconden aangekomen zijn in het stopplaats.</p>
- Velden: `datum` (date), `installatienaam_nederlands` (text), `installatienaam_frans` (text), `installatienaam_engels` (text), `ptcar_no` (int), `classificatie` (text), `classification` (text), `class` (text), `stiptheid` (double), `sumoftel` (double), `sumofreg` (double), `geo_point_2d` (geo_point_2d), `geo_shape` (geo_shape)
- Voorbeeld: `[{'datum': '2023-06', 'installatienaam_nederlands': 'BURST', 'installatienaam_frans': 'BURST', 'installatienaam_engels': 'BURST', 'ptcar_no': 235, 'classificatie': 'Zeer belangrijk station', 'classification': 'Gare très importante', 'class': 'Very important station', 'stiptheid': 88.3220910623946, 'sumoftel': 2372.0, 'sumofreg': 2095.0, 'geo_point_2d': {'lon': 3.920956498165175, 'lat': 50.90690477827913}, 'geo_shape': {'type': 'Feature', 'geometry': {'coordinates': [3.920956498165175, 50.90690477827913], 'type': 'Point'}, 'properties': {}}}, {'datum': '2023-06', 'installatienaam_nederlands': 'BRUSSEL-ZUID', 'installatienaam_frans': 'BRUXELLES-MIDI', 'installatienaam_engels': 'BRUSSELS-SOUTH'`

## `nationale-stiptheid-per-maand`

- Titel: Nationale stiptheid per maand
- Laatst gewijzigd: 2025-11-07T10:00:00+00:00 · records: 129
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p>Het stiptheidspercentage geeft het percentage weer van alle binnenlandse treinen die in een periode van een maand aangekomen zijn op hun eindbestemmingsstation met een vertraging van maximaal 5 minuten en 59 seconden. Voor de treinen die door de Brusselse Noord-Zuid verbinding rijden, geldt als metingspunt de aankomst in het eerste station van de verbinding dat zij op hun reisweg aandoen.</p><p
- Velden: `jaar` (date), `maand` (date), `regelmaat` (double), `tel` (int), `reg` (int), `min_rt` (int), `regelmaatneutralisatie` (double), `reg_neutr` (int), `tel_ytd` (int), `reg_ytd` (int), `regelmaat_ytd` (double)
- Voorbeeld: `[{'jaar': '2016', 'maand': '2016-02', 'regelmaat': 90.87574462257784, 'tel': 102233, 'reg': 92905, 'min_rt': 203292, 'regelmaatneutralisatie': 95.16594446020366, 'reg_neutr': 97291, 'tel_ytd': 202266, 'reg_ytd': 182804, 'regelmaat_ytd': 90.37801706663502}, {'jaar': '2016', 'maand': '2016-04', 'regelmaat': 90.56748080387244, 'tel': 99369, 'reg': 89996, 'min_rt': 195684, 'regelmaatneutralisatie': 96.48481920921012, 'reg_neutr': 95876, 'tel_ytd': 406313, 'reg_ytd': 367793, 'regelmaat_ytd': 90.51962403368832}, {'jaar': '2017', 'maand': '2017-06', 'regelmaat': 87.28014370181873, 'tel': 106888, 'reg': 93292, 'min_rt': 273664, 'regelmaatneutralisatie': 92.02903974253425, 'reg_neutr': 98368, 'tel_yt`

## `data_punctualite_trainic`

- Titel: Stiptheid van IC-relatie
- Laatst gewijzigd: 2025-11-07T10:00:00+00:00 · records: 10219
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p>Maandelijkse stiptheid van IC-relaties bij aankomst op hun eindbestemming. Voor de treinen die door de Brusselse Noord-Zuid verbinding rijden, geldt hiervoor het eerste station van de verbinding dat zij op hun reisweg aandoen. </p><p>Een trein wordt als stipt beschouwd als hij met minder dan 6 minuten vertraging in het station aankomt.</p>
- Velden: `maand` (date), `relatie` (text), `op_stat` (text), `regelmaat` (double), `tel` (int), `reg` (int), `min_rt` (int)
- Voorbeeld: `[{'maand': '2016-01', 'relatie': 'IC 02', 'op_stat': 'OOSTENDE', 'regelmaat': 90.15151515151516, 'tel': 528, 'reg': 476, 'min_rt': 1062}, {'maand': '2016-01', 'relatie': 'IC 03-2', 'op_stat': 'BLANKENBERGE', 'regelmaat': 91.28014842300557, 'tel': 539, 'reg': 492, 'min_rt': 933}, {'maand': '2016-01', 'relatie': 'IC 03-2', 'op_stat': 'BRUGGE', 'regelmaat': 94.12878787878788, 'tel': 528, 'reg': 497, 'min_rt': 523}]`

## `stiptheid-van-eurostar-treinen`

- Titel: Stiptheid van Eurostar - London Route treinen
- Laatst gewijzigd: 2025-11-07T10:00:00+00:00 · records: 129
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p>Maandelijkse stiptheid van Eurostar - London Route treinen op het Infrabel netwerk. </p><p>Vanaf 1 oktober 2023 wordt het merk Thalys vervangen door het merk Eurostar. Om de treinen naar Londen te onderscheiden van de continentale treinen, zullen de treinen op de Thalys-lijnen voortaan <b>'<a href="https://opendata.infrabel.be/explore/dataset/stiptheid-van-thalys-treinen/" target="_blank">Euros
- Velden: `jaar` (date), `maand1` (date), `tot` (int), `regnet_nmbs` (int), `nmbs` (double)
- Voorbeeld: `[{'jaar': '2016', 'maand1': '2016-04', 'tot': 555, 'regnet_nmbs': 528, 'nmbs': 95.13513513513514}, {'jaar': '2016', 'maand1': '2016-07', 'tot': 570, 'regnet_nmbs': 548, 'nmbs': 96.14035087719299}, {'jaar': '2016', 'maand1': '2016-09', 'tot': 526, 'regnet_nmbs': 513, 'nmbs': 97.52851711026615}]`

## `nationale-stiptheid-met-afgeschafte-treinen`

- Titel: Nationale stiptheid gemeten met afgeschafte treinen
- Laatst gewijzigd: 2025-11-07T10:00:00+00:00 · records: 129
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p>Het stiptheidspercentage geeft weer hoeveel procent van alle binnenlandse treinen, over een periode van een maand, met een vertraging van maximaal 5 minuten en 59 seconden aangekomen zijn in hun eindbestemmingsstation (voor de treinen die door de Brusselse Noord-Zuid verbinding rijden, geldt het eerste station van de Brusselse Noord-Zuid verbinding dat zij op hun reisweg aandoen), vergeleken me
- Velden: `maand2` (date), `tel` (int), `reg` (int), `id` (double)
- Voorbeeld: `[{'maand2': '2016-02', 'tel': 103564, 'reg': 92905, 'id': 89.70781352593565}, {'maand2': '2016-07', 'tel': 101208, 'reg': 93071, 'id': 91.96012172950755}, {'maand2': '2016-09', 'tel': 106295, 'reg': 94621, 'id': 89.0173573545322}]`

## `stiptheid-per-type-trein-en-per-moment`

- Titel: Stiptheid per type trein en per moment
- Laatst gewijzigd: 2025-11-07T10:00:00+00:00 · records: 1783
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p>Maandelijkse stiptheid per type trein (IC, S, P, L) en per moment (ochtend- en avondspits, daluren en weekend).</p><p>Het stiptheidspercentage geeft aan hoeveel procent van alle binnenlandse treinen, over een periode van een maand, met een vertraging van maximaal 5 minuten en 59 seconden, aangekomen zijn in hun eindbestemmingsstation. Voor de treinen die door de Brusselse Noord-Zuid verbinding 
- Velden: `maand` (date), `rel` (text), `regperiode` (text), `instant` (text), `moment_of_day` (text), `regelmaat` (double), `tel` (int), `reg` (int), `min_rt` (double)
- Voorbeeld: `[{'maand': '2016-01', 'rel': 'IC', 'regperiode': 'Avondspits', 'instant': 'Pointe du soir', 'moment_of_day': 'Evening peak hour', 'regelmaat': 85.71428571428571, 'tel': 6041, 'reg': 5178, 'min_rt': 18194.0}, {'maand': '2016-01', 'rel': 'L', 'regperiode': 'Avondspits', 'instant': 'Pointe du soir', 'moment_of_day': 'Evening peak hour', 'regelmaat': 90.01284521515736, 'tel': 3114, 'reg': 2803, 'min_rt': 5880.0}, {'maand': '2016-01', 'rel': 'L', 'regperiode': 'Daluren', 'instant': 'Heures creuses', 'moment_of_day': 'Off-peak hours', 'regelmaat': 92.95737819227752, 'tel': 11473, 'reg': 10665, 'min_rt': 17866.0}]`

## `stiptheid-bij-aankomst-in-brussels`

- Titel: Stiptheid bij aankomst in Brussel
- Laatst gewijzigd: 2025-11-07T10:00:00+00:00 · records: 129
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p>Maandelijkse stiptheid bij aankomst in het eerste Brusselse station van de Noord-Zuidverbinding. De trein wordt als stipt beschouwd als hij met minder dan 6 minuten vertraging in het station aankomt.</p>
- Velden: `maand` (date), `regelmaat` (double), `tel` (int), `reg` (int), `min_rt` (int)
- Voorbeeld: `[{'maand': '2016-05', 'regelmaat': 89.78887134964482, 'tel': 20272, 'reg': 18202, 'min_rt': 46890}, {'maand': '2016-09', 'regelmaat': 90.94628935693673, 'tel': 23217, 'reg': 21115, 'min_rt': 46445}, {'maand': '2017-02', 'regelmaat': 89.83976141131275, 'tel': 19783, 'reg': 17773, 'min_rt': 44389}]`

## `afgeschafte-treinen-per-maand-vanaf-2020`

- Titel: Afgeschafte treinen per maand vanaf 2020 (archive)
- Laatst gewijzigd: 2025-11-07T10:00:00+00:00 · records: 74
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p>Aantal en percentage afgeschafte treinen per maand. </p><p>Een trein kan worden afgeschaft over het geheel van zijn reisweg of over een deel daarvan.</p> <p>Tot september 2022 werd het percentage van afgeschafte treinen berekend met de verhouding tussen het maandelijkse aantal geannuleerde treinen en het aantal metingen in dezelfde periode. Op dezelfde wijze als voor de berekening van de stipth
- Velden: `maand` (date), `sup` (int), `partieel` (int), `totaal` (int), `aantal_treinen` (int), `sup0` (double)
- Voorbeeld: `[{'maand': '2020-01', 'sup': 2026, 'partieel': 1388, 'totaal': 638, 'aantal_treinen': 97908, 'sup0': 2.027338043108452}, {'maand': '2020-04', 'sup': 694, 'partieel': 421, 'totaal': 273, 'aantal_treinen': 53148, 'sup0': 1.2889565766501987}, {'maand': '2020-05', 'sup': 1615, 'partieel': 1213, 'totaal': 402, 'aantal_treinen': 88333, 'sup0': 1.7954818339485035}]`

## `spoorlopers`

- Titel: Spoorlopers
- Laatst gewijzigd: 2022-07-05T14:22:53.366000+00:00 · records: 100
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p> Spoorlopers zijn mensen die langs of op het spoor lopen. Spoorlopen is levensgevaarlijk en schadelijk voor de stiptheid. Infrabel is volop bezig met het beveiligen van de gevoeligste punten en het voorzien van verschillende technische en infrastructurele maatregelen tegen spoorlopen : </p><ul><li>struikelmatten die het door hun oneffenheid onmogelijk maken om het spoor over te steken;</li><li>
- Velden: `empty` (date), `kwartaal` (text), `indicator_id_nl` (text), `indicator_id_fr` (text), `indicator_id_en` (text), `aantal` (double)
- Voorbeeld: `[{'empty': '2014', 'kwartaal': 'Q4', 'indicator_id_nl': 'Meldingen van spoorlopers', 'indicator_id_fr': "Signalements d'intrusions", 'indicator_id_en': 'Intrusions reported', 'aantal': 108.0}, {'empty': '2014', 'kwartaal': 'Q4', 'indicator_id_nl': 'Doden/zwaargewond (FWI)', 'indicator_id_fr': 'Morts/Blessés graves (FWI)', 'indicator_id_en': 'Dead/seriously injured (FWI)', 'aantal': 5.1}, {'empty': '2015', 'kwartaal': 'Q1', 'indicator_id_nl': 'Meldingen van spoorlopers', 'indicator_id_fr': "Signalements d'intrusions", 'indicator_id_en': 'Intrusions reported', 'aantal': 109.0}]`

## `belangrijkste-incidenten`

- Titel: Belangrijkste incidenten en gevolgen voor de stiptheid
- Laatst gewijzigd: 2025-11-07T10:00:00+00:00 · records: 936
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p>Lijst van incidenten die in de loop van de maand meer dan 1.000 minuten vertraging bij reizigerstreinen hebben veroorzaakt. In de dataset is ook opgenomen hoeveel minuten vertraging en hoeveel afgeschafte reizigerstreinen aan dit incident worden toegeschreven. Het lijnnummer en de plaats van het incident zijn ook gegeven.</p><p><b>Nota bene </b>: Als onafhankelijk infrastructuurbeheerder en beh
- Velden: `month` (date), `date` (date), `lijn` (text), `plaats` (text), `lieu` (text), `place` (text), `aard_van_incident` (text), `description_de_l_incident` (text), `incident_desciption` (text), `min_delay` (int), `sup` (int)
- Voorbeeld: `[{'month': '2019-01', 'date': '2019-01-03', 'lijn': '96', 'plaats': 'SOIGNIES', 'lieu': 'SOIGNIES', 'place': 'SOIGNIES', 'aard_van_incident': 'Schade bovenleiding', 'description_de_l_incident': 'Avarie caténaire', 'incident_desciption': 'Damage catenary', 'min_delay': 1513, 'sup': 41}, {'month': '2019-01', 'date': '2019-01-15', 'lijn': '50A', 'plaats': 'Y.MEULEWIJK', 'lieu': 'Y.MEULEWIJK', 'place': 'Y.MEULEWIJK', 'aard_van_incident': 'Schade bovenleiding', 'description_de_l_incident': 'Avarie caténaire', 'incident_desciption': 'Damage catenary', 'min_delay': 1776, 'sup': 23}, {'month': '2019-01', 'date': '2019-01-18', 'lijn': '161', 'plaats': 'GROENENDAAL', 'lieu': 'GROENENDAAL', 'place': 'G`

## `ruwe-gegevens-van-stiptheid-d-1`

- Titel: Ruwe gegevens van stiptheid D-1
- Laatst gewijzigd: 2022-07-05T14:23:14.828000+00:00 · records: 44296
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p> Ruwe gegevens van vertrek en aankomst van (nationale en internationale) reizigerstreinen op al hun stations per dag per treinnummer. Data over de relaties en de spoorlijnen worden ook gegeven.</p><p>Deze dataset wordt dagelijks bijgewerkt met de gegevens van de vorige dag en deze update overschrijft de reeds bestaande gegevens.</p><p> Vertragingen worden aangegeven in seconden, "negatieve" ver
- Velden: `datdep` (date), `train_no` (text), `relation` (text), `train_serv` (text), `line_no_dep` (text), `real_time_arr` (text), `real_time_dep` (text), `planned_time_arr` (text), `planned_time_dep` (text), `delay_arr` (int), `delay_dep` (int), `relation_direction` (text), `ptcar_lg_nm_nl` (text), `line_no_arr` (text), `planned_date_arr` (date), `planned_date_dep` (date), `real_date_arr` (date), `real_date_dep` (date)
- Voorbeeld: `[{'datdep': '2026-10-12', 'train_no': '5727', 'relation': 'IC 24', 'train_serv': 'SNCB/NMBS', 'line_no_dep': '139', 'real_time_arr': '06:33:24', 'real_time_dep': '06:33:24', 'planned_time_arr': '06:31:00', 'planned_time_dep': '06:31:00', 'delay_arr': 144, 'delay_dep': 144, 'relation_direction': 'IC 24: LEUVEN -> CHARLEROI-CENTRAL', 'ptcar_lg_nm_nl': 'SINT-JORIS-WEERT', 'line_no_arr': '139', 'planned_date_arr': '2026-10-12', 'planned_date_dep': '2026-10-12', 'real_date_arr': '2026-10-12', 'real_date_dep': '2026-10-12'}, {'datdep': '2026-10-12', 'train_no': '5727', 'relation': 'IC 24', 'train_serv': 'SNCB/NMBS', 'line_no_dep': '139', 'real_time_arr': '06:35:06', 'real_time_dep': '06:35:06', 'p`

## `station_to_station`

- Titel: Voorstelling van de afstanden tussen aangrenzende stations op het spoorwegnet
- Laatst gewijzigd: 2022-07-05T14:23:19.314000+00:00 · records: 1385
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p>Indeling van het Infrabel-spoornetwerk volgens de kortste weg tussen twee aangrenzende reizigersstations op de reizigerslijnen. Deze lijst geeft ook een schatting van de afstand.</p> <p><b>Belangrijke opmerkingen:</b></p> <ul> <li>Als er twee trajecten mogelijk zijn tussen twee stations, werd het kortste traject gekozen.</li> <li>Het is aan de gebruikers om de fragmenten samen te brengen om de 
- Velden: `geo_shape` (geo_shape), `stationfrom_id` (text), `stationfrom_name` (text), `stationto_id` (text), `stationto_name` (text), `length` (double), `geo_point_2d` (geo_point_2d)
- Voorbeeld: `[{'geo_shape': {'type': 'Feature', 'geometry': {'coordinates': [[4.384250449864733, 50.50601206060287], [4.384444453534281, 50.505882480912895], [4.385064715374473, 50.50570494022463], [4.385683097849061, 50.50552710691666], [4.385993825734153, 50.50543230336324], [4.386145850422793, 50.505384045009215], [4.386296244656877, 50.50533520652116], [4.386642056844919, 50.505216295577874], [4.386833169290271, 50.50514679967691], [4.387023904161307, 50.50507904513669], [4.387687826083663, 50.50480810521252], [4.388323317621768, 50.504509345900914], [4.388634546895078, 50.50435097290422], [4.388926588995806, 50.50419399780002], [4.389244815329032, 50.504011361420446], [4.389555200867451, 50.50382303`

## `data_punctualite_typedetrain`

- Titel: Stiptheid per type trein per maand
- Laatst gewijzigd: 2025-11-07T10:00:00+00:00 · records: 477
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p>Maandelijkse stiptheid per type trein : L, S, P, IC</p><p>Het stiptheidspercentage geeft weer hoeveel procent van alle binnenlandse treinen, over een periode van een maand, met een vertraging van maximaal 5 minuten en 59 seconden, aangekomen zijn in hun eindbestemmingsstation. Voor de treinen die door de Brusselse Noord-Zuid verbinding rijden, geldt het eerste station van de verbinding dat zij 
- Velden: `maand` (date), `rel` (text), `regelmaat` (double), `tel` (int), `reg` (int), `min_rt` (int)
- Voorbeeld: `[{'maand': '2016-02', 'rel': 'S', 'regelmaat': 92.473172964451, 'tel': 19663, 'reg': 18183, 'min_rt': 33508}, {'maand': '2016-03', 'rel': 'IC', 'regelmaat': 89.78940650925335, 'tel': 50144, 'reg': 45024, 'min_rt': 112516}, {'maand': '2016-03', 'rel': 'P', 'regelmaat': 87.54200950283926, 'tel': 8629, 'reg': 7554, 'min_rt': 20811}]`

## `stiptheid-tgv`

- Titel: Stiptheid TGV
- Laatst gewijzigd: 2025-11-07T10:00:00+00:00 · records: 128
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p>Maandelijkse stiptheid van TGV's op het Infrabel netwerk. </p><p>Een TGV wordt als stipt beschouwd indien hij minder dan 6 minuten vertraging oploopt op het netwerk.</p>
- Velden: `maand1` (date), `tot` (int), `regnet` (int), `id` (double)
- Voorbeeld: `[{'maand1': '2016-01', 'tot': 395, 'regnet': 384, 'id': 96.7}, {'maand1': '2016-02', 'tot': 397, 'regnet': 385, 'id': 95.5}, {'maand1': '2016-04', 'tot': 347, 'regnet': 340, 'id': 97.1}]`

## `nationale-gepondereerde-stiptheid-per-maand`

- Titel: Nationale gepondereerde stiptheid per maand
- Laatst gewijzigd: 2025-11-07T10:00:00+00:00 · records: 129
- Licentie: Open licentie CC0 - Universeel
- Beschrijving: <p>Dit gepondereerd percentage houdt rekening met het aantal reizigers aan boord van de treinen: de vertraging van een volle trein in de spits weegt bijvoorbeeld zwaarder door dan die van een minder volle trein in de daluren.</p><p>Het stiptheidspercentage geeft aan hoeveel procent van alle binnenlandse treinen, over een periode van een maand, met een vertraging van maximaal 5 minuten en 59 second
- Velden: `maand2` (date), `tel` (double), `reg` (double), `id` (double)
- Voorbeeld: `[{'maand2': '2016-05', 'tel': 141628.0, 'reg': 124147.0, 'id': 87.65710170305306}, {'maand2': '2016-08', 'tel': 161049.0, 'reg': 146139.0, 'id': 90.74194810275134}, {'maand2': '2017-03', 'tel': 177300.0, 'reg': 155838.0, 'id': 87.89509306260575}]`

