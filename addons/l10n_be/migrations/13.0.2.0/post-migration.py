from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)

ACCOUNT_TAX_NAMES = [
    # In version 9.0
    {
        "attn_VAT-OUT-21-S": "21% Services",
        "attn_VAT-OUT-21-L": "21%",
        "attn_VAT-OUT-12-S": "12% Services",
        "attn_VAT-OUT-12-L": "12%",
        "attn_VAT-OUT-06-S": "6% Services",
        "attn_VAT-OUT-06-L": "6%",
        "attn_VAT-OUT-00-S": "0% Services",
        "attn_VAT-OUT-00-L": "0%",
        "attn_VAT-OUT-00-CC": "0% Cocontractant",
        "attn_VAT-OUT-00-EU-S": "0% EU Services",
        "attn_VAT-OUT-00-EU-L": "0% EU L",
        "attn_VAT-OUT-00-EU-T": "0% EU T",
        "attn_VAT-OUT-00-ROW": "0% Export Non EU",
        "attn_VAT-IN-V81-21": "21% Marchandises",
        "attn_VAT-IN-V81-12": "12% Marchandises",
        "attn_VAT-IN-V81-06": "6% Marchandises",
        "attn_VAT-IN-V81-00": "0% Marchandises",
        "attn_VAT-IN-V82-21-S": "21% Services",
        "attn_VAT-IN-V82-21-G": "21% Biens divers",
        "attn_VAT-IN-V82-12-S": "12% Services",
        "attn_VAT-IN-V82-12-G": "12% Biens divers",
        "attn_VAT-IN-V82-06-S": "6% Services",
        "attn_VAT-IN-V82-06-G": "6% Biens divers",
        "attn_VAT-IN-V82-00-S": "0% Services",
        "attn_VAT-IN-V82-00-G": "0% Biens divers",
        "attn_VAT-IN-V83-21": "21% Biens d'investissement",
        "attn_VAT-IN-V83-12": "12% Biens d'investissement",
        "attn_VAT-IN-V83-06": "6% Biens d'investissement",
        "attn_VAT-IN-V83-00": "0% Biens d'investissement",
        "attn_VAT-IN-V81-21-CC-C1": "VAT-IN-V81-21-CC-C1",
        "attn_VAT-IN-V81-21-CC-C2": "VAT-IN-V81-21-CC-C2",
        "attn_VAT-IN-V81-21-CC": "21% Cocontract. - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-12-CC-C1": "VAT-IN-V81-12-CC-C1",
        "attn_VAT-IN-V81-12-CC-C2": "VAT-IN-V81-12-CC-C2",
        "attn_VAT-IN-V81-12-CC": "12% Cocontract. - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-06-CC-C1": "VAT-IN-V81-06-CC-C1",
        "attn_VAT-IN-V81-06-CC-C2": "VAT-IN-V81-06-CC-C2",
        "attn_VAT-IN-V81-06-CC": "TVA Déductible 6% Cocontract. - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-00-CC": "TVA à l'entrée 0% Cocontract. - Approvisionn. et marchandises",
        "attn_VAT-IN-V82-21-CC-C1": "VAT-IN-V82-21-CC-C1",
        "attn_VAT-IN-V82-21-CC-C2": "VAT-IN-V82-21-CC-C2",
        "attn_VAT-IN-V82-21-CC": "TVA Déductible 21% Cocontract. - Services and other goods",
        "attn_VAT-IN-V82-12-CC-C1": "VAT-IN-V82-12-CC-C1",
        "attn_VAT-IN-V82-12-CC-C2": "VAT-IN-V82-12-CC-C2",
        "attn_VAT-IN-V82-12-CC": "TVA Déductible 12% Cocontract. - Services and other goods",
        "attn_VAT-IN-V82-06-CC-C1": "VAT-IN-V82-06-CC-C1",
        "attn_VAT-IN-V82-06-CC-C2": "VAT-IN-V82-06-CC-C2",
        "attn_VAT-IN-V82-06-CC": "TVA Déductible 6% Cocontract. - Services and other goods",
        "attn_VAT-IN-V82-00-CC": "TVA à l'entrée 0% Cocontract. - Services and other goods",
        "attn_VAT-IN-V83-21-CC-C1": "VAT-IN-V83-21-CC-C1",
        "attn_VAT-IN-V83-21-CC-C2": "VAT-IN-V83-21-CC-C2",
        "attn_VAT-IN-V83-21-CC": "TVA Déductible 21% Cocontract. - Biens d'investissement",
        "attn_VAT-IN-V83-12-CC-C1": "VAT-IN-V83-12-CC-C1",
        "attn_VAT-IN-V83-12-CC-C2": "VAT-IN-V83-12-CC-C2",
        "attn_VAT-IN-V83-12-CC": "TVA Déductible 12% Cocontract. - Biens d'investissement",
        "attn_VAT-IN-V83-06-CC-C1": "VAT-IN-V83-06-CC-C1",
        "attn_VAT-IN-V83-06-CC-C2": "VAT-IN-V83-06-CC-C2",
        "attn_VAT-IN-V83-06-CC": "TVA Déductible 6% Cocontract. - Biens d'investissement",
        "attn_VAT-IN-V83-00-CC": "TVA à l'entrée 0% Cocontract. - Biens d'investissement",
        "attn_VAT-IN-V82-CAR-EXC-C1": "Frais de voiture - TVA 50% Non Deductible",
        "attn_VAT-IN-V82-CAR-EXC-C2": "Frais de voiture - TVA 50% Deductible (Prix Excl.)",
        "attn_VAT-IN-V82-CAR-EXC": "TVA Entrant - Frais de voiture - VAT 50% Non Deductible (Price Excl.)",
        "attn_VAT-IN-V81-21-EU-C1": "VAT-IN-V81-21-EU-C1",
        "attn_VAT-IN-V81-21-EU-C2": "VAT-IN-V81-21-EU-C2",
        "attn_VAT-IN-V81-21-EU": "TVA Déductible 21% Intracomm. - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-12-EU-C1": "VAT-IN-V81-12-EU-C1",
        "attn_VAT-IN-V81-12-EU-C2": "VAT-IN-V81-12-EU-C2",
        "attn_VAT-IN-V81-12-EU": "TVA Déductible 12% Intracomm. - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-06-EU-C1": "VAT-IN-V81-06-EU-C1",
        "attn_VAT-IN-V81-06-EU-C2": "VAT-IN-V81-06-EU-C2",
        "attn_VAT-IN-V81-06-EU": "TVA Déductible 6% Intracomm. - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-00-EU": "TVA à l'entrée 0% Intracomm. - Approvisionn. et marchandises",
        "attn_VAT-IN-V82-21-EU-S-C1": "VAT-IN-V82-21-EU-S-C1",
        "attn_VAT-IN-V82-21-EU-S-C2": "VAT-IN-V82-21-EU-S-C2",
        "attn_VAT-IN-V82-21-EU-S": "TVA Déductible 21% Intracomm. - Services",
        "attn_VAT-IN-V82-21-EU-G-C1": "VAT-IN-V82-21-EU-G-C1",
        "attn_VAT-IN-V82-21-EU-G-C2": "VAT-IN-V82-21-EU-G-C2",
        "attn_VAT-IN-V82-21-EU-G": "TVA Déductible 21% Intracomm. - Biens divers",
        "attn_VAT-IN-V82-12-EU-S-C1": "VAT-IN-V82-12-EU-S-C1",
        "attn_VAT-IN-V82-12-EU-S-C2": "VAT-IN-V82-12-EU-S-C2",
        "attn_VAT-IN-V82-12-EU-S": "TVA Déductible 12% Intracomm. - Services",
        "attn_VAT-IN-V82-12-EU-G-C1": "VAT-IN-V82-12-EU-G-C1",
        "attn_VAT-IN-V82-12-EU-G-C2": "VAT-IN-V82-12-EU-G-C2",
        "attn_VAT-IN-V82-12-EU-G": "TVA Déductible 12% Intracomm. - Biens divers",
        "attn_VAT-IN-V82-06-EU-S-C1": "VAT-IN-V82-06-EU-S-C1",
        "attn_VAT-IN-V82-06-EU-S-C2": "VAT-IN-V82-06-EU-S-C2",
        "attn_VAT-IN-V82-06-EU-S": "TVA Déductible 6% Intracomm. - Services",
        "attn_VAT-IN-V82-06-EU-G-C1": "VAT-IN-V82-06-EU-G-C1",
        "attn_VAT-IN-V82-06-EU-G-C2": "VAT-IN-V82-06-EU-G-C2",
        "attn_VAT-IN-V82-06-EU-G": "TVA Déductible 6% Intracomm. - Biens divers",
        "attn_VAT-IN-V82-00-EU-S": "TVA à l'entrée 0% Intracomm. - Services",
        "attn_VAT-IN-V83-21-EU-C1": "VAT-IN-V83-21-EU-C1",
        "attn_VAT-IN-V83-21-EU-C2": "VAT-IN-V83-21-EU-C2",
        "attn_VAT-IN-V83-21-EU": "TVA Déductible 21% Intracomm. - Biens d'investissement",
        "attn_VAT-IN-V82-00-EU-G": "TVA à l'entrée 0% Intracomm. - Biens divers",
        "attn_VAT-IN-V83-12-EU-C1": "VAT-IN-V83-12-EU-C1",
        "attn_VAT-IN-V83-12-EU-C2": "VAT-IN-V83-12-EU-C2",
        "attn_VAT-IN-V83-12-EU": "TVA Déductible 12% Intracomm. - Biens d'investissement",
        "attn_VAT-IN-V83-06-EU-C1": "VAT-IN-V83-06-EU-C1",
        "attn_VAT-IN-V83-06-EU-C2": "VAT-IN-V83-06-EU-C2",
        "attn_VAT-IN-V83-06-EU": "TVA Déductible 6% Intracomm. - Biens d'investissement",
        "attn_VAT-IN-V83-00-EU": "TVA à l'entrée 0% Intracomm. - Biens d'investissement",
        "attn_VAT-IN-V81-21-ROW-CC-C1": "VAT-IN-V81-21-ROW-CC-C1",
        "attn_VAT-IN-V81-21-ROW-CC-C2": "VAT-IN-V81-21-ROW-CC-C2",
        "attn_VAT-IN-V81-21-ROW-CC": "TVA Déductible 21% Hors EU - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-12-ROW-CC-C1": "VAT-IN-V81-12-ROW-CC-C1",
        "attn_VAT-IN-V81-12-ROW-CC-C2": "VAT-IN-V81-12-ROW-CC-C2",
        "attn_VAT-IN-V81-12-ROW-CC": "TVA Déductible 12% Hors EU - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-06-ROW-CC-C1": "VAT-IN-V81-06-ROW-CC-C1",
        "attn_VAT-IN-V81-06-ROW-CC-C2": "VAT-IN-V81-06-ROW-CC-C2",
        "attn_VAT-IN-V81-06-ROW-CC": "TVA Déductible 6% Hors EU - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-00-ROW-CC": "TVA à l'entrée 0% Hors EU - Approvisionn. et marchandises",
        "attn_VAT-IN-V82-21-ROW-CC-C1": "VAT-IN-V82-21-ROW-CC-C1",
        "attn_VAT-IN-V82-21-ROW-CC-C2": "VAT-IN-V82-21-ROW-CC-C2",
        "attn_VAT-IN-V82-21-ROW-CC": "TVA Déductible 21% Hors EU - Services and other goods",
        "attn_VAT-IN-V82-12-ROW-CC-C1": "VAT-IN-V82-12-ROW-CC-C1",
        "attn_VAT-IN-V82-12-ROW-CC-C2": "VAT-IN-V82-12-ROW-CC-C2",
        "attn_VAT-IN-V82-12-ROW-CC": "TVA Déductible 12% Hors EU - Services and other goods",
        "attn_VAT-IN-V82-06-ROW-CC-C1": "VAT-IN-V82-06-ROW-CC-C1",
        "attn_VAT-IN-V82-06-ROW-CC-C2": "VAT-IN-V82-06-ROW-CC-C2",
        "attn_VAT-IN-V82-06-ROW-CC": "TVA Déductible 6% Hors EU - Services and other goods",
        "attn_VAT-IN-V82-00-ROW-CC": "TVA à l'entrée 0% Hors EU - Services and other goods",
        "attn_VAT-IN-V83-21-ROW-CC-C1": "VAT-IN-V83-21-ROW-CC-C1",
        "attn_VAT-IN-V83-21-ROW-CC-C2": "VAT-IN-V83-21-ROW-CC-C2",
        "attn_VAT-IN-V83-21-ROW-CC": "TVA Déductible 21% Hors EU - Biens d'investissement",
        "attn_VAT-IN-V83-12-ROW-CC-C1": "VAT-IN-V83-12-ROW-CC-C1",
        "attn_VAT-IN-V83-12-ROW-CC-C2": "VAT-IN-V83-12-ROW-CC-C2",
        "attn_VAT-IN-V83-12-ROW-CC": "TVA Déductible 12% Hors EU - Biens d'investissement",
        "attn_VAT-IN-V83-06-ROW-CC-C1": "VAT-IN-V83-06-ROW-CC-C1",
        "attn_VAT-IN-V83-06-ROW-CC-C2": "VAT-IN-V83-06-ROW-CC-C2",
        "attn_VAT-IN-V83-06-ROW-CC": "TVA Déductible 6% Hors EU - Biens d'investissement",
        "attn_VAT-IN-V83-00-ROW-CC": "0% Non EU - Biens d'investissement",
        "attn_VAT-IN-V61": "Régularisation en faveur de l'état",
        "attn_VAT-IN-V62": "Régularisation en faveur du déclarant",
    },

    # In version 10.0
    {
        "attn_VAT-IN-V83-21": "21% Biens d'investissement",
        "attn_VAT-IN-V83-12": "12% Biens d'investissement",
        "attn_VAT-IN-V83-06": "6% Biens d'investissement",
        "attn_VAT-IN-V83-00": "0% Biens d'investissement",
        "attn_VAT-IN-V81-21-CC-C1": "VAT-IN-V81-21-CC-C1",
        "attn_VAT-IN-V81-21-CC-C2": "VAT-IN-V81-21-CC-C2",
        "attn_VAT-IN-V81-21-CC": "21% Cocontract. - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-12-CC-C1": "VAT-IN-V81-12-CC-C1",
        "attn_VAT-IN-V81-12-CC-C2": "VAT-IN-V81-12-CC-C2",
        "attn_VAT-IN-V81-12-CC": "12% Cocontract. - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-06-CC-C1": "VAT-IN-V81-06-CC-C1",
        "attn_VAT-IN-V81-06-CC-C2": "VAT-IN-V81-06-CC-C2",
        "attn_VAT-IN-V81-06-CC": "TVA Déductible 6% Cocontract. - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-00-CC": "TVA à l'entrée 0% Cocontract. - Approvisionn. et marchandises",
        "attn_VAT-IN-V82-21-CC-C1": "VAT-IN-V82-21-CC-C1",
        "attn_VAT-IN-V82-21-CC-C2": "VAT-IN-V82-21-CC-C2",
        "attn_VAT-IN-V82-21-CC": "TVA Déductible 21% Cocontract. - Services and other goods",
        "attn_VAT-IN-V82-12-CC-C1": "VAT-IN-V82-12-CC-C1",
        "attn_VAT-IN-V82-12-CC-C2": "VAT-IN-V82-12-CC-C2",
        "attn_VAT-IN-V82-12-CC": "TVA Déductible 12% Cocontract. - Services and other goods",
        "attn_VAT-IN-V82-06-CC-C1": "VAT-IN-V82-06-CC-C1",
        "attn_VAT-IN-V82-06-CC-C2": "VAT-IN-V82-06-CC-C2",
        "attn_VAT-IN-V82-06-CC": "TVA Déductible 6% Cocontract. - Services and other goods",
        "attn_VAT-IN-V82-00-CC": "TVA à l'entrée 0% Cocontract. - Services and other goods",
        "attn_VAT-IN-V83-21-CC-C1": "VAT-IN-V83-21-CC-C1",
        "attn_VAT-IN-V83-21-CC-C2": "VAT-IN-V83-21-CC-C2",
        "attn_VAT-IN-V83-21-CC": "TVA Déductible 21% Cocontract. - Biens d'investissement",
        "attn_VAT-IN-V83-12-CC-C1": "VAT-IN-V83-12-CC-C1",
        "attn_VAT-IN-V83-12-CC-C2": "VAT-IN-V83-12-CC-C2",
        "attn_VAT-IN-V83-12-CC": "TVA Déductible 12% Cocontract. - Biens d'investissement",
        "attn_VAT-IN-V83-06-CC-C1": "VAT-IN-V83-06-CC-C1",
        "attn_VAT-IN-V83-06-CC-C2": "VAT-IN-V83-06-CC-C2",
        "attn_VAT-IN-V83-06-CC": "TVA Déductible 6% Cocontract. - Biens d'investissement",
        "attn_VAT-IN-V83-00-CC": "TVA à l'entrée 0% Cocontract. - Biens d'investissement",
        "attn_VAT-IN-V82-CAR-EXC-C1": "Frais de voiture - TVA 50% Non Deductible",
        "attn_VAT-IN-V82-CAR-EXC-C2": "Frais de voiture - TVA 50% Deductible (Prix Excl.)",
        "attn_VAT-IN-V82-CAR-EXC": "TVA Entrant - Frais de voiture - VAT 50% Non Deductible (Price Excl.)",
        "attn_VAT-IN-V81-21-EU-C1": "VAT-IN-V81-21-EU-C1",
        "attn_VAT-IN-V81-21-EU-C2": "VAT-IN-V81-21-EU-C2",
        "attn_VAT-IN-V81-21-EU": "TVA Déductible 21% Intracomm. - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-12-EU-C1": "VAT-IN-V81-12-EU-C1",
        "attn_VAT-IN-V81-12-EU-C2": "VAT-IN-V81-12-EU-C2",
        "attn_VAT-IN-V81-12-EU": "TVA Déductible 12% Intracomm. - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-06-EU-C1": "VAT-IN-V81-06-EU-C1",
        "attn_VAT-IN-V81-06-EU-C2": "VAT-IN-V81-06-EU-C2",
        "attn_VAT-IN-V81-06-EU": "TVA Déductible 6% Intracomm. - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-00-EU": "TVA à l'entrée 0% Intracomm. - Approvisionn. et marchandises",
        "attn_VAT-IN-V82-21-EU-S-C1": "VAT-IN-V82-21-EU-S-C1",
        "attn_VAT-IN-V82-21-EU-S-C2": "VAT-IN-V82-21-EU-S-C2",
        "attn_VAT-IN-V82-21-EU-S": "TVA Déductible 21% Intracomm. - Services",
        "attn_VAT-IN-V82-21-EU-G-C1": "VAT-IN-V82-21-EU-G-C1",
        "attn_VAT-IN-V82-21-EU-G-C2": "VAT-IN-V82-21-EU-G-C2",
        "attn_VAT-IN-V82-21-EU-G": "TVA Déductible 21% Intracomm. - Biens divers",
        "attn_VAT-IN-V82-12-EU-S-C1": "VAT-IN-V82-12-EU-S-C1",
        "attn_VAT-IN-V82-12-EU-S-C2": "VAT-IN-V82-12-EU-S-C2",
        "attn_VAT-IN-V82-12-EU-S": "TVA Déductible 12% Intracomm. - Services",
        "attn_VAT-IN-V82-12-EU-G-C1": "VAT-IN-V82-12-EU-G-C1",
        "attn_VAT-IN-V82-12-EU-G-C2": "VAT-IN-V82-12-EU-G-C2",
        "attn_VAT-IN-V82-12-EU-G": "TVA Déductible 12% Intracomm. - Biens divers",
        "attn_VAT-IN-V82-06-EU-S-C1": "VAT-IN-V82-06-EU-S-C1",
        "attn_VAT-IN-V82-06-EU-S-C2": "VAT-IN-V82-06-EU-S-C2",
        "attn_VAT-IN-V82-06-EU-S": "TVA Déductible 6% Intracomm. - Services",
        "attn_VAT-IN-V82-06-EU-G-C1": "VAT-IN-V82-06-EU-G-C1",
        "attn_VAT-IN-V82-06-EU-G-C2": "VAT-IN-V82-06-EU-G-C2",
        "attn_VAT-IN-V82-06-EU-G": "TVA Déductible 6% Intracomm. - Biens divers",
        "attn_VAT-IN-V82-00-EU-S": "TVA à l'entrée 0% Intracomm. - Services",
        "attn_VAT-IN-V83-21-EU-C1": "VAT-IN-V83-21-EU-C1",
        "attn_VAT-IN-V83-21-EU-C2": "VAT-IN-V83-21-EU-C2",
        "attn_VAT-IN-V83-21-EU": "TVA Déductible 21% Intracomm. - Biens d'investissement",
        "attn_VAT-IN-V82-00-EU-G": "TVA à l'entrée 0% Intracomm. - Biens divers",
        "attn_VAT-IN-V83-12-EU-C1": "VAT-IN-V83-12-EU-C1",
        "attn_VAT-IN-V83-12-EU-C2": "VAT-IN-V83-12-EU-C2",
        "attn_VAT-IN-V83-12-EU": "TVA Déductible 12% Intracomm. - Biens d'investissement",
        "attn_VAT-IN-V83-06-EU-C1": "VAT-IN-V83-06-EU-C1",
        "attn_VAT-IN-V83-06-EU-C2": "VAT-IN-V83-06-EU-C2",
        "attn_VAT-IN-V83-06-EU": "TVA Déductible 6% Intracomm. - Biens d'investissement",
        "attn_VAT-IN-V83-00-EU": "TVA à l'entrée 0% Intracomm. - Biens d'investissement",
        "attn_VAT-IN-V81-21-ROW-CC-C1": "VAT-IN-V81-21-ROW-CC-C1",
        "attn_VAT-IN-V81-21-ROW-CC-C2": "VAT-IN-V81-21-ROW-CC-C2",
        "attn_VAT-IN-V81-21-ROW-CC": "TVA Déductible 21% Hors EU - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-12-ROW-CC-C1": "VAT-IN-V81-12-ROW-CC-C1",
        "attn_VAT-IN-V81-12-ROW-CC-C2": "VAT-IN-V81-12-ROW-CC-C2",
        "attn_VAT-IN-V81-12-ROW-CC": "TVA Déductible 12% Hors EU - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-06-ROW-CC-C1": "VAT-IN-V81-06-ROW-CC-C1",
        "attn_VAT-IN-V81-06-ROW-CC-C2": "VAT-IN-V81-06-ROW-CC-C2",
        "attn_VAT-IN-V81-06-ROW-CC": "TVA Déductible 6% Hors EU - Approvisionn. et marchandises",
        "attn_VAT-IN-V81-00-ROW-CC": "TVA à l'entrée 0% Hors EU - Approvisionn. et marchandises",
        "attn_VAT-IN-V82-21-ROW-CC-C1": "VAT-IN-V82-21-ROW-CC-C1",
        "attn_VAT-IN-V82-21-ROW-CC-C2": "VAT-IN-V82-21-ROW-CC-C2",
        "attn_VAT-IN-V82-21-ROW-CC": "TVA Déductible 21% Hors EU - Services and other goods",
        "attn_VAT-IN-V82-12-ROW-CC-C1": "VAT-IN-V82-12-ROW-CC-C1",
        "attn_VAT-IN-V82-12-ROW-CC-C2": "VAT-IN-V82-12-ROW-CC-C2",
        "attn_VAT-IN-V82-12-ROW-CC": "TVA Déductible 12% Hors EU - Services and other goods",
        "attn_VAT-IN-V82-06-ROW-CC-C1": "VAT-IN-V82-06-ROW-CC-C1",
        "attn_VAT-IN-V82-06-ROW-CC-C2": "VAT-IN-V82-06-ROW-CC-C2",
        "attn_VAT-IN-V82-06-ROW-CC": "TVA Déductible 6% Hors EU - Services and other goods",
        "attn_VAT-IN-V82-00-ROW-CC": "TVA à l'entrée 0% Hors EU - Services and other goods",
        "attn_VAT-IN-V83-21-ROW-CC-C1": "VAT-IN-V83-21-ROW-CC-C1",
        "attn_VAT-IN-V83-21-ROW-CC-C2": "VAT-IN-V83-21-ROW-CC-C2",
        "attn_VAT-IN-V83-21-ROW-CC": "TVA Déductible 21% Hors EU - Biens d'investissement",
        "attn_VAT-IN-V83-12-ROW-CC-C1": "VAT-IN-V83-12-ROW-CC-C1",
        "attn_VAT-IN-V83-12-ROW-CC-C2": "VAT-IN-V83-12-ROW-CC-C2",
        "attn_VAT-IN-V83-12-ROW-CC": "TVA Déductible 12% Hors EU - Biens d'investissement",
        "attn_VAT-IN-V83-06-ROW-CC-C1": "VAT-IN-V83-06-ROW-CC-C1",
        "attn_VAT-IN-V83-06-ROW-CC-C2": "VAT-IN-V83-06-ROW-CC-C2",
        "attn_VAT-IN-V83-06-ROW-CC": "TVA Déductible 6% Hors EU - Biens d'investissement",
        "attn_VAT-IN-V83-00-ROW-CC": "0% Non EU - Biens d'investissement",
        "attn_VAT-IN-V61": "Régularisation en faveur de l'état",
        "attn_VAT-IN-V62": "Régularisation en faveur du déclarant",
    },
]


