import json
import subprocess
import sys

def ExtractFromModel(model, md_content):
    prompt = f"""Tu es un expert en extraction de données de factures.

    Extrait les informations clés de cette facture en format Markdown et retourne UNIQUEMENT un objet JSON valide avec ces champs exacts :

    {{
        "Nom de la societe": "",
        "Adresse": "",
        "Numero de la facture": "",
        "Date de la facture": "",
        "Client": "",
        "Total Hors Taxes (Total HT)": "",
        "Droit de timbre sur consommation": "",
        "Timbre fiscal": "",
        "Montant TTC": "",
        "TVA percentage": "",
        "TVA": "",
        "MF_CLIENT": "",
        "MF_FOURNISSEUR": ""
    }}

INSTRUCTIONS IMPORTANTES :
- Retourne UNIQUEMENT le JSON, aucun texte supplémentaire
- Utilise des guillemets doubles pour toutes les clés et valeurs
- Si une information n'existe pas, mets une chaîne vide ""
- Les montants doivent être des chaînes de caractères
- Assure-toi que le JSON est valide et bien formé

    Contenu de la facture :
    {md_content}"""
    
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        
        output = result.stdout.strip()
        
        json_start = output.find('{')
        json_end = output.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            print(f"No JSON found in output from {model}")
            print("Raw output:")
            print(output)
            return None
            
        json_str = output[json_start:json_end]
        
        try:
            data = json.loads(json_str)
            
            clean_data = {}
            for key in [
                "Nom de la societe", "Adresse", "Numero de la facture", 
                "Date de la facture", "Client", "Total Hors Taxes (Total HT)",
                "Droit de timbre sur consommation", "Timbre fiscal", 
                "Montant TTC", "TVA percentage", "TVA", 
                "MF_CLIENT", "MF_FOURNISSEUR"
            ]:
                if key in data:
                    clean_data[key] = data[key]
                else:
                    clean_data[key] = ""
            return clean_data
        except json.JSONDecodeError as e:
            print(f"Invalid JSON from {model}: {str(e)}")
            print("Problematic output:")
            print(json_str)
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"Error running model {model}: {e.stderr}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error with model {model}: {str(e)}", file=sys.stderr)
        return None

if __name__ == "__main__":
    md_file = "factureOffice.md"
    
    try:
        with open(md_file, "r", encoding="utf-8") as f:
            md_content = f.read()
            
        print("Trying llama3")
        res1 = ExtractFromModel("llama3", md_content)
        if res1:
            print(json.dumps(res1, indent=4, ensure_ascii=False))
        
        print("\nTrying Mistral")
        res2 = ExtractFromModel("mistral", md_content)
        if res2:
            print(json.dumps(res2, indent=4, ensure_ascii=False))
        
        print("\nTrying phi3")
        res3 = ExtractFromModel("phi3", md_content)
        if res3:
            print(json.dumps(res3, indent=4, ensure_ascii=False))
            
    except FileNotFoundError:
        print(f"Error: File {md_file} not found", file=sys.stderr)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)