from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)


ACCOUNT_TAX_NAMES = [
    # In version 9.0
    {
        "sale": {
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
        },
        "other": {
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
    },

    # In version 10.0
    {
        "other": {
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
    },

    # In version 11.0
    {
        "sale": {
            "attn_VAT-OUT-21-S": "21% S.",
            "attn_VAT-OUT-21-L": "21%",
            "attn_VAT-OUT-12-S": "12% S.",
            "attn_VAT-OUT-12-L": "12%",
            "attn_VAT-OUT-06-S": "6% S.",
            "attn_VAT-OUT-06-L": "6%",
            "attn_VAT-OUT-00-S": "0% S.",
            "attn_VAT-OUT-00-L": "0%",
            "attn_VAT-OUT-00-CC": "0% Cocont.",
            "attn_VAT-OUT-00-EU-S": "0% EU S.",
            "attn_VAT-OUT-00-EU-L": "0% EU M.",
            "attn_VAT-OUT-00-EU-T": "0% EU T.",
            "attn_VAT-OUT-00-ROW": "0% Non EU",
        },
        "other": {
            "attn_VAT-IN-V81-21": "21% M.",
            "attn_VAT-IN-V81-12": "12% M.",
            "attn_VAT-IN-V81-06": "6% M.",
            "attn_VAT-IN-V81-00": "0% M.",
            "attn_TVA-21-inclus-dans-prix": "21% S. TTC",
            "attn_VAT-IN-V82-21-S": "21% S.",
            "attn_VAT-IN-V82-21-G": "21% Biens divers",
            "attn_VAT-IN-V82-12-S": "12% S.",
            "attn_VAT-IN-V82-12-G": "12% Biens divers",
            "attn_VAT-IN-V82-06-S": "6% S.",
            "attn_VAT-IN-V82-06-G": "6% Biens divers",
            "attn_VAT-IN-V82-00-S": "0% S.",
            "attn_VAT-IN-V82-00-G": "0% Biens divers",
            "attn_VAT-IN-V83-21": "21% Biens d'investissement",
            "attn_VAT-IN-V83-12": "12% Biens d'investissement",
            "attn_VAT-IN-V83-06": "6% Biens d'investissement",
            "attn_VAT-IN-V83-00": "0% Biens d'investissement",
            "attn_VAT-IN-V81-21-CC-C1": "21% Cocont. Déductible M.",
            "attn_VAT-IN-V81-21-CC-C2": "21% Cocont. Récupérable M.",
            "attn_VAT-IN-V81-21-CC": "21% Cocont. M.",
            "attn_VAT-IN-V81-12-CC-C1": "12% Cocont. Déductible M.",
            "attn_VAT-IN-V81-12-CC-C2": "12% Cocont. Récupérable M.",
            "attn_VAT-IN-V81-12-CC": "12% Cocont. M.",
            "attn_VAT-IN-V81-06-CC-C1": "6% Cocont. Déductible M.",
            "attn_VAT-IN-V81-06-CC-C2": "6% Cocont. Récupérable M.",
            "attn_VAT-IN-V81-06-CC": "6% Cocont. M.",
            "attn_VAT-IN-V81-00-CC": "0% Cocont. M.",
            "attn_VAT-IN-V82-21-CC-C1": "21% Cocont. Déductible S.",
            "attn_VAT-IN-V82-21-CC-C2": "21% Cocont. Récupérable S.",
            "attn_VAT-IN-V82-21-CC": "21% Cocont .S.",
            "attn_VAT-IN-V82-12-CC-C1": "12% Cocont. Déductible S.",
            "attn_VAT-IN-V82-12-CC-C2": "12% Cocont. Récupérable S.",
            "attn_VAT-IN-V82-12-CC": "12% Cocont. S.",
            "attn_VAT-IN-V82-06-CC-C1": "6% Cocont. Déductible S.",
            "attn_VAT-IN-V82-06-CC-C2": "6% Cocont. Récupérable S.",
            "attn_VAT-IN-V82-06-CC": "6% Cocont. S.",
            "attn_VAT-IN-V82-00-CC": "0% Cocont. S.",
            "attn_VAT-IN-V83-21-CC-C1": "21% Cocont. Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-21-CC-C2": "21% Cocont. Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-21-CC": "21% Cocont. - Biens d'investissement",
            "attn_VAT-IN-V83-12-CC-C1": "12% Cocont. Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-12-CC-C2": "12% Cocont. Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-12-CC": "12% Cocont. - Biens d'investissement",
            "attn_VAT-IN-V83-06-CC-C1": "6% Cocont. Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-06-CC-C2": "6% Cocont. Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-06-CC": "6% Cocont. - Biens d'investissement",
            "attn_VAT-IN-V83-00-CC": "0% Cocont. - Biens d'investissement",
            "attn_VAT-IN-V82-CAR-EXC-C1": "50% Non Déductible - Frais de voiture",
            "attn_VAT-IN-V82-CAR-EXC-C2": "50% Déductible - Frais de voiture (Prix Excl.)",
            "attn_VAT-IN-V82-CAR-EXC": "50% Non Déductible - Frais de voiture (Prix Excl.)",
            "attn_VAT-IN-V81-21-EU-C1": "21% EU Déductible M.",
            "attn_VAT-IN-V81-21-EU-C2": "21% EU Récupérable M.",
            "attn_VAT-IN-V81-21-EU": "21% EU M.",
            "attn_VAT-IN-V81-12-EU-C1": "12% EU Déductible M.",
            "attn_VAT-IN-V81-12-EU-C2": "12% EU Récupérable M.",
            "attn_VAT-IN-V81-12-EU": "12% EU M.",
            "attn_VAT-IN-V81-06-EU-C1": "6% EU Déductible M.",
            "attn_VAT-IN-V81-06-EU-C2": "6% EU Récupérable M.",
            "attn_VAT-IN-V81-06-EU": "6% EU M.",
            "attn_VAT-IN-V81-00-EU": "0% EU M.",
            "attn_VAT-IN-V82-21-EU-S-C1": "21% EU Déductible S.",
            "attn_VAT-IN-V82-21-EU-S-C2": "21% EU Récupérable S.",
            "attn_VAT-IN-V82-21-EU-S": "21% EU S.",
            "attn_VAT-IN-V82-21-EU-G-C1": "21% EU Déductible - Biens divers",
            "attn_VAT-IN-V82-21-EU-G-C2": "21% EU Récupérable - Biens divers",
            "attn_VAT-IN-V82-21-EU-G": "21% EU - Biens divers",
            "attn_VAT-IN-V82-12-EU-S-C1": "12% EU Déductible S.",
            "attn_VAT-IN-V82-12-EU-S-C2": "12% EU Récupérable S.",
            "attn_VAT-IN-V82-12-EU-S": "12% EU S.",
            "attn_VAT-IN-V82-12-EU-G-C1": "12% EU Déductible - Biens divers",
            "attn_VAT-IN-V82-12-EU-G-C2": "TVA 12% EU Récupérable - Biens divers",
            "attn_VAT-IN-V82-12-EU-G": "12% EU - Biens divers",
            "attn_VAT-IN-V82-06-EU-S-C1": "6% EU Déductible S.",
            "attn_VAT-IN-V82-06-EU-S-C2": "6% EU Récupérable S.",
            "attn_VAT-IN-V82-06-EU-S": "6% EU S.",
            "attn_VAT-IN-V82-06-EU-G-C1": "6% EU Déductible - Biens divers",
            "attn_VAT-IN-V82-06-EU-G-C2": "6% EU Récupérable - Biens divers",
            "attn_VAT-IN-V82-06-EU-G": "6% EU - Biens divers",
            "attn_VAT-IN-V82-00-EU-S": "0% EU S.",
            "attn_VAT-IN-V83-21-EU-C1": "21% EU Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-21-EU-C2": "21% EU Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-21-EU": "21% EU - Biens d'investissement",
            "attn_VAT-IN-V82-00-EU-G": "0% EU - Biens divers",
            "attn_VAT-IN-V83-12-EU-C1": "12% EU Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-12-EU-C2": "12% EU Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-12-EU": "12% EU - Biens d'investissement",
            "attn_VAT-IN-V83-06-EU-C1": "6% EU Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-06-EU-C2": "6% EU Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-06-EU": "6% EU - Biens d'investissement",
            "attn_VAT-IN-V83-00-EU": "0% EU - Biens d'investissement",
            "attn_VAT-IN-V81-21-ROW-CC-C1": "21% Non EU Déductible M.",
            "attn_VAT-IN-V81-21-ROW-CC-C2": "21% Non EU Récupérable M.",
            "attn_VAT-IN-V81-21-ROW-CC": "21% Non EU M.",
            "attn_VAT-IN-V81-12-ROW-CC-C1": "12% Non EU Déductible M.",
            "attn_VAT-IN-V81-12-ROW-CC-C2": "12% Non EU Récupérable M.",
            "attn_VAT-IN-V81-12-ROW-CC": "12% Non EU M.",
            "attn_VAT-IN-V81-06-ROW-CC-C1": "6% Non EU Déductible M.",
            "attn_VAT-IN-V81-06-ROW-CC-C2": "6% Non EU Récupérable M.",
            "attn_VAT-IN-V81-06-ROW-CC": "6% Non EU M.",
            "attn_VAT-IN-V81-00-ROW-CC": "0% Non EU M.",
            "attn_VAT-IN-V82-21-ROW-CC-C1": "21% Non EU Déductible S.",
            "attn_VAT-IN-V82-21-ROW-CC-C2": "21% Non EU Récupérable S.",
            "attn_VAT-IN-V82-21-ROW-CC": "21% Non EU S.",
            "attn_VAT-IN-V82-12-ROW-CC-C1": "12% Non EU Déductible S.",
            "attn_VAT-IN-V82-12-ROW-CC-C2": "12% Non EU Récupérable S.",
            "attn_VAT-IN-V82-12-ROW-CC": "12% Non EU S.",
            "attn_VAT-IN-V82-06-ROW-CC-C1": "6% Non EU Déductible S.",
            "attn_VAT-IN-V82-06-ROW-CC-C2": "6% Non EU Récupérable S.",
            "attn_VAT-IN-V82-06-ROW-CC": "6% Non EU S.",
            "attn_VAT-IN-V82-00-ROW-CC": "0% Non EU S.",
            "attn_VAT-IN-V83-21-ROW-CC-C1": "21% Non EU Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-21-ROW-CC-C2": "21% Non EU Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-21-ROW-CC": "21% Non EU - Biens d'investissement",
            "attn_VAT-IN-V83-12-ROW-CC-C1": "12% Non EU Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-12-ROW-CC-C2": "12% Non EU Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-12-ROW-CC": "12% Non EU - Biens d'investissement",
            "attn_VAT-IN-V83-06-ROW-CC-C1": "6% Non EU Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-06-ROW-CC-C2": "6% Non EU Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-06-ROW-CC": "6% Non EU - Biens d'investissement",
            "attn_VAT-IN-V83-00-ROW-CC": "0% Non EU - Biens d'investissement",
            "attn_VAT-IN-V61": "Régularisation en faveur de l'état",
            "attn_VAT-IN-V62": "Régularisation en faveur du déclarant",
        },
    },

    # In version 12.0
    {
        "sale": {
            "attn_VAT-OUT-21-S": "21% S.",
            "attn_VAT-OUT-21-L": "21%",
            "attn_VAT-OUT-12-S": "12% S.",
            "attn_VAT-OUT-12-L": "12%",
            "attn_VAT-OUT-06-S": "6% S.",
            "attn_VAT-OUT-06-L": "6%",
            "attn_VAT-OUT-00-S": "0% S.",
            "attn_VAT-OUT-00-L": "0%",
            "attn_VAT-OUT-00-CC": "0% Cocont.",
            "attn_VAT-OUT-00-EU-S": "0% EU S.",
            "attn_VAT-OUT-00-EU-L": "0% EU M.",
            "attn_VAT-OUT-00-EU-T": "0% EU T.",
            "attn_VAT-OUT-00-ROW": "0% Non EU",
        },
        "other": {
            "attn_VAT-IN-V81-21": "21% M.",
            "attn_VAT-IN-V81-12": "12% M.",
            "attn_VAT-IN-V81-06": "6% M.",
            "attn_VAT-IN-V81-00": "0% M.",
            "attn_TVA-21-inclus-dans-prix": "21% S. TTC",
            "attn_VAT-IN-V82-21-S": "21% S.",
            "attn_VAT-IN-V82-21-G": "21% Biens divers",
            "attn_VAT-IN-V82-12-S": "12% S.",
            "attn_VAT-IN-V82-12-G": "12% Biens divers",
            "attn_VAT-IN-V82-06-S": "6% S.",
            "attn_VAT-IN-V82-06-G": "6% Biens divers",
            "attn_VAT-IN-V82-00-S": "0% S.",
            "attn_VAT-IN-V82-00-G": "0% Biens divers",
            "attn_VAT-IN-V83-21": "21% Biens d'investissement",
            "attn_VAT-IN-V83-12": "12% Biens d'investissement",
            "attn_VAT-IN-V83-06": "6% Biens d'investissement",
            "attn_VAT-IN-V83-00": "0% Biens d'investissement",
            "attn_VAT-IN-V81-21-CC-C1": "21% Cocont. Déductible M.",
            "attn_VAT-IN-V81-21-CC-C2": "21% Cocont. Récupérable M.",
            "attn_VAT-IN-V81-21-CC": "21% Cocont. M.",
            "attn_VAT-IN-V81-12-CC-C1": "12% Cocont. Déductible M.",
            "attn_VAT-IN-V81-12-CC-C2": "12% Cocont. Récupérable M.",
            "attn_VAT-IN-V81-12-CC": "12% Cocont. M.",
            "attn_VAT-IN-V81-06-CC-C1": "6% Cocont. Déductible M.",
            "attn_VAT-IN-V81-06-CC-C2": "6% Cocont. Récupérable M.",
            "attn_VAT-IN-V81-06-CC": "6% Cocont. M.",
            "attn_VAT-IN-V81-00-CC": "0% Cocont. M.",
            "attn_VAT-IN-V82-21-CC-C1": "21% Cocont. Déductible S.",
            "attn_VAT-IN-V82-21-CC-C2": "21% Cocont. Récupérable S.",
            "attn_VAT-IN-V82-21-CC": "21% Cocont .S.",
            "attn_VAT-IN-V82-12-CC-C1": "12% Cocont. Déductible S.",
            "attn_VAT-IN-V82-12-CC-C2": "12% Cocont. Récupérable S.",
            "attn_VAT-IN-V82-12-CC": "12% Cocont. S.",
            "attn_VAT-IN-V82-06-CC-C1": "6% Cocont. Déductible S.",
            "attn_VAT-IN-V82-06-CC-C2": "6% Cocont. Récupérable S.",
            "attn_VAT-IN-V82-06-CC": "6% Cocont. S.",
            "attn_VAT-IN-V82-00-CC": "0% Cocont. S.",
            "attn_VAT-IN-V83-21-CC-C1": "21% Cocont. Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-21-CC-C2": "21% Cocont. Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-21-CC": "21% Cocont. - Biens d'investissement",
            "attn_VAT-IN-V83-12-CC-C1": "12% Cocont. Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-12-CC-C2": "12% Cocont. Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-12-CC": "12% Cocont. - Biens d'investissement",
            "attn_VAT-IN-V83-06-CC-C1": "6% Cocont. Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-06-CC-C2": "6% Cocont. Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-06-CC": "6% Cocont. - Biens d'investissement",
            "attn_VAT-IN-V83-00-CC": "0% Cocont. - Biens d'investissement",
            "attn_VAT-IN-V82-CAR-EXC-C1": "50% Non Déductible - Frais de voiture",
            "attn_VAT-IN-V82-CAR-EXC-C2": "50% Déductible - Frais de voiture (Prix Excl.)",
            "attn_VAT-IN-V82-CAR-EXC": "50% Non Déductible - Frais de voiture (Prix Excl.)",
            "attn_VAT-IN-V81-21-EU-C1": "21% EU Déductible M.",
            "attn_VAT-IN-V81-21-EU-C2": "21% EU Récupérable M.",
            "attn_VAT-IN-V81-21-EU": "21% EU M.",
            "attn_VAT-IN-V81-12-EU-C1": "12% EU Déductible M.",
            "attn_VAT-IN-V81-12-EU-C2": "12% EU Récupérable M.",
            "attn_VAT-IN-V81-12-EU": "12% EU M.",
            "attn_VAT-IN-V81-06-EU-C1": "6% EU Déductible M.",
            "attn_VAT-IN-V81-06-EU-C2": "6% EU Récupérable M.",
            "attn_VAT-IN-V81-06-EU": "6% EU M.",
            "attn_VAT-IN-V81-00-EU": "0% EU M.",
            "attn_VAT-IN-V82-21-EU-S-C1": "21% EU Déductible S.",
            "attn_VAT-IN-V82-21-EU-S-C2": "21% EU Récupérable S.",
            "attn_VAT-IN-V82-21-EU-S": "21% EU S.",
            "attn_VAT-IN-V82-21-EU-G-C1": "21% EU Déductible - Biens divers",
            "attn_VAT-IN-V82-21-EU-G-C2": "21% EU Récupérable - Biens divers",
            "attn_VAT-IN-V82-21-EU-G": "21% EU - Biens divers",
            "attn_VAT-IN-V82-12-EU-S-C1": "12% EU Déductible S.",
            "attn_VAT-IN-V82-12-EU-S-C2": "12% EU Récupérable S.",
            "attn_VAT-IN-V82-12-EU-S": "12% EU S.",
            "attn_VAT-IN-V82-12-EU-G-C1": "12% EU Déductible - Biens divers",
            "attn_VAT-IN-V82-12-EU-G-C2": "TVA 12% EU Récupérable - Biens divers",
            "attn_VAT-IN-V82-12-EU-G": "12% EU - Biens divers",
            "attn_VAT-IN-V82-06-EU-S-C1": "6% EU Déductible S.",
            "attn_VAT-IN-V82-06-EU-S-C2": "6% EU Récupérable S.",
            "attn_VAT-IN-V82-06-EU-S": "6% EU S.",
            "attn_VAT-IN-V82-06-EU-G-C1": "6% EU Déductible - Biens divers",
            "attn_VAT-IN-V82-06-EU-G-C2": "6% EU Récupérable - Biens divers",
            "attn_VAT-IN-V82-06-EU-G": "6% EU - Biens divers",
            "attn_VAT-IN-V82-00-EU-S": "0% EU S.",
            "attn_VAT-IN-V83-21-EU-C1": "21% EU Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-21-EU-C2": "21% EU Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-21-EU": "21% EU - Biens d'investissement",
            "attn_VAT-IN-V82-00-EU-G": "0% EU - Biens divers",
            "attn_VAT-IN-V83-12-EU-C1": "12% EU Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-12-EU-C2": "12% EU Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-12-EU": "12% EU - Biens d'investissement",
            "attn_VAT-IN-V83-06-EU-C1": "6% EU Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-06-EU-C2": "6% EU Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-06-EU": "6% EU - Biens d'investissement",
            "attn_VAT-IN-V83-00-EU": "0% EU - Biens d'investissement",
            "attn_VAT-IN-V81-21-ROW-CC-C1": "21% Non EU Déductible M.",
            "attn_VAT-IN-V81-21-ROW-CC-C2": "21% Non EU Récupérable M.",
            "attn_VAT-IN-V81-21-ROW-CC": "21% Non EU M.",
            "attn_VAT-IN-V81-12-ROW-CC-C1": "12% Non EU Déductible M.",
            "attn_VAT-IN-V81-12-ROW-CC-C2": "12% Non EU Récupérable M.",
            "attn_VAT-IN-V81-12-ROW-CC": "12% Non EU M.",
            "attn_VAT-IN-V81-06-ROW-CC-C1": "6% Non EU Déductible M.",
            "attn_VAT-IN-V81-06-ROW-CC-C2": "6% Non EU Récupérable M.",
            "attn_VAT-IN-V81-06-ROW-CC": "6% Non EU M.",
            "attn_VAT-IN-V81-00-ROW-CC": "0% Non EU M.",
            "attn_VAT-IN-V82-21-ROW-CC-C1": "21% Non EU Déductible S.",
            "attn_VAT-IN-V82-21-ROW-CC-C2": "21% Non EU Récupérable S.",
            "attn_VAT-IN-V82-21-ROW-CC": "21% Non EU S.",
            "attn_VAT-IN-V82-12-ROW-CC-C1": "12% Non EU Déductible S.",
            "attn_VAT-IN-V82-12-ROW-CC-C2": "12% Non EU Récupérable S.",
            "attn_VAT-IN-V82-12-ROW-CC": "12% Non EU S.",
            "attn_VAT-IN-V82-06-ROW-CC-C1": "6% Non EU Déductible S.",
            "attn_VAT-IN-V82-06-ROW-CC-C2": "6% Non EU Récupérable S.",
            "attn_VAT-IN-V82-06-ROW-CC": "6% Non EU S.",
            "attn_VAT-IN-V82-00-ROW-CC": "0% Non EU S.",
            "attn_VAT-IN-V83-21-ROW-CC-C1": "21% Non EU Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-21-ROW-CC-C2": "21% Non EU Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-21-ROW-CC": "21% Non EU - Biens d'investissement",
            "attn_VAT-IN-V83-12-ROW-CC-C1": "12% Non EU Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-12-ROW-CC-C2": "12% Non EU Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-12-ROW-CC": "12% Non EU - Biens d'investissement",
            "attn_VAT-IN-V83-06-ROW-CC-C1": "6% Non EU Déductible - Biens d'investissement",
            "attn_VAT-IN-V83-06-ROW-CC-C2": "6% Non EU Récupérable - Biens d'investissement",
            "attn_VAT-IN-V83-06-ROW-CC": "6% Non EU - Biens d'investissement",
            "attn_VAT-IN-V83-00-ROW-CC": "0% Non EU - Biens d'investissement",
            "attn_VAT-IN-V61": "Régularisation en faveur de l'état",
            "attn_VAT-IN-V62": "Régularisation en faveur du déclarant",
        },
    },
]

# Based on l10n_be/data/account_tax_template_data.xml
NEW_ACCOUNT_TAX_CONFIG = {
    "attn_VAT-OUT-21-S": {
        "invoice": {
            "base": ["+03"],
            "tax": ["+54"],
        },
        "refund": {
            "base": ["+49"],
            "tax": ["+64"],
        },
    },

    "attn_VAT-OUT-21-L": {
        "invoice": {
            "base": ["+03"],
            "tax": ["+54"],
        },
        "refund": {
            "base": ["+49"],
            "tax": ["+64"],
        },
    },

    "attn_VAT-OUT-12-S": {
        "invoice": {
            "base": ["+02"],
            "tax": ["+54"],
        },
        "refund": {
            "base": ["+49"],
            "tax": ["+64"],
        },
    },

    "attn_VAT-OUT-12-L": {
        "invoice": {
            "base": ["+02"],
            "tax": ["+54"],
        },
        "refund": {
            "base": ["+49"],
            "tax": ["+64"],
        },
    },

    "attn_VAT-OUT-06-S": {
        "invoice": {
            "base": ["+01"],
            "tax": ["+54"],
        },
        "refund": {
            "base": ["+49"],
            "tax": ["+64"],
        },
    },

    "attn_VAT-OUT-06-L": {
        "invoice": {
            "base": ["+01"],
            "tax": ["+54"],
        },
        "refund": {
            "base": ["+49"],
            "tax": ["+64"],
        },
    },

    "attn_VAT-OUT-00-S": {
        "invoice": {
            "base": ["+00"],
            "tax": [],
        },
        "refund": {
            "base": ["+49"],
            "tax": [],
        },
    },

    "attn_VAT-OUT-00-L": {
        "invoice": {
            "base": ["+00"],
            "tax": [],
        },
        "refund": {
            "base": ["+49"],
            "tax": [],
        },
    },

    "attn_VAT-OUT-00-CC": {
        "invoice": {
            "base": ["+45"],
            "tax": [],
        },
        "refund": {
            "base": ["+49"],
            "tax": [],
        },
    },

    "attn_VAT-OUT-00-EU-S": {
        "invoice": {
            "base": ["+44"],
            "tax": [],
        },
        "refund": {
            "base": ["+48s44"],
            "tax": [],
        },
    },

    "attn_VAT-OUT-00-EU-L": {
        "invoice": {
            "base": ["+46L"],
            "tax": [],
        },
        "refund": {
            "base": ["+48s46L"],
            "tax": [],
        },
    },

    "attn_VAT-OUT-00-EU-T": {
        "invoice": {
            "base": ["+46T"],
            "tax": [],
        },
        "refund": {
            "base": ["+48s46T"],
            "tax": [],
        },
    },

    "attn_VAT-OUT-00-ROW": {
        "invoice": {
            "base": ["+47"],
            "tax": [],
        },
        "refund": {
            "base": ["+49"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V81-21": {
        "invoice": {
            "base": ["+81"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-81"],
            "tax": ["+63"],
        },
    },

    "attn_VAT-IN-V81-12": {
        "invoice": {
            "base": ["+81"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-81"],
            "tax": ["+63"],
        },
    },

    "attn_VAT-IN-V81-06": {
        "invoice": {
            "base": ["+81"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-81"],
            "tax": ["+63"],
        },
    },

    "attn_VAT-IN-V81-00": {
        "invoice": {
            "base": ["+81"],
            "tax": [],
        },
        "refund": {
            "base": ["+85", "-81"],
            "tax": [],
        },
    },

    "attn_TVA-21-inclus-dans-prix": {
        "invoice": {
            "base": ["+82"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-82"],
            "tax": ["+63"],
        },
    },

    "attn_VAT-IN-V82-21-S": {
        "invoice": {
            "base": ["+82"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-82"],
            "tax": ["+63"],
        },
    },

    "attn_VAT-IN-V82-21-G": {
        "invoice": {
            "base": ["+82"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-82"],
            "tax": ["+63"],
        },
    },

    "attn_VAT-IN-V82-12-S": {
        "invoice": {
            "base": ["+82"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-82"],
            "tax": ["+63"],
        },
    },

    "attn_VAT-IN-V82-12-G": {
        "invoice": {
            "base": ["+82"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-82"],
            "tax": ["+63"],
        },
    },

    "attn_VAT-IN-V82-06-S": {
        "invoice": {
            "base": ["+82"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-82"],
            "tax": ["+63"],
        },
    },

    "attn_VAT-IN-V82-06-G": {
        "invoice": {
            "base": ["+82"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-82"],
            "tax": ["+63"],
        },
    },

    "attn_VAT-IN-V82-00-S": {
        "invoice": {
            "base": ["+82"],
            "tax": [],
        },
        "refund": {
            "base": ["+85", "-82"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-00-G": {
        "invoice": {
            "base": ["+82"],
            "tax": [],
        },
        "refund": {
            "base": ["+85", "-82"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V83-21": {
        "invoice": {
            "base": ["+83"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-83"],
            "tax": ["+63"],
        },
    },

    "attn_VAT-IN-V83-12": {
        "invoice": {
            "base": ["+83"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-83"],
            "tax": ["+63"],
        },
    },

    "attn_VAT-IN-V83-06": {
        "invoice": {
            "base": ["+83"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-83"],
            "tax": ["+63"],
        },
    },

    "attn_VAT-IN-V83-00": {
        "invoice": {
            "base": ["+83"],
            "tax": [],
        },
        "refund": {
            "base": ["+85", "-83"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V81-21-CC-C1": {
        "invoice": {
            "base": ["+81", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-81", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V81-21-CC-C2": {
        "invoice": {
            "base": ["+81", "+87"],
            "tax": ["+56"],
        },
        "refund": {
            "base": ["+85", "-81", "-87"],
            "tax": [],
        },
    },


    # group tax seed child taxes (above)
    "attn_VAT-IN-V81-21-CC": "21% Cocont. M.",

    "attn_VAT-IN-V81-12-CC-C1": {
        "invoice": {
            "base": ["+81", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-81", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V81-12-CC-C2": {
        "invoice": {
            "base": ["+81", "+87"],
            "tax": ["+56"],
        },
        "refund": {
            "base": ["+85", "-81", "-87"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V81-12-CC": "12% Cocont. M.",

    "attn_VAT-IN-V81-06-CC-C1": {
        "invoice": {
            "base": ["+81", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-81", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V81-06-CC-C2": {
        "invoice": {
            "base": ["+81", "+87"],
            "tax": ["+56"],
        },
        "refund": {
            "base": ["+85", "-81", "-87"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V81-06-CC": "6% Cocont. M.",

    "attn_VAT-IN-V81-00-CC": {
        "invoice": {
            "base": ["+81", "+87"],
            "tax": [],
        },
        "refund": {
            "base": ["+85", "-81", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-21-CC-C1": {
        "invoice": {
            "base": ["+82", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-82", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-21-CC-C2": {
        "invoice": {
            "base": ["+82", "+87"],
            "tax": ["+56"],
        },
        "refund": {
            "base": ["+85", "-82", "-87"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V82-21-CC": "21% Cocont .S.",

    "attn_VAT-IN-V82-12-CC-C1": {
        "invoice": {
            "base": ["+82", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-82", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-12-CC-C2": {
        "invoice": {
            "base": ["+82", "+87"],
            "tax": ["+56"],
        },
        "refund": {
            "base": ["+85", "-82", "-87"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V82-12-CC": "12% Cocont. S.",

    "attn_VAT-IN-V82-06-CC-C1": {
        "invoice": {
            "base": ["+82", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-82", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-06-CC-C2": {
        "invoice": {
            "base": ["+82", "+87"],
            "tax": ["+56"],
        },
        "refund": {
            "base": ["+85", "-82", "-87"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V82-06-CC": "6% Cocont. S.",

    "attn_VAT-IN-V82-00-CC": {
        "invoice": {
            "base": ["+82", "+87"],
            "tax": [],
        },
        "refund": {
            "base": ["+85", "-82", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V83-21-CC-C1": {
        "invoice": {
            "base": ["+83", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-83", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V83-21-CC-C2": {
        "invoice": {
            "base": ["+83", "+87"],
            "tax": ["+56"],
        },
        "refund": {
            "base": ["+85", "-83", "-87"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V83-21-CC": "21% Cocont. - Biens d'investissement",

    "attn_VAT-IN-V83-12-CC-C1": {
        "invoice": {
            "base": ["+83", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-83", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V83-12-CC-C2": {
        "invoice": {
            "base": ["+83", "+87"],
            "tax": ["+56"],
        },
        "refund": {
            "base": ["+85", "-83", "-87"],
            "tax": [],
        },
    },


    # group tax seed child taxes (above)
    "attn_VAT-IN-V83-12-CC": "12% Cocont. - Biens d'investissement",

    "attn_VAT-IN-V83-06-CC-C1": {
        "invoice": {
            "base": ["+83", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-83", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V83-06-CC-C2": {
        "invoice": {
            "base": ["+83", "+87"],
            "tax": ["+56"],
        },
        "refund": {
            "base": ["+85", "-83", "-87"],
            "tax": [],
        },
    },


    # group tax seed child taxes (above)
    "attn_VAT-IN-V83-06-CC": "6% Cocont. - Biens d'investissement",

    "attn_VAT-IN-V83-00-CC": {
        "invoice": {
            "base": ["+83", "+87"],
            "tax": [],
        },
        "refund": {
            "base": ["+85", "-83", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-CAR-EXC-C1": {
        "invoice": {
            "base": ["+82"],
            "tax": ["+82"],
        },
        "refund": {
            "base": ["+85", "-82"],
            "tax": ["+85", "-82"],
        },
    },

    "attn_VAT-IN-V82-CAR-EXC-C2": {
        "invoice": {
            "base": ["+82"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-82"],
            "tax": ["+63"],
        },
    },


    # group tax seed child taxes (above)
    "attn_VAT-IN-V82-CAR-EXC": "50% Non Déductible - Frais de voiture (Prix Excl.)",

    "attn_VAT-IN-V81-21-EU-C1": {
        "invoice": {
            "base": ["+81", "+86"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+84", "-81", "-86"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V81-21-EU-C2": {
        "invoice": {
            "base": ["+81", "+86"],
            "tax": ["+55"],
        },
        "refund": {
            "base": ["+84", "-81", "-86"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V81-21-EU": "21% EU M.",

    "attn_VAT-IN-V81-12-EU-C1": {
        "invoice": {
            "base": ["+81", "+86"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+84", "-81", "-86"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V81-12-EU-C2": {
        "invoice": {
            "base": ["+81", "+86"],
            "tax": ["+55"],
        },
        "refund": {
            "base": ["+84", "-81", "-86"],
            "tax": [],
        },
    },


    # group tax seed child taxes (above)
    "attn_VAT-IN-V81-12-EU": "12% EU M.",

    "attn_VAT-IN-V81-06-EU-C1": {
        "invoice": {
            "base": ["+81", "+86"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+84", "-81", "-86"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V81-06-EU-C2": {
        "invoice": {
            "base": ["+81", "+86"],
            "tax": ["+55"],
        },
        "refund": {
            "base": ["+84", "-81", "-86"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V81-06-EU": "6% EU M.",

    "attn_VAT-IN-V81-00-EU": {
        "invoice": {
            "base": ["+81", "+86"],
            "tax": [],
        },
        "refund": {
            "base": ["+84", "-81", "-86"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-21-EU-S-C1": {
        "invoice": {
            "base": ["+82", "+88"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+84", "-82", "-88"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-21-EU-S-C2": {
        "invoice": {
            "base": ["+82", "+88"],
            "tax": ["+55"],
        },
        "refund": {
            "base": ["+84", "-82", "-88"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V82-21-EU-S": "21% EU S.",

    "attn_VAT-IN-V82-21-EU-G-C1": {
        "invoice": {
            "base": ["+82", "+86"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+84", "-82", "-86"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-21-EU-G-C2": {
        "invoice": {
            "base": ["+82", "+86"],
            "tax": ["+55"],
        },
        "refund": {
            "base": ["+84", "-82", "-86"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V82-21-EU-G": "21% EU - Biens divers",

    "attn_VAT-IN-V82-12-EU-S-C1": {
        "invoice": {
            "base": ["+82", "+88"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+84", "-82", "-88"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-12-EU-S-C2": {
        "invoice": {
            "base": ["+82", "+88"],
            "tax": ["+55"],
        },
        "refund": {
            "base": ["+84", "-82", "-88"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V82-12-EU-S": "12% EU S.",

    "attn_VAT-IN-V82-12-EU-G-C1": {
        "invoice": {
            "base": ["+82", "+86"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+84", "-82", "-86"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-12-EU-G-C2": {
        "invoice": {
            "base": ["+82", "+86"],
            "tax": ["+55"],
        },
        "refund": {
            "base": ["+84", "-82", "-86"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V82-12-EU-G": "12% EU - Biens divers",

    "attn_VAT-IN-V82-06-EU-S-C1": {
        "invoice": {
            "base": ["+82", "+88"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+84", "-82", "-88"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-06-EU-S-C2": {
        "invoice": {
            "base": ["+82", "+88"],
            "tax": ["+55"],
        },
        "refund": {
            "base": ["+84", "-82", "-88"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V82-06-EU-S": "6% EU S.",

    "attn_VAT-IN-V82-06-EU-G-C1": {
        "invoice": {
            "base": ["+82", "+86"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+84", "-82", "-86"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-06-EU-G-C2": {
        "invoice": {
            "base": ["+82", "+86"],
            "tax": ["+55"],
        },
        "refund": {
            "base": ["+84", "-82", "-86"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V82-06-EU-G": "6% EU - Biens divers",

    "attn_VAT-IN-V82-00-EU-S": {
        "invoice": {
            "base": ["+82", "+88"],
            "tax": [],
        },
        "refund": {
            "base": ["+84", "-82", "-88"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V83-21-EU-C1": {
        "invoice": {
            "base": ["+83", "+86"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+84", "-83", "-86"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V83-21-EU-C2": {
        "invoice": {
            "base": ["+83", "+86"],
            "tax": ["+55"],
        },
        "refund": {
            "base": ["+84", "-83", "-86"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V83-21-EU": "21% EU - Biens d'investissement",

    "attn_VAT-IN-V82-00-EU-G": {
        "invoice": {
            "base": ["+82", "+86"],
            "tax": [],
        },
        "refund": {
            "base": ["+84", "-82", "-86"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V83-12-EU-C1": {
        "invoice": {
            "base": ["+83", "+86"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+84", "-83", "-86"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V83-12-EU-C2": {
        "invoice": {
            "base": ["+83", "+86"],
            "tax": ["+55"],
        },
        "refund": {
            "base": ["+84", "-83", "-86"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V83-12-EU": "12% EU - Biens d'investissement",

    "attn_VAT-IN-V83-06-EU-C1": {
        "invoice": {
            "base": ["+83", "+86"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+84", "-83", "-86"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V83-06-EU-C2": {
        "invoice": {
            "base": ["+83", "+86"],
            "tax": ["+55"],
        },
        "refund": {
            "base": ["+84", "-83", "-86"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V83-06-EU": "6% EU - Biens d'investissement",

    "attn_VAT-IN-V83-00-EU": {
        "invoice": {
            "base": ["+83", "+86"],
            "tax": [],
        },
        "refund": {
            "base": ["+84", "-83", "-86"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V81-21-ROW-CC-C1": {
        "invoice": {
            "base": ["+81", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-81", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V81-21-ROW-CC-C2": {
        "invoice": {
            "base": ["+81", "+87"],
            "tax": ["+57"],
        },
        "refund": {
            "base": ["+85", "-81", "-87"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V81-21-ROW-CC": "21% Non EU M.",

    "attn_VAT-IN-V81-12-ROW-CC-C1": {
        "invoice": {
            "base": ["+81", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-81", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V81-12-ROW-CC-C2": {
        "invoice": {
            "base": ["+81", "+87"],
            "tax": ["+57"],
        },
        "refund": {
            "base": ["+85", "-81", "-87"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V81-12-ROW-CC": "12% Non EU M.",

    "attn_VAT-IN-V81-06-ROW-CC-C1": {
        "invoice": {
            "base": ["+81", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-81", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V81-06-ROW-CC-C2": {
        "invoice": {
            "base": ["+81", "+87"],
            "tax": ["+57"],
        },
        "refund": {
            "base": ["+85", "-81", "-87"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V81-06-ROW-CC": "6% Non EU M.",

    "attn_VAT-IN-V81-00-ROW-CC": {
        "invoice": {
            "base": ["+81", "+87"],
            "tax": [],
        },
        "refund": {
            "base": ["+85", "-81", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-21-ROW-CC-C1": {
        "invoice": {
            "base": ["+82", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-82", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-21-ROW-CC-C2": {
        "invoice": {
            "base": ["+82", "+87"],
            "tax": ["+57"],
        },
        "refund": {
            "base": ["+85", "-82", "-87"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V82-21-ROW-CC": "21% Non EU S.",

    "attn_VAT-IN-V82-12-ROW-CC-C1": {
        "invoice": {
            "base": ["+82", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-82", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-12-ROW-CC-C2": {
        "invoice": {
            "base": ["+82", "+87"],
            "tax": ["+57"],
        },
        "refund": {
            "base": ["+85", "-82", "-87"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V82-12-ROW-CC": "12% Non EU S.",

    "attn_VAT-IN-V82-06-ROW-CC-C1": {
        "invoice": {
            "base": ["+82", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-82", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V82-06-ROW-CC-C2": {
        "invoice": {
            "base": ["+82", "+87"],
            "tax": ["+57"],
        },
        "refund": {
            "base": ["+85", "-82", "-87"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V82-06-ROW-CC": "6% Non EU S.",

    "attn_VAT-IN-V82-00-ROW-CC": {
        "invoice": {
            "base": ["+82", "+87"],
            "tax": [],
        },
        "refund": {
            "base": ["+85", "-82", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V83-21-ROW-CC-C1": {
        "invoice": {
            "base": ["+83", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-83", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V83-21-ROW-CC-C2": {
        "invoice": {
            "base": ["+83", "+87"],
            "tax": ["+57"],
        },
        "refund": {
            "base": ["+85", "-83", "-87"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V83-21-ROW-CC": "21% Non EU - Biens d'investissement",

    "attn_VAT-IN-V83-12-ROW-CC-C1": {
        "invoice": {
            "base": ["+83", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-83", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V83-12-ROW-CC-C2": {
        "invoice": {
            "base": ["+83", "+87"],
            "tax": ["+57"],
        },
        "refund": {
            "base": ["+85", "-83", "-87"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V83-12-ROW-CC": "12% Non EU - Biens d'investissement",

    "attn_VAT-IN-V83-06-ROW-CC-C1": {
        "invoice": {
            "base": ["+83", "+87"],
            "tax": ["+59"],
        },
        "refund": {
            "base": ["+85", "-83", "-87"],
            "tax": [],
        },
    },

    "attn_VAT-IN-V83-06-ROW-CC-C2": {
        "invoice": {
            "base": ["+83", "+87"],
            "tax": ["+57"],
        },
        "refund": {
            "base": ["+85", "-83", "-87"],
            "tax": [],
        },
    },

    # group tax seed child taxes (above)
    "attn_VAT-IN-V83-06-ROW-CC": "6% Non EU - Biens d'investissement",

    "attn_VAT-IN-V83-00-ROW-CC": {
        "invoice": {
            "base": ["+83", "+87"],
            "tax": [],
        },
        "refund": {
            "base": ["+85", "-83", "-87"],
            "tax": [],
        },
    },

    # FIXME: not sure how to manage these items
    "attn_VAT-IN-V61": "Régularisation en faveur de l'état",
    "attn_VAT-IN-V62": "Régularisation en faveur du déclarant",
}


def _get_account_tax_template_xmlid(search_name, type_tax_use):
    """Return the first account.tax.template xmlid that match name"""
    for version in ACCOUNT_TAX_NAMES:
        taxes = version.get(type_tax_use, {})
        for xmlid, name in taxes.items():
            if search_name == name:
                return xmlid
    return None


def _get_tags(env, names):
    """Get records for account.account.tag that maches names"""
    tags = env["account.account.tag"]
    for name in names:
        tag = env["account.account.tag"].search(
            [("name", "=", name)], limit=1,
        )
        tags |= tag
    return tags

def _repartition_lines_iter(account_tax):
    """Special loop over repartition lines in an account.tax"""
    for repartition in account_tax.invoice_repartition_line_ids:
        yield ("invoice", repartition)
    for repartition in account_tax.refund_repartition_line_ids:
        yield ("refund", repartition)


def update_account_tax_based_on_templates(env):
    """
    Use account.tax.template to update existing account.tax
    """
    account_tax_ids = (
        env["account.tax"]
        .with_context(active_test=False)
        .search([])
    )
    for account_tax in account_tax_ids:
        if account_tax.type_tax_use == "sale":
            type_group = "sale"
        else:
            type_group = "other"
        xmlid = _get_account_tax_template_xmlid(
            account_tax.name, type_group
        )
        new_config = NEW_ACCOUNT_TAX_CONFIG.get(xmlid)
        if isinstance(new_config, dict):
            for reptype, repartition in _repartition_lines_iter(account_tax):
                repartition.tag_ids = _get_tags(
                    env,
                    new_config[reptype][repartition.repartition_type],
                )


@openupgrade.migrate()
def migrate(env, version):
    update_account_tax_based_on_templates(env)