def get_old_account_tax_names(xmlid):
    """
    Return a list of old names for the account.tax given matching the
    xmlid.
    """
    names = []
    for version in ACCOUNT_TAX_NAMES:
        name = version.get(xmlid)
        if name:
            names.append(name)
    return names


def get_tags(env, repartition_line_tmpl):
    """
    Return the tags linked to an account.tax.repartition.line.template
    """
    tag_names = []
    for report_line in repartition_line_tmpl.plus_report_line_ids:
        tag_names.append("+" + report_line.tag_name)
    for report_line in repartition_line_tmpl.minus_report_line_ids:
        tag_names.append("-" + report_line.tag_name)
    return env["account.account.tag"].search([("name", "in", tag_names)])


def is_account_tax_used(env, account_tax):
    """Return True if account_tax is used on an account.move.line."""
    env.cr.execute(
        """
        SELECT account_tax_id
        FROM account_move_line_account_tax_rel
        WHERE account_tax_id = %s
        """,
        (account_tax.id,),
    )
    return len(env.cr.fetchall()) > 0


def find_account_tax(env, xmlid, account_tax_template):
    """Return the account tax based on the given account.tax.template"""
    current_name = account_tax_template.name
    old_names = get_old_account_tax_names(xmlid)
    domain = [("type_tax_use", "=", account_tax_template.type_tax_use)]

    if not old_names:
        _logger.info(
            "Skipping account.tax.template '%s', because it's a new one.",
            current_name,
        )
        return env["account.tax"]

    _logger.info(
        "Looking for a account.tax that match account.tax.template '%s'.",
        current_name
    )
    account_taxes = env["account.tax"].search(
        domain + [("name", "=", current_name)]
    )

    if not account_taxes:
        _logger.info(
            "No account.tax named '%s', searching with older names.",
            current_name
        )
        account_taxes = env["account.tax"].search(
            domain + [("name", "in", old_names)]
        )

    nb_account_taxes = len(account_taxes)
    account_taxes_used = account_taxes.filtered(
        lambda r: is_account_tax_used(env, r)
    )

    if nb_account_taxes > 1:
        _logger.info(
            "There is several account.tax found for the "
            "account.tax.template '%s'. Trying to see which one is "
            "realy used.",
            current_name,
        )

        nb_account_taxes_used = len(account_taxes_used)
        if nb_account_taxes_used > 1:
            raise ValueError(
                "There is several account.tax found for the "
                "account.tax.template ID %s '%s' that are used on "
                "account.move.line. Clean up "
                "account.tax by renaming your specific account.tax "
                "and migrate it via a dedicated script. "
                "The matching account.tax ID %s"
                % (
                    account_tax_template.id,
                    current_name,
                    ", ".join(str(rec_id) for rec_id in account_taxes_used.ids)
                )
            )

        account_tax = account_taxes_used

    else:
        account_tax = account_taxes

    if not account_tax:
        _logger.error(
            "No matching account.tax for the account.tax.template '%s'.",
            current_name,
        )
    else:
        _logger.info(
            "Using account.tax ID %s '%s' that correspond to the "
            "account.tax.template '%s'.",
            account_tax.id,
            account_tax.name,
            current_name,
        )

    return account_tax


