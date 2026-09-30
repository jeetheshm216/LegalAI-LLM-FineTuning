"""Discovery engine for authoritative Indian Central Acts from India Code."""

import re
import json
import urllib.request
import urllib.parse
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import DiscoveredAct

# Official India Code Central Acts Registry with verified official handles & gazette bitstreams
OFFICIAL_INDIA_CODE_CENTRAL_ACTS: List[Dict[str, Any]] = [
    {
        "act_id": "COMPANIES_ACT_2013",
        "act_name": "The Companies Act, 2013",
        "short_title": "Companies Act, 2013",
        "act_number": "Act No. 18 of 2013",
        "enactment_year": 2013,
        "handle": "123456789/496128",
        "handle_url": "https://indiacode.gov.in/handle/123456789/496128",
        "text_url": "https://indiacode.gov.in/server/api/core/bitstreams/a63e1c66-2f83-41e6-90e4-930e0322ca75/content",
        "pdf_url": "https://indiacode.gov.in/server/api/core/bitstreams/df47fd71-4078-42b6-8836-c058e60fee27/content",
        "ministry": "Ministry of Corporate Affairs",
        "jurisdiction": "CENTRAL"
    },
    {
        "act_id": "IBC_2016",
        "act_name": "The Insolvency and Bankruptcy Code, 2016",
        "short_title": "Insolvency and Bankruptcy Code, 2016",
        "act_number": "Act No. 31 of 2016",
        "enactment_year": 2016,
        "handle": "123456789/496276",
        "handle_url": "https://indiacode.gov.in/handle/123456789/496276",
        "text_url": "https://indiacode.gov.in/server/api/core/bitstreams/c6dd8ae3-edef-4bf6-9c68-1efabdbe17ca/content",
        "pdf_url": "https://indiacode.gov.in/server/api/core/bitstreams/bf689ae0-08e3-47e2-92f2-1711a774254e/content",
        "ministry": "Ministry of Corporate Affairs",
        "jurisdiction": "CENTRAL"
    },
    {
        "act_id": "ARBITRATION_ACT_1996",
        "act_name": "The Arbitration and Conciliation Act, 1996",
        "short_title": "Arbitration and Conciliation Act, 1996",
        "act_number": "Act No. 26 of 1996",
        "enactment_year": 1996,
        "handle": "123456789/496493",
        "handle_url": "https://indiacode.gov.in/handle/123456789/496493",
        "text_url": "https://indiacode.gov.in/server/api/core/bitstreams/62f8d4e4-e8b8-44e7-84ae-45758a042c32/content",
        "pdf_url": "https://indiacode.gov.in/server/api/core/bitstreams/c368a901-3738-47f6-acb8-9885147945ec/content",
        "ministry": "Ministry of Law and Justice",
        "jurisdiction": "CENTRAL"
    },
    {
        "act_id": "CONSUMER_PROTECTION_ACT_2019",
        "act_name": "The Consumer Protection Act, 2019",
        "short_title": "Consumer Protection Act, 2019",
        "act_number": "Act No. 35 of 2019",
        "enactment_year": 2019,
        "handle": "123456789/496115",
        "handle_url": "https://indiacode.gov.in/handle/123456789/496115",
        "text_url": "https://indiacode.gov.in/server/api/core/bitstreams/7439fe51-6c2f-4e40-8fd0-84a47509deae/content",
        "pdf_url": "https://indiacode.gov.in/server/api/core/bitstreams/d546dfb5-3044-4661-981d-3e1771c290b9/content",
        "ministry": "Ministry of Consumer Affairs, Food and Public Distribution",
        "jurisdiction": "CENTRAL"
    },
    {
        "act_id": "TRANSFER_OF_PROPERTY_ACT_1882",
        "act_name": "The Transfer of Property Act, 1882",
        "short_title": "Transfer of Property Act, 1882",
        "act_number": "Act No. 4 of 1882",
        "enactment_year": 1882,
        "handle": "123456789/496421",
        "handle_url": "https://indiacode.gov.in/handle/123456789/496421",
        "text_url": "https://indiacode.gov.in/server/api/core/bitstreams/c21d342d-9d12-4e9b-a173-1052d31c1ff7/content",
        "pdf_url": "https://indiacode.gov.in/server/api/core/bitstreams/df9f8770-4efe-4cf9-85ba-1ea884649679/content",
        "ministry": "Ministry of Law and Justice",
        "jurisdiction": "CENTRAL"
    },
    {
        "act_id": "CPC_1908",
        "act_name": "The Code of Civil Procedure, 1908",
        "short_title": "Code of Civil Procedure, 1908",
        "act_number": "Act No. 5 of 1908",
        "enactment_year": 1908,
        "handle": "123456789/496430",
        "handle_url": "https://indiacode.gov.in/handle/123456789/496430",
        "text_url": "https://indiacode.gov.in/server/api/core/bitstreams/b7937012-4905-41ad-b114-e7e6b83a5e1f/content",
        "pdf_url": "https://indiacode.gov.in/server/api/core/bitstreams/fc9dad3f-97a9-4216-843b-934665693468/content",
        "ministry": "Ministry of Law and Justice",
        "jurisdiction": "CENTRAL"
    },
    {
        "act_id": "POCSO_ACT_2012",
        "act_name": "The Protection of Children from Sexual Offences Act, 2012",
        "short_title": "POCSO Act, 2012",
        "act_number": "Act No. 32 of 2012",
        "enactment_year": 2012,
        "handle": "123456789/496004",
        "handle_url": "https://indiacode.gov.in/handle/123456789/496004",
        "text_url": "https://indiacode.gov.in/server/api/core/bitstreams/2cc8cbca-3098-4d55-b9c1-f0b15b4bd5db/content",
        "pdf_url": "https://indiacode.gov.in/server/api/core/bitstreams/f21e8728-6f27-4c80-8fec-1688793a4dee/content",
        "ministry": "Ministry of Women and Child Development",
        "jurisdiction": "CENTRAL"
    },
    {
        "act_id": "PMLA_2002",
        "act_name": "The Prevention of Money-Laundering Act, 2002",
        "short_title": "PMLA, 2002",
        "act_number": "Act No. 15 of 2003",
        "enactment_year": 2002,
        "handle": "123456789/496293",
        "handle_url": "https://indiacode.gov.in/handle/123456789/496293",
        "text_url": "https://indiacode.gov.in/server/api/core/bitstreams/41d7b2c9-722b-4b70-98dd-28b8e4b64ced/content",
        "pdf_url": "https://indiacode.gov.in/server/api/core/bitstreams/e5a7b350-4e52-4a8f-bb47-fe0f186223e5/content",
        "ministry": "Ministry of Finance",
        "jurisdiction": "CENTRAL"
    },
    {
        "act_id": "NDPS_ACT_1985",
        "act_name": "The Narcotic Drugs and Psychotropic Substances Act, 1985",
        "short_title": "NDPS Act, 1985",
        "act_number": "Act No. 61 of 1985",
        "enactment_year": 1985,
        "handle": "123456789/496289",
        "handle_url": "https://indiacode.gov.in/handle/123456789/496289",
        "text_url": "https://indiacode.gov.in/server/api/core/bitstreams/655d309c-12f5-426c-b4d2-5d2503d9af9c/content",
        "pdf_url": "https://indiacode.gov.in/server/api/core/bitstreams/7e871cae-4f33-42ca-bcc4-0fe75bd4e65f/content",
        "ministry": "Ministry of Finance",
        "jurisdiction": "CENTRAL"
    },
    {
        "act_id": "SC_ST_POA_ACT_1989",
        "act_name": "The Scheduled Castes and the Scheduled Tribes (Prevention of Atrocities) Act, 1989",
        "short_title": "SC/ST (Prevention of Atrocities) Act, 1989",
        "act_number": "Act No. 33 of 1989",
        "enactment_year": 1989,
        "handle": "123456789/496156",
        "handle_url": "https://indiacode.gov.in/handle/123456789/496156",
        "text_url": "https://indiacode.gov.in/server/api/core/bitstreams/3733f25f-1de6-4fe7-b786-540f0f3f1757/content",
        "pdf_url": "https://indiacode.gov.in/server/api/core/bitstreams/d67f4b4f-ad81-4c64-9e89-215892887fa3/content",
        "ministry": "Ministry of Social Justice and Empowerment",
        "jurisdiction": "CENTRAL"
    },
    {
        "act_id": "MOTOR_VEHICLES_ACT_1988",
        "act_name": "The Motor Vehicles Act, 1988",
        "short_title": "Motor Vehicles Act, 1988",
        "act_number": "Act No. 59 of 1988",
        "enactment_year": 1988,
        "handle": "123456789/619305",
        "handle_url": "https://indiacode.gov.in/handle/123456789/619305",
        "text_url": "https://indiacode.gov.in/server/api/core/bitstreams/a6454f94-02bf-4188-aecc-676f2da0e51d/content",
        "pdf_url": "https://indiacode.gov.in/server/api/core/bitstreams/1d30ea4a-1331-4791-89bf-b820172bf790/content",
        "ministry": "Ministry of Road Transport and Highways",
        "jurisdiction": "CENTRAL"
    },
    {
        "act_id": "SPECIFIC_RELIEF_ACT_1963",
        "act_name": "The Specific Relief Act, 1963",
        "short_title": "Specific Relief Act, 1963",
        "act_number": "Act No. 47 of 1963",
        "enactment_year": 1963,
        "handle": "123456789/496392",
        "handle_url": "https://indiacode.gov.in/handle/123456789/496392",
        "text_url": "https://indiacode.gov.in/server/api/core/bitstreams/08b8295b-e1f9-4f93-854f-1a00429df098/content",
        "pdf_url": "https://indiacode.gov.in/server/api/core/bitstreams/d47b330c-8fdb-4a6b-9fcf-72201b62e1ba/content",
        "ministry": "Ministry of Law and Justice",
        "jurisdiction": "CENTRAL"
    },
]


