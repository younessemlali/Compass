import re
import sys
import os


def corriger_xml_compass(contenu_bytes):
    """
    Corrections pour les contrats Compass Group :
    1. Supprimer les blocs StaffingShift parasites (shiftPeriod != "weekly")
    2. Supprimer les balises superflues dans le bloc weekly : <Name>, <n>, <Hours>, <StartTime>, <Comment>
    3. Signaler les contrats avec IdValue non numérique à 6 chiffres (correction manuelle requise)
    """

    contenu = contenu_bytes.decode("iso-8859-1")
    warnings = []

    # Étape 1 : supprimer les blocs StaffingShift parasites (tout sauf shiftPeriod="weekly")
    pattern_bloc_parasite = re.compile(
        r'[ \t]*<StaffingShift\s+shiftPeriod="(?!weekly)[^"]*">.*?</StaffingShift>\r?\n?',
        re.DOTALL
    )
    contenu = pattern_bloc_parasite.sub("", contenu)

    # Étape 2 : supprimer balises superflues dans les blocs weekly restants
    for balise in ["Name", "n", "Hours", "StartTime", "Comment"]:
        pattern = re.compile(
            r'[ \t]*<' + balise + r'(\s[^>]*)?>.*?</' + balise + r'>\r?\n?',
            re.DOTALL
        )
        contenu = pattern.sub("", contenu)

    # Étape 3 : détecter les IdValue invalides (pas un code numérique à 6 chiffres)
    pattern_contrats = re.compile(
        r'<ContractId[^>]*>\s*<IdValue>([^<]+)</IdValue>\s*</ContractId>'
    )
    contrat_ids = pattern_contrats.findall(contenu)

    pattern_idvalue = re.compile(
        r'<StaffingShift shiftPeriod="weekly">.*?<IdValue[^>]*>([^<]+)</IdValue>',
        re.DOTALL
    )
    idvalues = pattern_idvalue.findall(contenu)

    for i, val in enumerate(idvalues):
        val = val.strip()
        if not re.match(r'^\d{6}$', val):
            contrat_ref = contrat_ids[i] if i < len(contrat_ids) else f"contrat #{i+1}"
            warnings.append(
                f"⚠️  Contrat {contrat_ref} : IdValue = '{val}' — code horaire invalide "
                f"(doit être numérique à 6 chiffres). Correction manuelle requise."
            )

    return contenu.encode("iso-8859-1"), warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python compass_corrector.py <fichier_xml> [dossier_sortie]")
        sys.exit(1)

    fichier = sys.argv[1]
    dossier_sortie = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(fichier))

    with open(fichier, "rb") as f:
        contenu = f.read()

    contenu_corrige, warnings = corriger_xml_compass(contenu)

    nom_fichier = os.path.basename(fichier)
    base, ext = os.path.splitext(nom_fichier)
    sortie = os.path.join(dossier_sortie, base + "_CORRIGE" + ext)

    with open(sortie, "wb") as f:
        f.write(contenu_corrige)

    print(f"✅ Fichier corrigé : {sortie}")

    if warnings:
        print("\n--- AVERTISSEMENTS (corrections manuelles requises) ---")
        for w in warnings:
            print(w)
    else:
        print("✅ Tous les codes horaires sont valides.")


if __name__ == "__main__":
    main()