def find_repartition_line(account_tax, repartition_line_tmpl):
    """
    Retrieve the repartition line that match the given repartition
    line from the account.tax.template
    """
    # Choose to search on invoice repartition lines or refund ones.
    if repartition_line_tmpl.invoice_tax_id:
        repartition_lines = account_tax.invoice_repartition_line_ids
    else:
        repartition_lines = account_tax.refund_repartition_line_ids

    repartition_lines = repartition_lines.filtered(
        lambda r: r.repartition_type == repartition_line_tmpl.repartition_type
    )

    if len(repartition_lines) > 1:
        repartition_lines = repartition_lines.filtered(
            lambda r: r.factor_percent == repartition_line_tmpl.factor_percent
        )

    if len(repartition_lines) > 1:
        repartition_lines = repartition_lines.filtered(
            lambda r: r.account_id == repartition_line_tmpl.account_id
        )

    if not repartition_lines:
        # TODO: maybe in this case we need to create the repartition.line ?
        # Or we should delegate this to account_chart_update ?
        _logger.error(
            "No matching account.tax.repartition.line on account.tax ID %s "
            "for the account.tax.repartition.line.template ID %s",
            account_tax.id,
            repartition_line_tmpl.id,
        )
    elif len(repartition_lines) > 1:
        _logger.error(
            "Several matching account.tax.repartition.line on account.tax "
            "ID %s for the account.tax.repartition.line.template ID %s."
            "Found account.tax.repartition.line ID %s.",
            account_tax.id,
            repartition_line_tmpl.id,
            ", ".join(str(rec_id) for rec_id in repartition_lines.ids),
        )
    else:
        _logger.info(
            "Found matching account.tax.repartition.line ID %s "
            "on account.tax ID %s "
            "for the account.tax.repartition.line.template ID %s",
            repartition_lines.id,
            account_tax.id,
            repartition_line_tmpl.id,
        )

    return repartition_lines