class IndiaCodeDiscoveryEngine:
    """Discovers Indian Central Acts from official India Code open repositories."""

    BASE_DSPACE_API = "https://indiacode.gov.in/server/api"

    def __init__(self, registry: Optional[List[Dict[str, Any]]] = None):
        self._catalogue = registry or OFFICIAL_INDIA_CODE_CENTRAL_ACTS

    def discover_central_acts(self, limit: Optional[int] = None) -> List[DiscoveredAct]:
        """Discovers available Central Acts from official India Code records."""
        now = datetime.now().isoformat()
        discovered = []

        items = self._catalogue[:limit] if limit else self._catalogue
        for item in items:
            act = DiscoveredAct(
                act_id=item["act_id"],
                act_name=item["act_name"],
                short_title=item["short_title"],
                handle_url=item["handle_url"],
                act_number=item.get("act_number"),
                enactment_year=item.get("enactment_year"),
                pdf_url=item.get("pdf_url"),
                text_url=item.get("text_url"),
                ministry=item.get("ministry"),
                jurisdiction_level="CENTRAL",
                source_id="SRC_INDIA_CODE",
                discovery_timestamp=now,
                raw_metadata=item
            )
            discovered.append(act)

        return discovered

    def discover_by_keyword(self, query: str) -> List[DiscoveredAct]:
        """Filters catalogue by query terms (e.g., 'Companies', 'Arbitration', 'Insolvency')."""
        q_lower = query.lower()
        all_acts = self.discover_central_acts()
        return [
            act for act in all_acts
            if q_lower in act.act_name.lower() or q_lower in act.short_title.lower() or q_lower in act.act_id.lower()
        ]

    def query_live_dspace(self, query: str, size: int = 10) -> List[Dict[str, Any]]:
        """Live query against India Code's DSpace search endpoint."""
        q_enc = urllib.parse.quote(f'dc.identifier.collection:ACT AND "{query}"')
        url = f"{self.BASE_DSPACE_API}/discover/search/objects?query={q_enc}&size={size}"
        req = urllib.request.Request(url, headers={"User-Agent": "LegalAI-IndianLawyerBot/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                objects = data.get("_embedded", {}).get("searchResult", {}).get("_embedded", {}).get("objects", [])
                results = []
                for obj in objects:
                    item = obj.get("_embedded", {}).get("indexableObject", {})
                    meta = item.get("metadata", {})
                    results.append({
                        "title": meta.get("dc.title", [{}])[0].get("value"),
                        "handle": item.get("handle"),
                        "uuid": item.get("id"),
                        "state": meta.get("dc.identifier.state_name", [{}])[0].get("value")
                    })
                return results
        except Exception as e:
            return []
