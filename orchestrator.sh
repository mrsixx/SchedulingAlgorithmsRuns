#find folder -name '*.json' -exec mv {} to_path \;
#find folder -name '*V0*.json' -exec mv {} to_path \;

echo "iniciando compilação dos resultados"

#python3 result-compiler.py results_dir output_prefix renamer_fn

# python3 result-compiler.py ant-battle-royale/070525/6_Fattahi/V0 6_Fattahi-V0 fattahi
# python3 result-compiler.py ant-battle-royale/070525/6_Fattahi/V1 6_Fattahi-V1 fattahi
# python3 result-compiler.py ant-battle-royale/070525/6_Fattahi/V2 6_Fattahi-V2 fattahi
# python3 result-compiler.py ant-battle-royale/070525/6_Fattahi/V3 6_Fattahi-V3 fattahi


# python3 result-compiler.py ant-battle-royale/090525/1_Brandimarte/V0 1_Brandimarte-V0 brandimarte
# python3 result-compiler.py ant-battle-royale/090525/1_Brandimarte/V1 1_Brandimarte-V1 brandimarte
# python3 result-compiler.py ant-battle-royale/090525/1_Brandimarte/V2 1_Brandimarte-V2 brandimarte
# python3 result-compiler.py ant-battle-royale/090525/1_Brandimarte/V3 1_Brandimarte-V3 brandimarte


# python3 result-compiler.py ant-battle-royale/090525/9_Ribeiro/V2 9_Ribeiro-V2 ribeiro
# python3 result-compiler.py ant-battle-royale/090525/9_Ribeiro/V3 9_Ribeiro-V3 ribeiro

# python3 result-compiler.py ant-battle-royale/090525/3_DPpaulli/V2 3_DPpaulli-V2 paulli
# python3 result-compiler.py ant-battle-royale/090525/3_DPpaulli/V3 3_DPpaulli-V3 paulli

python3 result-compiler.py ant-battle-royale/30052025/6_Fattahi/V0 6_Fattahi-V0 fattahi
python3 result-compiler.py ant-battle-royale/30052025/6_Fattahi/V1 6_Fattahi-V1 fattahi
echo "compilação finalizada"