def update_repartition_line(env, repartition_line, repartition_line_tmpl):
    """
    Update tag of the account.tax.repartition.line based on
    account.tax.repartition.line.template

    Update the following tables:
    - account_account_tag_account_tax_repartition_line_rel
    - account_account_tag_account_move_line_rel
    """
    # FIXME: I'm not sure if the table :
    #  - account_tax_repartition_financial_tags
    # should be updated or not.

    new_tag_ids = get_tags(env, repartition_line_tmpl)
    old_tag_ids = repartition_line.tag_ids

    # Update account_account_tag_account_tax_repartition_line_rel
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM account_account_tag_account_tax_repartition_line_rel
        WHERE account_tax_repartition_line_id = %s;
        """,
        (repartition_line.id,)
    )
    for new_tag_id in new_tag_ids:
        openupgrade.logged_query(
            env.cr,
            """
            INSERT INTO account_account_tag_account_tax_repartition_line_rel
            (account_tax_repartition_line_id, account_account_tag_id)
            VALUES (%s, %s)
            """,
            (repartition_line.id, new_tag_id.id),
        )

    # Update account_account_tag_account_move_line_rel
    domain = [
        "|",
        ("tax_ids", "=", repartition_line.tax_id.id),
        ("tax_line_id", "=", repartition_line.tax_id.id),
        ("tax_repartition_line_id", "=", False),
    ]
    if repartition_line.repartition_type == "base":
        # WARNING: Here I'm not sure if an account.move.line with a null
        # value as tax_base_amount should be considered equal to zero or
        # not. For now, I assume yes.
        domain.append("|")
        domain.append(("tax_base_amount", "=", 0))
        domain.append(("tax_base_amount", "=", False))
    if repartition_line.repartition_type == "tax":
        domain.append(("tax_base_amount", "!=", 0))

    account_move_line_ids = env["account.move.line"].search(domain)

    # Considering that "out_receipt" and "in_receipt" are not affected
    # by tags.
    if repartition_line.invoice_tax_id:
        account_move_line_ids = account_move_line_ids.filtered(
            lambda r: r.move_id.type in ("out_invoice", "in_invoice")
        )
    if repartition_line.refund_tax_id:
        # WARNING ! Some refund are invoices with a negative amount
        # This case is not taken into account.
        account_move_line_ids = account_move_line_ids.filtered(
            lambda r: r.move_id.type in ("out_refund", "in_refund")
        )

    # Adding account.move.line that are linked to this specific
    # repartition_line
    account_move_line_ids += env["account.move.line"].search(
        [("tax_repartition_line_id", "=", repartition_line.id)]
    )

    if not account_move_line_ids:
        return

    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM account_account_tag_account_move_line_rel
        WHERE account_move_line_id IN (%s)
        AND account_account_tag_id IN (%s)
        """ % (
            ",".join(str(rec_id) for rec_id in account_move_line_ids.ids),
            ",".join(str(rec_id) for rec_id in old_tag_ids.ids),
        ),
    )
    for new_tag_id in new_tag_ids:
        values = [
            "(%s, %s)" % (aml_id, new_tag_id.id)
            for aml_id in account_move_line_ids.ids
        ]
        openupgrade.logged_query(
            env.cr,
            """
            INSERT INTO account_account_tag_account_move_line_rel
            (account_move_line_id, account_account_tag_id)
            VALUES %s
            ON CONFLICT DO NOTHING
            """ % ",".join(values),
        )


