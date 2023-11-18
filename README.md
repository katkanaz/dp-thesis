1. Knižnice potrebné v rámci týchto skriptov sú v `requirements.txt` a môžu byť nainštalované
naraz pomocou`pip install -r requirements.txt`.
2. Pred spustením 1.skriptu `1_download_files.py` je nutné vytvoriť priečinok `data`, ktorý bude obsahovať
modelový súbor `components.cif.gz`s ideálnymi súradnicami (dostupný na stránkachChemical Components Dictionary).
Tiež musí obsahovať súbor `pdb_ids_PQ.json` s PDB kódmi štruktúr s cukrami získanými pomocou PatternQuery(PQ),
(extrakcia PDB kódov z PQ výsledkov - `misc_functions.get_pdb_ids_from_pq()`).
3. `1_download_files.py` - Stiahnutie mmCIF súborov štruktúr obsahujúcich sacharidy a tiež ich validačných súborov.
3. `2_categorize.py` - Roztriedenie jednotlivých cukorných rezdiuí na ligandy, glykozylácie a blízke kontakty.
4. `3_get_rscc_and_resolution.py` - Extrakcia celkového rozlíšenia štruktúr a hodnôt RSCC pre jednotlivé reziduá,
pre ktoré tento údaj existuje.
5. Pred spustením MotiveValidator (MV) je nutné z modelového `components.cif.gz` súboru odstrániť nesacharidové reziduá
(`misc_functions.remove_nonsugar_residues()`).
6. `misc_functions.get_rmsd_and_merge()` - Extrakcia RMSD z výsledkov MV a spojenie do jedného csv súboru spolu s
hodnotami RSCC a celkovým rozlíšením.
7. `4_graphs.py` - Vytvorenie korelácie medzi RMSD a RSCC a tiež histogramy frekvencie hodnôt RMSD pre 10
najčastejšie sa vyskytujúcich typov cukrov.
8. `misc_functions.get_average_rmsd_of_peaks()` - Priemerne RMSD píkov tvoriacich sa v historame, treba ručne upraviť
podľa toho ktorý chceme pík.
9. `misc_functions.analyze_graph()` - Aké typy cukrov sa vyskytujú v jednotlivých častiach grafu.
10. `misc_functions.remove_O6()` - Vymazanie kysíku O6 z cukrov kde sa vyskytovali dva píky.
11. `misc_functions.filter_ligands()` - Filtrácia dát ligandov, podľa zvolených kritérií kvality.
12. `5_run_PQ.py` - Extrakcia okolí špecifikovaného typu cukru.
13. `6_all_against_all_alignment.py` - Filtrácia a úprava získaných okolí a výpočet hodnôt RMSD každého okolia s každým.
14. `7_cluster_data.py` - Hierarchické klastrovanie okolí a získanie reprezentatívnych okolí pre každý klaster.
15. `misc_functions.compare_clusters()` - Koľkým klastrom z align-dát odpovedá klaster zo super dát.
16. `misc_functions.create_tanglegram()` - Tvorba tanglegramu na porovnanie dendrogramov z align- a super-dát
