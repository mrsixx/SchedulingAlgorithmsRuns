echo "iniciando compilação dos resultados"

#python3 result-compiler.py results_dir output_prefix renamer_fn
python3 result-compiler.py ant-battle-royale/070525/6_Fattahi/V0 6_Fattahi-V0 fattahi
python3 result-compiler.py ant-battle-royale/070525/6_Fattahi/V1 6_Fattahi-V1 fattahi
python3 result-compiler.py ant-battle-royale/070525/6_Fattahi/V2 6_Fattahi-V2 fattahi
python3 result-compiler.py ant-battle-royale/070525/6_Fattahi/V3 6_Fattahi-V3 fattahi


python3 result-compiler.py ant-battle-royale/090525/1_Brandimarte/V0 1_Brandimarte-V0 brandimarte
python3 result-compiler.py ant-battle-royale/090525/1_Brandimarte/V1 1_Brandimarte-V1 brandimarte
python3 result-compiler.py ant-battle-royale/090525/1_Brandimarte/V2 1_Brandimarte-V2 brandimarte
python3 result-compiler.py ant-battle-royale/090525/1_Brandimarte/V3 1_Brandimarte-V3 brandimarte

echo "compilação finalizada"