def get_account_tax_templates_iterator(env):
    """
    Return account.tax.template with their xmlid
    """
    module = "l10n_be"
    data = env['ir.model.data'].search([
        ('model', '=', 'account.tax.template'),
        ('module', 'like', module)
    ])
    for elem in data:
        account_tax_template = env["account.tax.template"].browse(elem.res_id)
        yield elem.name, account_tax_template


def apply_new_tax_tags_on_account_tax(env, account_tax, account_tax_template):
    """
    The normal migration script of module account tries to link the old
    account.account.tag to account.tax.repartition.line.
    Which does not reflect the new account.tax.template and new
    account.account.tag which comes with positive (debit) and negative
    (credit) flavors.
    This function replace the old tags by the new ones.
    """
    for repartition_line_tmpl in (
        account_tax_template.invoice_repartition_line_ids
        + account_tax_template.refund_repartition_line_ids
    ):
        repartition_line = find_repartition_line(
            account_tax, repartition_line_tmpl
        )
        if not repartition_line:
            _logger.info(
                "No account.tax.repartition.line found that match "
                "the repartition line ID %s of the account.tax.template "
                "ID %s '%s'",
                repartition_line_tmpl.id,
                account_tax_template.id,
                account_tax_template.name,
            )
            continue
        update_repartition_line(env, repartition_line, repartition_line_tmpl)


def update_account_tax(env):
    """
    Use account.tax.template to update existing account.tax
    """
    for xmlid, account_tax_template in get_account_tax_templates_iterator(env):
        account_tax = find_account_tax(env, xmlid, account_tax_template)

        if not account_tax:
            continue

        apply_new_tax_tags_on_account_tax(
            env, account_tax, account_tax_template
        )

        # Rename account_tax
        account_tax.name = account_tax_template.name


def remove_wrong_tag(env):
    """
    Remove tags on account.move.line that are not linked to an
    account.tax.
    """
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM account_account_tag_account_move_line_rel
        WHERE account_move_line_id IN (
            SELECT id FROM account_move_line
            WHERE id NOT IN (
                SELECT DISTINCT account_move_line_id
                FROM account_move_line_account_tax_rel
            )
        )
        """
    )


def unlink_tags_from_move_line(env, tag_xmlids):
    """Unlink tags from account.move.line"""
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM account_account_tag_account_move_line_rel r
        WHERE
            account_account_tag_id IN (
                SELECT res_id FROM ir_model_data
                WHERE
                    model = 'account.account.tag' AND
                    module = 'l10n_be' AND
                    name IN (%s)
            )
        """ % ",".join("'"+xmlid+"'" for xmlid in tag_xmlids),
    )


def disable_troublesome_tags(env):
    """Disable old tags"""
    openupgrade.logged_query(env.cr, """
        UPDATE account_account_tag
        SET active = FALSE
        WHERE
            name NOT LIKE '+%' AND
            name NOT LIKE '-%' AND
            applicability = 'taxes'
    """)


# Based on file l10n_be/data/account_tax_template_data.xml
# Also based on Mis Builder VAT report
# (Cadre I, II et III -> base, Cardre IV and following -> tax).
base_tag_xmlids = [
    "tax_tag_00",
    "tax_tag_01",
    "tax_tag_02",
    "tax_tag_03",
    "tax_tag_44",
    "tax_tag_45",
    "tax_tag_46L",
    "tax_tag_46T",
    "tax_tag_47",
    "tax_tag_48s44",
    "tax_tag_48s46L",
    "tax_tag_48s46T",
    "tax_tag_49",
    "tax_tag_81",
    "tax_tag_82",  # Also in tax (see line 1816), consider it as base
    "tax_tag_83",
    "tax_tag_84",
    "tax_tag_85",  # Also in tax (see line 1839), consider it as base
    "tax_tag_86",
    "tax_tag_87",
    "tax_tag_88",
]
tax_tag_xmlids = [
    "tax_tag_54",
    "tax_tag_55",
    "tax_tag_56",
    "tax_tag_57",
    "tax_tag_59",
    "tax_tag_61",
    "tax_tag_62",
    "tax_tag_63",
    "tax_tag_64",
]

# Missing (I don't know what to do with these tags)
# tax_tag_81_not_deductible
# tax_tag_82_not_deductible
# tax_tag_83_not_deductible
# tax_tag_85_not_deductible


@openupgrade.migrate()
def migrate(env, version):
    remove_wrong_tag(env)
    update_account_tax(env)
    unlink_tags_from_move_line(env, base_tag_xmlids + tax_tag_xmlids)
    disable_troublesome_tags(env)
